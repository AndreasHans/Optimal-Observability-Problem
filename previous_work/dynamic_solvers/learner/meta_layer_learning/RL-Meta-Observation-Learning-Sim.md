# POMDP Simulator for RL-based Observation Learning

## Goal
Create a simulation environment to learn observation assignments (Y) through actual POMDP episodes, rather than black-box oracle optimization.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  Outer Loop: Learn Observation Assignment Y    │
│  (Meta-learning: which states to group)         │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Inner Loop: Learn Policy π for fixed Y        │
│  (Standard POMDP RL: Q-learning, etc.)          │
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

---

## Component 2: Policy Learning (Inner Loop)

Learn optimal policy for **fixed Y** using standard POMDP RL algorithms.

### Option A: Belief-based Q-learning
```python
class BeliefQLearning:
    """Q-learning with belief state tracking."""

    def __init__(self, n_obs: int, n_actions: int):
        self.Q = {}  # Q(belief, action)
        self.n_obs = n_obs
        self.n_actions = n_actions

    def update_belief(self, belief, action, observation):
        """Bayesian belief update given (a, o)."""
        # P(s' | belief, a, o) using Bayes rule
        pass

    def train_episode(self, env: LinePOMDP):
        """Run one episode, update Q-values."""
        belief = initial_uniform_belief()
        total_reward = 0

        while not done:
            action = epsilon_greedy(belief, self.Q)
            obs, reward, done = env.step(action)

            # Update belief
            next_belief = self.update_belief(belief, action, obs)

            # Q-learning update
            self.update_Q(belief, action, reward, next_belief)

            belief = next_belief
            total_reward += reward

        return total_reward
```

### Option B: Simpler Observation-based Q-learning
```python
class ObservationQLearning:
    """Simpler: Q(observation, action) without explicit beliefs."""

    def __init__(self, n_obs: int, n_actions: int):
        self.Q = np.zeros((n_obs, n_actions))

    def train_episode(self, env: LinePOMDP):
        obs = env.reset()
        total_reward = 0

        while not done:
            action = epsilon_greedy(obs, self.Q)
            next_obs, reward, done = env.step(action)

            # Q-learning update
            self.Q[obs, action] += lr * (
                reward + gamma * max(self.Q[next_obs]) - self.Q[obs, action]
            )

            obs = next_obs
            total_reward += reward

        return total_reward
```

**Recommendation**: Start with **Option B** (simpler, faster convergence for exploration).

---

## Component 3: Y Learning (Outer Loop)

Evaluate Y based on learned policy performance.

```python
def meta_train(agent: POPAgent, env_spec: dict, meta_episodes: int):
    """
    Meta-learning loop for observation assignment Y.

    For each Y configuration:
      1. Sample Y from agent.theta
      2. Create environment with this Y
      3. Train policy π for this Y (inner loop)
      4. Evaluate π performance (avg reward over test episodes)
      5. Update agent.theta based on performance
    """

    for meta_ep in range(meta_episodes):
        # Sample observation assignment
        Y, probs = agent.sample()

        # Create environment with this Y
        env = LinePOMDP(size=env_spec['size'], goal=env_spec['goal'], Y=Y)

        # Train policy for this Y (inner loop)
        policy = ObservationQLearning(n_obs=agent.k, n_actions=2)

        for _ in range(inner_episodes):
            policy.train_episode(env)

        # Evaluate learned policy
        test_reward = evaluate_policy(policy, env, test_episodes=10)

        # Update Y using REINFORCE
        agent.update(Y, probs, test_reward)
```

---

## Component 4: Evaluation Metrics

Track:
1. **Inner loop**: Policy convergence speed, final performance
2. **Outer loop**: Y convergence, observation class distribution
3. **Comparison**: Compare learned Y with oracle-verified optimal Y

---

## Implementation Steps

3. **Implement ObservationQLearning** (simple baseline)
4. **Implement meta-training loop**
5. **Run experiments**: Compare learned Y vs oracle Y
6. **(Optional) Add belief-based methods** if obs-based insufficient

---

## Expected Outcome

- **Dense reward signal**: Every step provides learning signal
- **Generalizable**: Can evaluate Y on multiple episodes
- **Insight**: Understand which observation groupings enable good policies
- **Validation**: Use oracle to verify if learned Y is actually optimal
