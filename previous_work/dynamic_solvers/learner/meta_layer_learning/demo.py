"""
POMDP Simulator Demo
====================

Interactive demonstrations of the POMDP simulator with meta-learning.

Run this script to see:
1. How different observation assignments Y affect policy learning
2. How meta-learning discovers good Y assignments
3. Comparison across different world types
"""

import numpy as np
from learner.pomdp_simulation.pomdp_environment import LinePOMDPEnv, GridPOMDPEnv, MazePOMDPEnv
from previous_work.dynamic_solvers.learner.meta_layer_learning.q_learning import ObservationQLearning
from previous_work.dynamic_solvers.learner.meta_layer_learning.meta_learning import meta_train


def demo_observation_impact():
    """
    Demo 1: Show how Y affects policy learning.

    Compares three Y assignments on the same LineWorld:
    - Perfect: Each state has unique observation
    - Good: Adjacent states grouped (spatial structure)
    - Bad: Random grouping (no structure)
    """
    print("=" * 70)
    print("DEMO 1: Impact of Observation Assignment Y")
    print("=" * 70)
    print("\nQuestion: How does Y affect policy learning?")
    print("Environment: 8-state line, goal at position 7\n")

    size = 8
    goal = 7

    scenarios = [
        ("Perfect (unique obs)", np.array([0, 1, 2, 3, 4, 5, 6, 7])),
        ("Good (spatial)", np.array([0, 0, 1, 1, 2, 2, 3, 3])),
        ("Bad (random)", np.array([0, 2, 1, 0, 2, 1, 0, 3]))
    ]

    print("Observation Assignments:")
    for name, Y in scenarios:
        print(f"  {name:20s}: {Y}")

    print("\nTraining policies...\n")

    for name, Y in scenarios:
        env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y, seed=42)
        agent = ObservationQLearning(
            n_obs=len(np.unique(Y)),
            n_actions=2,
            learning_rate=0.1,
            seed=42
        )

        # Train
        metrics = agent.train(env, n_episodes=300, verbose=False)

        # Evaluate
        avg_reward, avg_length = agent.evaluate(env, n_episodes=20)

        # Show results
        print(f"{name:20s}: Reward={avg_reward:6.2f}, Length={avg_length:5.1f}, Policy={agent.get_policy()}")

    print("\nKey Insight:")
    print("  ✓ Good Y (spatial structure) enables efficient learning")
    print("  ✗ Bad Y (poor structure) makes learning harder")
    print()


def demo_meta_learning():
    """
    Demo 2: Meta-learning discovers good Y automatically.

    Shows that meta-learning can find observation assignments
    that enable good policy performance.
    """
    print("=" * 70)
    print("DEMO 2: Meta-Learning Discovers Good Y")
    print("=" * 70)
    print("\nQuestion: Can we learn Y automatically?")
    print("Approach: Meta-learning with REINFORCE\n")

    size = 6
    goal = 5
    k = 3

    def env_factory(Y):
        return LinePOMDPEnv(size=size, goal=goal, obs_function=Y, seed=42)

    print(f"Environment: {size} states, goal at {goal}")
    print(f"Observation classes: {k}")
    print("\nRunning meta-learning (30 episodes)...\n")

    result = meta_train(
        env_factory=env_factory,
        n_states=size,
        k=k,
        meta_episodes=30,
        inner_episodes=150,
        eval_episodes=10,
        method="softmax",
        meta_lr=0.1,
        seed=42,
        verbose=False
    )

    print(f"Best Y found:  {result.best_Y}")
    print(f"Best reward:   {result.best_reward:.2f}")

    # Compare with a known good Y
    Y_good = np.array([0, 0, 1, 1, 2, 2])
    env_good = env_factory(Y_good)
    agent_good = ObservationQLearning(n_obs=k, n_actions=2, seed=42)
    agent_good.train(env_good, n_episodes=150, verbose=False)
    reward_good, _ = agent_good.evaluate(env_good, n_episodes=10)

    print(f"\nComparison:")
    print(f"  Known good Y: {Y_good}")
    print(f"  Known good Y reward: {reward_good:.2f}")

    if result.best_reward >= reward_good * 0.9:
        print("\n✓ Meta-learning found a competitive Y!")
    else:
        print("\n→ Meta-learning could be improved with more episodes")

    # Show learning progress
    print(f"\nReward progression (first 10 episodes):")
    for i, r in enumerate(result.reward_history[:10]):
        print(f"  Episode {i+1:2d}: {r:6.2f}")
    print()


