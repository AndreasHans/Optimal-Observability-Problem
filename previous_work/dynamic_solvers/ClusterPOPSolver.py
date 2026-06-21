import time

from z3 import sat, BoolRef, unknown

from previous_work.dynamic_solvers.Z3SolverResult import Z3SolverResult
from previous_work.dynamic_solvers.Z3Executor import Z3Executor
from previous_work.dynamic_solvers.builders.POMDPAdapter import POMDPAdapter
from previous_work.dynamic_solvers.builders.pop.POPSpec import POPSpec
from previous_work.dynamic_solvers.builders.ssp.SSPSpec import SSPSpec
from previous_work.dynamic_solvers.utils import stirling_partitions


def rank_partitions(tpmc: POPSpec | SSPSpec, partitions: list[list[list[int]]]) -> list[tuple[int, int, int]]:
    """
    Compute heuristic scores for each partition and return a ranking of partition indices.

    Heuristics used:
    - equivalence_score: counts how many blocks in the partition contain a common action for
      all atomic groups in that block (i.e. an 'equivalence' relation where a single action
      is optimal across the block).
    - constraint_score: the number of constraints that can be imposed on the strategy
      variables when the partition is applied. For example, blocks with an equivalence relation
      can stay optimal when set the rate of a common action to 1 and the rest to 0 (adding |Act| constraints).

    Args:
        tpmc (POPSpec | SSPSpec): a tpMC specification object.
        partitions (list[list[list[int]]]): The list of partitions to score.

    Returns:
        list[tuple[int,int,int]]: A list of tuples (partition_index, equivalence_score,
            constraint_score), sorted in descending order by (equivalence_score, constraint_score).
    """

    atomic_groups = list(tpmc.clusters.keys())
    ranking_partitions = []
    for (p, partition) in enumerate(partitions):
        equivalence_score = 0
        constraint_score = 0
        for block in partition:
            actions_per_atomic_group = [atomic_groups[atomic_group_idx].actions for atomic_group_idx in block]
            actions_in_block = set.union(*actions_per_atomic_group)
            equivalence_relation = True if len(set.intersection(*actions_per_atomic_group)) > 0 else False

            if equivalence_relation:
                equivalence_score += 1
                constraint_score += len(tpmc.actions)
            else:
                constraint_score += sum(1 for a in tpmc.actions if a not in actions_in_block)
        ranking_partitions.append((p, equivalence_score, constraint_score))
    return sorted(ranking_partitions, key=lambda ranking: (ranking[1], ranking[2]), reverse=True)


