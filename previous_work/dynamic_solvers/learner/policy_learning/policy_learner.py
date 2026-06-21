"""
Policy Learner for POMDP Environments
======================================

Learns optimal policies π(a|o) for fixed observation functions Y.
Used as the inner loop of the two-learner architecture.

Architecture:
    - PolicyLearner: Abstract base class
    - TabularQLearner: Q-learning with tabular representation
    - REINFORCELearner: Policy gradient with discrete policy
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

import sys
from pathlib import Path

# Add pomdp_sim to path
pomdp_sim_path = Path(__file__).parent.parent.parent / "pomdp_sim"
if str(pomdp_sim_path) not in sys.path:
    sys.path.insert(0, str(pomdp_sim_path))

from pomdp_environment import BasePOMDPEnvironment


@dataclass
class PolicyPerformance:
    """Performance metrics for a learned policy."""
    avg_steps: float  # Average steps to goal (primary metric for meta-learner)
    avg_return: float  # Average cumulative reward
    success_rate: float  # Fraction of episodes reaching goal
    std_steps: float  # Standard deviation of steps
    n_trials: int  # Number of evaluation trials


class PolicyLearner(ABC):
    """
    Abstract base class for policy learning algorithms.

    Learns π(a|o) for a fixed observation function Y in a POMDP environment.
    """

    def __init__(self, n_observations: int, n_actions: int, seed: Optional[int] = None):
        """
        Args:
            n_observations: Number of observation classes
            n_actions: Number of actions
            seed: Random seed for reproducibility
        """
        self.n_obs = n_observations
        self.n_actions = n_actions
        self.rng = np.random.default_rng(seed)

    @abstractmethod
    def select_action(self, observation: int, explore: bool = True) -> int:
        """
        Select action given observation.

        Args:
            observation: Current observation
            explore: Whether to use exploration (training) or exploitation (evaluation)

        Returns:
            Action to take
        """
        pass

    @abstractmethod
    def update(self, observation: int, action: int, reward: float,
               next_observation: int, terminated: bool):
        """
        Update policy based on transition.

        Args:
            observation: Current observation
            action: Action taken
            reward: Reward received
            next_observation: Next observation
            terminated: Whether episode terminated
        """
        pass

    @abstractmethod
    def reset_episode(self):
        """Reset any episode-specific state (for episodic algorithms)."""
        pass

    def train(self, env: BasePOMDPEnvironment, n_episodes: int,
              max_steps: int = 1000, verbose: bool = False) -> Dict[str, Any]:
        """
        Train policy on environment.

        Args:
            env: POMDP environment to train on
            n_episodes: Number of training episodes
            max_steps: Maximum steps per episode
            verbose: Whether to print training progress

        Returns:
            Training statistics dictionary
        """
        episode_returns = []
        episode_lengths = []

        for episode in range(n_episodes):
            obs, _ = env.reset()
            self.reset_episode()

            episode_return = 0.0
            step_count = 0

            for step in range(max_steps):
                # Select action
                action = self.select_action(obs, explore=True) # Explore during training

                # Take action
                next_obs, reward, terminated, truncated, info = env.step(action)

                # Update policy
                self.update(obs, action, reward, next_obs, terminated) # Learn

                episode_return += reward
                step_count += 1
                obs = next_obs

                if terminated or truncated:
                    break

            # Track statistics
            episode_returns.append(episode_return)
            episode_lengths.append(step_count)

            if verbose and episode % 10 == 0:
                recent_return = np.mean(episode_returns[-10:])
                recent_length = np.mean(episode_lengths[-10:])
                print(f"Episode {episode:3d} | Avg Return: {recent_return:6.2f} | Avg Steps: {recent_length:5.1f}")

        return {
            'episode_returns': episode_returns,
            'episode_lengths': episode_lengths,
            'final_avg_return': np.mean(episode_returns[-10:]),
            'final_avg_steps': np.mean(episode_lengths[-10:])
        }

    def evaluate(self, env: BasePOMDPEnvironment, n_trials: int = 10,
                 max_steps: int = 1000, seed: Optional[int] = None) -> PolicyPerformance:
        """
        Evaluate learned policy.

        Args:
            env: POMDP environment to evaluate on
            n_trials: Number of evaluation trials
            max_steps: Maximum steps per trial
            seed: Random seed for evaluation

        Returns:
            PolicyPerformance metrics
        """
        trial_returns = []
        trial_steps = []
        successes = 0

        for trial in range(n_trials):
            obs, _ = env.reset(seed=seed + trial if seed else None)
            self.reset_episode()

            trial_return = 0.0
            step_count = 0

            for step in range(max_steps):
                # Select action (no exploration)
                action = self.select_action(obs, explore=False)

                # Take action
                obs, reward, terminated, truncated, info = env.step(action)

                trial_return += reward
                step_count += 1

                if terminated:
                    successes += 1
                    break

                if truncated:
                    break

            trial_returns.append(trial_return)
            trial_steps.append(step_count)

        return PolicyPerformance(
            avg_steps=np.mean(trial_steps),
            avg_return=np.mean(trial_returns),
            success_rate=successes / n_trials,
            std_steps=np.std(trial_steps),
            n_trials=n_trials
        )

    def train_and_evaluate(self, env: BasePOMDPEnvironment,
                          n_train_episodes: int = 100,
                          n_eval_trials: int = 10,
                          max_steps: int = 1000,
                          verbose: bool = False) -> PolicyPerformance:
        """
        Train policy and evaluate performance.

        This is the main interface for the meta-learner.

        Args:
            env: POMDP environment
            n_train_episodes: Number of training episodes
            n_eval_trials: Number of evaluation trials
            max_steps: Maximum steps per episode/trial
            verbose: Whether to print progress

        Returns:
            PolicyPerformance after training
        """
        # Train
        self.train(env, n_train_episodes, max_steps, verbose)

        # Evaluate
        performance = self.evaluate(env, n_eval_trials, max_steps)

        if verbose:
            print(f"\n{'='*50}")
            print(f"Evaluation Results ({n_eval_trials} trials):")
            print(f"  Avg Steps:    {performance.avg_steps:.2f} ± {performance.std_steps:.2f}")
            print(f"  Avg Return:   {performance.avg_return:.2f}")
            print(f"  Success Rate: {performance.success_rate:.1%}")
            print(f"{'='*50}\n")

        return performance


class TabularQLearner(PolicyLearner):
    """
    Q-Learning with tabular Q-function representation.

    Suitable for small observation spaces (< 1000 observations).
    Uses epsilon-greedy exploration.
    """

    def __init__(self, n_observations: int, n_actions: int,
                 lr: float = 0.1, gamma: float = 0.99,
                 epsilon_start: float = 1.0, epsilon_end: float = 0.01,
                 epsilon_decay: float = 0.995,
                 seed: Optional[int] = None):
        """
        Args:
            n_observations: Number of observation classes
            n_actions: Number of actions
            lr: Learning rate (alpha)
            gamma: Discount factor
            epsilon_start: Initial exploration rate
            epsilon_end: Final exploration rate
            epsilon_decay: Epsilon decay factor per episode
            seed: Random seed
        """
        super().__init__(n_observations, n_actions, seed)

        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        # Q-table: Q[observation][action]
        self.Q = np.zeros((n_observations, n_actions))

    def select_action(self, observation: int, explore: bool = True) -> int:
        """Epsilon-greedy action selection."""
        if explore and self.rng.random() < self.epsilon:
            # Explore: random action
            return self.rng.integers(0, self.n_actions)
        else:
            # Exploit: greedy action
            return int(np.argmax(self.Q[observation]))

    def update(self, observation: int, action: int, reward: float,
               next_observation: int, terminated: bool):
        """Q-learning update."""
        if terminated:
            # Terminal state: no future value
            target = reward
        else:
            # Non-terminal: bootstrap from next state
            target = reward + self.gamma * np.max(self.Q[next_observation])

        # Q-learning update
        td_error = target - self.Q[observation, action]
        self.Q[observation, action] += self.lr * td_error

    def reset_episode(self):
        """Decay epsilon after each episode."""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def get_q_values(self) -> np.ndarray:
        """Return Q-table for inspection."""
        return self.Q.copy()


class REINFORCELearner(PolicyLearner):
    """
    REINFORCE policy gradient algorithm.

    Uses a parameterized policy π_θ(a|o) with softmax over logits.
    Suitable for small to medium observation spaces.
    """

    def __init__(self, n_observations: int, n_actions: int,
                 lr: float = 0.01, gamma: float = 0.99,
                 baseline_decay: float = 0.9,
                 seed: Optional[int] = None):
        """
        Args:
            n_observations: Number of observation classes
            n_actions: Number of actions
            lr: Learning rate
            gamma: Discount factor
            baseline_decay: Baseline moving average decay
            seed: Random seed
        """
        super().__init__(n_observations, n_actions, seed)

        self.lr = lr
        self.gamma = gamma
        self.baseline_decay = baseline_decay

        # Policy parameters: logits[observation][action]
        self.logits = np.zeros((n_observations, n_actions))

        # Baseline for variance reduction
        self.baseline = 0.0

        # Episode trajectory buffer
        self.trajectory = []

    def softmax(self, logits: np.ndarray) -> np.ndarray:
        """Numerically stable softmax."""
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / np.sum(exp_logits)

    def select_action(self, observation: int, explore: bool = True) -> int:
        """Sample from policy distribution."""
        probs = self.softmax(self.logits[observation])

        if explore:
            # Sample from distribution
            action = self.rng.choice(self.n_actions, p=probs)
        else:
            # Greedy: most probable action
            action = int(np.argmax(probs))

        return action

    def update(self, observation: int, action: int, reward: float,
               next_observation: int, terminated: bool):
        """Store transition in trajectory buffer."""
        self.trajectory.append((observation, action, reward))

    def reset_episode(self):
        """
        Update policy using complete trajectory (REINFORCE).
        Called at the end of each episode.
        """
        if len(self.trajectory) == 0:
            return

        # Compute discounted returns (G_t)
        returns = []
        G = 0.0
        for obs, action, reward in reversed(self.trajectory):
            G = reward + self.gamma * G
            returns.insert(0, G)

        # Update baseline
        avg_return = np.mean(returns)
        self.baseline = self.baseline_decay * self.baseline + (1 - self.baseline_decay) * avg_return

        # REINFORCE update
        for (obs, action, _), G in zip(self.trajectory, returns):
            # Get policy probabilities
            probs = self.softmax(self.logits[obs])

            # Advantage
            advantage = G - self.baseline

            # Gradient: advantage * ∇log π(a|o)
            # For softmax policy: ∇log π(a|o) = (1[a] - π(a|o))
            grad = np.zeros(self.n_actions)
            grad[action] = 1.0
            grad -= probs

            # Update logits
            self.logits[obs] += self.lr * advantage * grad

        # Clear trajectory
        self.trajectory = []

    def get_policy_probs(self) -> np.ndarray:
        """Return policy probabilities for inspection."""
        probs = np.zeros_like(self.logits)
        for obs in range(self.n_obs):
            probs[obs] = self.softmax(self.logits[obs])
        return probs


if __name__ == "__main__":
    # Example usage
    from pomdp_environment import LinePOMDPEnv
    from previous_work.dynamic_solvers.builders.enums import OOPVariant

    # Create environment with a specific observation function
    size = 11
    goal = 5
    obs_function = np.array([0, 0, 0, 0, 0, -1, 1, 1, 1, 1, 1])  # 2 observation classes

    env = LinePOMDPEnv(
        size=size,
        goal=goal,
        obs_function=obs_function,
        pomdp_variant=OOPVariant.POP,
        step_penalty=-1.0,
        goal_reward=0.0,
        stochastic=False,
        seed=42
    )

    print("Testing TabularQLearner:")
    print("=" * 50)
    q_learner = TabularQLearner(
        n_observations=4,
        n_actions=2,
        lr=0.1,
        epsilon_start=1.0,
        epsilon_end=0.01,
        epsilon_decay=0.99,
        seed=42
    )

    performance = q_learner.train_and_evaluate(
        env,
        n_train_episodes=200,
        n_eval_trials=20,
        verbose=True
    )

    print("\nTesting REINFORCELearner:")
    print("=" * 50)
    reinforce_learner = REINFORCELearner(
        n_observations=4,
        n_actions=2,
        lr=0.01,
        gamma=0.99,
        seed=42
    )

    performance = reinforce_learner.train_and_evaluate(
        env,
        n_train_episodes=200,
        n_eval_trials=20,
        verbose=True
    )
