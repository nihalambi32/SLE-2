"""
bfs_dfs_maze.py
All-in-one script: maze generator, BFS/DFS, experiment runner, and
py-spy profiling driver, combined into a single file.

Usage:
    python bfs_dfs_maze.py            # runs the timing experiment
                                       # (writes results.json, fig1_maze.png,
                                       # fig3_time_chart.png)

    python bfs_dfs_maze.py --heavy    # runs the heavy-repeat driver instead
                                       # (for py-spy flame-graph capture)

    py-spy record -o flamegraph.svg --rate 150 -- python bfs_dfs_maze.py --heavy
"""

import json
import random
import sys
import time
from collections import deque

import matplotlib.pyplot as plt


# ============================================================
# Maze generation
# ============================================================

def generate_maze(width, height, wall_density=0.24, seed=None):
    """
    Generate a solvable grid maze.

    Args:
        width, height: maze dimensions.
        wall_density: probability that any given non-start/goal cell
            is a wall (report uses 22-26%).
        seed: optional int for reproducible mazes.

    Returns:
        (grid, start, goal) where grid is a list[list[int]] of 0/1
        (0 = open, 1 = wall), start = (0, 0),
        goal = (height - 1, width - 1).
    """
    rng = random.Random(seed)
    start = (0, 0)
    goal = (height - 1, width - 1)

    while True:
        grid = [
            [1 if rng.random() < wall_density else 0 for _ in range(width)]
            for _ in range(height)
        ]
        grid[start[0]][start[1]] = 0
        grid[goal[0]][goal[1]] = 0

        if _is_solvable(grid, start, goal):
            return grid, start, goal


def _is_solvable(grid, start, goal):
    """Quick internal reachability check (plain BFS, no instrumentation)."""
    height, width = len(grid), len(grid[0])
    seen = {start}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        if (r, c) == goal:
            return True
        for nr, nc in get_neighbors((r, c), grid):
            if (nr, nc) not in seen:
                seen.add((nr, nc))
                queue.append((nr, nc))
    return False


def get_neighbors(cell, grid):
    """
    Return valid, in-bounds, non-wall neighbours of `cell` in a fixed
    order: up, down, left, right. This fixed order matters for DFS,
    since DFS's path (and therefore its speed) is sensitive to the
    order neighbours are generated in.
    """
    r, c = cell
    height, width = len(grid), len(grid[0])
    neighbors = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):  # up, down, left, right
        nr, nc = r + dr, c + dc
        if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == 0:
            neighbors.append((nr, nc))
    return neighbors


# ============================================================
# Search algorithms
# ============================================================

def _reconstruct_path(came_from, start, goal):
    if goal not in came_from and goal != start:
        return None
    path = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return path


def bfs(grid, start, goal):
    """
    Breadth-first search. Complete and optimal on an unweighted grid.
    Returns (path, nodes_expanded).
    """
    frontier = deque([start])
    came_from = {}
    seen = {start}
    nodes_expanded = 0

    while frontier:
        current = frontier.popleft()
        nodes_expanded += 1

        if current == goal:
            return _reconstruct_path(came_from, start, goal), nodes_expanded

        for neighbor in get_neighbors(current, grid):
            if neighbor not in seen:
                seen.add(neighbor)
                came_from[neighbor] = current
                frontier.append(neighbor)

    return None, nodes_expanded


def dfs(grid, start, goal, depth_limit=1000):
    """
    Depth-limited depth-first search. Not guaranteed to find the
    shortest path -- only *a* path, if one exists within depth_limit.
    Uses an explicit stack of (cell, depth) pairs rather than
    recursion, to avoid hitting Python's recursion limit on large
    mazes. Returns (path, nodes_expanded).
    """
    frontier = [(start, 0)]
    came_from = {}
    seen = {start}
    nodes_expanded = 0

    while frontier:
        current, depth = frontier.pop()
        nodes_expanded += 1

        if current == goal:
            return _reconstruct_path(came_from, start, goal), nodes_expanded

        if depth >= depth_limit:
            continue

        for neighbor in get_neighbors(current, grid):
            if neighbor not in seen:
                seen.add(neighbor)
                came_from[neighbor] = current
                frontier.append((neighbor, depth + 1))

    return None, nodes_expanded


