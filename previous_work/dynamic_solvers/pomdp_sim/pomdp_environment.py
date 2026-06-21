"""
POMDP Environment Simulator
============================

Generic POMDP simulator supporting different world types (Line, Grid, Maze).
Agents observe aliased observations based on the assigned observation function, not true world states.

Architecture:
    - BasePOMDPEnvironment: Abstract interface
    - LineWorld: 1D navigation
    - GridWorld: 2D grid navigation
    - MazeWorld: 2D graph navigation with obstacles
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional, List, Any

import gymnasium
import numpy as np
from gymnasium import spaces
from typing_extensions import override

from previous_work.dynamic_solvers.builders.enums import OOPVariant
from previous_work.dynamic_solvers.builders.worlds import Line, Grid, Maze, World


@dataclass
class EnvInfo:
    """Additional information returned by environment."""
    true_state: Any # The exact state for the current agent location
    observation_class: int # The observation class marking the agent location
    step_count: int # Number of steps taken in the current experience rollout


class BasePOMDPEnvironment(World, gymnasium.Env, ABC):
    """
    Abstract base class for POMDP simulated environments.

    Key concepts:
    - State space: The true underlying states (hidden from agent)
    - Observation space: Aliased observations determined by the observation function (on the world map)
    - Observation function: Observation assignment mapping true states to observation classes
    """

    def __init__(self, obs_function: np.ndarray, pomdp_variant: OOPVariant, seed: Optional[int] = None):
        """
        Args:
            obs_function: Observation assignment array mapping states to observation classes
            seed: Random seed for reproducibility
        """
        self.actions = ['up', 'right', 'down', 'left']
        self.obs_function = np.array(obs_function)
        self.pomdp_variant = pomdp_variant  # Store variant for get_observation

        if pomdp_variant is OOPVariant.SSP:
            # SSP: Sensors reveal state identity, non-sensors don't
            # Number of unique observations = n_states (one per sensor location) + 1 (no sensor)
            self.n_obs = len(obs_function)
            self.observation_space = spaces.Discrete(self.n_obs)
        else: # OOPVariant.POP
            self.n_obs = len(np.unique(obs_function))
            self.observation_space = spaces.Discrete(self.n_obs)

        self.action_space = spaces.Discrete(len(self.actions))

        self._np_random = np.random.default_rng(seed)

        self.state = None
        self.step_count = 0

    @property
    def np_random(self) -> np.random.Generator:
        """Returns the environment's internal random number generator."""
        if self._np_random is None:
            self._np_random = np.random.default_rng()
        return self._np_random

    @abstractmethod
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[int, dict]:
        """
        Reset the environment to initial state.

        Args:
            seed: Random seed for reproducibility
            options: Additional options for reset (unused)

        Returns:
            observation: Initial observation
            info: Additional information dictionary
        """
        pass

    @abstractmethod
    def step(self, action: int) -> Tuple[int, float, bool, bool, EnvInfo]:
        """
        Execute action and transition to the next state.
        Run one timestep of the environment's dynamics using the agent action.

        When the end of an episode is reached (`terminated` or `truncated`) call `.reset()` to reset the environment's
        initial state for the next episode.

        Args:
            action: Action to take

        Returns:
            observation: Observed class in the environment for the next state achieved due to the action.
            reward: Immediate reward as a result of taking the action.
            terminated: Whether the episode has reached the terminal state (goal reached).
            truncated: Whether the episode achieved the truncation condition (e.g., time limit reached).
            info: Auxiliary diagnostic information (true state, metrics)
        """
        pass

    @abstractmethod
    def transition(self, state: Any, action: int) -> Any:
        """
        State transition function.

        Args:
            state: Current state
            action: Action to execute

        Returns:
            Next state (may be stochastic)
        """
        pass

    def get_observation(self, state: Any) -> int:
        """
        Map true state to observation class using the observation function.

        Semantics:
            - POP: Returns obs_function[state] (states with same obs are aliased)
            - SSP: If obs_function[state] == 1 (sensor), returns state_idx + 1 (unique, offset to avoid collision)
                   If obs_function[state] == 0 (no sensor), returns 0 (aliased "unknown")
                   If obs_function[state] == -1 (goal), returns -1

        Args:
            state: True state (hidden from agent)

        Returns:
            Observation class that agent sees
        """
        state_idx = self._state_to_index(state)
        obs_value = self.obs_function[state_idx]

        if self.pomdp_variant == OOPVariant.SSP:
            # SSP: Sensors reveal state identity, non-sensors are aliased
            if obs_value == 1:  # Sensor present
                # Return state_idx + 1 to avoid collision with "no sensor" (0)
                return state_idx + 1  # Observations 1, 2, 3, ... for states 0, 1, 2, ...
            elif obs_value == -1:  # Goal
                return -1  # Goal marker
            else:  # No sensor (obs_value == 0)
                return 0  # Unknown observation (all non-sensor states aliased)
        else:
            # POP: Direct observation from obs_function (states can be aliased)
            return obs_value

    @abstractmethod
    def _state_to_index(self, state: Any) -> int:
        """Convert state representation to linear index for observation lookup."""
        pass

    @abstractmethod
    def _index_to_state(self, index: int) -> Any:
        """Convert linear index to state representation."""
        pass

    @property
    @abstractmethod
    def n_states(self) -> int:
        """Total number of states."""
        pass

    @property
    @abstractmethod
    def n_actions(self) -> int:
        """Total number of actions."""
        pass


