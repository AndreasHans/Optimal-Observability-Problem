"""
Q-Learning Algorithm for POMDP Policy Learning (Inner Loop)
============================================================

Implements observation-based Q-learning to learn policies for fixed Y.
The agent maintains Q(observation, action) without explicit belief tracking.
"""

import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass
from previous_work.dynamic_solvers.pomdp_sim.pomdp_environment import BasePOMDPEnvironment


@dataclass
class TrainingMetrics:
    """Metrics collected during training."""
    episode_rewards: List[float]
    episode_lengths: List[int]
    epsilon_values: List[float]


class ObservationQLearning:
    """
    Observation-based Q-learning for POMDPs.

    Learns Q(observation, action) without explicit belief state tracking.
    Simpler than belief-based methods but can still learn good policies
    if observation assignment Y provides sufficient information.
    """

    def __init__(
        self,
        n_obs: int,
        n_actions: int,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
        seed: Optional[int] = None
    ):
        """
        Args:
            n_obs: Number of observation classes
            n_actions: Number of actions
            learning_rate: Learning rate (alpha)
            discount_factor: Discount factor (gamma)
            epsilon_start: Initial exploration rate
            epsilon_end: Minimum exploration rate
            epsilon_decay: Decay rate for epsilon
            seed: Random seed
        """
        self.n_obs = n_obs
        self.n_actions = n_actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        self.rng = np.random.RandomState(seed)

        # Initialize Q-table
        self.Q = np.zeros((n_obs, n_actions))

        # Training statistics
        self.total_steps = 0
        self.episodes_trained = 0

    def select_action(self, obs: int, epsilon: Optional[float] = None) -> int:
        """
        Select action using epsilon-greedy policy.

        Args:
            obs: Current observation
            epsilon: Exploration rate (uses self.epsilon if None)

        Returns:
            Selected action
        """
        if epsilon is None:
            epsilon = self.epsilon

        if self.rng.rand() < epsilon:
            # Explore: random action
            return self.rng.randint(0, self.n_actions)
        else:
            # Exploit: best action
            return int(np.argmax(self.Q[obs]))

    def update(
        self,
        obs: int,
        action: int,
        reward: float,
        next_obs: int,
        done: bool
    ) -> float:
        """
        Q-learning update rule.

        Q(s,a) <- Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]

        Args:
            obs: Current observation
            action: Action taken
            reward: Reward received
            next_obs: Next observation
            done: Whether episode terminated

        Returns:
            TD error (for monitoring)
        """
        # Current Q-value
        current_q = self.Q[obs, action]

        # Target Q-value
        if done:
            target_q = reward
        else:
            target_q = reward + self.gamma * np.max(self.Q[next_obs])

        # TD error
        td_error = target_q - current_q

        # Update Q-value
        self.Q[obs, action] += self.lr * td_error

        return td_error

    def train_episode(
        self,
        env: BasePOMDPEnvironment,
        max_steps: int = 1000
    ) -> Tuple[float, int]:
        """
        Train for one episode.

        Args:
            env: POMDP environment
            max_steps: Maximum steps per episode

        Returns:
            total_reward: Cumulative reward
            steps: Number of steps taken
        """
        obs = env.reset()
        total_reward = 0.0
        steps = 0

        for step in range(max_steps):
            # Select action
            action = self.select_action(obs)

            # Execute action
            next_obs, reward, done, info = env.step(action)

            # Update Q-table
            self.update(obs, action, reward, next_obs, done)

            # Accumulate reward and update state
            total_reward += reward
            obs = next_obs
            steps += 1
            self.total_steps += 1

            if done:
                break

        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        self.episodes_trained += 1

        return total_reward, steps

    def train(
        self,
        env: BasePOMDPEnvironment,
        n_episodes: int,
        max_steps: int = 1000,
        verbose: bool = False,
        eval_interval: int = 100
    ) -> TrainingMetrics:
        """
        Train for multiple episodes.

        Args:
            env: POMDP environment
            n_episodes: Number of training episodes
            max_steps: Maximum steps per episode
            verbose: Print progress
            eval_interval: Print stats every N episodes

        Returns:
            Training metrics
        """
        metrics = TrainingMetrics(
            episode_rewards=[],
            episode_lengths=[],
            epsilon_values=[]
        )

        for episode in range(n_episodes):
            reward, length = self.train_episode(env, max_steps)

            metrics.episode_rewards.append(reward)
            metrics.episode_lengths.append(length)
            metrics.epsilon_values.append(self.epsilon)

            if verbose and (episode + 1) % eval_interval == 0:
                avg_reward = np.mean(metrics.episode_rewards[-eval_interval:])
                avg_length = np.mean(metrics.episode_lengths[-eval_interval:])
                print(f"Episode {episode+1}/{n_episodes}: "
                      f"Avg Reward={avg_reward:.2f}, "
                      f"Avg Length={avg_length:.1f}, "
                      f"Epsilon={self.epsilon:.3f}")

        return metrics

    def evaluate(
        self,
        env: BasePOMDPEnvironment,
        n_episodes: int = 10,
        max_steps: int = 1000,
        render: bool = False
    ) -> Tuple[float, float]:
        """
        Evaluate learned policy (greedy, no exploration).

        Args:
            env: POMDP environment
            n_episodes: Number of evaluation episodes
            max_steps: Maximum steps per episode
            render: Whether to print episode trajectory

        Returns:
            avg_reward: Average reward per episode
            avg_length: Average episode length
        """
        rewards = []
        lengths = []

        for episode in range(n_episodes):
            obs = env.reset()
            total_reward = 0.0
            steps = 0

            if render:
                print(f"\n--- Evaluation Episode {episode+1} ---")
                print(env.render())

            for step in range(max_steps):
                # Greedy action selection (no exploration)
                action = self.select_action(obs, epsilon=0.0)

                # Execute action
                next_obs, reward, done, info = env.step(action)

                if render:
                    print(env.render())

                total_reward += reward
                obs = next_obs
                steps += 1

                if done:
                    if render:
                        print(f"Goal reached! Reward={total_reward:.1f}, Steps={steps}")
                    break

            rewards.append(total_reward)
            lengths.append(steps)

        avg_reward = np.mean(rewards)
        avg_length = np.mean(lengths)

        return avg_reward, avg_length

    def get_policy(self) -> np.ndarray:
        """
        Extract learned policy as π(obs) -> action.

        Returns:
            Policy array of shape [n_obs]
        """
        return np.argmax(self.Q, axis=1)

    def save(self, filepath: str):
        """Save Q-table to file."""
        np.save(filepath, self.Q)

    def load(self, filepath: str):
        """Load Q-table from file."""
        self.Q = np.load(filepath)

    def reset_statistics(self):
        """Reset training statistics."""
        self.total_steps = 0
        self.episodes_trained = 0

    def __repr__(self) -> str:
        return (f"ObservationQLearning(n_obs={self.n_obs}, "
                f"n_actions={self.n_actions}, "
                f"episodes_trained={self.episodes_trained}, "
                f"total_steps={self.total_steps})")


class SarsaLearning(ObservationQLearning):
    """
    SARSA: On-policy variant of Q-learning.

    Uses (S, A, R, S', A') instead of (S, A, R, S').
    More conservative than Q-learning.
    """

    def train_episode(
        self,
        env: BasePOMDPEnvironment,
        max_steps: int = 1000
    ) -> Tuple[float, int]:
        """Train one episode using SARSA updates."""
        obs = env.reset()
        action = self.select_action(obs)
        total_reward = 0.0
        steps = 0

        for step in range(max_steps):
            # Execute action
            next_obs, reward, done, info = env.step(action)

            # Select next action
            next_action = self.select_action(next_obs)

            # SARSA update: use next_action (not max)
            current_q = self.Q[obs, action]
            if done:
                target_q = reward
            else:
                target_q = reward + self.gamma * self.Q[next_obs, next_action]

            td_error = target_q - current_q
            self.Q[obs, action] += self.lr * td_error

            # Update state and action
            obs = next_obs
            action = next_action
            total_reward += reward
            steps += 1
            self.total_steps += 1

            if done:
                break

        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        self.episodes_trained += 1

        return total_reward, steps
