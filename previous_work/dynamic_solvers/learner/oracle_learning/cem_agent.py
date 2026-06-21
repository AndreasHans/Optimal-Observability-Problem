import numpy as np
from z3 import sat, unsat

from previous_work.dynamic_solvers.StormExecutor import StormExecutor
from previous_work.dynamic_solvers.builders.pop.POPSpec import POPSpec
from builders.ssp import LineTPMC
from previous_work.dynamic_solvers.builders.ssp.SSPSpec import SSPSpec
from previous_work.dynamic_solvers.Z3Executor import Z3Executor
from previous_work.dynamic_solvers.builders.POMDPAdapter import POMDPAdapter
from previous_work.dynamic_solvers.learner.guess import start_observation_function


class CEMAgent:
    """Cross-Entropy Method agent for observation assignment learning."""

    def __init__(self, tpmc: POPSpec | SSPSpec,
                 goal: int, n_states: int, n_classes: int, budget: int,
                 elite_frac: float = 0.4, smoothing: float = 0.1):
        """
        Args:
            goal: Goal state index
            n_states: Number of states
            n_classes: Number of observation classes (budget)
            elite_frac: Fraction of samples to use as elites (top performers)
            smoothing: Exponential smoothing factor for theta updates (0=no smoothing, 1=no update)
        """
        self.n = n_states
        self.goal = goal
        self.k = n_classes
        self.elite_frac = elite_frac
        self.smoothing = smoothing
        self.budget = budget

        # theta[i, c] = logit for observation class c at state i
        self.theta = self._initialize_theta(tpmc, "atomic")

    def _initialize_theta(self, tpmc: POPSpec | SSPSpec, strategy: str = "uniform") -> np.ndarray:
        # initialize logits for uniform distribution
        theta = np.zeros((self.n, self.k), dtype=float)

        if strategy == "atomic":
            # Perform initial guess based on merging of atomic groups
            mpb = tpmc.minimal_pos_budget()
            obs_function = start_observation_function(tpmc, mpb)
            print(obs_function)
            beta = 2.5
            for i in range(len(obs_function)):
                if obs_function[i] == -1:
                    continue
                theta[i, :] = -beta
                theta[i][obs_function[i]] = beta
        return theta

    def softmax(self, logits):
        """Numerically stable softmax."""
        e = np.exp(logits - np.max(logits))
        return e / np.sum(e)

    def get_probs(self):
        """Get current probability distribution for all states."""
        probs = np.zeros((self.n, self.k))
        for i in range(self.n):
            if i != self.goal:
                probs[i] = self.softmax(self.theta[i])
        return probs

    def sample(self):
        """Sample single observation assignment Y."""
        Y = []
        for i in range(self.n):
            if i == self.goal:
                Y.append(-1)
            else:
                probs = self.softmax(self.theta[i])
                Y.append(np.random.choice(self.k, p=probs))
        return Y

    def sample_batch(self, batch_size: int):
        """Sample batch of observation assignments."""
        return [self.sample() for _ in range(batch_size)]

    def update_from_elites(self, elite_samples: list[list[int]]):
        """
        Update theta to maximize likelihood of elite samples.

        Args:
            elite_samples: List of Y assignments that performed best
        """
        # Count observations per state in elite samples
        counts = np.zeros((self.n, self.k))

        for Y in elite_samples:
            for i in range(self.n):
                if i != self.goal:
                    counts[i, Y[i]] += 1

        # Convert counts to probabilities (MLE)
        new_probs = np.zeros((self.n, self.k))
        for i in range(self.n):
            if i != self.goal:
                total = counts[i].sum()
                if total > 0:
                    new_probs[i] = counts[i] / total
                else:
                    # No elite samples for this state, keep uniform
                    new_probs[i] = np.ones(self.k) / self.k

        # Convert probabilities back to logits (inverse softmax)
        # Use log probabilities as logits (up to constant)
        new_theta = np.log(new_probs + 1e-10)  # Add small epsilon for numerical stability

        # Smooth update: theta_new = (1-α)*theta_new + α*theta_old
        self.theta = (1 - self.smoothing) * new_theta + self.smoothing * self.theta


