# Batch Runner for BMSSP Solver — Implementation Plan

## 1. Goal

Build a small Python driver that reads a CSV config file listing several BMSSP
solver instances, runs each instance (either as a threshold-check or as a
minimization problem) using either the deterministic or randomized solver,
and writes a CSV report with timing, status, and the resulting expected
reward.

Constraints:

- Pure Python.
- Only the standard library plus dependencies already used by the existing
  solvers (`z3-solver`, and whatever `MDP`/`MDPVariants` already pull in).
  No new third-party libraries.
- Runnable from the repo root, e.g. `python main/run_batch.py <config.csv>`.

## 2. Input format

A CSV file (header required) with columns:

```
family,type,size,budget,memory,threshold,verbose
```

Example:

```
family,type,size,budget,memory,threshold,verbose
deterministic,Line,7,1,2,<3,
deterministic,Maze,7,1,4,,
randomized,Grid,5,2,3,<=7/2,
deterministic,Line,4,1,2,<=10/3,
```

Column semantics:

| Column      | Type                         | Notes                                                                 |
|-------------|------------------------------|-----------------------------------------------------------------------|
| `family`    | `deterministic`/`randomized` | Case-insensitive. Selects `BMSSP_solver_deterministic` or `BMSSP_solver_randomized`. Any other value → row `error`. |
| `type`      | string                       | One of `line`, `grid`, `maze` (case-insensitive). Maps to `line_n`, `grid_corner_n`, `maze_n` in `MDPVariants.py`. |
| `size`      | int                          | `n` parameter passed to the MDP constructor.                          |
| `budget`    | int                          | Sensor budget.                                                        |
| `memory`    | int                          | Memory budget.                                                        |
| `threshold` | see below                    | Empty ⇒ **minimization mode** (`Optimize()`). Otherwise a comparator + rational: `<k`, `<=k`, `<k/d`, or `<=k/d`. |
| `verbose`   | `yes` / `no`                 | Case-insensitive. When `yes`, an extra per-row dump file is written to `main/output/` containing the `BMSSPResult` details (sensors, `pi`, `theta`, `delta`, `min_exp_rew`, solve time). When `no` (or anything else), no dump file is produced. The column is **not** echoed to the results CSV. Any value other than `yes`/`no` is treated as `no` (no error). |

Threshold parsing:

- Must start with either `<=` or `<`. The comparator chooses the
  `strict_less` argument passed to the solver: `<` → `True`, `<=` → `False`.
- The remainder is the rational value. Accepted forms:
  - `k` — integer, mapped to `(k, 1)`.
  - `k/d` — rational, mapped to `(k, d)` with `d != 0`.
- Whitespace around the comparator and value is tolerated.
- Empty/whitespace-only field ⇒ minimization mode; the comparator is
  irrelevant in that mode (internally we still default `strict_less=True`).
- Malformed threshold ⇒ row marked `error`.

Parsing rules:

- Lines starting with `#` and blank lines are skipped.
- Column order is fixed; header names are used only for validation.
- A row that fails to parse does **not** abort the batch: it is written to
  the output CSV with `status=error` and empty `time`/`reward`.

## 3. Output format

Written to **`main/output/<input-stem>.csv`** (folder auto-created). The
output filename mirrors the input filename — e.g. an input
`main/configs/experiments.csv` produces `main/output/experiments.csv`.

If the file already exists it is **overwritten** (same name as input, per
request).

Columns (same order as the input row minus `verbose`, plus three result
columns):

```
family,type,size,budget,memory,threshold,time,status,reward
```

- `family`, `type`, `size`, `budget`, `memory`, `threshold`: copied
  verbatim from the input row (threshold echoed in its original textual
  form, e.g. `<=7/2`). The `verbose` column is **not** included.
