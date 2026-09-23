# Contribution Log

## AI tools used
Claude (Anthropic) — helped write and structure the maze generator,
BFS/DFS implementation, the profiling/driver scripts, and the
chart/flame-graph generation scripts, plus this repo's documentation.

## What AI helped with
- Writing `maze.py` (maze generation, `get_neighbors()`)
- Writing `search.py` (`bfs()` / `dfs()` implementations)
- Setting up the py-spy flame-graph capture workflow (`profile_heavy.py`)
- Drafting the chart/figure generation code in `run_experiments.py`
  (maze plot, time-comparison bar chart)
- Laying out the README and this contribution log

## What was done manually
- Chose the maze sizes, wall densities, and random seeds for the
  best/average/worst-case comparison
- Ran `run_experiments.py` and `profile_heavy.py`
- Reviewed the numbers in `results.json`
- Checked that the flame graph output matched the raw node counts
- Wrote the justification and conclusions based on the actual data
  produced by these scripts, not from theory alone

## Log

| Date | Change |
|---|---|
| 2026-09-23 | Initial commit: maze generator, BFS/DFS, experiment runner, profiling driver, README |
