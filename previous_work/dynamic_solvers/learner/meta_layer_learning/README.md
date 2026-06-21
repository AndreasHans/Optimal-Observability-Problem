# POMDP Simulator with Meta-Learning

A complete POMDP (Partially Observable Markov Decision Process) simulation framework for learning observation assignments through reinforcement learning.

## Overview

This simulator implements a **two-level learning architecture**:

1. **Inner Loop**: Learn optimal policies for a fixed observation assignment Y using Q-learning
2. **Outer Loop**: Learn which observation assignment Y enables the best policy performance using meta-learning

### Why This Matters

In POMDPs, agents don't see the true state but receive observations. The observation function (Y) maps states to observation classes. A good Y should:
- Preserve task-relevant information
- Enable efficient policy learning
- Group similar states together

This framework learns Y through actual POMDP episodes, providing dense reward signals for optimization.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Outer Loop: Learn Observation Assignment Y    │
│  (Meta-learning: which states to group)         │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Inner Loop: Learn Policy π for fixed Y        │
│  (Standard POMDP RL: Q-learning, SARSA)         │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  POMDP Environment Simulator                    │
│  - State transitions                            │
│  - Observation function (depends on Y)          │
│  - Reward structure                             │
└─────────────────────────────────────────────────┘
```

## Components

### 1. POMDP Environments (`pomdp_environment.py`)

Three world types with a unified interface:

- **LineWorld**: 1D navigation (states: positions on a line)
- **GridWorld**: 2D navigation (states: grid cells)
- **MazeWorld**: 2D navigation with obstacles

All environments support:
- Customizable observation assignments (Y)
- Deterministic or stochastic transitions
- Goal-based rewards

### 2. Q-Learning (`q_learning.py`)

Observation-based Q-learning for POMDPs:

- **ObservationQLearning**: Standard off-policy Q-learning
- **SarsaLearning**: On-policy SARSA variant

Features:
- Epsilon-greedy exploration
- Decay schedules
- Training and evaluation modes
- Q-table persistence

### 3. Meta-Learning (`meta_learning.py`)

Learn observation assignments through policy gradient methods:

- **ObservationAssignmentAgent**: Samples Y from learned distribution
- **meta_train()**: REINFORCE-based meta-training loop
- **random_search()**: Baseline for comparison

## Installation

```bash
# Navigate to learner directory
cd learner

# Install dependencies (if needed)
pip install numpy matplotlib
```

## Quick Start

### Example 1: Train a Policy for Fixed Y

```python
from pomdp_environment import LineWorld
from q_learning import ObservationQLearning
import numpy as np

# Create environment with observation assignment
size = 8
goal = 7
Y = np.array([0, 0, 1, 1, 2, 2, 3, 3])  # Group adjacent states

env = LineWorld(size=size, goal=goal, Y=Y)

# Create Q-learning agent
agent = ObservationQLearning(
    n_obs=len(np.unique(Y)),
    n_actions=2,
    learning_rate=0.1,
    discount_factor=0.95
)

# Train
metrics = agent.train(env, n_episodes=500, verbose=True)

# Evaluate
avg_reward, avg_length = agent.evaluate(env, n_episodes=10)
print(f"Average reward: {avg_reward:.2f}")
print(f"Learned policy: {agent.get_policy()}")
```

### Example 2: Meta-Learn Observation Assignment

```python
from pomdp_environment import LineWorld
from meta_learning import meta_train

size = 8
goal = 7
k = 4  # Number of observation classes

# Environment factory
def env_factory(Y):
    return LineWorld(size=size, goal=goal, Y=Y)

# Run meta-training
result = meta_train(
    env_factory=env_factory,
    n_states=size,
    k=k,
    meta_episodes=50,
    inner_episodes=200,
    eval_episodes=10,
    method="softmax",
    verbose=True
)

print(f"Best Y found: {result.best_Y}")
print(f"Best reward: {result.best_reward:.2f}")
```

### Example 3: GridWorld Navigation

```python
from pomdp_environment import GridWorld
from q_learning import ObservationQLearning
import numpy as np

