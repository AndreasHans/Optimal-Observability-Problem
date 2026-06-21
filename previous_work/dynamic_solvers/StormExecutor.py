import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import stormpy
from z3 import CheckSatResult

from previous_work.dynamic_solvers.Z3SolverResult import Z3SolverResult

# Get the directory containing this module for resolving relative paths
_MODULE_DIR = Path(__file__).parent.resolve()
import stormpy.pomdp
from stormpy import BuilderOptions, PrismProgram
from stormpy.pomdp import BeliefExplorationModelCheckerOptionsDouble

from previous_work.dynamic_solvers.builders.POMDPAdapter import POMDPAdapter
from previous_work.dynamic_solvers.builders.enums import PuzzleType
from builders.ssp import LineTPMC


@dataclass
class StormWorldConfig:
    """Configuration for a specific world type's pre-built model."""
    puzzle_type: PuzzleType
    model_path: str
    max_budget: int
    max_dim1: int                   # Line: length, Grid: width, Maze: width
    max_dim2: Optional[int] = None  # Grid: height, Maze: depth, Line: None

    def get_dimensions_dict(self) -> dict:
        """Get dimensions as a dictionary for easier access."""
        dims = {"dim1": self.max_dim1}
        if self.max_dim2 is not None:
            dims["dim2"] = self.max_dim2
        return dims

    def __str__(self) -> str:
        if self.max_dim2 is not None:
            return f"{self.puzzle_type.name}: {self.model_path} (max: {self.max_dim1}x{self.max_dim2})"
        return f"{self.puzzle_type.name}: {self.model_path} (max: {self.max_dim1})"


class StormModelRegistry:
    """Registry of available pre-built Storm models."""

    def __init__(self):
        self.configs: dict[PuzzleType, StormWorldConfig] = {}
        self._initialize_default_configs()

    def _initialize_default_configs(self):
        """Initialize with default model configurations."""
        # Resolve paths relative to the module directory
        integration_dir = _MODULE_DIR / "storm-integration"

        self.register(StormWorldConfig(
            puzzle_type=PuzzleType.LINE,
            model_path=str(integration_dir / "line.prism"),
            max_budget=50,
            max_dim1=250,  # Update based on your actual model
        ))

        self.register(StormWorldConfig(
            puzzle_type=PuzzleType.GRID,
            model_path=str(integration_dir / "grid.prism"),
            max_budget=10,
            max_dim1=10,  # width - Update based on your actual model
            max_dim2=10,   # height
        ))

        self.register(StormWorldConfig(
            puzzle_type=PuzzleType.MAZE,
            model_path=str(integration_dir / "maze.prism"),
            max_budget=30,
            max_dim1=20,  # width - Update based on your actual model
            max_dim2=10,  # depth
        ))

    def register(self, config: StormWorldConfig):
        """Register a new model configuration."""
        self.configs[config.puzzle_type] = config

    def get(self, puzzle_type: PuzzleType) -> StormWorldConfig:
        """Get configuration for a puzzle type."""
        if puzzle_type not in self.configs:
            raise ValueError(f"No model configuration found for {puzzle_type}")
        return self.configs[puzzle_type]

    def __str__(self) -> str:
        lines = ["Available Storm Models:"]
        for config in self.configs.values():
            lines.append(f"  - {config}")
        return "\n".join(lines)


def _build_world_definition_const(pomdp: POMDPAdapter, used_budget: int) -> dict[str, int]:
    world_consts = {
        "BUDGET": used_budget,
        "GOAL": pomdp.goal,
    }
    dim1, dim2 = pomdp.get_dimensions()
    match pomdp.puzzle_type:
        case PuzzleType.LINE:
            world_consts.update({"LENGTH": dim1})
        case PuzzleType.GRID:
            world_consts.update({"WIDTH": dim1})
            world_consts.update({"HEIGHT": dim2})
        case PuzzleType.MAZE:
            world_consts.update({"WIDTH": dim1})
            world_consts.update({"HEIGHT": dim2})
    return world_consts

