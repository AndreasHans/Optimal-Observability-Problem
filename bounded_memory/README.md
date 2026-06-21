# bounded_memory

This folder contains the active bounded-memory solver workflow for OOP/BMSSP-style models (line, grid, maze) using Z3.

The standard workflow is:

1. Define experiments in CSV.
2. Run `run_batch.py`.
3. Inspect generated CSV results in `output/`.

## What This Module Does

- Builds parametric MDP families (`line`, `grid`, `maze`) from `MDPVariants.py`.
- Solves observability design constraints with several solver families.
- Supports either:
	- Threshold checking (`<k`, `<=k`, `<k/d`, `<=k/d`), or
	- Minimization mode (empty threshold).

## Requirements

- Python 3.10+ (3.11+ recommended)
- `z3-solver==4.13.0`

## Setup

From this folder:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run a Batch Experiment

Use one of the CSV files in `inputs/`:

```powershell
python run_batch.py inputs\test_6_1.csv
```

You can run any other input CSV in the same way.

## Input CSV Format

Expected columns:

```text
family,type,size,budget,memory,threshold
```

Valid values:

- `family`: `deterministic`, `randomized`, `symmetry`, `memory`, `restricted`, `forced`, `general heuristics`, `general heuristics and world`
- `type`: `line`, `grid`, `maze`
- `size`, `budget`, `memory`: integers
- `threshold`:
	- empty string for minimization mode
	- or one of: `<k`, `<=k`, `<k/d`, `<=k/d`

Example:

```csv
family,type,size,budget,memory,threshold
deterministic,line,15,1,2,<=7
randomized,grid,5,2,3,<=9/2
symmetry,maze,7,1,3,
```

## Outputs

For input `inputs/test_6_1.csv`, output is created in:

- `output/test_6_1/test_6_1.csv`

Output CSV columns:

```text
family,type,size,budget,memory,threshold,time,status,reward
```

Where:

- `status` is one of `sat`, `unsat`, `unknown`, `timeout`, `error`
- `reward` is filled only for `sat`
- `time` is solver time in seconds

Per-instance text dumps are also produced in the same output subfolder.

## Running One Instance Directly

The batch script launches `_run_one.py` internally. You can call it manually:

```powershell
python _run_one.py deterministic line 15 1 2 "<=7"
```

With dump:

```powershell
python _run_one.py deterministic line 15 1 2 "<=7" --dump output\single-run.txt
```

## Key Files

- `run_batch.py`: Batch runner with CSV parsing and result writing
- `_run_one.py`: Single-run worker in a fresh subprocess
- `BMSSP_solver_deterministic.py`: Deterministic baseline solver
- `BMSSP_solver_randomized.py`: Randomized solver
- `BMSSP_deterministic_memory_symmetry.py`: Symmetry-based heuristic variant
- `BMSSP_deterministic_MemoryRestrict.py`: Memory restriction heuristic variant
- `BMSSP_det_forced_action.py`: Forced-action heuristic variant
- `BMSSP_det_forced_restricted.py`: Combined forced-action and restricted-memory heuristic
- `BMSSP_deterministic_general_heuristics.py`: Combined heuristic solver
- `BMSSP_deterministic_general_heuristics_with_world.py`: Heuristics plus world-specific constraints

## Troubleshooting

- If `status=error`, inspect terminal output first; malformed CSV fields are a common cause.
- If runs timeout, reduce `size` or try a heuristic family (`symmetry`, `memory`, `forced`, `restricted`).
- If Z3 import fails, verify your Python interpreter has `z3-solver==4.13.0` installed.

