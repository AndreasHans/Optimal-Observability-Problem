"""
Test script for POMDP environments.

Demonstrates LineWorld, GridWorld, and MazeWorld with different observation assignments.
This file focuses on integration testing - full environment lifecycle with observations, rewards, and rendering.
For unit tests of navigation mechanics, see test_env_navigation.py
"""

import numpy as np
from pomdp_simulation.pomdp_environment import LinePOMDPEnv, GridPOMDPEnv, MazePOMDPEnv
from previous_work.dynamic_solvers.builders.enums import OOPVariant


def test_line_world():
    """Test LineWorld with different observation assignments."""
    print("=" * 60)
    print("Testing LineWorld")
    print("=" * 60)

    size = 5
    goal = 4

    # Test 1: Perfect observations (each state has unique observation)
    print("\n1. Perfect observations (Y = [0, 1, 2, 3, 4]):")
    Y_perfect = np.array([0, 1, 2, 3, 4])
    env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y_perfect, pomdp_variant=OOPVariant.POP, seed=42)

    obs, info = env.reset()
    print(f"Initial: {env.render()}")

    for step in range(10):
        action = 1  # Always move right
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Step {step+1}: {env.render()} | Reward={reward:.1f}")
        if terminated:
            print(f"Goal reached in {step+1} steps!")
            break

    # Test 2: Aliased observations (multiple states share same observation)
    print("\n2. Aliased observations (Y = [0, 0, 1, 1, 2]):")
    Y_aliased = np.array([0, 0, 1, 1, 2])
    env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y_aliased, pomdp_variant=OOPVariant.POP, seed=42)

    obs, info = env.reset()
    print(f"Initial: {env.render()}")

    for step in range(10):
        action = 1  # Always move right
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Step {step+1}: {env.render()} | Reward={reward:.1f}")
        if terminated:
            print(f"Goal reached in {step+1} steps!")
            break

    # Test 3: Stochastic transitions
    print("\n3. Stochastic transitions (slip_prob=0.3):")
    env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y_perfect, pomdp_variant=OOPVariant.POP,
                       stochastic=True, slip_prob=0.3, seed=42)

    obs, info = env.reset()
    print(f"Initial: {env.render()}")

    for step in range(15):
        action = 1  # Try to move right
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Step {step+1}: {env.render()} | Reward={reward:.1f}")
        if terminated:
            print(f"Goal reached in {step+1} steps (with slipping!)!")
            break


def test_grid_world():
    """Test GridWorld with 2D navigation."""
    print("\n" + "=" * 60)
    print("Testing GridWorld")
    print("=" * 60)

    rows, cols = 3, 3
    goal = (2, 2)  # Bottom-right corner

    # Observation assignment: group by Manhattan distance to goal
    # State (0,0)->idx 0, (0,1)->idx 1, (0,2)->idx 2
    # State (1,0)->idx 3, (1,1)->idx 4, (1,2)->idx 5
    # State (2,0)->idx 6, (2,1)->idx 7, (2,2)->idx 8
    Y = np.array([
        4, 3, 2,  # Row 0: distances 4, 3, 2 from goal
        3, 2, 1,  # Row 1: distances 3, 2, 1 from goal
        2, 1, 0   # Row 2: distances 2, 1, 0 (goal)
    ])

    env = GridPOMDPEnv(rows=rows, cols=cols, goal=goal, obs_function=Y, pomdp_variant=OOPVariant.POP, seed=42)

    obs, info = env.reset()
    print(f"Initial state:\n{env.render()}\n")

    # Simple policy: move right then down
    actions = [1, 1, 2, 2]  # right, right, down, down
    action_names = ['up', 'right', 'down', 'left']

    for step, action in enumerate(actions):
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Action: {action_names[action]}")
        print(f"{env.render()}")
        print(f"Reward={reward:.1f}\n")
        if terminated:
            print(f"Goal reached in {step+1} steps!")
            break