def _build_sensor_selection_const(obs_function: list[int], max_budget: int) -> dict[str, int]:
    """Build constants mapping for sensor selections based on the observation function."""
    sensor_positions = [idx for idx, obs_value in enumerate(obs_function) if obs_value == 1]

    # Validate budget constraints based on the observation function
    if len(sensor_positions) > max_budget:
        raise ValueError(f"Observation function has {len(sensor_positions)} activated sensors,"
                         f"but the maximum admissible budget is {max_budget} in the static model.")

    # Build the dictionary of constant parameters for sensor positions
    constants = {f"POS{i+1}": position for i, position in enumerate(sensor_positions)}
    unused_sensors = {f"POS{i+1}": 0 for i in range(len(sensor_positions), max_budget)}
    constants.update(unused_sensors)
    return constants

@dataclass
class StormResult:
    type: str
    analysis_time: float
    lower_bound: float = 0.0
    upper_bound: float = 0.0
    width: float = 0.0
    reward: float = 0.0
    obs: dict[str, int] = None
    result: Optional[bool] = None
    raw: Optional[str] = None


def _parse_storm_result_from_output(output: str) -> StormResult:
    """Parse storm-pomdp result from stdout/stderr output into a dictionary."""

    # Extract timing (optional)
    timing_match = re.search(r'Time for POMDP analysis:\s*([0-9]+\.[0-9]+)s\.', output)

    # Pattern for interval results: [lower, upper] with width
    # Matches: [31/12, 3] (width=5/12) (approx. [2.583333333, 3] (width=0.4166666667))
    interval_pattern = (
        r'Result:\s*'  # "Result: "
        r'\[([^,]+),\s*([^\]]+)\]'  # [31/12, 3] - captures any content
        r'\s*\(width=([^)]+)\)'  # (width=5/12)
        r'\s*\(approx\.\s*'  # (approx. 
        r'\[([0-9.]+),\s*([0-9.]+)\]'  # [2.583333333, 3]
        r'(?:\s*\(width=([0-9.]+)\))?'  # optional (width=0.4166666667)
        r'\)'  # closing )
    )

    # Pattern for single value results: value (approx. decimal)
    single_pattern = r'Result:\s*([0-9/]+)\s*\(approx\.\s*([0-9.]+)\)'

    # Try interval pattern first
    interval_match = re.search(interval_pattern, output)
    if interval_match:
        lower_approx = float(interval_match.group(4))
        upper_approx = float(interval_match.group(5))
        width_approx = float(interval_match.group(6)) if interval_match.group(6) else None

        return StormResult(
            type="interval",
            lower_bound=lower_approx,
            upper_bound=upper_approx,
            width=width_approx,
            result=True,
            reward= upper_approx,
            analysis_time = float(timing_match.group(1)) if timing_match else None,
        )

    # Try single value pattern
    single_match = re.search(single_pattern, output)
    if single_match:
        exact_value = single_match.group(1)
        approx_value = float(single_match.group(2))

        return StormResult(
            type="exact",
            lower_bound=approx_value,
            upper_bound=approx_value,
            result=True,
            reward=approx_value,
            analysis_time=float(timing_match.group(1)) if timing_match else None,
        )

    # Fallback: try to find any "Result:" line
    fallback_pattern = r'Result:\s*([^\n]+)'
    fallback_match = re.search(fallback_pattern, output)
    if fallback_match:
        return StormResult(
            type="fallback",
            raw=fallback_match.group(1),
            result=True,
            analysis_time=float(timing_match.group(1)) if timing_match else None,
        )

    raise ValueError(f"Could not parse result from storm-pomdp output:\n{output}")

def _configure_buildfull_options() -> BuilderOptions:
    options = stormpy.BuilderOptions()
    options.set_build_all_reward_models(True)
    options.set_build_all_labels(True)
    options.set_build_choice_labels(True)
    return options

def _define_program_constants(program: PrismProgram, constants: dict[str, int]) -> PrismProgram:
    storm_mappings = {}
    manager = program.expression_manager

    for const_name, value in constants.items():
        # Retrieve variable from the parsed program's expression manager
        variable = manager.get_variable(const_name)
        expression = manager.create_integer(value)
        storm_mappings[variable] = expression

    return program.define_constants(storm_mappings)


