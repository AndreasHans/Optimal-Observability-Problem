"""
Meta-Learning for Observation Assignment Y (Outer Loop)
========================================================

Learns which observation assignment Y enables best policy performance.

Uses policy gradient methods (REINFORCE) to optimize Y based on
the performance of policies learned for each Y configuration.
"""

import numpy as np
from typing import Tuple, List, Optional, Callable
from dataclasses import dataclass
from learner.pomdp_simulation.pomdp_environment import BasePOMDPEnvironment
from previous_work.dynamic_solvers.learner.meta_layer_learning.q_learning import ObservationQLearning


@dataclass
class MetaTrainingResult:
    """Results from meta-training."""
    best_Y: np.ndarray
    best_reward: float
    Y_history: List[np.ndarray]
    reward_history: List[float]
    theta_history: List[np.ndarray]


class ObservationAssignmentAgent:
    """
    Agent that learns to sample good observation assignments Y.

    Uses a parameterized distribution over Y assignments and updates
    parameters based on policy performance (REINFORCE).
    """

    def __init__(
        self,
        n_states: int,
        k: int,
        method: str = "softmax",
        learning_rate: float = 0.01,
        temperature: float = 1.0,
        seed: Optional[int] = None
    ):
        """
        Args:
            n_states: Number of states in the environment
            k: Number of observation classes
            method: Sampling method ("softmax", "epsilon_greedy", "random")
            learning_rate: Learning rate for parameter updates
            temperature: Temperature for softmax (higher = more exploration)
            seed: Random seed
        """
        self.n_states = n_states
        self.k = k
        self.method = method
        self.lr = learning_rate
        self.temperature = temperature
        self.rng = np.random.RandomState(seed)

        # Initialize parameters
        # theta[i, j] = logit probability of assigning state i to observation class j
        self.theta = np.zeros((n_states, k))

        # Track statistics
        self.n_samples = 0

    def sample(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sample an observation assignment Y.

        Returns:
            Y: Assignment array [n_states] mapping states to observations
            log_probs: Log probabilities [n_states] for this sample (for REINFORCE)
        """
        self.n_samples += 1

        if self.method == "random":
            # Uniform random sampling
            Y = self.rng.randint(0, self.k, size=self.n_states)
            log_probs = np.log(1.0 / self.k) * np.ones(self.n_states)

        elif self.method == "softmax":
            # Sample from categorical distribution via softmax
            Y = np.zeros(self.n_states, dtype=int)
            log_probs = np.zeros(self.n_states)

            for i in range(self.n_states):
                # Softmax probabilities
                logits = self.theta[i] / self.temperature
                exp_logits = np.exp(logits - np.max(logits))  # Numerical stability
                probs = exp_logits / np.sum(exp_logits)

                # Sample observation class
                obs = self.rng.choice(self.k, p=probs)
                Y[i] = obs

                # Log probability
                log_probs[i] = np.log(probs[obs] + 1e-10)

        elif self.method == "epsilon_greedy":
            # Epsilon-greedy: mostly greedy, sometimes random
            epsilon = 0.1
            Y = np.zeros(self.n_states, dtype=int)
            log_probs = np.zeros(self.n_states)

            for i in range(self.n_states):
                if self.rng.rand() < epsilon:
                    obs = self.rng.randint(0, self.k)
                    log_probs[i] = np.log(epsilon / self.k + 1e-10)
                else:
                    obs = np.argmax(self.theta[i])
                    log_probs[i] = np.log(1 - epsilon + epsilon / self.k + 1e-10)

                Y[i] = obs

        else:
            raise ValueError(f"Unknown sampling method: {self.method}")

        return Y, log_probs

    def update(
        self,
        Y: np.ndarray,
        log_probs: np.ndarray,
        reward: float,
        baseline: float = 0.0
    ):
        """
        Update parameters using REINFORCE gradient.

        ∇J(θ) = (R - b) * ∇log π(Y|θ)

        Args:
            Y: Sampled assignment
            log_probs: Log probabilities for this sample
            reward: Performance of policy trained on this Y
            baseline: Baseline for variance reduction
        """
        if self.method == "random":
            return  # No updates for random sampling

        # Advantage (reward - baseline)
        advantage = reward - baseline

        # REINFORCE gradient update
        for i in range(self.n_states):
            obs = Y[i]

            if self.method == "softmax":
                # Gradient of log softmax
                logits = self.theta[i] / self.temperature
                exp_logits = np.exp(logits - np.max(logits))
                probs = exp_logits / np.sum(exp_logits)

                # ∇log π = e_obs - probs (one-hot minus softmax)
                grad = np.zeros(self.k)
                grad[obs] = 1.0
                grad -= probs

                # Update: θ += lr * advantage * grad
                self.theta[i] += self.lr * advantage * grad / self.temperature

            elif self.method == "epsilon_greedy":
                # Simple gradient: increase θ for chosen obs
                self.theta[i, obs] += self.lr * advantage

    def get_best_Y(self) -> np.ndarray:
        """Return the current best Y (greedy selection)."""
        return np.argmax(self.theta, axis=1)

    def reset(self):
        """Reset parameters."""
        self.theta = np.zeros((self.n_states, self.k))
        self.n_samples = 0


def meta_train(
    env_factory: Callable[[np.ndarray], BasePOMDPEnvironment],
    n_states: int,
    k: int,
    meta_episodes: int = 100,
    inner_episodes: int = 200,
    eval_episodes: int = 10,
    method: str = "softmax",
    meta_lr: float = 0.01,
    inner_lr: float = 0.1,
    discount: float = 0.95,
    seed: Optional[int] = None,
    verbose: bool = True
) -> MetaTrainingResult:
    """
    Meta-training loop for learning observation assignment Y.

    Args:
        env_factory: Function that creates environment given Y
        n_states: Number of states
        k: Number of observation classes
        meta_episodes: Number of meta-training episodes
        inner_episodes: Number of training episodes for each Y
        eval_episodes: Number of evaluation episodes per Y
        method: Sampling method for Y
        meta_lr: Learning rate for Y updates
        inner_lr: Learning rate for policy learning
        discount: Discount factor
        seed: Random seed
        verbose: Print progress

    Returns:
        Meta-training results
    """
    # Initialize meta-agent
    meta_agent = ObservationAssignmentAgent(
        n_states=n_states,
        k=k,
        method=method,
        learning_rate=meta_lr,
        seed=seed
    )

    # Track results
    Y_history = []
    reward_history = []
    theta_history = []
    best_Y = None
    best_reward = -np.inf

    # Running baseline for variance reduction
    reward_baseline = 0.0

    if verbose:
        print("=" * 60)
        print("Meta-Training: Learning Observation Assignment Y")
        print("=" * 60)
        print(f"States: {n_states}, Observation classes: {k}")
        print(f"Meta episodes: {meta_episodes}")
        print(f"Inner episodes: {inner_episodes}")
        print(f"Sampling method: {method}")
        print()

    for meta_ep in range(meta_episodes):
        # Sample Y
        Y, log_probs = meta_agent.sample()

        # Create environment with this Y
        env = env_factory(Y)

        # Train policy for this Y (inner loop)
        policy = ObservationQLearning(
            n_obs=k,
            n_actions=env.n_actions,
            learning_rate=inner_lr,
            discount_factor=discount,
            epsilon_decay=0.995,
            seed=seed
        )

        # Train
        policy.train(env, n_episodes=inner_episodes, verbose=False)

        # Evaluate
        eval_reward, eval_length = policy.evaluate(
            env, n_episodes=eval_episodes, render=False
        )

        # Update running baseline
        reward_baseline = 0.9 * reward_baseline + 0.1 * eval_reward

        # Update meta-agent
        meta_agent.update(Y, log_probs, eval_reward, baseline=reward_baseline)

        # Track results
        Y_history.append(Y.copy())
        reward_history.append(eval_reward)
        theta_history.append(meta_agent.theta.copy())

        # Update best
        if eval_reward > best_reward:
            best_reward = eval_reward
            best_Y = Y.copy()

        if verbose and (meta_ep + 1) % 10 == 0:
            recent_rewards = reward_history[-10:]
            avg_reward = np.mean(recent_rewards)
            print(f"Meta-episode {meta_ep+1}/{meta_episodes}: "
                  f"Reward={eval_reward:.2f}, "
                  f"Avg(last 10)={avg_reward:.2f}, "
                  f"Best={best_reward:.2f}")
            print(f"  Current Y: {Y}")
            if best_Y is not None:
                print(f"  Best Y:    {best_Y}")

    if verbose:
        print("\n" + "=" * 60)
        print("Meta-Training Complete")
        print("=" * 60)
        print(f"Best reward: {best_reward:.2f}")
        print(f"Best Y: {best_Y}")
        print()

    return MetaTrainingResult(
        best_Y=best_Y,
        best_reward=best_reward,
        Y_history=Y_history,
        reward_history=reward_history,
        theta_history=theta_history
    )


def random_search(
    env_factory: Callable[[np.ndarray], BasePOMDPEnvironment],
    n_states: int,
    k: int,
    n_trials: int = 100,
    inner_episodes: int = 200,
    eval_episodes: int = 10,
    inner_lr: float = 0.1,
    discount: float = 0.95,
    seed: Optional[int] = None,
    verbose: bool = True
) -> MetaTrainingResult:
    """
    Baseline: Random search over Y assignments.

    Args:
        (same as meta_train, but n_trials instead of meta_episodes)

    Returns:
        Results with best Y found
    """
    rng = np.random.RandomState(seed)

    Y_history = []
    reward_history = []
    best_Y = None
    best_reward = -np.inf

    if verbose:
        print("=" * 60)
        print("Random Search Baseline")
        print("=" * 60)
        print(f"States: {n_states}, Observation classes: {k}")
        print(f"Trials: {n_trials}")
        print()

    for trial in range(n_trials):
        # Random Y
        Y = rng.randint(0, k, size=n_states)

        # Create environment
        env = env_factory(Y)

        # Train policy
        policy = ObservationQLearning(
            n_obs=k,
            n_actions=env.n_actions,
            learning_rate=inner_lr,
            discount_factor=discount,
            seed=seed
        )
        policy.train(env, n_episodes=inner_episodes, verbose=False)

        # Evaluate
        eval_reward, _ = policy.evaluate(env, n_episodes=eval_episodes, render=False)

        # Track
        Y_history.append(Y)
        reward_history.append(eval_reward)

        if eval_reward > best_reward:
            best_reward = eval_reward
            best_Y = Y.copy()

        if verbose and (trial + 1) % 10 == 0:
            recent = reward_history[-10:]
            print(f"Trial {trial+1}/{n_trials}: "
                  f"Reward={eval_reward:.2f}, "
                  f"Avg(last 10)={np.mean(recent):.2f}, "
                  f"Best={best_reward:.2f}")

    if verbose:
        print("\n" + "=" * 60)
        print("Random Search Complete")
        print("=" * 60)
        print(f"Best reward: {best_reward:.2f}")
        print(f"Best Y: {best_Y}")

    return MetaTrainingResult(
        best_Y=best_Y,
        best_reward=best_reward,
        Y_history=Y_history,
        reward_history=reward_history,
        theta_history=[]
    )
