"""
Quick test to verify POMDP environment with World inheritance.
"""
import numpy as np
from pomdp_simulation.pomdp_environment import LinePOMDPEnv, GridPOMDPEnv, MazePOMDPEnv
from previous_work.dynamic_solvers.builders.enums import OOPVariant


def test_lineworld():
    """Test LineWorld inherits from Line and uses navigate()."""
    print("Testing LineWorld...")

    # Create a simple 5-position line
    size = 5
    Y = np.array([0, 1, 1, 2, -1])  # Observation function
    env = LinePOMDPEnv(size=size, goal=4, obs_function=Y, pomdp_variant=OOPVariant.POP, seed=42)

    # Test navigation
    env.state = 2

    # Test left action (0)
    next_state = env.transition(env.state, action=0)
    assert next_state == 1, f"Expected state 1, got {next_state}"
    print(f"  ✓ Left action: state 2 -> {next_state}")

    # Test right action (1)
    next_state = env.transition(2, action=1)
    assert next_state == 3, f"Expected state 3, got {next_state}"
    print(f"  ✓ Right action: state 2 -> {next_state}")

    # Test boundary (left at 0)
    next_state = env.transition(0, action=0)
    assert next_state == 0, f"Expected state 0, got {next_state}"
    print(f"  ✓ Left boundary: state 0 -> {next_state}")

    print("✓ LineWorld tests passed!\n")


def test_gridworld():
    """Test GridWorld inherits from Grid and uses navigate() with converters."""
    print("Testing GridWorld...")

    # Create a 3x4 grid
    rows, cols = 3, 4
    Y = np.arange(rows * cols)  # Simple observation function
    env = GridPOMDPEnv(rows=rows, cols=cols, goal=(2, 3), obs_function=Y,
                       pomdp_variant=OOPVariant.POP, seed=42)

    # Test navigation from (1, 1)
    state = (1, 1)

    # Test up action (0)
    next_state = env.transition(state, action=0)
    assert next_state == (0, 1), f"Expected (0, 1), got {next_state}"
    print(f"  ✓ Up action: {state} -> {next_state}")

    # Test right action (1)
    next_state = env.transition(state, action=1)
    assert next_state == (1, 2), f"Expected (1, 2), got {next_state}"
    print(f"  ✓ Right action: {state} -> {next_state}")

    # Test down action (2)
    next_state = env.transition(state, action=2)
    assert next_state == (2, 1), f"Expected (2, 1), got {next_state}"
    print(f"  ✓ Down action: {state} -> {next_state}")

    # Test left action (3)
    next_state = env.transition(state, action=3)
    assert next_state == (1, 0), f"Expected (1, 0), got {next_state}"
    print(f"  ✓ Left action: {state} -> {next_state}")

    # Test boundary (up at row 0)
    next_state = env.transition((0, 1), action=0)
    assert next_state == (0, 1), f"Expected (0, 1), got {next_state}"
    print(f"  ✓ Up boundary: (0, 1) -> {next_state}")

    print("✓ GridWorld tests passed!\n")


