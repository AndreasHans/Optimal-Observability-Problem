import gc
import time

from z3 import (set_option, Solver, Context,
                unsat, sat, unknown, BoolRef)

from previous_work.dynamic_solvers.Z3SolverResult import Z3SolverResult
from previous_work.dynamic_solvers.builders.OOPSpec import OOPSpec
from previous_work.dynamic_solvers.builders.POMDPAdapter import POMDPAdapter


class Z3Executor:
    solver: Solver
    verbose: bool

    def __init__(self, ctx: Context, verbose: bool):
        self.verbose = verbose
        self.solver = Solver(ctx=ctx)
        self.exp_rew_formula = None
        # Set global Z3 options (call once per solver instance)
        set_option(max_args=1000000, max_lines=100000000)

    def set_timeout(self, timeout_ms: int):
        """Set solver-specific timeout."""
        self.solver.set("timeout", timeout_ms)
        return

    def wrap_timeout_check(self, timeout_ms: int):
        import threading
        result = []

        def check_wrapper():
            try:
                result.append(self.solver.check())
            except:
                result.append(unknown)

        thread = threading.Thread(target=check_wrapper, daemon=True)
        thread.start()
        thread.join(timeout_ms / 1000.0)

        if thread.is_alive():
            # Signal Z3 to interrupt its computation
            try:
                self.solver.interrupt()
                thread.join(timeout=5.0)  # Give Z3 time to cleanup gracefully
            except:
                del thread
                pass  # If interrupt fails, daemon thread won't block process exit
            return unknown

        return result[0] if len(result) > 0 else unknown

    def prepare_constraints(self, spec: OOPSpec | POMDPAdapter, threshold: str):
        """
        Prepare static constraints for either tpMC synthesis or POMDP evaluation.

        Args:
            spec: Either an OOPSpec (tpMC) or POMDPAdapter (POMDP)
            threshold: Threshold constraint string (e.g., "<= 10")
        """
        if isinstance(spec, POMDPAdapter):
            # POMDP mode: only add observation-independent constraints
            # Bellman equations will be added per observation function via add_pomdp_observation()
            base_constraints = spec.build_y_independent_constraints(threshold)
        else:
            # tpMC mode: add all constraints (including observation synthesis)
            spec.declare_variables()
            base_constraints = spec.collect_constraints(threshold)
        self.exp_rew_formula = spec.exp_rew_evaluator
        self.solver.add(base_constraints)

    def evaluate_pomdp(self, pomdp: POMDPAdapter, obs_function: list[int], timeout_ms: int,
                       extra_constraints: None | list[BoolRef] = None) -> Z3SolverResult:
        """
        Evaluate a POMDP with a specific observation function using push/pop.

        This is more efficient than creating a new solver for each observation function.

        Args:
            pomdp: The POMDPAdapter instance (must have had prepare_constraints called)
            obs_function: The observation function to evaluate
            timeout_ms: Solver timeout in milliseconds
            extra_constraints: Any other relevant constraint(s) to pass to the solver

        Returns:
            ResultOOP with solve time, result, reward, and model
        """
        # Push a new scope
        self.solver.push()
        assert len(obs_function) == pomdp.size

        try:
            # Add Bellman constraints for this observation function
            bellman_constraints = pomdp.collect_bellman_constraints(obs_function)
            self.solver.add(bellman_constraints)
            if extra_constraints:
                self.solver.add(extra_constraints)

            # Solve
            result = self.solve(timeout_ms)
            result.obs = pomdp.extract_obs_solution(obs_function)
            return result

        finally:
            # Pop the scope (removes observation-specific constraints)
            self.solver.pop()

    def solve_2_shot_repair(self, tpmc: OOPSpec, timeout_ms: int) -> Z3SolverResult:
        # First shot without budget constraint
        result = self.solve(timeout_ms)
        time_shot = result.solve_time if result.solve_time else timeout_ms
        # Attempt to repair the relaxed solution from before

        self.solver.push()
        try:
            self.solver.add(tpmc.repair_constraints())
            result = self.solve(timeout_ms)
            result.solve_time += time_shot
        finally:
            self.solver.pop()
        return result

    def solve(self, timeout_ms: int) -> Z3SolverResult:

        if self.verbose:
            print(" ⚡  Solving...")
            print()

        # Solving phase timing for benchmarks (CPU time)
        cpu_start = time.process_time()
        result = self.wrap_timeout_check(timeout_ms)
        cpu_end = time.process_time()
        solve_time = cpu_end - cpu_start

        model = None
        reward = None
        reward_frac = None
        if result == sat:
            if self.verbose:
                print(' ✅  Solution found!')
            model = self.solver.model()
            reward_frac = model.eval(self.exp_rew_formula)
            reward = reward_frac.as_fraction()
        elif result == unsat:
            if self.verbose:
                print(' ❌  No solution!')
        else:
            if self.verbose:
                print(' ❔  Unknown!')

        return Z3SolverResult(
            solve_time=solve_time,
            result=result,
            reward=reward,
            reward_frac=reward_frac,
            model=model
        )

    def cleanup(self):
        """Clean up Z3 objects."""
        if self.solver is not None:
            del self.solver
            self.solver = None
        gc.collect()

    def push(self):
        self.solver.push()

    def pop(self):
        self.solver.pop()