def demo_world_types():
    """
    Demo 3: Different world types (Line, Grid, Maze).

    Shows that the same Q-learning algorithm works across
    different environment types.
    """
    print("=" * 70)
    print("DEMO 3: Multiple World Types")
    print("=" * 70)
    print("\nQuestion: Does the simulator support different world types?")
    print("Answer: Yes! Line, Grid, and Maze worlds.\n")

    # 1. LineWorld
    print("--- LineWorld (1D) ---")
    line_env = LinePOMDPEnv(size=5, goal=4, obs_function=np.array([0, 0, 1, 1, 2]), seed=42)
    print("Initial state:")
    print(line_env.render())
    line_env.step(1)  # Move right
    print("After moving right:")
    print(line_env.render())
    print()

    # 2. GridWorld
    print("--- GridWorld (2D) ---")
    Y_grid = np.array([2, 2, 1, 2, 1, 1, 1, 1, 0])
    grid_env = GridPOMDPEnv(rows=3, cols=3, goal=(2, 2), obs_function=Y_grid, seed=42)
    print("Initial state:")
    print(grid_env.render())
    grid_env.step(1)  # Move right
    print("\nAfter moving right:")
    print(grid_env.render())
    print()

    # 3. MazeWorld
    print("--- MazeWorld (2D with obstacles) ---")
    obstacles = [(1, 1), (1, 2)]
    Y_maze = np.array([0, 0, 0, 0, 1, 0, 0, 0, 1])
    maze_env = MazePOMDPEnv(
        rows=3, cols=3, goal=(2, 2),
        obstacles=obstacles, obs_function=Y_maze, seed=42
    )
    print("Initial state (# = obstacle):")
    print(maze_env.render())
    maze_env.step(1)  # Try to move right
    print("\nAfter action:")
    print(maze_env.render())
    print()


def demo_training_visualization():
    """
    Demo 4: Visualize training process.

    Shows how Q-values evolve during training and how the
    learned policy performs.
    """
    print("=" * 70)
    print("DEMO 4: Training Visualization")
    print("=" * 70)
    print("\nQuestion: How does the agent learn?")
    print("Environment: 5-state line with good observation assignment\n")

    size = 5
    goal = 4
    Y = np.array([0, 0, 1, 1, 2])

    env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y, seed=42)
    agent = ObservationQLearning(
        n_obs=3,
        n_actions=2,
        learning_rate=0.2,
        discount_factor=0.9,
        epsilon_start=1.0,
        epsilon_end=0.01,
        seed=42
    )

    print("Training progress:")
    checkpoints = [10, 50, 100, 200]

    for checkpoint in checkpoints:
        # Train to checkpoint
        current_ep = agent.episodes_trained
        agent.train(env, n_episodes=checkpoint - current_ep, verbose=False)

        # Evaluate
        avg_reward, avg_length = agent.evaluate(env, n_episodes=10)

        print(f"  After {checkpoint:3d} episodes: Reward={avg_reward:6.2f}, "
              f"Length={avg_length:4.1f}, Epsilon={agent.epsilon:.3f}")

    print(f"\nFinal Q-table:")
    print("  Obs | Left  | Right")
    print("  ----|-------|-------")
    for obs in range(3):
        print(f"   {obs}  | {agent.Q[obs, 0]:5.2f} | {agent.Q[obs, 1]:5.2f}")

    print(f"\nLearned policy: {agent.get_policy()}")
    print("(0=left, 1=right)")

    # Show sample episode
    print("\nSample episode with learned policy:")
    env.reset()
    print(f"  {env.render()}")
    for step in range(10):
        obs = env.get_observation(env.state)
        action = agent.select_action(obs, epsilon=0.0)
        action_name = "left" if action == 0 else "right"
        obs, reward, done, info = env.step(action)
        print(f"  Action: {action_name:5s} -> {env.render()}")
        if done:
            print(f"  Goal reached in {step+1} steps!")
            break
    print()


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 70)
    print("# POMDP SIMULATOR DEMONSTRATION")
    print("# Learning Observation Assignments through Reinforcement Learning")
    print("#" * 70)
    print()

    try:
        demo_observation_impact()
        input("Press Enter to continue to Demo 2...")
        print()

        demo_meta_learning()
        input("Press Enter to continue to Demo 3...")
        print()

        demo_world_types()
        input("Press Enter to continue to Demo 4...")
        print()

        demo_training_visualization()

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        return

    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Run test_environments.py for environment tests")
    print("  2. Run test_q_learning.py for Q-learning tests")
    print("  3. Run test_meta_learning.py for meta-learning tests")
    print("  4. See README.md for API documentation")
    print()


if __name__ == "__main__":
    main()