def test_mazeworld():
    """Test MazeWorld inherits from Maze with fixed structure."""
    print("Testing MazeWorld...")

    # Create a 5x5 maze with vertical walls and a free horizontal corridor at top
    # Layout:
    #   . . . . .  (row 0 - free horizontal corridor)
    #   . # . # .  (row 1 - walls at cols 1, 3)
    #   . # . # .  (row 2 - walls at cols 1, 3)
    #   . # . # .  (row 3 - walls at cols 1, 3)
    #   . # . # .  (row 4 - walls at cols 1, 3)
    # State numbering (17 states total):
    #   0-4: top row (0,0) to (0,4)
    #   5-7: row 1 - (1,0), (1,2), (1,4)
    #   8-10: row 2 - (2,0), (2,2), (2,4)
    #   11-13: row 3 - (3,0), (3,2), (3,4)
    #   14-16: row 4 - (4,0), (4,2), (4,4)
    width, depth = 5, 5
    n_states = width + 3 * (depth - 1)  # 5 + 12 = 17 states

    goal = 15  # State 15 = position (4, 2) = middle corridor bottom
    Y = np.arange(n_states)  # Simple observation function
    env = MazePOMDPEnv(width=width, depth=depth, goal=goal, obs_function=Y,
                       pomdp_variant=OOPVariant.POP, seed=42)

    # Test movement in top row (free horizontal corridor)
    state = 0  # Position (0, 0)

    # Move right along top corridor (should succeed)
    next_state = env.transition(state, action=1)  # Right to state 1
    assert next_state == 1, f"Expected state 1, got {next_state}"
    print(f"  ✓ Top corridor movement (right): state {state} -> {next_state}")

    # Continue moving right
    state = 1  # Position (0, 1)
    next_state = env.transition(state, action=1)  # Right to state 2
    assert next_state == 2, f"Expected state 2, got {next_state}"
    print(f"  ✓ Top corridor movement (right): state {state} -> {next_state}")

    # Test movement in left vertical corridor
    state = 5  # Position (1, 0) - left corridor, row 1

    # Try to move right into wall (should stay in place)
    next_state = env.transition(state, action=1)  # Right into wall
    assert next_state == 5, f"Expected to stay at state 5, got {next_state}"
    print(f"  ✓ Wall collision (right): state {state} -> {next_state} (stayed in place)")

    # Move down in corridor (should succeed)
    next_state = env.transition(state, action=2)  # Down to state 8
    assert next_state == 8, f"Expected state 8, got {next_state}"
    print(f"  ✓ Vertical corridor movement (down): state {state} -> {next_state}")

    # Move up back to top corridor (should succeed)
    state = 5  # Position (1, 0)
    next_state = env.transition(state, action=0)  # Up to state 0
    assert next_state == 0, f"Expected state 0, got {next_state}"
    print(f"  ✓ Vertical corridor movement (up): state {state} -> {next_state}")

    # Test movement in middle vertical corridor
    state = 9  # Position (2, 2) - middle corridor, row 2

    # Try to move left into wall (should stay in place)
    next_state = env.transition(state, action=3)  # Left into wall
    assert next_state == 9, f"Expected to stay at state 9, got {next_state}"
    print(f"  ✓ Wall collision (left): state {state} -> {next_state} (stayed in place)")

    # Try to move right into wall (should stay in place)
    next_state = env.transition(state, action=1)  # Right into wall
    assert next_state == 9, f"Expected to stay at state 9, got {next_state}"
    print(f"  ✓ Wall collision (right): state {state} -> {next_state} (stayed in place)")

    # Move down toward goal (should succeed)
    next_state = env.transition(state, action=2)  # Down to state 12
    assert next_state == 12, f"Expected state 12, got {next_state}"
    print(f"  ✓ Vertical corridor movement (down): state {state} -> {next_state}")

    # Test reaching goal
    state = 12  # Position (3, 2)
    next_state = env.transition(state, action=2)  # Down to goal at state 15
    assert next_state == 15, f"Expected goal at state 15, got {next_state}"
    print(f"  ✓ Movement to goal: state {state} -> {next_state}")

    print("✓ MazeWorld tests passed!\n")


def test_grid_converters():
    """Test state-index converters work correctly."""
    print("Testing converters...")

    rows, cols = 3, 4
    Y = np.arange(rows * cols)
    env = GridPOMDPEnv(rows=rows, cols=cols, goal=(2, 3), obs_function=Y,
                       pomdp_variant=OOPVariant.POP, seed=42)

    # Test various conversions
    test_cases = [
        ((0, 0), 0),
        ((0, 3), 3),
        ((1, 1), 5),
        ((2, 3), 11),
    ]

    for state, expected_idx in test_cases:
        idx = env._state_to_index(state)
        assert idx == expected_idx, f"state_to_index({state}) = {idx}, expected {expected_idx}"

        recovered_state = env._index_to_state(idx)
        assert recovered_state == state, f"index_to_state({idx}) = {recovered_state}, expected {state}"

        print(f"  ✓ {state} <-> {idx}")

    print("✓ Converter tests passed!\n")

def test_maze_converters():
    """Test state-to-grid-position mapping for maze."""
    print("Testing maze state-to-grid converters...")

    width, depth = 5, 5
    n_states = width + 3 * (depth - 1)  # 17 states
    Y = np.arange(n_states)

    env = MazePOMDPEnv(width=width, depth=depth, goal=15, obs_function=Y,
                       pomdp_variant=OOPVariant.POP, seed=42)

    # Test state index to grid position conversions
    test_cases = [
        (0, (0, 0)),   # Top row left
        (2, (0, 2)),   # Top row middle
        (4, (0, 4)),   # Top row right
        (5, (1, 0)),   # Row 1 left corridor
        (6, (1, 2)),   # Row 1 middle corridor
        (7, (1, 4)),   # Row 1 right corridor
        (9, (2, 2)),   # Row 2 middle corridor
        (12, (3, 2)),  # Row 3 middle corridor
        (15, (4, 2)),  # Row 4 middle corridor (goal)
        (16, (4, 4)),  # Row 4 right corridor
    ]

    for state_idx, expected_pos in test_cases:
        grid_pos = env._state_to_grid_pos(state_idx)
        assert grid_pos == expected_pos, f"state_to_grid_pos({state_idx}) = {grid_pos}, expected {expected_pos}"
        print(f"  ✓ State {state_idx} -> {grid_pos}")

    print("✓ Maze converter tests passed!\n")

if __name__ == "__main__":
    test_lineworld()
    test_gridworld()
    test_mazeworld()
    test_grid_converters()
    test_maze_converters()
    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
