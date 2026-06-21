"""
Test Meta-Learning for Observation Assignment Y.

Demonstrates that the meta-learning algorithm can discover good Y assignments
that enable efficient policy learning.
"""

import numpy as np
import matplotlib.pyplot as plt
from learner.pomdp_simulation.pomdp_environment import LinePOMDPEnv, GridPOMDPEnv
from previous_work.dynamic_solvers.learner.meta_layer_learning.meta_learning import meta_train, random_search


def test_line_world_meta():
    """Test meta-learning on LineWorld."""
    print("=" * 70)
    print("Test 1: Meta-Learning on LineWorld")
    print("=" * 70)

    size = 8
    goal = 7
    k = 4  # 4 observation classes

    # Environment factory
    def env_factory(Y):
        return LinePOMDPEnv(size=size, goal=goal, obs_function=Y, seed=42)

    # Run meta-training
    result = meta_train(
        env_factory=env_factory,
        n_states=size,
        k=k,
        meta_episodes=50,
        inner_episodes=200,
        eval_episodes=10,
        method="softmax",
        meta_lr=0.05,
        seed=42,
        verbose=True
    )

    print("\n" + "-" * 70)
    print("Analysis of Learned Y")
    print("-" * 70)

    # Compare with known good/bad Y assignments
    Y_perfect = np.arange(size)  # Would need k=8
    Y_good = np.array([0, 0, 1, 1, 2, 2, 3, 3])  # Spatial grouping
    Y_bad = np.array([0, 2, 1, 0, 2, 1, 0, 3])   # Random grouping

    # Evaluate learned Y
    print(f"\nLearned Y: {result.best_Y}")
    print(f"Good Y:    {Y_good}")
    print(f"Bad Y:     {Y_bad}")

    # Check if learned Y has spatial structure
    def has_spatial_structure(Y):
        """Check if adjacent states have same or similar observations."""
        violations = sum(abs(Y[i] - Y[i+1]) > 1 for i in range(len(Y)-1))
        return violations

    learned_violations = has_spatial_structure(result.best_Y)
    good_violations = has_spatial_structure(Y_good)
    bad_violations = has_spatial_structure(Y_bad)

    print(f"\nSpatial structure violations:")
    print(f"  Learned: {learned_violations}")
    print(f"  Good:    {good_violations}")
    print(f"  Bad:     {bad_violations}")

    if learned_violations <= good_violations + 1:
        print("\n✓ Learned Y has good spatial structure!")
    else:
        print("\n✗ Learned Y has poor spatial structure")

    return result


def test_random_search_baseline():
    """Compare meta-learning with random search."""
    print("\n" + "=" * 70)
    print("Test 2: Meta-Learning vs Random Search Baseline")
    print("=" * 70)

    size = 6
    goal = 5
    k = 3

    def env_factory(Y):
        return LinePOMDPEnv(size=size, goal=goal, obs_function=Y, seed=42)

    # Meta-learning
    print("\n[1/2] Running meta-learning...")
    meta_result = meta_train(
        env_factory=env_factory,
        n_states=size,
        k=k,
        meta_episodes=30,
        inner_episodes=150,
        eval_episodes=5,
        method="softmax",
        meta_lr=0.1,
        seed=42,
        verbose=False
    )

    # Random search
    print("[2/2] Running random search baseline...")
    random_result = random_search(
        env_factory=env_factory,
        n_states=size,
        k=k,
        n_trials=30,
        inner_episodes=150,
        eval_episodes=5,
        seed=42,
        verbose=False
    )

    # Compare
    print("\n" + "-" * 70)
    print("Comparison")
    print("-" * 70)
    print(f"Meta-learning best reward: {meta_result.best_reward:.2f}")
    print(f"Random search best reward: {random_result.best_reward:.2f}")
    print(f"\nMeta-learning best Y: {meta_result.best_Y}")
    print(f"Random search best Y: {random_result.best_Y}")

    # Plot learning curves
    try:
        plot_comparison(meta_result, random_result)
    except Exception as e:
        print(f"\nNote: Could not generate plot: {e}")

    if meta_result.best_reward >= random_result.best_reward:
        print("\n✓ Meta-learning performed as well or better than random search!")
    else:
        print("\n✗ Random search found better Y (meta-learning may need more episodes)")

    return meta_result, random_result


