import numpy as np
from z3 import sat, unsat, unknown

from builders.pop import LineTPMC, GridTPMC
from previous_work.dynamic_solvers.builders.pop.POPSpec import POPSpec
from previous_work.dynamic_solvers.Z3Executor import Z3Executor
from previous_work.dynamic_solvers.builders.POMDPAdapter import POMDPAdapter
from previous_work.dynamic_solvers.learner.guess import start_observation_function


class ObservativeAgent:
    """Agent for positional observability problem (POP) with multi-class observations using Categorical distribution."""

    def __init__(self, tpmc: POPSpec, goal: int,
                 n_states: int, n_classes: int, lr: float = 0.05):
        """
        Args:
            goal: Goal state index
            n_states: Number of states
            n_classes: Number of observation classes (budget)
            lr: Learning rate
        """
        self.n = n_states
        self.goal = goal
        self.k = n_classes
        self.lr = lr
        self.tpmc = tpmc

        # theta[i, c] is the logit for observation class c at state i
        self.theta = self._initialize_theta("atomic")
        self.baseline = 0.0 # prevent random noise from destabilizing the update

    def _initialize_theta(self, strategy: str) -> np.ndarray:
        """Initialize theta with different strategies.

        Args:
            strategy: "uniform", "alternating", or "atomic"

        Returns:
            theta: [n_states, n_classes] logit array
        """
        theta = np.zeros((self.n, self.k), dtype=float)

        if strategy == "uniform":
            # All zeros = uniform sampling across classes
            return theta

        elif strategy == "alternating":
            # Assign alternating spatial patterns
            for i in range(self.n):
                if i != self.goal:
                    preferred_class = i % self.k
                    theta[i, preferred_class] = 1.5
            return theta

        elif strategy == "atomic":
            # Perform initial guess based on merging of atomic groups
            obs_function = start_observation_function(self.tpmc, self.tpmc.budget)
            print(" ".join(list(map(str, obs_function))))
            beta = 2.5
            for i in range(len(obs_function)):
                if obs_function[i] == -1:
                    continue
                theta[i, :] = -beta
                theta[i][obs_function[i]] = beta
            return theta
        else:
            raise ValueError(f"Unknown init_strategy: {strategy}")

    def reset_theta(self, strategy: str):
        """Reset theta with a new initialization strategy."""
        self.theta = self._initialize_theta(strategy)
        self.baseline = 0.0

    def softmax(self, logits):
        """Numerically stable softmax."""
        e = np.exp(logits - np.max(logits))
        return e / np.sum(e)

    def sample(self):
        """Sample categorical observation assignment Y."""
        Y = []
        probs_list = []

        for i in range(self.n):
            if i == self.goal:
                Y.append(-1)
                probs_list.append(None)
            else:
                probs = self.softmax(self.theta[i])
                Y.append(np.random.choice(self.k, p=probs))
                probs_list.append(probs)

        return Y, probs_list

    def update(self, Y: list[int], probs_list: list, reward: float):
        """REINFORCE update for Categorical distribution - MINIMIZATION."""
        self.baseline = 0.9 * self.baseline + 0.1 * reward
        advantage = reward - self.baseline

        for i in range(self.n):
            if i == self.goal or probs_list[i] is None:
                continue

            # One-hot encoding of sampled class
            onehot = np.zeros(self.k)
            onehot[Y[i]] = 1

            # Gradient: (onehot - probs)
            grad = onehot - probs_list[i]
            # Negative sign for MINIMIZATION (gradient descent)
            self.theta[i] -= self.lr * advantage * grad


def train(agent: ObservativeAgent, oracle: Z3Executor, pomdp: POMDPAdapter,
              episodes: int = 200, timeout: int = 10000,
              penalty_unsat: float = 1000, penalty_timeout: float = 500):
    """Train observative agent (POP) with oracle feedback as black-box optimization."""

    stats = {'sat': 0, 'unsat': 0, 'timeout': 0, 'best_reward': float('inf'), 'best_Y': None}

    for ep in range(episodes):
        Y, probs = agent.sample()
        print(Y)
        result = oracle.evaluate_pomdp(pomdp, Y, timeout)

        if result.result == sat:
            reward = float(result.reward.as_fraction())
            stats['sat'] += 1
            if reward < stats['best_reward']:  # MINIMIZATION: track lowest reward
                stats['best_reward'] = reward
                stats['best_Y'] = Y.copy()
        elif result.result == unsat:
            reward = penalty_unsat
            stats['unsat'] += 1
        else:
            reward = penalty_timeout
            stats['timeout'] += 1

        agent.update(Y, probs, reward)

        if ep % 10 == 0:
            obs_dist = [Y.count(c) for c in range(agent.k)]
            print(f"EP {ep:03d} | R={reward:7.2f} | B={agent.baseline:7.2f} | "
                  f"SAT={stats['sat']:3d} UNSAT={stats['unsat']:2d} TO={stats['timeout']:2d} | dist={obs_dist}")

    return agent, stats

if __name__ == "__main__":
    budget = 2
    width, height = 10, 10
    goal = 99
    tau = "900 / 99"
    threshold = f"<= {tau}"
    tpmc = GridTPMC(budget, goal, width, height, determinism=False, verbose=False)
    context = tpmc.ctx
    pomdp = POMDPAdapter(tpmc)

    solver = Z3Executor(context, verbose=True)
    solver.prepare_constraints(pomdp, threshold)

    agent = ObservativeAgent(tpmc, goal, n_states=tpmc.size, n_classes=budget)

    trained_agent, stats = train(agent, solver, pomdp, episodes=20, timeout=10000)
    final_Y, _ = trained_agent.sample()
    print(f"\nBest Y: {stats['best_Y']}")
    print(f"Best reward: {stats['best_reward']}")
