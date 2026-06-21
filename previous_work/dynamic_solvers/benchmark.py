"""
Benchmarking unit for executing OOP problem instances.
Leverages existing dynamic_solvers classes for robust execution.
"""

import argparse
import csv
import gc
import multiprocessing
import os
import sys
from contextlib import nullcontext
from dataclasses import dataclass
from multiprocessing import Process, Queue
from typing import List, Dict, Any, Unpack

from alive_progress import alive_bar
from halo import Halo

from previous_work.dynamic_solvers.builders.typedicts import ExtOperationParams

TIMEOUT = 90000

@dataclass
class BenchmarkConfig(argparse.Namespace):
    """Configuration for a single benchmark instance (problem definition only)."""
    variant: str
    world: str
    budget: int
    goal: int
    threshold: str
    length: int | None = None
    width: int | None = None
    height: int | None = None
    deterministic: bool = False
    timeout: int = TIMEOUT


def _instance_worker(config: BenchmarkConfig, result_queue: Queue, hyperparams: ExtOperationParams):
    """Worker function to run a single instance loaded from the configuration.
     The solver runs in an isolated process, publishing results to the queue.
     Process-specific code with multiprocessing patterns for fresh state and proper cleanup.
     """
    try:
        # Import here to ensure fresh imports in a new process
        from previous_work.dynamic_solvers.Z3Executor import Z3Executor
        from previous_work.dynamic_solvers.builders.TPMCFactory import TPMCFactory

        # Create TPMC instance based on configuration & operational hyperparameters
        # Factory handles string-to-enum conversion at the API boundary
        tpmc_instance = TPMCFactory.create(
            config.variant, config.world,
            length=config.length,
            width=config.width,
            height=config.height,
            goal=config.goal,
            budget=config.budget,
            determinism=config.deterministic,
            **hyperparams,  # Runtime operational hyperparameters
        )

        # Create a solver and configure it
        solver = Z3Executor(tpmc_instance.ctx, verbose=False)
        solver.set_timeout(config.timeout)

        if hyperparams["cluster"] and config.variant.lower() == 'pop':
            from previous_work.dynamic_solvers.ClusterPOPSolver import ClusterPOPSolver
            cluster_solver = ClusterPOPSolver(solver, tpmc_instance, verbose=True, threshold=config.threshold)
            result = cluster_solver.solve(timeout_ms=config.timeout)
        else:
            solver.prepare_constraints(tpmc_instance, config.threshold)
            if hyperparams.get('budget_repair', False):
                result = solver.solve_2_shot_repair(tpmc_instance, config.timeout)
            else:
                result = solver.solve(config.timeout)
        solver.cleanup()

        # Determine status
        result_status = str(result.result).upper()

        # Convert reward to string if it exists (can't pickle Z3 objects)
        reward_str = str(result.reward) if result.reward is not None else None

        benchmark_result = {
            'variant': config.variant,
            'model': create_model_description(config),
            'threshold': config.threshold,
            'budget': config.budget,
            'time': result.solve_time if result.solve_time + 2 < config.timeout / 1000.0 else -1.0,
            'reward': reward_str,
            'status': result_status,
            'error': None
        }

        result_queue.put(benchmark_result)

    except Exception as e:
        result_queue.put({
            'variant': config.variant,
            'model': create_model_description(config),
            'threshold': config.threshold,
            'budget': config.budget,
            'time': None,
            'reward': "N/A",
            'status': "ERROR",
            'error': e
        })


def create_model_description(config: BenchmarkConfig) -> str:
    """Model description for interfaces"""
    if config.world == 'line':
        return f"L({config.length})"
    elif config.world == 'grid':
        return f"G({config.width}x{config.height})"
    elif config.world == 'maze':
        return f"M({config.width}x{config.height})"
    return f"{config.world.upper()}(?)"