- `time`: solve time in seconds, taken from `Z3Result.solve_time` (CPU time
  already measured inside each solver's `main`). Formatted with 6 decimal
  places. Empty on timeout or error.
- `status`: one of `sat`, `unsat`, `unknown`, `timeout`, `error`.
- `reward`: the `min_exp_rew` value extracted from the Z3 model when
  `status=sat`; empty otherwise. Integers as plain `int`; rationals as
  `num/den` (e.g. `7/2`). The `csv` module handles any quoting.

### 3.1 Per-row verbose dump (when `verbose=yes`)

When a row has `verbose=yes`, an additional plain-text file is written
to `main/output/` containing the full `BMSSPResult` (the same content
`BMSSPResult.print()` produces on stdout: `min_exp_rew`, enabled
sensors, all `pi`, `theta`, `delta` values, solve time).

Filename convention (embeds all config parameters so multiple rows do
not collide):

```
<input-stem>-<family>-<type>-n<size>-b<budget>-m<memory>-t<threshold-slug>.txt
```

- `<threshold-slug>` is the raw threshold text with unsafe characters
  replaced: `<` → `lt`, `<=` → `le`, `/` → `_`. An empty threshold
  becomes `min` (for minimization). Examples:
  - `<=7/2` → `le7_2`
  - `<3` → `lt3`
  - (empty) → `min`
- Example full path:
  `main/output/sample_config-deterministic-line-n7-b1-m2-tlt3.txt`

The dump is written **only** when `status=sat` and `verbose=yes`;
for `unsat`/`unknown`/`timeout`/`error` there is nothing useful to
dump, so no file is produced.

If two rows have identical parameters, the file is overwritten (same
run semantics as the main CSV).

For any other value of `verbose` (including `no`, empty, or anything
else), no dump file is produced and nothing beyond the CSV is written.

## 4. High-level architecture

```
main/
  run_batch.py          <-- new: batch driver (spawns subprocesses)
  _run_one.py           <-- new: worker that runs one solver instance
  sample_config.csv     <-- new: smoke-test input
```

### 4.1 Dispatch model: subprocess per row

Each config row is executed by spawning a **new Python subprocess** that
runs a small worker script. This guarantees a clean Z3 state per run and
lets us enforce a hard wall-clock timeout with
`subprocess.run(..., timeout=...)`.

The existing solver CLIs print status but not a machine-readable result,
so relying on their stdout is fragile. Instead, we add a dedicated
worker `main/_run_one.py` that imports the chosen solver module, calls
its `main(...)` function, and prints a single JSON line to stdout like:

```json
{"status": "sat", "time": 0.123, "reward": "7/2"}
```

The batch runner spawns this worker and parses the last non-empty stdout
line as JSON.

Worker CLI (all args are strings, passed positionally):

```
python main/_run_one.py <family> <type> <size> <budget> <memory> <threshold>
```

where `<threshold>` is either the empty string (minimization) or the raw
`<…`/`<=…` form from the CSV. The worker does the threshold parsing
itself so the comparator and value stay together.

### 4.2 Data classes (in `run_batch.py`)

```python
@dataclass
class ConfigRow:
    family: str                 # 'deterministic' | 'randomized'
    type: str                   # 'line' | 'grid' | 'maze'
    size: int
    budget: int
    memory: int
    threshold_raw: str          # original text, echoed to output

@dataclass
class ResultRow:
    config: ConfigRow
    time: Optional[float]
    status: str                 # sat | unsat | unknown | timeout | error
    reward: Optional[str]
```

### 4.3 Control flow (`run_batch.py`)

1. Parse CLI: `python main/run_batch.py <config.csv>`.
2. Resolve output path: `main/output/<input-stem>.csv`. Create
   `main/output/` if missing. Open the output file for writing and emit
   the header.
3. Read config rows (skip blanks and `#` comments).
4. For each row:
   1. Validate and normalize fields. On failure → `ResultRow(status='error')`.
   2. Compute the verbose dump path when `verbose=yes` (using the slug
      rules in §3.1). Pass it to the worker via a `--dump <path>`
      argument. If `verbose` is not `yes`, no `--dump` argument is
      passed and the worker writes nothing extra.
   3. Spawn
      `python main/_run_one.py <family> <type> <size> <budget> <memory> <threshold_raw> [--dump <path>]`
      via `subprocess.run(..., capture_output=True, text=True, timeout=300)`.
      The 300-second (5-minute) wall-clock limit is hard-coded.
   4. On `TimeoutExpired` → `status='timeout'`, empty `time`/`reward`.
   5. On non-zero exit code or unparseable stdout → `status='error'`.
   6. On success → parse the last non-empty stdout line as JSON and
      populate `time`, `status`, `reward`.
   7. Append the row to the CSV immediately and `flush()`, so partial
      progress survives a killed batch.
5. Print a one-line summary: total, sat, unsat, unknown, timeout, error.

### 4.4 Worker flow (`_run_one.py`)

1. Parse CLI args.
2. Build the MDP via `MDPVariants` (same dispatch as the existing
   solvers).
3. Parse threshold:
   - Empty ⇒ `threshold_terms=None`, `strict_less=True` (ignored by the
     solver in minimization mode).
   - Else split comparator (`<=` or `<`) from the value; then split the
     value on `/` for `(num, den)` or `(int, 1)`.
4. Dispatch:
   - `deterministic` → `BMSSP_solver_deterministic.main(mdp, budget, threshold_terms, memory, strict_less)`.
   - `randomized` → `BMSSP_solver_randomized.main(mdp, budget, threshold_terms, memory, strict_less)`.
5. On `z3result.result == sat`, extract `min_exp_rew` from the model:

   ```python
   val = model.eval(min_exp_rew, model_completion=True)
   if val.is_int_value():
       reward = str(val.as_long())
   else:
       reward = f"{val.numerator_as_long()}/{val.denominator_as_long()}"
   ```

   `min_exp_rew` is imported from the chosen solver module (both modules
   define it at module scope).
6. If `sat` and `--dump <path>` was given, call
   `ParseModel.parse_model(z3result)` to obtain a `BMSSPResult`, then
   write the output of its `print()` method (captured via
   `contextlib.redirect_stdout` into a file handle opened at `<path>`)
   to that file. If `--dump` was not given, skip this step.
7. Print a single JSON line:
   - `sat`     → `{"status":"sat","time":<secs>,"reward":"<n>" or "<n/d>"}`
   - `unsat`   → `{"status":"unsat","time":<secs>}`
   - `unknown` → `{"status":"unknown","time":<secs>}` (no reason string)
8. Exit 0 on success; exit 1 on any internal exception (traceback goes to
   stderr, not to the output CSV).

### 4.5 Timeout handling

- Enforced by the batch runner with `subprocess.run(..., timeout=300)`.
- On timeout the subprocess is killed; the row's `time` and `reward` are
  left empty, `status='timeout'`.
- No per-row override in v1; the 5-minute limit is hard-coded.

## 5. Robustness requirements

- Unknown `family` → `error`, batch continues.
- Unknown `type` → `error`.
- Non-integer `size`/`budget`/`memory` → `error`.
- Malformed `threshold` (missing comparator, non-integer num/den, zero
  denominator) → `error`.
- Output directory `main/output/` is auto-created.

## 6. Testing / validation

- Ship `main/sample_config.csv` with rows covering: deterministic +
  threshold, deterministic + minimization, randomized + threshold, an
  intentionally unsat threshold.
- Manual smoke test: `python main/run_batch.py main/sample_config.csv`,
  cross-check against running the solvers' CLIs by hand.
- No unit tests in v1.

## 7. Work items

1. Create `main/_run_one.py` (worker).
2. Create `main/run_batch.py` (driver).
3. Add `main/sample_config.csv`.
4. Short usage snippet in `main/`'s README (or top-level README).

---

## 8. Remaining open questions

None. All prior questions have been resolved:

- The randomized solver has been extended to support minimization mode
  (`threshold_terms=None` → `Optimize()` + `solver.minimize(min_exp_rew)`)
  in parallel with the deterministic solver, so `family=randomized`
  with an empty `threshold` now works just like `family=deterministic`
  with an empty `threshold`.
- `verbose=yes` produces a per-row BMSSPResult dump file in
  `main/output/` named after the config parameters (see §3.1).
- `verbose=no` (or anything else) suppresses the dump entirely.
# Batch Runner for BMSSP Solver — Implementation Plan