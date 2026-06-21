"""
Utility Functions for POMDP Simulator
======================================

Helper functions for evaluation, visualization, and analysis.
"""

import numpy as np
from typing import Tuple, Dict
import matplotlib.pyplot as plt
from previous_work.dynamic_solvers.learner.meta_layer_learning.q_learning import ObservationQLearning


def evaluate_Y_assignment(
    env_factory,
    Y: np.ndarray,
    n_episodes: int = 200,
    eval_episodes: int = 10,
    learning_rate: float = 0.1,
    seed: int = None
) -> Tuple[float, float, ObservationQLearning]:
    """
    Evaluate a single Y assignment.

    Args:
        env_factory: Function that creates environment given Y
        Y: Observation assignment to evaluate
        n_episodes: Training episodes
        eval_episodes: Evaluation episodes
        learning_rate: Q-learning learning rate
        seed: Random seed

    Returns:
        avg_reward: Average evaluation reward
        avg_length: Average episode length
        agent: Trained agent
    """
    env = env_factory(Y)
    n_obs = len(np.unique(Y))

    agent = ObservationQLearning(
        n_obs=n_obs,
        n_actions=env.n_actions,
        learning_rate=learning_rate,
        seed=seed
    )

    agent.train(env, n_episodes=n_episodes, verbose=False)
    avg_reward, avg_length = agent.evaluate(env, n_episodes=eval_episodes)

    return avg_reward, avg_length, agent


def compare_Y_assignments(
    env_factory,
    Y_dict: Dict[str, np.ndarray],
    n_episodes: int = 200,
    eval_episodes: int = 10,
    seed: int = None
) -> Dict[str, Dict]:
    """
    Compare multiple Y assignments.

    Args:
        env_factory: Function that creates environment given Y
        Y_dict: Dictionary mapping names to Y assignments
        n_episodes: Training episodes per Y
        eval_episodes: Evaluation episodes per Y
        seed: Random seed

    Returns:
        Dictionary with results for each Y
    """
    results = {}

    print("Comparing Y assignments...")
    for name, Y in Y_dict.items():
        print(f"  Evaluating {name}...", end=" ")

        avg_reward, avg_length, agent = evaluate_Y_assignment(
            env_factory, Y, n_episodes, eval_episodes, seed=seed
        )

        results[name] = {
            'Y': Y,
            'avg_reward': avg_reward,
            'avg_length': avg_length,
            'agent': agent
        }

        print(f"Reward={avg_reward:.2f}, Length={avg_length:.1f}")

    return results


def analyze_Y_structure(Y: np.ndarray) -> Dict:
    """
    Analyze structural properties of observation assignment Y.

    Args:
        Y: Observation assignment

    Returns:
        Dictionary with analysis metrics
    """
    n_states = len(Y)
    n_obs = len(np.unique(Y))

    # Compression ratio
    compression = n_obs / n_states

    # Spatial violations (adjacent states with very different observations)
    violations = 0
    for i in range(n_states - 1):
        if abs(Y[i] - Y[i+1]) > 1:
            violations += 1

    # Observation distribution
    obs_counts = np.bincount(Y, minlength=n_obs)
    balance = np.std(obs_counts) / np.mean(obs_counts) if np.mean(obs_counts) > 0 else 0

    return {
        'n_states': n_states,
        'n_obs': n_obs,
        'compression_ratio': compression,
        'spatial_violations': violations,
        'balance_coefficient': balance,
        'obs_distribution': obs_counts
    }