rows, cols = 4, 4
goal = (3, 3)

# Create Y based on Manhattan distance to goal
Y = np.zeros(rows * cols, dtype=int)
for r in range(rows):
    for c in range(cols):
        idx = r * cols + c
        dist = abs(r - goal[0]) + abs(c - goal[1])
        Y[idx] = min(dist, 4)

env = GridWorld(rows=rows, cols=cols, goal=goal, Y=Y)
agent = ObservationQLearning(n_obs=len(np.unique(Y)), n_actions=4)

metrics = agent.train(env, n_episodes=1000, verbose=True)
agent.evaluate(env, n_episodes=5, render=True)
```

## Running Tests

```bash
# Test environments
python test_environments.py

# Test Q-learning
python test_q_learning.py

# Test meta-learning
python test_meta_learning.py
```

## File Structure

```
learner/
├── README.md                      # This file
├── pomdp_simulator_plan.md        # Original design plan
├── pomdp_environment.py           # Environment implementations
├── q_learning.py                  # Q-learning algorithms
├── meta_learning.py               # Meta-learning for Y
├── test_environments.py           # Environment tests
├── test_q_learning.py             # Q-learning tests
└── test_meta_learning.py          # Meta-learning tests
```

## Key Concepts

### Observation Assignment (Y)

Y is an array mapping each state to an observation class:
- `Y[state] = observation_class`
- Agent sees observation classes, not true states
- Good Y preserves task-relevant structure

**Example**: For LineWorld with 8 states:
- Perfect: `Y = [0, 1, 2, 3, 4, 5, 6, 7]` (each state unique)
- Good: `Y = [0, 0, 1, 1, 2, 2, 3, 3]` (spatial grouping)
- Bad: `Y = [0, 2, 1, 0, 2, 1, 0, 3]` (random grouping)

### Inner vs Outer Loop

**Inner Loop** (Q-learning):
- Input: Fixed Y
- Output: Policy π
- Goal: Maximize cumulative reward

**Outer Loop** (Meta-learning):
- Input: Task specification
- Output: Observation assignment Y
- Goal: Find Y that enables best policy learning

### REINFORCE Algorithm

The meta-learner uses policy gradients:
1. Sample Y from parameterized distribution
2. Train policy for this Y
3. Evaluate policy performance (reward R)
4. Update distribution: increase probability of good Y

## Parameters

### Environment Parameters

- `size` / `rows`, `cols`: World dimensions
- `goal`: Goal state/position
- `Y`: Observation assignment
- `step_penalty`: Cost per step (typically -1)
- `goal_reward`: Reward at goal (typically 0)
- `stochastic`: Enable stochastic transitions
- `slip_prob`: Probability of random movement

### Q-Learning Parameters

- `learning_rate`: Step size for Q-updates (α)
- `discount_factor`: Future reward discount (γ)
- `epsilon_start`: Initial exploration rate
- `epsilon_end`: Minimum exploration rate
- `epsilon_decay`: Decay rate per episode

### Meta-Learning Parameters

- `meta_episodes`: Number of Y samples to try
- `inner_episodes`: Training episodes per Y
- `eval_episodes`: Evaluation episodes per Y
- `method`: Sampling method ("softmax", "random")
- `meta_lr`: Learning rate for Y updates

## Results

The meta-learning successfully discovers observation assignments that:
1. Enable faster policy convergence
2. Achieve higher final performance
3. Show spatial structure (adjacent states → similar observations)

See test outputs for detailed comparisons.

## Extensions

Possible extensions:
1. **Belief-based Q-learning**: Track belief states explicitly
2. **Deep RL**: Replace tabular Q with neural networks
3. **Multi-task learning**: Learn Y across multiple environments
4. **Hierarchical Y**: Learn multi-level observation abstractions
5. **Constraint-based Y**: Incorporate domain knowledge

## References

Based on the POMDP simulator plan for RL-based observation learning. See `pomdp_simulator_plan.md` for the original design document.