from typing import List

from z3 import z3, Implies, Sum, BoolRef

from previous_work.dynamic_solvers.builders.IndexStorage import IndexStorage
from previous_work.dynamic_solvers.builders.TPMCFactory import OOPVariant
from previous_work.dynamic_solvers.builders.enums import Precision
from previous_work.dynamic_solvers.builders.pop.POPSpec import POPSpec
from previous_work.dynamic_solvers.builders.ssp.SSPSpec import SSPSpec


class POMDPAdapter:
    """
    Adapter pattern: convert a tpMC specification to POMDP by fixing the observation function.

    Composition over inheritance (avoid code duplication) - Wrapper/Adapter pattern.
    Clear semantic: "POMDP is a tpMC with Y fixed"

    This adapter enables efficient evaluation of multiple observation functions by:
    1. Pre-computing Bellman equations for all possible observations
    2. Caching Y-independent constraints
    3. Quickly collecting relevant constraints for any given Y
    """

    def __init__(self, tpmc_spec: SSPSpec | POPSpec):
        """
        Create a POMDP evaluator by wrapping a tpMC specification and enforcing the observation function.

        Args:
            tpmc_spec: An initialized POPSpec or SSPSpec instance (with variables declared)
        """
        self._spec = tpmc_spec
        self._spec.Y = []
        self.mode = OOPVariant.SSP if isinstance(tpmc_spec, SSPSpec) else OOPVariant.POP
        if self._spec.determinism:
            builder = self._compute_state_bellman_det
        else:
            builder = self._compute_state_bellman_rand

        self.goal = self._spec.goal
        self.budget = self._spec.budget
        self._spec.ExpRew = self._spec.declare_expected_rewards()
        if self.mode == OOPVariant.SSP:
            self._spec.X = self._spec.declare_strategy_mapping([s for s in range(self._spec.size) if s != self.goal])
        else:
            self._spec.X = self._spec.declare_strategy_mapping()

        # Pre-compute all possible Bellman equations
        self.storage = IndexStorage(self.goal, builder)
        self.storage.precompute(self._spec.size, (self.goal, self.ExpRew[self.goal] == 0))

        # Cache Y-independent constraints (computed once, reused for all Y)
        self.obs_independent_constraints = None

    def _compute_state_bellman_det(self, state: int, state_idx: int) -> dict[int, List[z3.BoolRef]]:
        """
        Build Bellman equations for a given state for all possible observations (deterministic strategies).

        Pre-computes constraints for each possible observation value.

        Args:
            state: The actual state no. in the world
            state_idx: The index in the non-goal state list (accounting for goal removal)

        Returns:
            Dict mapping observation value -> list of Bellman equation constraints
        """
        is_relaxed = (self._spec.precision is Precision.RELAXED)

        equations = {}
        if self.mode == OOPVariant.SSP:
            iterator = [0, 1]
        else:
            iterator = range(self.budget)

        for obs in iterator:
            if self.mode == OOPVariant.SSP:
                strat_idx = state_idx if obs == 1 else -1
            else:
                strat_idx = obs

            # Collect all action implications for this observation
            obs_constraints = []
            for a in range(len(self._spec.actions)):
                next_state = self._spec.navigate(state, a)
                reward_relation = (self.ExpRew[state] >= 1 + self.ExpRew[next_state] if is_relaxed
                                  else self.ExpRew[state] == 1 + self.ExpRew[next_state])
                obs_constraints.append(
                    Implies(self.X[strat_idx][a], reward_relation, self._spec.ctx)
                )

            equations[obs] = obs_constraints

        return equations

    def _compute_state_bellman_rand(self, state: int, state_idx: int) -> dict[int, List[z3.BoolRef]]:
        """
        Build Bellman equations for a given state for all possible observations (randomized strategies).

        Pre-computes constraints for each possible observation value.

        Args:
            state: The actual state no. in the world
            state_idx: The index in the non-goal state list (accounting for goal removal)

        Returns:
            Dict mapping observation value -> list of Bellman equation constraints
        """
        is_relaxed = (self._spec.precision is Precision.RELAXED)

        equations = {}
        if self.mode == OOPVariant.SSP:
            iterator = [0, 1]
        else:
            iterator = range(self.budget)

        for obs in iterator:
            # Determine which strategy to use based on observation
            if self.mode == OOPVariant.SSP:
                strat_idx = state_idx if obs == 1 else -1
            else:
                strat_idx = obs

            # Build weighted sum of expected rewards over actions
            weighted_rewards = Sum([
                self.X[strat_idx][a] * self.ExpRew[self._spec.navigate(state, a)]
                for a in range(len(self._spec.actions))
            ])

            # For randomized strategies, there's typically one constraint per observation
            equations[obs] = ([self.ExpRew[state] >= 1 + weighted_rewards] if is_relaxed
                                else [self.ExpRew[state] == 1 + weighted_rewards])

        return equations

    def build_y_independent_constraints(self, threshold: str) -> List[z3.BoolRef]:
        """
        Build and cache constraints that don't depend on Y.

        These are computed once and reused for all observation functions.

        Args:
            threshold: Threshold constraint string (e.g., "<= 10")

        Returns:
            List of Y-independent constraints
        """
        if self.obs_independent_constraints is None:
            self.obs_independent_constraints = [
                *self._spec.build_fully_observable_constraints(),
                self._spec.build_threshold_constraint(threshold),
                *self._spec.build_strategy_constraints(),
            ]
        return self.obs_independent_constraints

    def collect_bellman_constraints(self, obs_function: list[int] | None = None) -> List[z3.BoolRef]:
        """
        Collect all constraints for the POMDP problem with the given observation function.

        Args:
            obs_function: Observation function to use. If None, uses self.Y

        Returns:
            List of all constraints for the POMDP solver
        """
        self._spec.console.print("__________________________________________________________________"
                                 "\n ♻️ Pushing Bellman equations dependent on the observation function")
        # Get Y-dependent Bellman equations (from pre-computed storage)
        bellman_equations = self.storage.collect(obs_function)
        self._spec.console.print(bellman_equations)
        self._spec.console.print(" Release scope (pop constraints)"
                                 "\n ____________________________________________________________________")
        return bellman_equations

    def infer_ssp_strategy_constraints(self, obs_function: list[int]) -> list[BoolRef]:
        strategy_constraints = []
        for state, sensor_on in enumerate(obs_function):
            if sensor_on != 1:
                continue
            for direction in self._spec.clusters:
                if state in self._spec.clusters[direction]:
                    idx = state if state < self._spec.goal else state - 1
                    for a, action in enumerate(self._spec.actions):
                        if action not in direction.actions:
                            strategy_constraints.append(self._spec.X[idx][a] == (False if self._spec.determinism else 0))
                        elif {action} == direction.actions:
                            strategy_constraints.append(self._spec.X[idx][a] == (True if self._spec.determinism else 1))
                    break
        return strategy_constraints

    # Delegate attribute access to wrapped spec for convenience
    def __getattr__(self, name):
        """Delegate attribute/method access to the wrapped tpMC spec."""
        return getattr(self._spec, name)