def test_maze_world():
    """Test MazeWorld with fixed structure: 3 vertical corridors + free horizontal corridor."""
    print("\n" + "=" * 60)
    print("Testing MazeWorld (3 vertical corridors + free top row)")
    print("=" * 60)

    width, depth = 5, 5
    n_states = width + 3 * (depth - 1)  # 17 states
    goal = 15  # State 15 = position (4, 2) = middle corridor bottom

    # Standard maze layout: vertical walls at columns 1 and 3, free top row
    # Layout:
    #   . . . . .  (row 0 - free horizontal corridor)
    #   . # . # .  (row 1 - walls at cols 1, 3)
    #   . # . # .  (row 2 - walls at cols 1, 3)
    #   . # . # .  (row 3 - walls at cols 1, 3)
    #   . # . # .  (row 4 - walls at cols 1, 3)
    # State numbering: 0-4 (top row), then 3 states per row (left/middle/right corridors)
    # States 0-4: row 0, States 5-7: row 1, States 8-10: row 2, etc.

    # Observation assignment: group by depth
    # Top row: obs 0 (shared across all 5 positions)
    # Vertical corridors: obs 1-4 by row (aliased across all 3 corridors)
    Y = np.zeros(n_states, dtype=int)
    for state in range(n_states):
        if state < width:
            Y[state] = 0  # Top row
        else:
            row = (state - width) // 3 + 1
            Y[state] = row  # Rows 1-4 -> obs 1-4

    # Goal gets unique observation
    Y[goal] = 5

    env = MazePOMDPEnv(width=width, depth=depth, goal=goal,
                       obs_function=Y, pomdp_variant=OOPVariant.POP, seed=42)

    obs, info = env.reset()
    print(f"Initial state:\n{env.render()}\n")
    print("Note: Agent can navigate in top horizontal corridor (states 0-4)")
    print("      and three vertical corridors (left/middle/right)")
    print("Observation function: States at same depth share observations\n")

    # Manual navigation - demonstrate corridor movement
    print("Attempting to navigate to goal...")

    for step in range(30):
        current_state = env.state

        # Simple policy: try to reach middle corridor (state 6) and move down
        if current_state < width:  # In top corridor
            # Move toward middle column (state 2)
            if current_state < 2:
                action = 1  # Move right
            elif current_state > 2:
                action = 3  # Move left
            else:  # At state 2 (position 0,2)
                action = 2  # Move down into middle corridor
        elif current_state in [6, 9, 12, 15]:  # In middle corridor
            # Move down toward goal
            action = 2  # Move down
        else:  # In left or right corridor
            # Move up to top corridor first
            action = 0  # Move up

        obs, reward, terminated, truncated, info = env.step(action)

        if step < 10 or terminated:  # Print first 10 steps and final
            print(f"Step {step+1}:")
            print(f"{env.render()}")
            print(f"State={current_state}, Obs={obs}, Reward={reward:.1f}\n")

        if terminated:
            print(f"Goal reached in {step+1} steps!")
            break

    if not terminated:
        print("Did not reach goal in 30 steps")


def test_observation_aliasing():
    """Demonstrate the importance of observation assignment Y."""
    print("\n" + "=" * 60)
    print("Demonstrating Observation Aliasing")
    print("=" * 60)

    size = 8
    goal = 7

    # Scenario 1: Good Y - preserves spatial structure
    Y_good = np.array([0, 0, 1, 1, 2, 2, 3, 3])

    # Scenario 2: Bad Y - random grouping
    Y_bad = np.array([0, 2, 1, 0, 2, 1, 0, 3])

    print("\nScenario 1: Good Y (preserves spatial structure)")
    print(f"Y = {Y_good}")
    env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y_good, pomdp_variant=OOPVariant.POP, seed=10)
    obs, info = env.reset()
    print(f"{env.render()}")

    for _ in range(3):
        obs, reward, terminated, truncated, info = env.step(1)  # Move right
        print(f"{env.render()}")
        if terminated:
            break

    print("\n\nScenario 2: Bad Y (poor spatial structure)")
    print(f"Y = {Y_bad}")
    env = LinePOMDPEnv(size=size, goal=goal, obs_function=Y_bad, pomdp_variant=OOPVariant.POP, seed=10)
    obs, info = env.reset()
    print(f"{env.render()}")

    for _ in range(3):
        obs, reward, terminated, truncated, info = env.step(1)  # Move right
        print(f"{env.render()}")
        if terminated:
            break

    print("\nNote: With bad Y, consecutive states may have non-consecutive observations,")
    print("making it harder for the agent to learn a good policy!")


if __name__ == "__main__":
    test_line_world()
    test_grid_world()
    test_maze_world()
    test_observation_aliasing()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