def test_different_k_values():
    """Test meta-learning with different numbers of observation classes."""
    print("\n" + "=" * 70)
    print("Test 3: Impact of Number of Observation Classes (k)")
    print("=" * 70)

    size = 8
    goal = 7

    def env_factory(Y):
        return LinePOMDPEnv(size=size, goal=goal, obs_function=Y, seed=42)

    results = {}

    for k in [2, 3, 4, 6]:
        print(f"\n--- Testing k={k} ---")

        result = meta_train(
            env_factory=env_factory,
            n_states=size,
            k=k,
            meta_episodes=30,
            inner_episodes=150,
            eval_episodes=5,
            method="softmax",
            meta_lr=0.1,
            seed=42,
            verbose=False
        )

        results[k] = result

        print(f"k={k}: Best reward = {result.best_reward:.2f}, Y = {result.best_Y}")

    # Summary
    print("\n" + "-" * 70)
    print("Summary: Reward vs Number of Observation Classes")
    print("-" * 70)
    for k, result in results.items():
        print(f"k={k}: {result.best_reward:.2f}")

    # Find optimal k
    best_k = max(results.keys(), key=lambda k: results[k].best_reward)
    print(f"\nBest k: {best_k} (reward: {results[best_k].best_reward:.2f})")

    return results


def test_gridworld_meta():
    """Test meta-learning on 2D GridWorld."""
    print("\n" + "=" * 70)
    print("Test 4: Meta-Learning on GridWorld")
    print("=" * 70)

    rows, cols = 3, 3
    goal = (2, 2)
    n_states = rows * cols
    k = 4

    def env_factory(Y):
        return GridPOMDPEnv(rows=rows, cols=cols, goal=goal, obs_function=Y, seed=42)

    print(f"Environment: {rows}x{cols} grid, {n_states} states")
    print(f"Goal: {goal}")
    print(f"Observation classes: {k}")

    result = meta_train(
        env_factory=env_factory,
        n_states=n_states,
        k=k,
        meta_episodes=40,
        inner_episodes=300,
        eval_episodes=10,
        method="softmax",
        meta_lr=0.05,
        seed=42,
        verbose=True
    )

    # Visualize learned Y
    print("\n" + "-" * 70)
    print("Learned Y (observation assignment for grid)")
    print("-" * 70)

    Y_grid = result.best_Y.reshape(rows, cols)
    print("\nGrid visualization (observation classes):")
    for r in range(rows):
        print(" ".join(str(Y_grid[r, c]) for c in range(cols)))

    print(f"\nGoal position {goal} has observation: {Y_grid[goal]}")

    return result


def plot_comparison(meta_result, random_result):
    """Plot comparison of meta-learning vs random search."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Learning curves
    ax1.plot(meta_result.reward_history, label='Meta-learning', linewidth=2)
    ax1.plot(random_result.reward_history, label='Random search', linewidth=2, alpha=0.7)
    ax1.axhline(meta_result.best_reward, color='blue', linestyle='--', alpha=0.5,
                label=f'Meta best: {meta_result.best_reward:.2f}')
    ax1.axhline(random_result.best_reward, color='orange', linestyle='--', alpha=0.5,
                label=f'Random best: {random_result.best_reward:.2f}')

    ax1.set_xlabel('Episode/Trial')
    ax1.set_ylabel('Evaluation Reward')
    ax1.set_title('Meta-Learning vs Random Search')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Distribution of rewards
    ax2.hist(meta_result.reward_history, bins=15, alpha=0.6, label='Meta-learning')
    ax2.hist(random_result.reward_history, bins=15, alpha=0.6, label='Random search')
    ax2.set_xlabel('Evaluation Reward')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Distribution of Y Performance')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('/Users/adrianzvizdenco/Master -  Courses/DTU CSE/MSc Thesis/OOP/learner/meta_learning_comparison.png', dpi=150)
    print("\nPlot saved to: learner/meta_learning_comparison.png")


def run_full_demo():
    """Run comprehensive demonstration."""
    print("\n" + "#" * 70)
    print("# POMDP Meta-Learning: Learning Observation Assignments")
    print("#" * 70)

    # Test 1: Basic meta-learning
    test_line_world_meta()

    # Test 2: Compare with baseline
    test_random_search_baseline()

    # Test 3: Different k values
    test_different_k_values()

    # Test 4: GridWorld
    test_gridworld_meta()

    print("\n" + "=" * 70)
    print("All meta-learning tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    run_full_demo()
