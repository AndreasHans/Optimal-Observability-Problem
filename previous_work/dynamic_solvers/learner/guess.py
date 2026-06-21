from previous_work.dynamic_solvers.ClusterPOPSolver import rank_partitions
from previous_work.dynamic_solvers.builders.enums import OOPVariant
from previous_work.dynamic_solvers.builders.pop.POPSpec import POPSpec
from builders.ssp import GridTPMC
from previous_work.dynamic_solvers.builders.ssp.SSPSpec import SSPSpec
from previous_work.dynamic_solvers.direction import Direction
from previous_work.dynamic_solvers.utils import stirling_partitions


def start_observation_function(tpmc: POPSpec | SSPSpec, min_budget: int):
    variant = tpmc.variant()
    no_atomic_groups = len(tpmc.clusters)
    no_blocks = min(no_atomic_groups, min_budget if variant == OOPVariant.SSP else tpmc.budget)

    # Given a budget B, we generate all possible partitions for atomic groups into B blocks
    partitions = list(stirling_partitions(n=no_atomic_groups, k=no_blocks))
    # Rank the generated partitions of atomic groups by equivalence-constraining heuristic
    ranking_partitions = rank_partitions(tpmc, partitions)
    # Select the best partition according to the heuristic comparator
    best_partition = partitions[ranking_partitions[0][0]]
    if variant is OOPVariant.POP:
        # Construct the observation function induced by the selected partition of atomic groups
        return apply_partition(tpmc, best_partition)
    else: # OOPVariant.SSP
        return activate_sensors(tpmc, best_partition, tpmc.budget)


def activate_sensors(tpmc: SSPSpec, partition: list[list[int]], budget: int) -> list[int]:
    atomic_group_sizes = list(map(len, tpmc.clusters.values()))
    atomic_groups = list(tpmc.clusters.keys())
    # print(atomic_groups)

    def block_size(block: list[int]):
        return sum(atomic_group_sizes[i] for i in block)

    def common_dir(block: list[int]):
        actions = set.intersection(*[atomic_groups[g].actions for g in block])
        return Direction.action_to_dir(actions)

    partition_data = [(block, block_size(block), common_dir(block)) for block in partition]
    sorted_blocks = sorted(partition_data, key=lambda x: x[1])

    deactivated_dir = sorted_blocks[-1][2]
    partition_data = [(block[0], block[1], block[2] is deactivated_dir.opposite()) for block in sorted_blocks]
    sorted_blocks = sorted(partition_data, key=lambda x: (-int(x[2]), x[1]))
    print(sorted_blocks)


    allocated, active = 0, []
    idx = 0
    while allocated < budget and idx < len(sorted_blocks) - 1:
        block = sorted_blocks[idx]
        if budget - allocated >= block[1]:
            allocated += block[1]
            for key in block[0]:
                active.extend(tpmc.clusters[atomic_groups[key]])
            idx += 1
        else:
            break

    if idx < len(sorted_blocks) - 1:
        sorted_groups = sorted(sorted_blocks[idx][0],key=lambda x: atomic_group_sizes[x], reverse=True)
        for ag_idx in sorted_groups:
            if budget - allocated >= atomic_group_sizes[ag_idx]:
                allocated += atomic_group_sizes[ag_idx]
                active.extend(tpmc.clusters[atomic_groups[ag_idx]])
            else:
                delta = budget - allocated
                active.extend(list(tpmc.clusters[atomic_groups[ag_idx]])[:delta])
                break

    # print(active)
    observation_function = [0] * tpmc.size
    observation_function[tpmc.goal] = -1
    for state in active:
        observation_function[state] = 1

    return observation_function


def apply_partition(tpmc: POPSpec | SSPSpec, partition: list[list[int]]):
    observation_function = [-1] * tpmc.size
    atomic_groups = list(tpmc.clusters.keys())

    for b, block in enumerate(partition):
        for atomic_group_idx in block:
            for state in tpmc.clusters[atomic_groups[atomic_group_idx]]:
                observation_function[state] = b

    return observation_function


if __name__ == "__main__":
    tpmc = GridTPMC(budget=10, goal=12, width=5, height=5)
    mpb = tpmc.minimal_pos_budget()

    # For POP use the actual budget for ranking partitions, for SSP - the minimal positional budget (B*)
    obs_function = start_observation_function(tpmc, mpb)
    model = tpmc.extract_obs_solution(obs_function)
    drawing = tpmc.draw_model(model, goal_state=12, budget=10, use_color=True)
    print(drawing)
