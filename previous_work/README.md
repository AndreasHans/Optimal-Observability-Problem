# OOP (Optimal Observability Problem) [![DOI](https://zenodo.org/badge/784124809.svg)](https://zenodo.org/doi/10.5281/zenodo.10948053)

This repository constitutes the artefact for the CAV 2024 paper

> Alyzia Maria-Konsta, Alberto Lluch Lafuente, Christoph Matheja\
> **What should be observed for optimal reward in POMDPs?**\
> 36th International Conference on Computer Aided Verification (CAV 2024)\
> DOI: *coming soon*

Partially observable Markov Decision Processes (POMDPs) are a standard model for agents making decisions in uncertain environments. The paper studies the *Optimal Observability Problem* (OOP): Given a POMDP M, how should one change M's observation capabilities within a fixed budget such that its (minimal) expected reward remains below a given threshold?

The code provided here can be used to solve OOP problems (within the decidable fragments of the OOP) and to reproduce the results of the paper. 

# Features
* We provide scripts to automatically generate size-varying instances of the OOP for 3 parametric benchmarks of 2-dimensional POMDPs (line, grid and maze). 
* Additional parameters of the OOP that can be specified are the desidered threshold, the class of strategies (deterministic or randomized), and (when relevant) a set of fixed observations to select from.
* We provide instructions and scripts to reproduce all experiments in the CAV paper.
* We provide detailed instructions to generate and solve additional instances of the OOP.
* We provide some pre-generated models for convenience.
* We provide a script to test the correctness of our code.

# Implementation
* All the scripts are written in Python. Some of the scripts generate additional code. In particular, the scripts that generate instances of the OOP produce scripts in Python and in PRISM's input language.
* For executing the scripts provided in this repository, we have used Z3 version 4.12.4 - 64 bit, Python 3.8.10 and PRISM version 4.8.dev. 

# Docker

One can use docker to run all scripts. The corresponding dockerfile is part of this repository.
To build it, it suffices to run

```
docker build -t artifact . 
```
After that, the following command opens a shell in which one can run the scripts:

```
docker run -it artifact /bin/bash
```

For example, the following two commands can then be used to reproduce table 1 and table 2 from the paper:

```
python3 create_table_1.py

python3 create_table_2.py

```

# Installation instructions

For running the scripts it is requied to install:
* Z3 : https://github.com/Z3Prover/z3 the installation instructions are in the link. Since we use the Python wrapper it can also be installd by the command:   pip install z3-solver
* PRISM : https://www.prismmodelchecker.org/manual/InstallingPRISM/Instructions the installation instructions are in the link.

# Reproducing the results of the CAV 2024 paper

We provide scripts to recreate the results of Table 1 and Table 2 of the CAV 2024 paper: `create_table_1.py` and `create_table_2.py`.

For running the PRISM code in `create_table_2.py`, you have to enter the path of PRISM on the begining of the file (`path_to_prism`).
Also, for mac users it is required to install the package:

```
brew install coreutils

```

The timeout time is currently at 60 seconds. Example:

```
python3 create_table_1.py

python3 create_table_2.py

```
The above commands will create table_1.csv and table_2.csv. We also include the csv files in the repository. Exact timings might differ slightly depending on the used machine. For comparison, we provide the result files from a test run on the author's test machine.

The columns of the created csv files match the columns of Table 1 and Table 2 of the paper, there is a detailed analysis of each column and row in Section 5.3.

# Usage / Example (Z3)
The folders contain the models used for the experiments. The Python scripts are provided in the the folders `deterministic_strategies` and `randomised_strategies`. Each of which contains folders `POP` and `SSP`, which are two decidable fragments of the OOP.

The scripts can be run using the command: 

```
python3 script.py

```
We used the following command for measuring run time: 

```
time python3 script.py

```

For example, we can run the instance of the OOP located in folder `deterministic_strategies/POP/line/` by running 

```
python3 deterministic_strategies/POP/line/line_5_det_z3.py 

```

To obtain the following solution (It is printed in results.txt)

```
This is a solution:
[xo2r = 0,
 ys32 = 1,
 xo1r = 1,
 pi0 = 2,
 ys42 = 1,
 ys12 = 0,
 pi4 = 2,
 ys02 = 0,
 ys41 = 0,
 pi1 = 1,
 ys11 = 1,
 pi2 = 0,
 ys31 = 0,
 ys01 = 1,
 xo2l = 1,
 xo1l = 0,
 pi3 = 1]
```

