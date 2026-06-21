"""
Test Q-Learning on POMDP environments.

Demonstrates how observation assignment Y affects policy learning.
"""

import numpy as np
import matplotlib.pyplot as plt
from learner.pomdp_simulation.pomdp_environment import LinePOMDPEnv, GridPOMDPEnv
from previous_work.dynamic_solvers.learner.meta_layer_learning.q_learning import ObservationQLearning


def test_line_world_perfect_obs():
    """Test Q-learning on LineWorld with perfect observations."""
    print("=" * 60)
    print("Test 1: LineWorld with Perfect Observations")
    print("=" * 60)

    size = 8
    goal = 7
    Y_perfect = np.arange(size)  # Each state has unique observation

    env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y_perfect, seed=42)
    agent = ObservationQLearning(
        n_obs=len(np.unique(Y_perfect)),
        n_actions=2,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon_start=1.0,
        epsilon_end=0.01,
        epsilon_decay=0.995,
        seed=42
    )

    print(f"\nEnvironment: {size} states, goal at {goal}")
    print(f"Observation assignment Y: {Y_perfect}")
    print(f"Number of observation classes: {agent.n_obs}")

    # Train
    print("\nTraining...")
    metrics = agent.train(env, n_episodes=500, verbose=True, eval_interval=100)

    # Evaluate
    print("\nEvaluation (greedy policy):")
    avg_reward, avg_length = agent.evaluate(env, n_episodes=10, render=False)
    print(f"Average Reward: {avg_reward:.2f}")
    print(f"Average Episode Length: {avg_length:.1f}")

    # Show learned policy
    print(f"\nLearned Policy: {agent.get_policy()}")
    print("(0=left, 1=right)")

    return metrics


def test_line_world_aliased_obs():
    """Test Q-learning with aliased observations."""
    print("\n" + "=" * 60)
    print("Test 2: LineWorld with Aliased Observations")
    print("=" * 60)

    size = 8
    goal = 7

    # Group states: [0,1] -> 0, [2,3] -> 1, [4,5] -> 2, [6,7] -> 3
    Y_aliased = np.array([0, 0, 1, 1, 2, 2, 3, 3])

    env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y_aliased, seed=42)
    agent = ObservationQLearning(
        n_obs=len(np.unique(Y_aliased)),
        n_actions=2,
        learning_rate=0.1,
        discount_factor=0.95,
        seed=42
    )

    print(f"\nEnvironment: {size} states, goal at {goal}")
    print(f"Observation assignment Y: {Y_aliased}")
    print(f"Number of observation classes: {agent.n_obs}")

    # Train
    print("\nTraining...")
    metrics = agent.train(env, n_episodes=500, verbose=True, eval_interval=100)

    # Evaluate
    print("\nEvaluation (greedy policy):")
    avg_reward, avg_length = agent.evaluate(env, n_episodes=10, render=False)
    print(f"Average Reward: {avg_reward:.2f}")
    print(f"Average Episode Length: {avg_length:.1f}")

    print(f"\nLearned Policy: {agent.get_policy()}")
    print("(0=left, 1=right)")

    return metrics


def test_line_world_bad_obs():
    """Test Q-learning with poor observation assignment."""
    print("\n" + "=" * 60)
    print("Test 3: LineWorld with Poor Observation Assignment")
    print("=" * 60)

    size = 8
    goal = 7

    # Random, uninformative grouping
    Y_bad = np.array([0, 2, 1, 0, 2, 1, 0, 3])

    env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y_bad, seed=42)
    agent = ObservationQLearning(
        n_obs=len(np.unique(Y_bad)),
        n_actions=2,
        learning_rate=0.1,
        discount_factor=0.95,
        seed=42
    )

    print(f"\nEnvironment: {size} states, goal at {goal}")
    print(f"Observation assignment Y: {Y_bad}")
    print(f"Number of observation classes: {agent.n_obs}")

    # Train
    print("\nTraining...")
    metrics = agent.train(env, n_episodes=500, verbose=True, eval_interval=100)

    # Evaluate
    print("\nEvaluation (greedy policy):")
    avg_reward, avg_length = agent.evaluate(env, n_episodes=10, render=False)
    print(f"Average Reward: {avg_reward:.2f}")
    print(f"Average Episode Length: {avg_length:.1f}")

    print(f"\nLearned Policy: {agent.get_policy()}")

    return metrics