def aggregate_trial_results(trial_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate results from multiple trials according to the specified rules:
    - All trial timeouts -> instance timeout
    - All trial unsat -> instance unsat with average runtime
    - All trial unknown -> instance unknown with average runtime
    - Any trial error -> instance error
    - Any trial SAT -> drop timeouts, average SAT runtimes
    """
    if not trial_results:
        raise ValueError("No trial results to aggregate")

    # Use first result as template
    aggregated = trial_results[0].copy()

    # Collect statuses and times
    statuses = [r['status'] for r in trial_results]
    times = [r['time'] for r in trial_results]

    # Count different outcomes
    timeout_count = sum(1 for t in times if t is None or t < 0)
    error_count = sum(1 for s in statuses if s == "ERROR")

    # Find first error message if any
    errors = [r.get('error') for r in trial_results if r.get('error') is not None]
    error_message = errors[0] if errors else None

    sat_results = [r for r in trial_results if r['status'] == 'SAT' and r['time'] > 0]
    proper_unknowns = [r for r in trial_results if r['status'] == 'UNKNOWN' and r['time'] > 0]
    unsat_results = [r for r in trial_results if r['status'] == 'UNSAT' and r['time'] > 0]

    # Apply aggregation rules
    if error_count > 0:
        # Any errors -> report error
        aggregated['status'] = 'ERROR'
        aggregated['time'] = None
        aggregated['error'] = f"One of trials failed with error: {error_message}"
        aggregated['reward'] = None
    elif timeout_count == len(trial_results):
        # All timeouts -> timeout
        aggregated['status'] = statuses[0]  # Keep original status
        aggregated['time'] = -1.0
    elif len(sat_results) > 0:
        # At least one SAT -> average SAT runtimes (drop timeouts)
        avg_time = sum(r['time'] for r in sat_results) / len(sat_results)
        aggregated['time'] = avg_time
        aggregated['status'] = 'SAT'
        aggregated['reward'] = sat_results[0]['reward']  # Use first SAT reward
    elif len(unsat_results) == len(trial_results):
        # All UNSAT -> unsat
        aggregated['status'] = 'UNSAT'
        aggregated['time'] = sum(r['time'] for r in unsat_results) / len(unsat_results)
    elif len(proper_unknowns) == len(trial_results):
        # All proper UNKNOWN -> unknown
        aggregated['status'] = 'UNKNOWN'
        aggregated['time'] = sum(r['time'] for r in proper_unknowns) / len(proper_unknowns)
    else:
        # Mixed results (shouldn't happen for deterministic problems, but handle gracefully)
        # Prefer SAT, then UNSAT, then timeout
        if len(sat_results) > 0:
            avg_time = sum(r['time'] for r in sat_results) / len(sat_results)
            aggregated['time'] = avg_time
            aggregated['status'] = 'SAT'
        elif len(unsat_results) > 0:
            aggregated['status'] = 'UNSAT'
            aggregated['time'] = sum(r['time'] for r in unsat_results) / len(unsat_results)
        elif len(proper_unknowns) > 0:
            aggregated['status'] = 'UNKNOWN'
            aggregated['time'] = sum(r['time'] for r in proper_unknowns) / len(proper_unknowns)
        else:
            aggregated['status'] = 'UNKNOWN'
            aggregated['time'] = -1.0

    return aggregated


def is_docker_environment():
    """Check if running in Docker container."""
    return (
        os.path.exists('/.dockerenv') or
        os.environ.get('DOCKER_CONTAINER') == 'true' or
        not sys.stdout.isatty()
    )


def load_configurations_from_csv_file(csv_file: str) -> List[BenchmarkConfig]:
    """Load benchmark configurations from a CSV file."""
    configs = []

    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)

        for row_num, row in enumerate(reader, start=2):
            try:
                config = BenchmarkConfig(
                    variant=row['variant'].strip().lower(),
                    world=row['world'].strip().lower(),
                    budget=int(row['budget']),
                    goal=int(row['goal']),
                    threshold=row['threshold'].strip(),
                    length=int(row['length']) if row.get('length', '').strip() else None,
                    width=int(row['width']) if row.get('width', '').strip() else None,
                    height=int(row['height']) if row.get('height', '').strip() else None,
                    deterministic=row.get('deterministic', '').strip().lower() in ['true', '1', 'yes'],
                    timeout=int(row.get('timeout', str(TIMEOUT))),
                )
                configs.append(config)

            except (ValueError, KeyError) as e:
                print(f"⚠️  Warning: Skipping invalid row {row_num} in {csv_file}: {e}")

    return configs


class BenchmarkRunner:
    """Benchmarking unit using existing dynamic_solvers infrastructure."""

    def __init__(self, output_csv: str = "benchmark_results.csv", benchmark_verbose: bool = False,
                 trials: int = 1, **hyperparams: Unpack[ExtOperationParams]):
        self.output_csv = output_csv
        self.results: List[Dict[str, Any]] = []
        self.verbose = benchmark_verbose
        self.docker_env = is_docker_environment()
        self.trials = trials

        # Operational parameters passed to all workers (runtime choices, not problem definition)
        self.op_hyperparams = hyperparams

    def load_configurations(self, csv_files: List[str]) -> List[BenchmarkConfig]:
        """Load benchmark configurations from multiple CSV files consecutively."""
        all_configs = []

        for csv_file in csv_files:

            configs = load_configurations_from_csv_file(csv_file)
            all_configs.extend(configs)

            if self.verbose:
                print(f"📂 Loaded {len(configs)} configurations from {csv_file}")

        return all_configs

    def execute_isolated_trial(self, config: BenchmarkConfig) -> Dict[str, Any]:
        """Run a single trial of a problem instance in an isolated process."""
        model_desc = create_model_description(config)

        # Create queue for result communication from processes
        result_queue : Queue[dict] = Queue()

        # Solve instance in a separate process, passing operational params
        process = Process(target=_instance_worker, args=(config, result_queue, self.op_hyperparams))
        process.start()
        process.join()  # Wait for completion

        # Get result from the queue
        if not result_queue.empty():
            benchmark_result = result_queue.get()
        else:
            benchmark_result = {
                'variant': config.variant,
                'model': model_desc,
                'threshold': config.threshold,
                'budget': config.budget,
                'time': None,
                'reward': "N/A",
                'status': "ERROR",
                'error': "Process terminated without result"
            }

        return benchmark_result

    def execute_instance(self, config: BenchmarkConfig) -> Dict[str, Any]:
        """Run a problem instance with multiple trials and aggregate results."""
        model_desc = create_model_description(config)
        instance_text = f"{config.variant.upper()} instance {model_desc} w/ B: {config.budget}; τ: '{config.threshold}'"

        halo = Halo(text=f"Running ... {instance_text}", spinner="dots12", color="magenta")
        if self.verbose and not self.docker_env:
            halo.start()

        # Run multiple trials
        trial_results = []
        for trial in range(self.trials):
            if self.verbose and self.trials > 1:
                # Clear out spinner text before adjusting it
                sys.stdout.write('\033[2K')  # Clear line
                sys.stdout.write('\r')  # Move to the beginning
                sys.stdout.flush()

                halo.text = f"Running trial ({trial + 1}/{self.trials}) ... {instance_text}"

            trial_result = self.execute_isolated_trial(config)
            trial_results.append(trial_result)

        # Aggregate results if multiple trials
        if self.trials > 1:
            benchmark_result = aggregate_trial_results(trial_results)
        else:
            benchmark_result = trial_results[0]

        # Display result accordingly
        if benchmark_result['time'] is None and benchmark_result['status'] == "ERROR":
            if self.verbose:
                halo.fail(f"Error: {instance_text} | {benchmark_result['error']}")
            return benchmark_result
        elif benchmark_result['time'] is not None and benchmark_result['time'] > 0:
            time_print = f"{benchmark_result['time']:.4f}s"
            timeout = False
        else:
            time_print = "TIMEOUT"
            timeout = True

        if self.verbose:
            # Clear out the spinner text if needed
            # sys.stdout.write('\033[1A')  # Move up
            sys.stdout.write('\033[2K')  # Clear line
            sys.stdout.write('\r')  # Move to the beginning
            sys.stdout.flush()

            trial_info = f" (avg over {self.trials} trials)" if self.trials > 1 else ""
            halo_message = (f"{"Timed-out" if timeout else " Solved"}: {instance_text} "
                            f"| Time: {time_print}{trial_info} "
                            f"| Satisfiability: {benchmark_result['status']} "
                            f"| Reward: {benchmark_result['reward'] if benchmark_result['reward'] is not None else "N/A"}\n")

            if timeout:
                halo.stop_and_persist("⌛", halo_message)
            else:
                halo.succeed(halo_message)

        return benchmark_result

    def run_benchmark(self, configs: List[BenchmarkConfig]) -> None:
        """Run all benchmark configurations."""
        print(f"🎯 Started benchmark run with {len(configs)} configurations\n")

        # Disable alive_bar in Docker environments or when verbose
        use_progress_bar = not self.verbose and not is_docker_environment()

        progress_context = (
            nullcontext() if not use_progress_bar
            else alive_bar(total=len(configs),
                           title='Benchmarking...',
                           length=20,
                           bar='smooth',
                           spinner='dots',
                           stats=False)
        )

        with progress_context as bar:
            for i, config in enumerate(configs, 1):
                result = self.execute_instance(config)
                self.results.append(result)
                if bar is not None:
                    bar()
                self.cleanup()

        print(f"\n🏁 Benchmark run completed! Results will be saved to: {self.output_csv}")

    def save_results_to_csv(self) -> None:
        """Save benchmark results to CSV file."""
        with open(self.output_csv, 'w', newline='') as file:
            writer = csv.writer(file)

            # Write headers
            writer.writerow(['Variant', 'Model', 'Threshold', 'Budget', 'Time (s)', 'Reward', 'Status', 'Error'])

            # Write results
            for result in self.results:
                writer.writerow([
                    result['variant'].upper(),
                    result['model'],
                    result['threshold'],
                    result['budget'],
                    f"{result['time']:.6f}" if result['time'] and result['time'] > 0 else "t.o.",
                    result['reward'] if result['reward'] is not None else "N/A",
                    result['status'],
                    result['error'] or ""
                ])

    def cleanup(self) -> None:
        """Call garbage collection."""
        gc.collect()


def main():
    """Main entry point for the benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Benchmark runner for OOP problem instances",
        epilog="Examples:\n  python3 benchmark.py config.csv --output results.csv\n  python3 benchmark.py config1.csv config2.csv --output results.csv"
    )

    parser.add_argument('config_csv', nargs='+', help='One or more CSV files with benchmark configurations')
    parser.add_argument('--output', '-o', default='benchmark_results.csv', help='Output CSV file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output for benchmark')
    parser.add_argument('--trials', '-t', type=int, default=1, help='Number of trials to run for each configuration (default: 1)')
    parser.add_argument('--bellman-format', '-bf', type=str, choices=['default', 'common', 'adapted'], default='default',
        help='Bellman equation format: "default" (variant-specific), "common" (with stay-in-place), "adapted" (without stay-in-place)'
    )
    parser.add_argument('--precision', '-p', type=str, choices=['strict', 'relaxed'], default='relaxed',
        help='Constraint precision mode: "strict" (equality == for optimal solutions), "relaxed" (inequality >= for Bellman, <= for budget, finding invariants)'
    )
    parser.add_argument('--real-encoding', '-re', action='store_true', help='Encoding of TPMC parameters as real variables (slow performance)')
    parser.add_argument('--budget-repair', '-br', action='store_true', help='Budget repair mode for SSP (first solve with no budget constraint, then repair the solution to fit the budget)')
    parser.add_argument('--order-constraints', '-order', type=str,
        help='Comma-separated order of assertion of HL constraint groups for OOP instances. Should be a permutation of 0,1,2,3'
    )
    parser.add_argument('--cluster', action='store_true',
        help='Use a clustering algorithm to attempt to solve all POMDPs for a POP instance. Only applicable for POP variant.'
    )

    args = parser.parse_args()

    try:
        if is_docker_environment():
            print("🐳 Detected Docker environment. Limiting stdout throughput...")

        if not args.config_csv:
            parser.print_help()
            sys.exit(1)

        print(f"\nHyperparameters:\n"
              f"   Bellman format       -> {args.bellman_format}\n"
              f"   Optimality Precision -> {args.precision}\n"
              f"   Encoding             -> {"Real" if args.real_encoding else "Boolean"}\n"
              f"   Budget Repair        -> {"✅" if args.budget_repair else "❌"}\n"
              f"   Trials no.           -> {args.trials}\n"
              f"   Verbose output       -> {"✅" if args.verbose else "❌"}\n"
              f"   Ordering             -> {args.order_constraints if args.order_constraints else "default"}")

        # Check that all config files exist
        for config_file in args.config_csv:
            if not os.path.exists(config_file):
                print(f"❌ Configuration file not found: {config_file}")
                sys.exit(1)

        # Parse order of constraints if provided
        order_constraints = args.order_constraints
        try:
            if order_constraints:
                order_constraints = list(map(int, args.order_constraints.split(',')))
                if sorted(order_constraints) != [0, 1, 2, 3]:
                    raise ValueError
        except ValueError:
            print(f"❌ Invalid order_constraints format: {order_constraints}. Must be a comma-separated permutation of 0,1,2,3.")
            sys.exit(1)

        # Run benchmarks
        runner = BenchmarkRunner(
            args.output, args.verbose, args.trials,
            verbose=False,
            bellman_format=args.bellman_format,
            precision=args.precision,
            bool_encoding=not args.real_encoding,
            budget_repair=args.budget_repair,
            order_constraints=order_constraints,
            cluster=args.cluster,
        )

        try:
            configs = runner.load_configurations(args.config_csv)

            if not configs:
                print("❌ No valid configurations found")
                sys.exit(1)

            runner.run_benchmark(configs)
            runner.save_results_to_csv()

        finally:
            runner.cleanup()

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    # Required for multiprocessing on macOS/Windows
    multiprocessing.set_start_method('spawn', force=True)
    main()
