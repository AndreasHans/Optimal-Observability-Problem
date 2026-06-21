from abc import ABC
from itertools import chain
from typing import List, override

from z3 import z3, Or, Sum, And, Implies, Not, PbEq, PbLe

from previous_work.dynamic_solvers.builders.OOPSpec import OOPSpec
from previous_work.dynamic_solvers.builders.enums import Precision, BellmanFormat, OOPVariant
from previous_work.dynamic_solvers.utils import init_var_type


class SSPSpec(OOPSpec, ABC):
    def declare_variables(self):
        # TODO! Use pre-computed dictionary for sensor mapping (especially with multiple goals)
        # O(1) lookup - minimal overhead, big readability gain
        # self.state_to_sensor = {state: idx for idx, state in enumerate(self.nongoal_states)}
        self.console.print("\n  ⚙️  Declaring variables...", justify="center")

        nongoal_states = [s for s in range(self.size) if s != self.goal]
        self.ExpRew = self.declare_expected_rewards()
        self.Y = self.declare_observation_function(nongoal_states)
        self.X = self.declare_strategy_mapping(nongoal_states)

    def declare_observation_function(self, sensor_states: List[int]) -> List[ z3.ArithRef | z3.BoolRef ]:
        # Choice of observations on each non-goal state (state sensors)
        # e.g. `ys0 == 1` means that in state 0 the sensor is on, `ys0 == 0` - state sensor is off
        self.console.print("\n# Choice of observation on each non-goal state (state sensors that are on/off)")

        # Initialize variables based on encoding mode w/ dynamic constructor (Late-binding Factory Pattern)
        initializer = init_var_type(self.bool_encoding)
        state_to_observation = [initializer(f'ys{s}', self.ctx)
                                for s in sensor_states]

        self.console.print(state_to_observation)
        return state_to_observation

    def declare_strategy_mapping(self, sensor_states: List[int]) -> List[List[z3.ExprRef]]:
        # Action rates of strategies per state (when the sensor is on), or default strategy (when the sensor is off)
        self.console.print("\n# Action rates of strategies per state (when sensor is on), or default strategy (when the sensor is off)")

        # Parametric late-bound factory based on encoding mode
        initializer = init_var_type(self.bool_encoding and self.determinism)
        sensor_to_action = [[initializer(f'xo{s}{act}', self.ctx) for act in self.actions] for s in sensor_states]

        # Default strategy variables per action (when no sensor is observed - unknown state)
        default_policy = [initializer(f'x⊥{act}', self.ctx) for act in self.actions]
        sensor_to_action.append(default_policy)

        self.console.print(sensor_to_action)
        return sensor_to_action

    @override
    def _compute_state_bellman_bool_det(self, state: int, sensor: int) -> List[z3.BoolRef]:
        is_relaxed = (self.precision is Precision.RELAXED)
        equations = []

        for a in range(len(self.actions)):
            next_state = self.navigate(state, a)
            reward_relation = (self.ExpRew[state] >= 1 + self.ExpRew[next_state] if is_relaxed
                                else self.ExpRew[state] == 1 + self.ExpRew[next_state])

            # Next state activation -> reward computation with next state expected reward
            # TODO!: Disjunction of activations in implication lhs. for streamlining

            # Sensor on and chosen action for sensor
            activation = And(self.Y[sensor], self.X[sensor][a], self.ctx)
            equations.append(Implies(activation, reward_relation, self.ctx))

            # Sensor off and default action chosen
            activation = And(Not(self.Y[sensor], self.ctx), self.X[-1][a], self.ctx)
            equations.append(Implies(activation, reward_relation, self.ctx))
        return equations

    @override
    def _compute_state_bellman_bool_rand(self, state: int, sensor: int) -> List[z3.BoolRef]:
        is_relaxed = (self.precision is Precision.RELAXED)
        equations = []

        # Weighted next-state rewards for activated sensor
        weighted_rewards_on = Sum([self.X[sensor][a] * self.ExpRew[self.navigate(state, a)]
                                   for a in range(len(self.actions))])
        equations.append(Implies(self.Y[sensor],
                                self.ExpRew[state] >= 1 + weighted_rewards_on if is_relaxed
                                else self.ExpRew[state] == 1 + weighted_rewards_on,
                                self.ctx))

        # Weighted next-state rewards for deactivated sensor (default observation)
        weighted_rewards_off = Sum([self.X[-1][a] * self.ExpRew[self.navigate(state, a)]
                                    for a in range(len(self.actions))])
        equations.append(Implies(Not(self.Y[sensor], self.ctx),
                                self.ExpRew[state] >= 1 + weighted_rewards_off if is_relaxed
                                else self.ExpRew[state] == 1 + weighted_rewards_off,
                                self.ctx))

        return equations

    def build_action_term(self, action_idx: int, state_idx: int) -> z3.ArithRef:
        return ((1 - self.Y[state_idx]) * self.X[-1][action_idx] +
                self.Y[state_idx] * self.X[state_idx][action_idx])

    @override
    def initialize_terms(self) -> list[int]:
        """For SSP instances w/o determinism use adapted Bellman equation format."""
        if self.bellman_format is BellmanFormat.DEFAULT:
            return [] if not self.determinism else [1]
        return super().initialize_terms()

    @override
    def build_destination_rew(self, next_state: int) -> z3.ArithRef:
        """For SSP instances w/o determinism adapt Bellman equations.
        Add reward of single transition (1) to the next state's expected reward towards the goal."""
        if self.bellman_format is BellmanFormat.DEFAULT:
            return 1 + self.ExpRew[next_state] if not self.determinism else self.ExpRew[next_state]
        return super().build_destination_rew(next_state)

    def build_observation_constraints(self) -> List[z3.BoolRef]:
        # Observation function constraints - every state should be mapped to some observable class
        # For SSP, 2 observation classes exist: activated sensor or unknown - complete encoding as bools
        if self.bool_encoding:
            constraints = []
        else:
            self.console.print(f"\n# Observation function constraints - every state should be mapped to some observable class"
                               f"\n# For SSP, 2 observation classes exist: activated sensor or unknown")
            constraints = [Or(sensor == 0, sensor == 1, self.ctx) for sensor in self.Y]
            self.console.print(constraints)
        return constraints

    def build_budget_constraint(self):
        # Budget constraint - total sensors used <= budget
        self.console.print("\n# Budget constraint - total no. of sensors activated <= budget")

        is_relaxed = (self.precision is Precision.RELAXED)

        if self.bool_encoding:
            # When working with the pseudo-boolean dedicated solver, we should enforce reward monotonicity
            # Take full benefit in the distinguishability power of the full observation budget
            # constraint = PbLe([(y, 1) for y in self.Y], self.budget) # ❌ worse performance

            # Cardinality constraint equal B w/ pseudo-booleans (more performant than If(y,1,0) summation)
            constraint = PbEq([(y, 1) for y in self.Y], self.budget, self.ctx)
        else:
            if is_relaxed:
                # Relax budget in combination with Bellman-Invariance relaxation
                # Not enforcing information monotonicity for rewards - ignore the distinguishability power of obs. functions
                constraint = Sum(self.Y) <= self.budget
            else:
                constraint = Sum(self.Y) == self.budget

        self.console.print(constraint)
        return constraint

    def collect_constraints(self, threshold: str) -> List[z3.BoolRef]:
        self.console.print("\n  🛠️  Building constraints...", justify="center")

        if self.order_constraints is not None:
            builders = [
                lambda: [*self.build_fully_observable_constraints(), self.build_threshold_constraint(threshold)],
                lambda: self.build_bellman_equations(),
                lambda: [*self.build_strategy_constraints(), *self.build_observation_constraints()],
                lambda: [self.build_budget_constraint()],
            ]

            self.console.print("\nApplying order of constraints:")
            self.console.print(", ".join(f"{i} <- {order}" for (i, order) in enumerate(self.order_constraints)))

            constraints = [builders[i]() for i in self.order_constraints]

            # Flatten constraints for solver loading
            return list(chain.from_iterable(constraints))

        constraints = [
            * self.build_fully_observable_constraints(),
            * self.build_bellman_equations(),
            self.build_threshold_constraint(threshold),
            * self.build_strategy_constraints(),
            * self.build_observation_constraints(),
            self.build_budget_constraint() if not self.budget_repair else True,
        ]
        return constraints

    @override
    def repair_constraints(self) -> List[z3.BoolRef]:
        if self.budget_repair:
            return [self.build_budget_constraint()]
        return []

    @override
    def extract_obs_solution(self, obs_function: list[int]) -> dict[str, int]:
        return {f"ys{i}": obs_function[i] for i in range(self.size)}

    @override
    def variant(self):
        return OOPVariant.SSP
