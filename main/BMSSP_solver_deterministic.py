from typing import List

from z3 import *
from MDP import MDP
from MDPVariants import grid_corner_n, line_n, maze_n
import time
import sys

from Z3Result import Z3Result
from BMSSPResult import BMSSPResult
from ParseModel import ParseModel

theta_vars = dict()
delta_vars = dict()
pi_vars = dict()
y_vars = dict()
reachable_vars = dict()
used_memory_state_vars = dict()
bot = 'bot'

min_exp_rew = Real('min_exp_rew')

def init_variables(mdp:MDP, memory_budget: Int) -> None:
    y_vars.clear()
    pi_vars.clear()
    theta_vars.clear()
    delta_vars.clear()
    reachable_vars.clear()
    used_memory_state_vars.clear()

    states = list(mdp.states())

    for s in mdp.states():
        y_vars[s] = Bool(f'y_{s}')

    for s in mdp.states():
         for c in range(memory_budget):
            pi_vars[s,c] = Real(f'pi_{s}_{c}')
            reachable_vars[s,c] = Bool(f'reach_{s}_{c}')

    for c in range(memory_budget):
        for o in states:
            for a in mdp.actions():
                theta_vars[c,o,a] = Bool(f'theta_{c}_{o}_{a}')
        for a in mdp.actions():
            theta_vars[c,bot,a] = Bool(f'theta_{c}_{bot}_{a}')

    for c in range(memory_budget):
        for o in states:
            for c2 in range(memory_budget):
                delta_vars[c,o,c2] = Bool(f'delta_{c}_{o}_{c2}')

        for c2 in range(memory_budget):
            delta_vars[c,bot,c2] = Bool(f'delta_{c}_{bot}_{c2}')

    for c in range(memory_budget):
        used_memory_state_vars[c] = Bool(f'used_mem_{c}')

def y(s:int):
    return y_vars[s]

def pi(s:int, c:int):
    return pi_vars[s,c]

def theta(c:int, o:int, a:str):
    return theta_vars[c,o,a]

def delta(c:int, o:int, c2:int):
    return delta_vars[c,o,c2]

def reachable(s:int, c:int):
    return reachable_vars[s,c]

def used_memory_state(c:int):
    return used_memory_state_vars[c]

def add_constraint(solver: Solver, constraint):
    #print(constraint)
    solver.add(constraint)