The provided OOP instances in folders `deterministic_strategies` and `randomised_strategies` are only a subset of the instances considered in the paper. One can of course edit the generated code to make variations. For example, to change the threshold one can edit change the line below this comment

```
### We want to check if the minimal expected cost is below some threshold <=threshold
```

to speficy the desired threshold.

However, we provide a more convenient way to produce OOP variants,namely by using the scripts: `create*Model*.py` and `create*Model*SSP.py`. 

The script `create*Model*.py` produces the instances of the POP and the script `create*Model*SSP.py` produces instances of the SSP.

The scripts can be run as follow in the follwing example:

```
python3 createLine.py 5 2 2 '<= Q(3,2)' 0 

```

Where the input parameters are:
* size of the model (e.g. length of the line, length of the sides of the grid, etc.)
* goal state (states are numbered 0, 1, ...)
* budget 
* threshold
* determinism (if det=0 we produce the code for randomized strategies if det=1 for the deterministic ones) 

The above command generates a file `line_5_ran_z3.py` that we can run with 

```
python3 line_5_ran_z3.py

```

to botain (It is printed in results.txt)

```
This is a solution:
[xo2r = 1,
 ys32 = 0,
 xo1r = 0,
 pi0 = 2,
 ys42 = 0,
 ys12 = 1,
 pi4 = 2,
 ys02 = 1,
 ys41 = 1,
 pi1 = 1,
 ys11 = 0,
 pi2 = 0,
 ys31 = 1,
 ys01 = 0,
 xo2l = 0,
 xo1l = 1,
 pi3 = 1]
```

SSP instances are generated similarly, with the main difference being that we need to specify the fixed sensors. For example:

```
python3 createLineSSP.py 5 2 2 '<= Q(3,2)' 0 ' 0 0 | 1 1 | 3 3 | 4 4' 

```

The first arguments are the same as before. The last one indicates the available fixed  sensors: '0 0 | 1 1 | ...' indicates that state 0 emits observation 0, state 1 emits observation 1, etc.

The script obtained can be run with

```
python3 ssp_line_5_ran_z3.py

``` 

to obtain (It is printed in results.txt)

```
This is a solution:
[y3 = 1,
 xo1r = 1/2,
 xo0r = 1/2,
 pi0 = 2,
 xo4r = 0,
 y1 = 0,
 xo3r = 0,
 y4 = 1,
 xor = 1,
 pi4 = 2,
 xo4l = 1,
 y0 = 0,
 xol = 0,
 pi2 = 0,
 xo0l = 1/2,
 pi3 = 1,
 xo1l = 1/2,
 xo3l = 1,
 pi1 = 1]
```

Since generating the fixed sensors manually can be tedious, we provide a python script predefined.py that can be run to produce them. For example, 

```
python3 predefined_line.py 100

```

produces a txt file with all fixed sensors for states 0 to 99.

Similar scripts are provided for grid and maze models. For example, the maze we can use

```
python3 predefined_maze.py 3 5

```

# Usage / Example (PRISM)

The folder prism_deterministic_strategies contains the PRISM models used for the experiments. The models can be run as follows:

```
./prism -pf 'Rmin=? [F 'target']' model.sm -exact

```
We used the following command for the time: 

```
time ./prism -pf 'Rmin=? [F 'target']' model.sm -exact

```
Other models can be created using the scripts: create*Model*.py and create*Model*SSP.py included in each folder -line, grid, maze. As before create*Model*.py creates models for POP, while create*Model*SSP.py creates models for SSP. One can again use the predefined.py script to create the sequence of fixed sensors. Example of using the scripts:

```
python3 createLine.py 5 2 2 (size, target, budget)

```

```
python3 createLineSSP.py 5 2 2 '0 0 | 1 1 | 3 3 | 4 4' (size, target, budget, fixed sensors)

```
For the grid, scripts have the same usage as the line. As before the size is given for one side (size = 3 means 9 states).

Example Maze

```
python3 createMaze.py 3 5 9 4 (size of the rows, size of the columns, target, budget)

```

# Test Results

The script `test_results.py` can test the solution found for any deterministic strategy or the cases where the given threshold is the optimal one.

The solution found should be in the file `results.txt`. The input is the size of the model and the model. Example:

```
python3 line_9_det_z3.py > results.txt

python3 test_results.py 9 line

```