class ClusterPOPSolver:
    solver: Z3Executor
    tpmc: POPSpec
    verbose: bool
    adapter: POMDPAdapter

    def __init__(self, solver: Z3Executor, tpmc: POPSpec, verbose: bool, threshold: str) -> None:
        self.solver = solver
        self.tpmc = tpmc
        self.verbose = verbose
        self.adapter = POMDPAdapter(tpmc)
        self.solver.prepare_constraints(self.adapter, threshold)

    def solve(self, timeout_ms: int) -> Z3SolverResult:
        """
        Attempts to solve a POP instance by solving and evaluating the underlying POMDPs in it.

        The core algorithmic idea is to group states into 'atomic groups' based on their respective
        optimal action(s) in the underlying MDP. Eventually we explore a constant number of observation
        functions that combine the atomic distinguishability groups into observation classes.

        The observation functions are solved in an order specified by heuristic scores that estimate
        1) how close an observation function is to the optimal, and
        2) how much an observation function constraints its possible strategies.

        Args:
            timeout_ms (int): The timeout in milliseconds for the solver.

        Returns:
            ResultOOP with solve time, result, reward, and model (if any was found).
        """
        number_atomic_groups = len(self.tpmc.clusters)
        number_blocks = self.tpmc.budget
        k = min(number_atomic_groups, number_blocks)

        # Given a budget B, we generate all possible partitions for atomic groups into B blocks
        start = time.process_time()
        partitions = list(stirling_partitions(n=number_atomic_groups, k=k))

        now = time.process_time()
        if self.verbose:
            print(f"\nThere are S({number_atomic_groups},{k}) = {len(partitions)} partitions to explore")
            print(f"Generated partitions in {(now - start):.4f}s")
        start = now

        ranking_partitions = rank_partitions(self.tpmc, partitions)
        now = time.process_time()
        if self.verbose:
            print(f"\nRanking of observation functions completed in {(now - start):.4f}s")
        start = now

        result = self.search(partitions, ranking_partitions, timeout_ms)
        now = time.process_time()
        if self.verbose:
            print(f"\nSearch completed in {(now - start):.4f}s")

        return result

    def search(self, partitions: list[list[list[int]]], ranking_partitions: list[tuple[int, int, int]], timeout_ms) -> Z3SolverResult:
        """
        Args:
            partitions (list[list[list[int]]]): The list of partitions (each partition is a list
                of blocks and each block is a list of atomic-group indices).
            ranking_partitions (list[tuple[int,int,int]]): Ranked metadata for partitions.
            timeout_ms (int): Timeout in milliseconds.

        Returns:
            ResultOOP: If a satisfiable model is found it is returned immediately. Otherwise, a
                ResultOOP with result=unknown and the elapsed solve_time is returned.
        """

        atomic_groups = list(self.tpmc.clusters.keys())
        total_solve_time = 0
        for partition_idx, equivalence_score, constraint_score in ranking_partitions:
            partition = partitions[partition_idx]
            if self.verbose:
                partition_str = [[atomic_groups[atomic_group_idx].name for atomic_group_idx in block] for block in partition]
                print(f"Evaluating partition: {partition_str} | h_equivalence_score = {equivalence_score}, h_constraint_score = {constraint_score}")

            observation_function, strategy_constraints = self.apply_partition_to_states(partition)
            assert constraint_score == len(strategy_constraints)

            # We use a default 30s timeout for each POMDP evaluation
            result = self.solver.evaluate_pomdp(self.adapter, observation_function, 30000, strategy_constraints)

            if result.result == sat:
                result.obs = self.adapter.extract_obs_solution(observation_function)
                result.solve_time += total_solve_time
                return result
            else:
                total_solve_time += result.solve_time
                if self.verbose:
                    print(f"Time to solve: {result.solve_time:.4f}s | Result = {result.result}")
                if total_solve_time * 1000 > timeout_ms:
                    return Z3SolverResult(
                        solve_time=total_solve_time,
                        result=unknown,
                        reward=None,
                        model=None
                    )

        # Call the TPMC solver as a fallback
        return self.solver.solve(timeout_ms=timeout_ms - total_solve_time * 1000)

    def apply_partition_to_states(self, partition: list[list[int]]) -> tuple[list[int], list[BoolRef]]:
        """
        Applies the given partition to the states, creating an observation function and strategy constraints.

        Args:
            partition (list[list[int]]): The partition to be applied, containing blocks of atomic group indices.

        Returns:
            tuple[list[int], list[BoolRef]]: A tuple containing the observation function and strategy constraints.
        """
        observation_function = [-1] * self.tpmc.size
        strategy_constraints = []
        atomic_groups = list(self.tpmc.clusters.keys())

        for b, block in enumerate(partition):
            actions_per_atomic_group = [atomic_groups[atomic_group_idx].actions for atomic_group_idx in block]
            actions_in_block = set.union(*actions_per_atomic_group)
            common_actions = set.intersection(*actions_per_atomic_group)
            common_action = None if len(common_actions) == 0 else common_actions.pop()

            for a, action in enumerate(self.tpmc.actions):
                if common_action is not None and action == common_action:
                    # If there's some common action, we can force it to 1 and others to 0.
                    strategy_constraints.append(self.tpmc.X[b][a] == (True if self.tpmc.determinism else 1))
                elif ((common_action is not None and action != common_action) or
                      common_action is None and action not in actions_in_block):
                    # Actions that do not appear in the block can be forced to 0. Any action that is not
                    # the common action (if any) can also be forced to 0.
                    strategy_constraints.append(self.tpmc.X[b][a] == (False if self.tpmc.determinism else 0))

            for atomic_group_idx in block:
                atomic_group = atomic_groups[atomic_group_idx]
                for state in self.tpmc.clusters[atomic_group]:
                    observation_function[state] = b

        return observation_function, strategy_constraints
