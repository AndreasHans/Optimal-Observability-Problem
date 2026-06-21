from typing import Callable, List
from z3 import z3


class IndexStorage:
    """
    Storage for pre-computed Bellman equation constraints.
    This allows efficient constraint collection when the observation function Y changes.
    """

    def __init__(self, goal: int, builder: Callable[[int, int], dict[int, List[z3.BoolRef]]]):
        """
        Initialize the storage.

        Args:
            goal: The goal state index
            builder: Function that builds Bellman equations for a state
                     Returns dict mapping observation -> list of constraints
        """
        self.builder = builder
        self.goal = goal
        self.storage: dict[int, dict[int, List[z3.BoolRef]] | z3.BoolRef] = {}
        self._is_precomputed = False

    def precompute(self, size: int, goal_rew: tuple[int, z3.BoolRef | bool]) -> None:
        """
        Pre-compute Bellman equations for all states and all possible observations.

        Args:
            size: The number of states in the world
            goal_rew: Tuple of (goal_state, goal_constraint)
        """
        goal, exp_rew = goal_rew

        for state in range(size):
            if state == goal:
                # Goal state has a simple constraint: ExpRew[goal] == 0
                self.storage[goal] = exp_rew
                continue

            # Decrement the state index after processing the goal state
            state_idx = state - 1 if state > goal else state

            # Builder returns dict[obs -> List[BoolRef]]
            # Store all possible observation-conditional constraints for this state
            self.storage[state] = self.builder(state, state_idx)

        self._is_precomputed = True

    def collect(self, obs_function: list[int]) -> List[z3.BoolRef]:
        """
        Collect constraints for a specific observation function.

        Args:
            obs_function: The observation assignment for each state
                         -1 indicates goal state, otherwise obs class/sensor value

        Returns:
            List of Bellman equation constraints matching the observation function
        """
        if not self._is_precomputed:
            raise RuntimeError("Must call precompute() before collect()")

        constraints = []
        for state in range(len(obs_function)):
            obs = obs_function[state]

            if obs == -1 and state == self.goal:
                # Goal state constraint
                constraints.append(self.storage[state])
            else:
                # Non-goal state: retrieve constraints focusing on observations
                state_constraints = self.storage[state][obs]

                # Handle both single constraint and list of constraints
                if isinstance(state_constraints, list):
                    constraints.extend(state_constraints)
                else:
                    constraints.append(state_constraints)
        return constraints
