# SLE-2
# BFS vs DFS Maze Path-Finding — Profiling Study

A small profiling exercise comparing **Breadth-First Search (BFS)** and
**depth-limited Depth-First Search (DFS, limit = 1000)** on randomly
generated grid mazes, using [py-spy](https://github.com/benfred/py-spy)
for CPU flame graphs and `time.perf_counter` for precise per-run timing.

## Problem

Grid-based maze path-finding: a maze with randomly placed walls, a
single start cell (top-left) and a single goal cell (bottom-right),
regenerated until solvable. Both algorithms explore neighbours in a
fixed order (up, down, left, right).

## Method

- **Timing:** `time.perf_counter()`, 5 runs per algorithm per maze
  size, 3 maze sizes (20x20, 40x40, 70x70) — 15 runs total per
  algorithm.
- **Node count:** number of states popped off the frontier (the
  queue for BFS, the stack for DFS), counted inside each function.
- **Flame graph:** `profile_heavy.py` repeats the worst-case (70x70)
  run 1,500 times per algorithm so py-spy's sampler collects enough
  data.

## Repo layout

```
maze.py              # maze generator + get_neighbors()
search.py             # bfs() and dfs(), both return (path, nodes_expanded)
run_experiments.py    # times both algorithms on 3 maze sizes, writes results.json + charts
profile_heavy.py      # heavy-repeat driver for py-spy flame graph capture
CONTRIBUTIONS.md      # log of what was AI-assisted vs done manually
```

## Running it

```bash
pip install matplotlib

# Run the timing experiment (writes results.json, fig1_maze.png, fig3_time_chart.png)
python run_experiments.py

# Capture a flame graph (requires py-spy: pip install py-spy)
py-spy record -o flamegraph.svg --rate 150 -- python profile_heavy.py
```

## Results

Across all three maze sizes, BFS always finds the true shortest path,
while DFS never does — but DFS is consistently faster and expands
fewer nodes, because on these mazes its fixed up/down/left/right
neighbour order combined with the wall layout lets it reach the goal
with less backtracking than BFS's full level-by-level sweep requires.

| Maze | BFS steps | DFS steps | BFS nodes expanded | DFS nodes expanded |
|---|---|---|---|---|
| 20x20 | 38 | 72 | 295 | 155 |
| 40x40 | 78 | 166 | 1212 | 674 |
| 70x70 | 138 | 390 | 3739 | 2421 |

(Exact figures vary slightly by run since the mazes are randomly
generated; see `results.json` after running `run_experiments.py`.)

## Takeaway

BFS is complete and optimal on an unweighted graph like a maze
(`O(b^d)` time and space) — use it whenever the shortest path
actually matters. DFS's speed advantage here is a property of this
maze's wall layout and fixed neighbour order, not a general guarantee
of DFS; a fast DFS result should never be trusted as "good enough"
without checking the path length it actually returned.

## Credits

Course: Introduction to Artificial Intelligence — SLE-2 Profiling
Report exercise. See `CONTRIBUTIONS.md` for the AI-assistance
breakdown.