def main(mdp: MDP, sensor_budget: int, threshold_terms: List[int], memory_budget: int, strict_less: bool) -> Z3Result:
    solver = Solver()

    states = list(mdp.states())
    goals = set(mdp.goals())
    non_goal_states = [s for s in states if s not in goals]
    initial_states = list(mdp.initial_states())

    init_variables(mdp, memory_budget)

    # Every initial state is reachable with the initial memory state
    for s in initial_states:
        add_constraint(solver, reachable(s, 0))

    # A (state, memory) pair is reachable if we can reach it from some predecessor (state, memory) pair
    for s in non_goal_states:
        for c in range(memory_budget):
            for a in mdp.actions():
                for c2 in range(memory_budget):
                    for s2 in mdp.post(s, a):
                        add_constraint(
                            solver,
                            Implies(
                                And(reachable(s, c), y(s), theta(c, s, a), delta(c, s, c2)),
                                reachable(s2, c2)
                            )
                        )
                        add_constraint(
                            solver,
                            Implies(
                                And(reachable(s, c), Not(y(s)), theta(c, bot, a), delta(c, bot, c2)),
                                reachable(s2, c2)
                            )
                        )

    #We cannot do better than the fully observable case
    for s in mdp.states():
        for c in range(memory_budget):
            add_constraint(solver, pi(s, c) >= mdp.optimal_cost(s))

    # Fix pi for unreachable (s, c) pairs to a large value
    # Upper bound on pi for reachable pairs: worst-case cost in the MDP
    M = 9999
    for s in mdp.states():
        for c in range(memory_budget):
            add_constraint(solver, Implies(Not(reachable(s, c)), pi(s, c) == M))
            add_constraint(solver, Implies(reachable(s, c), pi(s, c) < M))

    threshold = Q(threshold_terms[0], threshold_terms[1]) if len(threshold_terms) > 1 else threshold_terms[0]

    # We want to check if the minimal expected cost is below some threshold
    if strict_less:
        add_constraint(solver, Sum([pi(s, 0) for s in initial_states]) *  Q(1, len(initial_states)) < threshold)
    else:
        add_constraint(solver, Sum([pi(s, 0) for s in initial_states]) *  Q(1, len(initial_states)) <= threshold)

    # Compute the minimum expected reward
    add_constraint(solver, min_exp_rew == Sum([pi(s, 0) for s in initial_states]) *  Q(1, len(initial_states)))

    # Expected cost/reward equations
    for s in mdp.goals():
        for c in range(memory_budget):
            add_constraint(solver, Implies(reachable(s, c), pi(s, c) == 0))

    for s in non_goal_states:
        for c in range(memory_budget):
            for a in mdp.actions():
                for c2 in range(memory_budget):
                    cost = mdp.reward(s) + Sum([
                        mdp.transition(s, a, s2) * pi(s2, c2)
                        for s2 in mdp.post(s, a)
                    ])
                    # Observed case: y(s) true, observation = s
                    add_constraint(
                        solver,
                        Implies(
                            And(reachable(s, c), y(s), theta(c, s, a), delta(c, s, c2)),
                            pi(s, c) == cost
                        )
                    )
                    # Unobserved case: y(s) false, observation = bot
                    add_constraint(
                        solver,
                        Implies(
                            And(reachable(s, c), Not(y(s)), theta(c, bot, a), delta(c, bot, c2)),
                            pi(s, c) == cost
                        )
                    )

    for c in range(memory_budget):
        for o in states:
            add_constraint(solver, PbEq([(theta(c,o,a), 1) for a in mdp.actions()], 1))
        add_constraint(solver, PbEq([(theta(c,bot,a), 1) for a in mdp.actions()], 1))

    for c in range(memory_budget):
        for o in states:
            add_constraint(solver, PbEq([(delta(c,o,c2), 1) for c2 in range(memory_budget)], 1))
        add_constraint(solver, PbEq([(delta(c,bot,c2), 1) for c2 in range(memory_budget)], 1))

    # Sensor budget constraint
    add_constraint(solver, PbEq([(y(s), 1) for s in non_goal_states], sensor_budget))

    # Define used_memory_state(c) to be true iff a memory state c is reachable  
    for c in range(memory_budget):
        add_constraint(
            solver,
            used_memory_state(c) == Or([reachable(s, c) for s in states])
        )

    # Symmetry breaking: force memory states to be used in order
    for c in range(1, memory_budget):
        # A memory state cannot be used unless the previous one is used
        add_constraint(solver, Implies(used_memory_state(c), used_memory_state(c - 1)))

    cpu_start = time.process_time()
    result = solver.check()
    cpu_end = time.process_time()
    solve_time = cpu_end - cpu_start
    return Z3Result(result, solver.model() if result == sat else None, solve_time)

if __name__ == "__main__":

    print("Parsing arguments...")

    type = sys.argv[1]
    n = int(sys.argv[2])
    sensor_budget = int(sys.argv[3])
    threshold_terms = tuple(int(x) for x in sys.argv[4][1:-1].split(','))
    memory_budget = int(sys.argv[5])
    strict_less = sys.argv[6].lower() == 'true' if len(sys.argv) > 6 else True

    print("Parsed arguments:")
    print(f"Type: {type}, n: {n}, sensor_budget: {sensor_budget}, threshold_terms: {threshold_terms}, memory_budget: {memory_budget}, strict_less: {strict_less}")

    print("Creating MDP...")
    if type == 'grid':
        mdp = grid_corner_n(n)
    elif type == 'line':
        mdp = line_n(n)
    elif type == 'maze':
        mdp = maze_n(n)
    else:
        raise ValueError(f"Unknown MDP type: {type}")

    print("Created MDP!")
    print("Running solver...")
    z3result = main(mdp, sensor_budget, threshold_terms, memory_budget, strict_less)

    if z3result.result == sat:
        print("Success")
        bmssp_result = ParseModel.parse_model(z3result)
        bmssp_result.print()

    elif z3result.result == unsat:
        print('No solution')
        print("Time taken: ", z3result.solve_time, " seconds")
    else:
        print('Unknown')

    print("Done!")