class LinePOMDPEnv(Line, BasePOMDPEnvironment):
    """
    1D Line World POMDP.

    States: [0, 1, 2, ..., size-1]
    Actions: 0=left, 1=right
    Goal: Reach a specific position
    Observations: Determined by Y mapping
    """

    def __init__(
        self,
        size: int,
        goal: int,
        obs_function: np.ndarray,
        pomdp_variant: OOPVariant,
        step_penalty: float = -1.0,
        goal_reward: float = 0.0,
        stochastic: bool = False,
        slip_prob: float = 0.0,
        seed: Optional[int] = None
    ):
        """
        Args:
            size: Number of positions in the line
            goal: Goal position
            obs_function: Observation assignment [size]
            pomdp_variant: Type of POMDP (SSP or POP)
            step_penalty: Reward per step (typically negative)
            goal_reward: Reward for reaching goal
            stochastic: Whether transitions are stochastic
            slip_prob: Probability of staying in place (if stochastic)
            seed: Random seed
        """
        assert len(obs_function) == size, f"Y length {len(obs_function)} must match size {size}"
        assert 0 <= goal < size, f"Goal {goal} out of bounds [0, {size})"

        Line.__init__(self, length=size, goal=goal)
        BasePOMDPEnvironment.__init__(self, obs_function, pomdp_variant, seed)
        # Restore Line actions (BasePOMDPEnvironment.__init__ overwrites them)
        self.actions = ['l', 'r']
        self.action_space = spaces.Discrete(len(self.actions))
        self.step_penalty = step_penalty
        self.goal_reward = goal_reward
        self.stochastic = stochastic
        self.slip_prob = slip_prob

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[int, dict]:
        """Start at random position (excluding goal)."""
        self._np_random = np.random.default_rng(seed)

        valid_starts = [s for s in range(self.size) if s != self.goal]
        self.state = self.np_random.choice(valid_starts)
        self.step_count = 0

        obs = self.get_observation(self.state)
        info = {}
        return obs, info

    def step(self, action: int) -> Tuple[int, float, bool, bool, EnvInfo]:
        """Execute action in line world."""
        assert action in [0, 1], f"Invalid action {action}, must be 0 (left) or 1 (right)"

        # State transition
        next_state = self.transition(self.state, action)

        # Reward and termination
        if next_state == self.goal:
            reward = self.goal_reward
            terminated = True
        else:
            reward = self.step_penalty
            terminated = False

        truncated = False  # No time limit in this environment

        # Update state
        self.state = next_state
        self.step_count += 1

        # Get observation
        obs = self.get_observation(self.state)

        info = EnvInfo(
            true_state=self.state,
            observation_class=obs,
            step_count=self.step_count
        )

        return obs, reward, terminated, truncated, info

    def transition(self, state: int, action: int) -> int:
        """Move left (0) or right (1) along the line."""
        # Stochastic transition: slip and stay in place
        if self.stochastic and self.np_random.random() < self.slip_prob:
            return state

        # Deterministic transition through inherited World navigation
        return self.navigate(state, action)

    def _state_to_index(self, state: int) -> int:
        return state

    def _index_to_state(self, index: int) -> int:
        return index

    @property
    def n_states(self) -> int:
        return self.size

    @property
    def n_actions(self) -> int:
        return 2

    def render(self) -> str:
        """Visualize current state."""
        line = ['.' for _ in range(self.size)]
        line[self.goal] = 'G'
        line[self.state] = 'A'
        obs = self.get_observation(self.state)
        return f"[{''.join(line)}] State={self.state}, Obs={obs}"