def visualize_Y_lineworld(Y: np.ndarray, title: str = "Observation Assignment"):
    """
    Visualize Y assignment for LineWorld.

    Args:
        Y: Observation assignment
        title: Plot title
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 4))

    # State-observation mapping
    ax1.bar(range(len(Y)), Y, color='steelblue', alpha=0.7)
    ax1.set_xlabel('State')
    ax1.set_ylabel('Observation Class')
    ax1.set_title(title)
    ax1.grid(True, alpha=0.3, axis='y')

    # Observation distribution
    obs_counts = np.bincount(Y)
    ax2.bar(range(len(obs_counts)), obs_counts, color='coral', alpha=0.7)
    ax2.set_xlabel('Observation Class')
    ax2.set_ylabel('Count')
    ax2.set_title('States per Observation Class')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    return fig


def visualize_Y_gridworld(
    Y: np.ndarray,
    rows: int,
    cols: int,
    title: str = "Observation Assignment"
):
    """
    Visualize Y assignment for GridWorld.

    Args:
        Y: Observation assignment (flattened)
        rows: Grid rows
        cols: Grid columns
        title: Plot title
    """
    Y_grid = Y.reshape(rows, cols)

    fig, ax = plt.subplots(figsize=(6, 6))

    im = ax.imshow(Y_grid, cmap='tab10', vmin=0, vmax=9)

    # Add text annotations
    for r in range(rows):
        for c in range(cols):
            ax.text(c, r, str(Y_grid[r, c]),
                   ha="center", va="center", color="black", fontsize=14)

    ax.set_xticks(range(cols))
    ax.set_yticks(range(rows))
    ax.set_xlabel('Column')
    ax.set_ylabel('Row')
    ax.set_title(title)

    plt.colorbar(im, ax=ax, label='Observation Class')
    plt.tight_layout()
    return fig


def plot_training_curves(metrics_dict: Dict, title: str = "Training Curves"):
    """
    Plot training curves for multiple experiments.

    Args:
        metrics_dict: Dictionary mapping names to TrainingMetrics
        title: Plot title
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    for name, metrics in metrics_dict.items():
        # Smooth rewards
        window = min(50, len(metrics.episode_rewards) // 10)
        if window > 1:
            smoothed = np.convolve(
                metrics.episode_rewards,
                np.ones(window)/window,
                mode='valid'
            )
            ax1.plot(smoothed, label=name, linewidth=2)
        else:
            ax1.plot(metrics.episode_rewards, label=name, linewidth=2)

        # Episode lengths
        if window > 1:
            smoothed_len = np.convolve(
                metrics.episode_lengths,
                np.ones(window)/window,
                mode='valid'
            )
            ax2.plot(smoothed_len, label=name, linewidth=2)
        else:
            ax2.plot(metrics.episode_lengths, label=name, linewidth=2)

    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Reward')
    ax1.set_title('Episode Rewards')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Steps')
    ax2.set_title('Episode Length')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.suptitle(title)
    plt.tight_layout()
    return fig


def save_experiment_results(
    filepath: str,
    env_spec: Dict,
    Y: np.ndarray,
    agent: ObservationQLearning,
    metrics: Dict
):
    """
    Save experiment results to file.

    Args:
        filepath: Output file path
        env_spec: Environment specification
        Y: Observation assignment
        agent: Trained agent
        metrics: Training/evaluation metrics
    """
    np.savez(
        filepath,
        env_spec=env_spec,
        Y=Y,
        Q_table=agent.Q,
        policy=agent.get_policy(),
        metrics=metrics
    )
    print(f"Results saved to: {filepath}")


def load_experiment_results(filepath: str) -> Dict:
    """
    Load experiment results from file.

    Args:
        filepath: Input file path

    Returns:
        Dictionary with experiment data
    """
    data = np.load(filepath, allow_pickle=True)
    return {
        'env_spec': data['env_spec'].item(),
        'Y': data['Y'],
        'Q_table': data['Q_table'],
        'policy': data['policy'],
        'metrics': data['metrics'].item()
    }


def print_Y_analysis(Y: np.ndarray, name: str = "Y"):
    """
    Print analysis of Y assignment.

    Args:
        Y: Observation assignment
        name: Name for display
    """
    analysis = analyze_Y_structure(Y)

    print(f"\nAnalysis of {name}:")
    print(f"  States: {analysis['n_states']}")
    print(f"  Observation classes: {analysis['n_obs']}")
    print(f"  Compression ratio: {analysis['compression_ratio']:.2f}")
    print(f"  Spatial violations: {analysis['spatial_violations']}")
    print(f"  Balance coefficient: {analysis['balance_coefficient']:.2f}")
    print(f"  Distribution: {analysis['obs_distribution']}")


def generate_good_Y(n_states: int, k: int, method: str = "spatial") -> np.ndarray:
    """
    Generate a good Y assignment using heuristics.

    Args:
        n_states: Number of states
        k: Number of observation classes
        method: Generation method ("spatial", "uniform", "random")

    Returns:
        Y assignment
    """
    if method == "spatial":
        # Spatial grouping: adjacent states in same group
        states_per_obs = n_states // k
        Y = np.repeat(np.arange(k), states_per_obs)
        # Handle remainder
        if len(Y) < n_states:
            Y = np.concatenate([Y, np.full(n_states - len(Y), k-1)])
        return Y

    elif method == "uniform":
        # Uniform distribution
        Y = np.zeros(n_states, dtype=int)
        for i in range(n_states):
            Y[i] = i % k
        return Y

    elif method == "random":
        # Random assignment
        return np.random.randint(0, k, size=n_states)

    else:
        raise ValueError(f"Unknown method: {method}")