def test_grid_world():
    """Test Q-learning on GridWorld."""
    print("\n" + "=" * 60)
    print("Test 4: GridWorld Navigation")
    print("=" * 60)

    rows, cols = 4, 4
    goal = (3, 3)

    # Observation based on Manhattan distance to goal
    Y = np.zeros(rows * cols, dtype=int)
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            dist = abs(r - goal[0]) + abs(c - goal[1])
            Y[idx] = min(dist, 4)  # Cap at 4 observation classes

    env = GridPOMDPEnv(rows=rows, cols=cols, goal=goal, obs_function=Y, seed=42)
    agent = ObservationQLearning(
        n_obs=len(np.unique(Y)),
        n_actions=4,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon_decay=0.995,
        seed=42
    )

    print(f"\nEnvironment: {rows}x{cols} grid, goal at {goal}")
    print(f"Number of observation classes: {agent.n_obs}")

    # Train
    print("\nTraining...")
    metrics = agent.train(env, n_episodes=1000, verbose=True, eval_interval=200)

    # Evaluate
    print("\nEvaluation (greedy policy):")
    avg_reward, avg_length = agent.evaluate(env, n_episodes=10, render=False)
    print(f"Average Reward: {avg_reward:.2f}")
    print(f"Average Episode Length: {avg_length:.1f}")

    # Show one episode
    print("\nSample Episode:")
    agent.evaluate(env, n_episodes=1, render=True)

    return metrics


def compare_y_assignments():
    """Compare learning curves for different Y assignments."""
    print("\n" + "=" * 60)
    print("Comparison: Impact of Observation Assignment Y")
    print("=" * 60)

    size = 8
    goal = 7

    # Three different Y assignments
    Y_perfect = np.arange(size)
    Y_good = np.array([0, 0, 1, 1, 2, 2, 3, 3])
    Y_bad = np.array([0, 2, 1, 0, 2, 1, 0, 3])

    configs = [
        ("Perfect (unique)", Y_perfect),
        ("Good (spatial)", Y_good),
        ("Bad (random)", Y_bad)
    ]

    results = {}

    for name, Y in configs:
        print(f"\nTraining with {name} observations...")
        env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y, seed=42)
        agent = ObservationQLearning(
            n_obs=len(np.unique(Y)),
            n_actions=2,
            seed=42
        )

        metrics = agent.train(env, n_episodes=500, verbose=False)
        avg_reward, avg_length = agent.evaluate(env, n_episodes=20)

        results[name] = {
            'metrics': metrics,
            'eval_reward': avg_reward,
            'eval_length': avg_length
        }

        print(f"  Eval Reward: {avg_reward:.2f}, Eval Length: {avg_length:.1f}")

    # Plot learning curves
    try:
        plot_comparison(results)
    except Exception as e:
        print(f"\nNote: Could not generate plot: {e}")

    return results


def plot_comparison(results):
    """Plot learning curves for comparison."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    window = 50
    for name, data in results.items():
        rewards = data['metrics'].episode_rewards

        # Moving average
        avg_rewards = np.convolve(rewards, np.ones(window)/window, mode='valid')

        ax1.plot(avg_rewards, label=name, linewidth=2)

    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Average Reward')
    ax1.set_title('Learning Curves (50-episode moving average)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Bar chart of final performance
    names = list(results.keys())
    eval_rewards = [results[n]['eval_reward'] for n in names]

    ax2.bar(names, eval_rewards, color=['green', 'blue', 'red'])
    ax2.set_ylabel('Average Reward (Evaluation)')
    ax2.set_title('Final Performance')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('/Users/adrianzvizdenco/Master -  Courses/DTU CSE/MSc Thesis/OOP/learner/q_learning_comparison.png', dpi=150)
    print("\nPlot saved to: learner/q_learning_comparison.png")


if __name__ == "__main__":
    # Run tests
    test_line_world_perfect_obs()
    test_line_world_aliased_obs()
    test_line_world_bad_obs()
    test_grid_world()

    # Comprehensive comparison
    compare_y_assignments()

    print("\n" + "=" * 60)
    print("All Q-learning tests completed!")
    print("=" * 60)
