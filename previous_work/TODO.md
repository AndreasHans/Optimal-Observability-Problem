# TODO

## Architecture Design for Solving and Benchmarking

`main` (`Benchmark` class?)
- `@param` solver: `z3`, etc
- `@param` OOP variant: `POP`, `SSP`  
- `@param` map type: `line`, `grid`, `maze`  
- `@param` kwargs/args: problem parameters (`size`, `goal`, `budget`, `goal`, etc)



## Alternative 1:
At the root level of `dynamic_solvers` have a
- `main` script:
  - `argparser` for kwargs defining the problem instance
  - `tabler` for benchmarking and logging results
  - `benchmark` option: run the solver multiple times under memory/time tracking
- `tpMCSolver.py`: 
  - contains a Z3 solver instance
  - solves tpMC: `TPMCSolver.solve(instance: OOP)`
- `tpMCFactory.py`:
  - return OOP instance based on OOP variant and map type
- `builders` package for inheritance between problem variants:
    - `OOP` base class
    - `POP` variant package:
      - `POP` base class
      - `POPLine`
      - `POPGrid`
      - `POPMaze`
    - `SSP` variant package:
      - `SSP` base class
      - `SSPLine`
      - `SSPGrid`
      - `SSPMaze`

```
python3 -m dynamic_solvers.benchmark_runner dynamic_solvers/Pos-OOP-config.csv --output Pos-OOP-results.csv
```

## Cleanup work on API solvers & benchmarker:
 - [X] Aim for same performance/results as the file writing (match the constraints identically)
 - [X] Extend threshold parser to handle integers as well
 - [ ] Experiment with HTML conversion of model drawings