def train_cem(agent: CEMAgent, oracle: Z3Executor | StormExecutor, pomdp: POMDPAdapter,
              iterations: int = 50, batch_size: int = 20, timeout: int = 10000,
              penalty_unsat: float = -50, penalty_timeout: float = -100):
    """
    Train CEM agent with batched oracle evaluation.

    Args:
        agent: CEMAgent instance
        oracle: TPMCSolver instance
        pomdp: POMDPAdapter instance
        iterations: Number of CEM iterations
        batch_size: Number of samples per iteration
        timeout: Oracle timeout in milliseconds
        penalty_unsat: Penalty for UNSAT
        penalty_timeout: Penalty for timeout

    Returns:
        Trained agent and statistics
    """
    n_elites = max(1, int(batch_size * agent.elite_frac))

    stats = {
        'sat': 0, 'unsat': 0, 'timeout': 0,
        'best_reward': float('-inf'), 'best_Y': None,
        'history': []
    }

    for iteration in range(iterations):
        # Sample batch
        samples = agent.sample_batch(batch_size)
        # print(samples)
        rewards = []

        # Evaluate all samples
        for Y in samples:
            result = None
            if isinstance(oracle, Z3Executor):
                result = oracle.evaluate_pomdp(pomdp, Y, timeout)
            elif isinstance(oracle, StormExecutor):
                # Call for finite-state controller through `storm-pomdp` subprocess calls (using Sparse Exact POMDP)
                storm_res = oracle.evaluate_pomdp_fsc_cli(pomdp, Y, timeout)
                result = oracle.convert_storm_z3_result(storm_res)

            if result.result == sat:
                reward = float(result.reward)
                stats['sat'] += 1
                if reward < stats['best_reward']:
                    stats['best_reward'] = reward
                    stats['best_Y'] = Y.copy()
            elif result.result == unsat:
                reward = penalty_unsat
                stats['unsat'] += 1
            else:
                reward = penalty_timeout
                stats['timeout'] += 1

            rewards.append(reward)
        print(rewards)

        # Select elite samples (top performers)
        elite_indices = np.argsort(rewards)[0:n_elites]
        elite_samples = [samples[i] for i in elite_indices]
        elite_rewards = [rewards[i] for i in elite_indices]

        # Update distribution based on elites
        agent.update_from_elites(elite_samples)

        # Logging
        mean_reward = np.mean(rewards)
        elite_mean = np.mean(elite_rewards)

        stats['history'].append({
            'iteration': iteration,
            'mean_reward': mean_reward,
            'elite_mean': elite_mean,
            'best_reward': min(rewards)
        })

        print(f"Iter {iteration:03d} | Mean={mean_reward:7.2f} Elite={elite_mean:7.2f} "
              f"Best={min(rewards):7.2f} | SAT={stats['sat']:3d} UNSAT={stats['unsat']:2d} "
              f"TO={stats['timeout']:2d}")

    # Final summary
    print("\n" + "="*80)
    print("CEM Training Complete")
    print(f"Total evaluations: {iterations * batch_size}")
    print(f"SAT:     {stats['sat']:4d} ({stats['sat']/(iterations*batch_size)*100:.1f}%)")
    print(f"UNSAT:   {stats['unsat']:4d} ({stats['unsat']/(iterations*batch_size)*100:.1f}%)")
    print(f"TIMEOUT: {stats['timeout']:4d} ({stats['timeout']/(iterations*batch_size)*100:.1f}%)")
    stats['best_reward'] = stats['history'][-1]['best_reward']
    print(f"Best reward: {stats['best_reward']:.3f}")
    print("="*80)


    return agent, stats

if __name__ == "__main__":
    # POP Setting:
    # budget = 2
    # size = 31
    # goal = 15
    # tau = 16
    # threshold_q = 1

    # SSP Setting:
    budget = 30
    size = 61
    goal = 30
    tau = 31
    threshold_q = 1

    threshold = f"<= Q({tau * threshold_q}, 2)"
    tpmc = LineTPMC(budget, goal, size, determinism=False, verbose=False)
    context = tpmc.ctx
    pomdp = POMDPAdapter(tpmc)

    z3_solver = Z3Executor(context, verbose=True)
    storm_solver = StormExecutor(verbose=False, puzzle_type=tpmc.puzzle_type)

    z3_solver.prepare_constraints(pomdp, threshold)

    agent = CEMAgent(tpmc, goal, n_states=size, n_classes=2, budget=budget)

    # Training: soft guidance toward budget
    trained_agent, stats = train_cem(agent, z3_solver, pomdp, iterations=10, batch_size=10,
                                     timeout=10000, penalty_timeout=50, penalty_unsat=100)

    # Inference: enforce exact budget via top-k
    final_Y = trained_agent.sample()
    n_active_final = sum(1 for y in final_Y if y == 1)

    print(f"\nBest reward: {stats['best_reward']}")
    print(f"Final inference Y has {n_active_final} active sensors (budget={budget})")
    print(f"Final inference: {final_Y}")
