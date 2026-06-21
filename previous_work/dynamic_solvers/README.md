# Scaling Observation-aware Planning in Uncertain Domains

# Docker

One can use Docker 🐳 to run all instances or the entire benchmark in an isolated environment. The `Dockerfile` manifest 
in the current package, installs all dependencies and lays out the entrypoint to run the scripts. The `docker-compose.yaml`
manifest configures a service that runs the benchmark module using the specified environment variables and mounts the locations
of input config files and output tables with results.

## Service
The most straightforward way to run the benchmarks from the paper tables is to deploy the composed service. Run the following
command from the current directory, to first build the Docker image and then start the service:

```bash
docker compose up --build
```
After the benchmark completes, the results will be available in the mounted `out` directory as specified by the `OUTPUT_CSV` environment variable.
To run the service in detached mode, add the `-d` flag to the command above. The service will stop automatically after the benchmark completes, however
it can be stopped using the command:

```bash
docker compose down
```


## Build
To build the image, run the following command **from the root directory** of the repository:

```bash
docker build -f dynamic_solvers/Dockerfile -t oop-artifact .
```
The image will be tagged as `oop-artifact` and be available in the local Docker image registry.

## Run
An alternative for running benchmarks is to set up an environment file containing the variables: `CONFIG_CSV`, `OUTPUT_CSV`, `VERBOSE`
For example, one can create the file `.env`:
```dotenv
 CONFIG_CSV=/configs/Pos-OOP-config.csv  # Path to the config file (list of problem instances)
 OUTPUT_CSV=/out/benchmark-Pos-POP.csv   # Path to the output CSV table with benchmark results
 VERBOSE=-v                              # Verbosity flag for logging, empty for quiet mode
```
Then one can run the benchmark module from the image entrypoint by providing the environment file and mounting the output directory as a container volume:
```bash
docker run --env-file .env -it -v "$(pwd)"/out:/out oop-artifact
```

To run a single problem instance, one can pass the `python3` command for executing the `run` module along with the necessary arguments in the argument list. 
For example, to run the `POP` variant on the `Line` with verbose output and timeout of $2$ minutes, one can use the command:

```bash
docker run -it oop-artifact 'python3 -m dynamic_solvers.run pop line -b 2 -g 124 -ln 249 -t "<= 125" --timeout 120000 -v'
```

For freedom of calling the scripts and performing multiple tasks, one can start an interactive shell in the container using the command:
```bash
docker run -it oop-artifact /bin/bash
```

For example, the following two commands can then be used to reproduce the benchmarks in table 1 and table 2 from the paper:

```bash
python3 -m dynamic_solvers.benchmark dynamic_solvers/PD-OOP-config.csv --output dynamic_solvers/PD-OOP-results.csv

python3 -m dynamic_solvers.benchmark dynamic_solvers/Pos-OOP-config.csv --output dynamic_solvers/Pos-OOP-results.csv

```

Batch edit timeout setting for benchmarking (default = 900000ms):
```bash
sed -i 's/<CURRENT_TIMEOUT>/<NEW_TIMEOUT_MS>/g' <CONFIG-FILE>
```