class GridPOMDPEnv(Grid, BasePOMDPEnvironment):
    """
    2D Grid World POMDP.

    States: (row, col) positions
    Actions: 0=up, 1=right, 2=down, 3=left
    Goal: Reach a specific (row, col) position
    Observations: Determined by Y mapping
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        goal: Tuple[int, int],
        obs_function: np.ndarray,
        pomdp_variant: OOPVariant,
        step_penalty: float = -1.0,
        goal_reward: float = 0.0,
        stochastic: bool = False,
        slip_prob: float = 0.1,
        seed: Optional[int] = None
    ):
        """
        Args:
            rows: Number of rows
            cols: Number of columns
            goal: Goal position (row, col)
            obs_function: Observation assignment [rows * cols]
            pomdp_variant: Type of induced POMDP (SSP or POP)
            step_penalty: Reward per step
            goal_reward: Reward for reaching goal
            stochastic: Whether transitions are stochastic
            slip_prob: Probability of slipping (moving perpendicular)
            seed: Random seed
        """
        assert len(obs_function) == rows * cols, f"Y length {len(obs_function)} must match grid size {rows * cols}"
        assert 0 <= goal[0] < rows and 0 <= goal[1] < cols, "Goal out of bounds"

        self.rows = rows
        self.cols = cols
        self.goal_state = goal

        Grid.__init__(self, width=cols, height=rows, goal=self._state_to_index(goal))
        BasePOMDPEnvironment.__init__(self, obs_function, pomdp_variant, seed)

        # Override actions to match POMDP ordering: 0=up, 1=right, 2=down, 3=left
        self.actions = ['u', 'r', 'd', 'l']

        self.step_penalty = step_penalty
        self.goal_reward = goal_reward
        self.stochastic = stochastic
        self.slip_prob = slip_prob

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[int, dict]:
        """Start at random position (excluding goal)."""
        self._np_random = np.random.default_rng(seed)

        while True:
            row = int(self.np_random.integers(0, self.rows))
            col = int(self.np_random.integers(0, self.cols))
            if (row, col) != self.goal:
                self.state = (row, col)
                break
        self.step_count = 0

        obs = self.get_observation(self.state)
        info = {}
        return obs, info

    def step(self, action: int) -> Tuple[int, float, bool, bool, EnvInfo]:
        """Execute action in grid world."""
        assert 0 <= action < 4, f"Invalid action {action}, must be in [0, 3]"

        # State transition
        next_state = self.transition(self.state, action)

        # Reward and termination
        if next_state == self.goal:
            reward = self.goal_reward
            terminated = True
        else:
            reward = self.step_penalty
            terminated = False

        truncated = False  # No time limit in this environment

        # Update state
        self.state = next_state
        self.step_count += 1

        # Get observation
        obs = self.get_observation(self.state)

        info = EnvInfo(
            true_state=self.state,
            observation_class=obs,
            step_count=self.step_count
        )

        return obs, reward, terminated, truncated, info

    def transition(self, state: Tuple[int, int], action: int) -> Tuple[int, int]:
        """Move in grid: 0=up, 1=right, 2=down, 3=left."""
        # Stochastic transition: slip perpendicular
        if self.stochastic and self.np_random.random() < self.slip_prob:
            # Slip perpendicular to intended direction
            if action in [0, 2]:  # Up/Down -> slip Left/Right
                action = self.np_random.choice([1, 3])
            else:  # Left/Right -> slip Up/Down
                action = self.np_random.choice([0, 2])

        # Deterministic transition using inherited World.navigate() with converters
        # Convert tuple -> int, navigate, then int -> tuple
        state_idx = self._state_to_index(state)
        next_idx = self.navigate(state_idx, action)
        return self._index_to_state(next_idx)

    def _state_to_index(self, state: Tuple[int, int]) -> int:
        """Convert (row, col) to linear index."""
        row, col = state
        return row * self.cols + col

    def _index_to_state(self, index: int) -> Tuple[int, int]:
        """Convert linear index to (row, col)."""
        row = index // self.cols
        col = index % self.cols
        return (row, col)

    @property
    def n_states(self) -> int:
        return self.rows * self.cols

    @property
    def n_actions(self) -> int:
        return 4

    def render(self) -> str:
        """Visualize current grid state."""
        if self.state is None:
            raise Exception("Should call environment.reset() before rendering")

        grid = [['.' for _ in range(self.cols)] for _ in range(self.rows)]
        grid[self.goal_state[0]][self.goal_state[1]] = 'G'
        grid[self.state[0]][self.state[1]] = 'A'

        obs = self.get_observation(self.state)
        grid_str = '\n'.join([''.join(row) for row in grid])
        return f"{grid_str}\nState={self.state}, Obs={obs}"


class MazePOMDPEnv(Maze, BasePOMDPEnvironment):
    """
    2D Maze World POMDP with fixed structure.

    Structure:
    - Top row (width states): horizontal corridor connecting all columns
    - Remaining rows: 3 vertical corridors at columns 0, width//2, width-1
    - Vertical walls at intermediate columns prevent horizontal movement in lower rows

    State space: width + 3 * (depth - 1) states (walls are not states)
    """

    def __init__(
        self,
        width: int,
        depth: int,
        goal: int,
        obs_function: np.ndarray,
        pomdp_variant: OOPVariant,
        step_penalty: float = -1.0,
        goal_reward: float = 0.0,
        stochastic: bool = False,
        slip_prob: float = 0.1,
        seed: Optional[int] = None
    ):
        """
        Args:
            width: Number of columns (must be odd, e.g., 5)
            depth: Number of rows (e.g., 5)
            goal: Goal state index (0 to width + 3*(depth-1) - 1)
            obs_function: Observation assignment [width + 3*(depth-1)]
            pomdp_variant: Type of POMDP (SSP or POP)
            step_penalty: Reward per step (typically negative)
            goal_reward: Reward for reaching goal
            stochastic: Whether transitions are stochastic
            slip_prob: Probability of slipping (moving perpendicular)
            seed: Random seed
        """
        if width % 2 == 0:
            raise ValueError(f"Width must be odd for maze, got {width}")

        expected_size = width + 3 * (depth - 1)
        assert len(obs_function) == expected_size, f"Y length {len(obs_function)} must match maze size {expected_size}"
        assert 0 <= goal < expected_size, f"Goal {goal} out of bounds [0, {expected_size})"

        Maze.__init__(self, width=width, depth=depth, goal=goal)
        BasePOMDPEnvironment.__init__(self, obs_function, pomdp_variant, seed)

        # Override actions to match POMDP ordering: 0=up, 1=right, 2=down, 3=left
        self.actions = ['u', 'r', 'd', 'l']

        self.goal = goal
        self.step_penalty = step_penalty
        self.goal_reward = goal_reward
        self.stochastic = stochastic
        self.slip_prob = slip_prob

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[int, dict]:
        """Start at random position (excluding goal)."""
        self._np_random = np.random.default_rng(seed)

        valid_starts = [s for s in range(self.size) if s != self.goal]
        self.state = self.np_random.choice(valid_starts)
        self.step_count = 0

        obs = self.get_observation(self.state)
        info = {}
        return obs, info

    def step(self, action: int) -> Tuple[int, float, bool, bool, EnvInfo]:
        """Execute action in maze."""
        assert 0 <= action < 4, f"Invalid action {action}, must be in [0, 3]"

        # State transition
        next_state = self.transition(self.state, action)

        # Reward and termination
        if next_state == self.goal:
            reward = self.goal_reward
            terminated = True
        else:
            reward = self.step_penalty
            terminated = False

        truncated = False  # No time limit in this environment

        # Update state
        self.state = next_state
        self.step_count += 1

        # Get observation
        obs = self.get_observation(self.state)

        info = EnvInfo(
            true_state=self.state,
            observation_class=obs,
            step_count=self.step_count
        )

        return obs, reward, terminated, truncated, info

    def transition(self, state: int, action: int) -> int:
        """Move in maze: 0=up, 1=right, 2=down, 3=left."""
        # Stochastic transition: slip perpendicular
        if self.stochastic and self.np_random.random() < self.slip_prob:
            # Slip perpendicular to intended direction
            if action in [0, 2]:  # Up/Down -> slip Left/Right
                action = self.np_random.choice([1, 3])
            else:  # Left/Right -> slip Up/Down
                action = self.np_random.choice([0, 2])

        # Inherited Maze navigation which handles the topology deterministically
        return self.navigate(state, action)

    def _state_to_index(self, state: int) -> int:
        """Convert state to linear index (identity for maze)."""
        return state

    def _index_to_state(self, index: int) -> int:
        """Convert linear index to state (identity for maze)."""
        return index

    def _state_to_grid_pos(self, state: int) -> Tuple[int, int]:
        """Convert state index to (row, col) grid position for visualization."""
        if state < self.width:
            # Top row
            return 0, state
        else:
            # Vertical corridors
            offset = state - self.width
            row = offset // 3 + 1
            corridor_idx = offset % 3  # 0=left, 1=middle, 2=right
            col = corridor_idx * (self.width // 2)
            return row, col

    @property
    def n_states(self) -> int:
        return self.size

    @property
    def n_actions(self) -> int:
        return 4

    def render(self) -> str:
        """Visualize maze with walls."""
        # Create full grid with walls
        grid = [['#' for _ in range(self.width)] for _ in range(self.depth)]

        # Mark free positions (top row + 3 vertical corridors)
        for state in range(self.size):
            row, col = self._state_to_grid_pos(state)
            grid[row][col] = '.'

        # Add goal and agent
        goal_row, goal_col = self._state_to_grid_pos(self.goal)
        grid[goal_row][goal_col] = 'G'

        agent_row, agent_col = self._state_to_grid_pos(self.state)
        if self.state != self.goal:
            grid[agent_row][agent_col] = 'A'

        obs = self.get_observation(self.state)
        grid_str = '\n'.join([''.join(row) for row in grid])
        return f"{grid_str}\nState={self.state}, Obs={obs}, Steps={self.step_count}"


if __name__ == '__main__':
    grid_env = GridPOMDPEnv(
        rows=5, cols=5, goal=(4,3),
        obs_function=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, -1, 1]),
        pomdp_variant=OOPVariant.SSP,
        step_penalty=-1,
        goal_reward=0
    )
    obs, info = grid_env.reset()
    print(grid_env.render())
    while obs != -1:
        action_index = int(input("Action index: "))
        obs, reward, _, _, _ =  grid_env.step(action_index)
        if obs > 1:
            print(f"Observed sensor for state: {grid_env._index_to_state(obs - 1)}")
        else:
            print(f"Observed: {obs}")
    print(f"Goal achieved!")
    print(f"Info: {info}")