class StormExecutor:
    """Storm-pomdp execution binder for finite-state controllers of SSP-induced POMDPs"""

    def __init__(self, verbose: bool, puzzle_type: Optional[PuzzleType] = None):
        self.puzzle_type = puzzle_type
        self.verbose = verbose
        self.model_registry = StormModelRegistry()
        self.static_program = None
        self.property = None
        self.world_config = None
        if self.puzzle_type is not None:
            self._start_prism_parsing()

    def _start_prism_parsing(self):
        """Perform parsing of the pre-built PRISM model and reward property for reaching the goal"""
        # Select the static model according to the world/puzzle type
        self.world_config = self.model_registry.get(self.puzzle_type)
        # Parse the pre-built PRISM model
        self.static_program = stormpy.parse_prism_program(self.world_config.model_path, simplify=True)
        property_str = f"Rmin=?[ F \"gameover\"]"
        # Construct the PRISM property for the minimum expected reward
        self.property = stormpy.parse_properties_for_prism_program(property_str, self.static_program)

    def _validate_pomdp(self, pomdp: POMDPAdapter, obs_function: list[int]):
        """Validate that POMDP parameters are within static model bounds."""
        if pomdp.budget > self.world_config.max_budget:
            raise ValueError(f"Budget {pomdp.budget} exceeds maximum admissible budget in the static model "
                             f"<{self.world_config.max_budget}>.")

        # if sum(obs_function) + 1 > pomdp.budget:
        #     raise ValueError(f"Observation function exceeds the budget of the declared POMDP {pomdp.budget} ")

        if len(obs_function) != pomdp.size:
            raise ValueError(f"Observation function length {len(obs_function)} "
                             f"does not match POMDP size {pomdp.size}")

        dim1, dim2 = pomdp.get_dimensions()

        if (dim1 > self.world_config.max_dim1 or
                (dim2 is not None and dim2 > self.world_config.max_dim2)):
            raise ValueError(f"Dimensions {dim1}x{dim2} exceeds maximum dimensions in the static model "
                             f"<{self.world_config.max_dim1}x{self.world_config.max_dim2}>.")

    def _build_constants_cli_string(self, obs_function: list[int], pomdp: POMDPAdapter) -> str:
        """
        Build the constants string for storm-pomdp command line.

        Args:
            obs_function: Observation function (sensor placements)
            pomdp: POMDP adapter instance

        Returns:
            Comma-separated string of constants (e.g., "N=10,GOAL=5,BUDGET=3,POS1=0,...")
        """
        # Get sensor selections
        sensor_consts = _build_sensor_selection_const(obs_function, self.world_config.max_budget)

        used_budget = obs_function.count(1)

        # Get world definition
        world_consts = _build_world_definition_const(pomdp, used_budget)

        # Combine all constants
        all_constants = {**world_consts, **sensor_consts}

        # Build comma-separated string
        const_pairs = [f"{key}={value}" for key, value in sorted(all_constants.items())]
        return ",".join(const_pairs)

    def evaluate_pomdp_fsc_binder(self, pomdp: POMDPAdapter, obs_function: list[int], timeout_ms: int):
        if self.puzzle_type is None:
            self.puzzle_type = pomdp.puzzle_type
            self._start_prism_parsing()

        self._validate_pomdp(pomdp, obs_function)

        constants = {
            **_build_sensor_selection_const(obs_function, self.world_config.max_budget),
            **_build_world_definition_const(pomdp),
        }

        # Instantiate all constant parameters in the PRISM model
        self.static_program = _define_program_constants(self.static_program, constants)

        # Build the parsed POMDP model with full labels and rewards (make it canonic)
        build_options = _configure_buildfull_options()
        model = stormpy.build_sparse_model_with_options(self.static_program, build_options)
        model = stormpy.pomdp.make_canonic(model)

        # Attempt for Sparse and Exact POMDP models (no integration for exact PMC)
        # model = stormpy.build_sparse_exact_model_with_options(self.static_program, build_options)
        # model = stormpy.pomdp.make_canonic(model)

        # TODO! Require the memory bound for belief-MDP controllers to 1 === memoryless
        # Setup belief exploration options
        belexpl_options = BeliefExplorationModelCheckerOptionsDouble(False, True)
        belexpl_options.use_state_elimination_cutoff = False
        belexpl_options.use_clipping = False
        # belexpl_options.clipping_grid_res = 25 # finer resolution -> more memory
        belexpl_options.exploration_time_limit = timeout_ms // 1000
        # Model check with Belief Exploration (memory-less belief MDP -> finite-state controller)
        checker = stormpy.pomdp.BeliefExplorationModelCheckerDouble(model, belexpl_options)

        # Set global timeout before model checking
        stormpy.set_timeout(timeout_ms // 1000)  # Timeout in seconds

        try:
            start = time.process_time()
            # Extract the underlying formula from the PRISM reward property and run the model checker
            result = checker.check(self.property[0].raw_formula, [])
            end = time.process_time()
            return StormResult(
                type='binder',
                analysis_time=end - start,
                lower_bound=result.lower_bound,
                upper_bound=result.upper_bound,
                width=abs(result.upper_bound - result.lower_bound),
                obs=pomdp.extract_obs_solution(obs_function),
                reward=result.upper_bound,
                result=True
            )
        except Exception as e:
            print(e)
            return StormResult(
                type='unknown',
                analysis_time=timeout_ms,
                lower_bound=0,
                upper_bound=0,
                width=0,
                reward=0,
                result=False
            )
        finally:
            # Reset timeout after completion
            stormpy.reset_timeout()

    def evaluate_pomdp_fsc_cli(self, pomdp: POMDPAdapter, obs_function: list[int], timeout_ms: int, memory_bound: int = 1):
        """Evaluate a POMDP using the storm-pomdp command-line tool."""
        if self.puzzle_type is None:
            self.puzzle_type = pomdp.puzzle_type
            self._start_prism_parsing()

        self._validate_pomdp(pomdp, obs_function)

        if self.verbose:
            print(f" 🚀 Evaluating POMDP via storm-pomdp CLI:")
            print(f"    Puzzle type: {self.puzzle_type.name}")
            print(f"    Size: {pomdp.size}, Goal: {pomdp.goal}, Budget: {pomdp.budget}")
            print(f"    Observation function: {obs_function}")
            print(f"    Memory-full (finite-state controller, memory-less belief exploration)")

        # Build constants string
        constants_str = self._build_constants_cli_string(obs_function, pomdp)

        try:
            # Build the storm-pomdp command
            cmd = [
                "storm-pomdp",
                "--prism", self.world_config.model_path,
                "--constants", constants_str,
                "--prop", 'Rmin=?[F "gameover"]',
                "--buildfull",
                "--belief-exploration",
                "--exact",
                "--memorybound", str(memory_bound),
                # "--exportdot", "model.dot",
            ]

            if self.verbose:
                print(f" 🔨 Running storm-pomdp...")
                print(f"    Command: {' '.join(cmd)}")

            # Execute storm-pomdp
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_ms / 1000.0,  # Convert ms to seconds
                check=True
            )

            lines = result.stdout.splitlines()
            if self.verbose:
                print(f" ✅ storm-pomdp completed successfully")
                print("\n".join(lines[-3:]))

            # Parse result from stdout
            parsed_result = _parse_storm_result_from_output("\n".join(lines[-3:]))
            parsed_result.obs = pomdp.extract_obs_solution(obs_function)
            return parsed_result

        except subprocess.TimeoutExpired:
            if self.verbose:
                print(f" ⏱️  storm-pomdp timed out after {timeout_ms}ms")
            obs = pomdp.extract_obs_solution(obs_function)
            return StormResult("timeout", timeout_ms, 0.0, 0.0, 0.0, 0.0, obs, False, None)

        except subprocess.CalledProcessError as e:
            if self.verbose:
                print(f" ❌ storm-pomdp failed with exit code {e.returncode}")
                print(f"    stderr: {e.stderr}")
            raise

        except FileNotFoundError:
            raise FileNotFoundError(
                "storm-pomdp not found in PATH. "
                "Please ensure Storm is installed and storm-pomdp is accessible."
            )

    def convert_storm_z3_result(self, input: StormResult) -> Z3SolverResult:
        sat_res = CheckSatResult((-1) ** (1 + int(input.result)) if input.result else 0)
        return Z3SolverResult(input.analysis_time, sat_res, None, input.reward)


if __name__ == "__main__":
    tpmc = LineTPMC(budget=29, goal=30, length=61)
    pomdp = POMDPAdapter(tpmc)
    exec = StormExecutor(verbose=True, puzzle_type=pomdp.puzzle_type)
    f_obs = [0] + [1]*29 + [-1] + [0]*30
    result = exec.evaluate_pomdp_fsc_cli(pomdp, f_obs, 30000)
    print(f"Reward: {result.reward} in {result.analysis_time}s")
