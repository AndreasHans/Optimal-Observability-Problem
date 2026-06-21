from abc import ABC
from itertools import chain
from typing import List, override

from z3 import z3, Or, Sum, Implies, And, Not, PbEq

from previous_work.dynamic_solvers.builders.OOPSpec import OOPSpec
from previous_work.dynamic_solvers.builders.enums import Precision, OOPVariant
from previous_work.dynamic_solvers.utils import init_var_type


class POPSpec(OOPSpec, ABC):
    def declare_variables(self):
        self.console.print("\n  ⚙️  Declaring variables...", justify="center")
        observable_states = [s for s in range(self.size) if s != self.goal]

        self.ExpRew = self.declare_expected_rewards()
        self.Y = self.declare_observation_function(observable_states)
        self.X = self.declare_strategy_mapping()

    def declare_observation_function(self, observable_states: List[int]) -> List[List[z3.ArithRef]]:
        # Choice of observations on the states (e.g. `ys0o1 = 1` means that in state 0, observable 1 is observed)
        self.console.print("\n# Choice of observations (e.g. `ys0o1 = 1` means that in state 0, observable 1 is observed)")

        # Initialize variables based on encoding mode w/ dynamic constructor (Late-binding Factory Pattern)
        initializer = init_var_type(self.bool_encoding)
        state_to_observation = [[initializer(f'ys{s}o{o+1}', self.ctx)
                                    for o in range(self.budget)]
                                    for s in observable_states]

        self.console.print(state_to_observation)
        return state_to_observation

    def declare_strategy_mapping(self) -> List[List[z3.ArithRef]]:
        # Action rates of observation-based strategies (e.g. `xo1a = 1` means for observation 1, action `a` is taken)
        self.console.print("\n# Action rates of observation-based strategies "
                           "(e.g. `xo1a = p` means for observation 1, action `a` is taken with probability `p`).")

        # Parametric late-bound factory based on encoding mode
        initializer = init_var_type(self.bool_encoding and self.determinism)
        observation_to_action = [[initializer(f'xo{o+1}{act}', self.ctx)
                                    for act in self.actions]
                                    for o in range(self.budget)]

        self.console.print(observation_to_action)
        return observation_to_action

    @override
    def _compute_state_bellman_bool_det(self, state: int, state_idx: int) -> List[z3.BoolRef]:
        is_relaxed = (self.precision is Precision.RELAXED)
        return [
            Implies(
                And(self.Y[state_idx][o], self.X[o][a], self.ctx),
                # Bellman relaxation (≥ Invariance): identify an invariant upper bound on expected rewards (original ==)
                self.ExpRew[state] >= 1 + self.ExpRew[self.navigate(state, a)] if is_relaxed
                else self.ExpRew[state] == 1 + self.ExpRew[self.navigate(state, a)],
                self.ctx)
            for o in range(self.budget)
            for a in range(len(self.actions))
        ]

    @override
    def _compute_state_bellman_bool_rand(self, state: int, state_idx: int) -> List[z3.BoolRef]:
        is_relaxed = (self.precision is Precision.RELAXED)

        return [
            Implies(
                self.Y[state_idx][o],
                # Bellman relaxation (≥ Invariance): identify an invariant upper bound on expected rewards (original ==)
                self.ExpRew[state] >= 1 + Sum([self.ExpRew[self.navigate(state, a)] * self.X[o][a]
                                                for a in range(len(self.actions))]) if is_relaxed
                else self.ExpRew[state] == 1 + Sum([self.ExpRew[self.navigate(state, a)] * self.X[o][a]
                                                    for a in range(len(self.actions))]),
                self.ctx)
            for o in range(self.budget)
        ]

    def build_action_term(self, action_idx: int, state_idx: int):
        return Sum([self.Y[state_idx][o] * self.X[o][action_idx]
                    for o in range(self.budget)])

    def build_observation_constraints(self) -> List[z3.BoolRef]:
        # Observation function constraints - every state should be mapped to some observable class
        self.console.print("\n# Observation function constraints - every state should be mapped to a single/concrete observable class (total function)")
        constraints = []

        if self.bool_encoding:
            # Every state is assigned some observation (at least one of them, total function)
            constraints.extend([Or(*state_obs, self.ctx) for state_obs in self.Y])
            # For each state, assigned observations are mutually exclusive (if one is marked, others are refuted)
            constraints.extend([
                Implies(
                    self.Y[s][o1],
                    And(*[Not(self.Y[s][o2], self.ctx) for o2 in range(self.budget) if o2 != o1], self.ctx),
                    self.ctx)
                for s in range(len(self.Y))
                for o1 in range(self.budget)
            ])

            # Try no. 2: ITE operators to perform the sum over booleans - function maps to a single observation
            # Decidability ensured if using 1.0 (z3.Real) instead of 1 (z3.Int)
            # constraints.extend([Sum(state_obs) == 1.0 for state_obs in self.Y])

            # Try no. 3: Pseudo-Boolean equality constraint - function maps to a single observation
            constraints.extend([PbEq([(obs, 1) for obs in state_obs], 1, self.ctx) for state_obs in self.Y])
        else:
            # Every state is assigned some observation (exactly one of them, total function property)
            # Observations are either assigned or not - bind to binary values
            constraints.extend([Or(obs == 0, obs == 1, self.ctx)
                                    for state_obs in self.Y
                                    for obs in state_obs])

            # Degenerate categorical distributions (one-hot) of observation assignments for each state (only a single observation class can be assigned)
            constraints.extend([Sum(state_obs) == 1 for state_obs in self.Y])

        self.console.print(constraints)
        return constraints

    def collect_constraints(self, threshold: str) -> List[z3.BoolRef]:
        self.console.print("\n  🛠️  Building constraints...", justify="center")

        if self.order_constraints is not None:
            builders = [
                lambda: [*self.build_fully_observable_constraints(), self.build_threshold_constraint(threshold)],
                lambda: self.build_bellman_equations(),
                lambda: [*self.build_strategy_constraints(), *self.build_observation_constraints()],
                lambda: [],
            ]
            self.console.print("\nApplying order of constraints:")
            self.console.print(", ".join(f"{i} <- {order}" for (i, order) in enumerate(self.order_constraints)))
            constraints = [builders[i]() for i in self.order_constraints]

            # Flatten constraints for solver loading
            return list(chain.from_iterable(constraints))

        constraints = [
            *self.build_fully_observable_constraints(),
            *self.build_bellman_equations(),
            self.build_threshold_constraint(threshold),
            *self.build_strategy_constraints(),
            *self.build_observation_constraints(),
        ]

        return constraints

    @override
    def repair_constraints(self) -> List[z3.BoolRef]:
        return []

    @override
    def extract_obs_solution(self, obs_function: list[int]) -> dict[str, int]:
        return {f"ys{s}o{o+1}": obs_function[s] == o for s in range(self.size) for o in range(self.budget)}

    @override
    def variant(self):
        return OOPVariant.POP