# ============================================================
# Timing experiment (default mode)
# ============================================================

TEST_CASES = [
    {"name": "20x20 (best case)", "size": 20, "seed": 1},
    {"name": "40x40 (average case)", "size": 40, "seed": 2},
    {"name": "70x70 (worst case)", "size": 70, "seed": 3},
]
RUNS_PER_CASE = 5


def time_algorithm(fn, grid, start, goal, runs=RUNS_PER_CASE):
    times = []
    path, nodes_expanded = None, 0
    for _ in range(runs):
        t0 = time.perf_counter()
        path, nodes_expanded = fn(grid, start, goal)
        times.append(time.perf_counter() - t0)
    return {
        "avg_time_s": sum(times) / len(times),
        "min_time_s": min(times),
        "max_time_s": max(times),
        "path_len": len(path) - 1 if path else None,  # steps, not cells
        "nodes_expanded": nodes_expanded,
    }


def _plot_maze(grid, start, goal, out_path):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(grid, cmap="binary")
    ax.scatter(*start[::-1], c="green", s=80, label="start")
    ax.scatter(*goal[::-1], c="red", s=80, label="goal")
    ax.set_title("Maze layout")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _plot_times(results, out_path):
    names = list(results.keys())
    bfs_times = [results[n]["bfs"]["avg_time_s"] * 1000 for n in names]
    dfs_times = [results[n]["dfs"]["avg_time_s"] * 1000 for n in names]

    x = range(len(names))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([i - width / 2 for i in x], bfs_times, width, label="BFS")
    ax.bar([i + width / 2 for i in x], dfs_times, width, label="DFS")
    ax.set_xticks(list(x))
    ax.set_xticklabels(names, rotation=15, ha="right")
    ax.set_ylabel("Avg time (ms)")
    ax.set_title("BFS vs DFS: average runtime per maze size")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def run_timing_experiment():
    results = {}
    first_maze_fig_saved = False

    for case in TEST_CASES:
        grid, start, goal = generate_maze(
            case["size"], case["size"], wall_density=0.24, seed=case["seed"]
        )
        results[case["name"]] = {
            "bfs": time_algorithm(bfs, grid, start, goal),
            "dfs": time_algorithm(dfs, grid, start, goal),
        }

        if not first_maze_fig_saved:
            _plot_maze(grid, start, goal, "fig1_maze.png")
            first_maze_fig_saved = True

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    _plot_times(results, "fig3_time_chart.png")

    print("Done. Wrote results.json, fig1_maze.png, fig3_time_chart.png")
    for name, r in results.items():
        print(f"\n{name}")
        print(f"  BFS: {r['bfs']['path_len']} steps, "
              f"{r['bfs']['nodes_expanded']} nodes, "
              f"{r['bfs']['avg_time_s']*1000:.2f} ms avg")
        print(f"  DFS: {r['dfs']['path_len']} steps, "
              f"{r['dfs']['nodes_expanded']} nodes, "
              f"{r['dfs']['avg_time_s']*1000:.2f} ms avg")


# ============================================================
# Heavy-repeat driver (for py-spy flame graph capture: --heavy)
# ============================================================

HEAVY_REPEATS = 1500
HEAVY_MAZE_SIZE = 70


def run_heavy_profile():
    grid, start, goal = generate_maze(
        HEAVY_MAZE_SIZE, HEAVY_MAZE_SIZE, wall_density=0.24, seed=3
    )

    for _ in range(HEAVY_REPEATS):
        bfs(grid, start, goal)

    for _ in range(HEAVY_REPEATS):
        dfs(grid, start, goal)


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    if "--heavy" in sys.argv:
        run_heavy_profile()
    else:
        run_timing_experiment()
