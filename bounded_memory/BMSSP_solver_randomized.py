from typing import List, Optional

from z3 import *
from MDP import MDP
from MDPVariants import grid_corner_n, line_n, maze_n
import time
import sys

from Z3Result import Z3Result
from BMSSPResult import BMSSPResult
from ParseModel import ParseModel

theta_vars = dict()
theta_step_vars = dict()
delta_vars = dict()
pi_vars = dict()
y_vars = dict()
reachable_vars = dict()
bot = 'bot'
TIMEOUT_MS =   1000 * 120 * 2 #timeout for individual runs. Second part of equation is in seconds

min_exp_rew = Real('min_exp_rew')

def init_variables(mdp:MDP, memory_budget: Int) -> None:
    y_vars.clear()
    pi_vars.clear()
    theta_vars.clear()
    theta_step_vars.clear()
    delta_vars.clear()
    reachable_vars.clear()

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
                theta_vars[c,o,a] = Real(f'theta_{c}_{o}_{a}')
                theta_step_vars[c,o,a] = Int(f'theta_step_{c}_{o}_{a}')
        for a in mdp.actions():
            theta_vars[c,bot,a] = Real(f'theta_{c}_{bot}_{a}')
            theta_step_vars[c,bot,a] = Int(f'theta_step_{c}_{bot}_{a}')

    for c in range(memory_budget):
        for o in states:
            for c2 in range(memory_budget):
                delta_vars[c,o,c2] = Bool(f'delta_{c}_{o}_{c2}')

        for c2 in range(memory_budget):
            delta_vars[c,bot,c2] = Bool(f'delta_{c}_{bot}_{c2}')


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

def add_constraint(solver: Solver, constraint):
    #print(constraint)
    solver.add(constraint)

def main(mdp: MDP, sensor_budget: int, threshold_terms: Optional[List[int]], memory_budget: int, strict_less: bool) -> Z3Result:
    # If threshold_terms is None/empty, run in minimization mode using Optimize();
    # otherwise run in threshold-check mode using Solver().
    minimize_mode = not threshold_terms
    solver = Optimize() if minimize_mode else Solver()

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
                                And(reachable(s, c), y(s), theta(c, s, a) > 0, delta(c, s, c2)),
                                reachable(s2, c2)
                            )
                        )
                        add_constraint(
                            solver,
                            Implies(
                                And(reachable(s, c), Not(y(s)), theta(c, bot, a) > 0, delta(c, bot, c2)),
                                reachable(s2, c2)
                            )
                        )

    #We cannot do better than the fully observable case
    for s in mdp.states():
        for c in range(memory_budget):
            add_constraint(solver, pi(s, c) >= mdp.optimal_cost(s))

    # Compute the minimum expected reward
    add_constraint(solver, min_exp_rew == Sum([pi(s, 0) for s in initial_states]) *  Q(1, len(initial_states)))

    if minimize_mode:
        solver.minimize(min_exp_rew)
    else:
        threshold = Q(threshold_terms[0], threshold_terms[1]) if len(threshold_terms) > 1 else threshold_terms[0]

        # We want to check if the minimal expected cost is below some threshold
        if strict_less:
            add_constraint(solver, min_exp_rew < threshold)
        else:
            add_constraint(solver, min_exp_rew <= threshold)

    # Expected cost/reward equations
    for s in mdp.goals():
        for c in range(memory_budget):
            add_constraint(solver, Implies(reachable(s, c), pi(s, c) == 0))

    for s in non_goal_states:
        for c in range(memory_budget):
                y_terms = []
                not_y_terms = []
                for a in mdp.actions():
                    for c2 in range(memory_budget):
                        succ_cost = Sum([
                            mdp.transition(s, a, s2) * pi(s2, c2)
                            for s2 in mdp.post(s, a)
                        ])
                        y_terms.append(theta(c, s, a) * If(delta(c, s, c2), succ_cost, RealVal(0)))
                        not_y_terms.append(theta(c, bot, a) * If(delta(c, bot, c2), succ_cost, RealVal(0)))

                eq1 = Sum(y_terms) if y_terms else RealVal(0)
                eq2 = Sum(not_y_terms) if not_y_terms else RealVal(0)

                add_constraint(
                    solver,
                    Implies(reachable(s, c), pi(s, c) == mdp.reward(s) + If(y(s), eq1, eq2))
                )

    steps = 2

    for c in range(memory_budget):
        for o in states:
            for a in mdp.actions():
                add_constraint(solver, And(theta_step_vars[c,o,a] >= 0, theta_step_vars[c,o,a] <= steps))
                add_constraint(solver, theta(c,o,a) == theta_step_vars[c,o,a] * Q(1, steps))
            add_constraint(solver, Sum([theta(c,o,a) for a in mdp.actions()]) == 1)
        for a in mdp.actions():
            add_constraint(solver, And(theta_step_vars[c,bot,a] >= 0, theta_step_vars[c,bot,a] <= steps))
            add_constraint(solver, theta(c,bot,a) == theta_step_vars[c,bot,a] * Q(1, steps))
        add_constraint(solver, Sum([theta(c,bot,a) for a in mdp.actions()]) == 1)

    for c in range(memory_budget):
        for o in states:
            add_constraint(solver, PbEq([(delta(c,o,c2), 1) for c2 in range(memory_budget)], 1))
        add_constraint(solver, PbEq([(delta(c,bot,c2), 1) for c2 in range(memory_budget)], 1))

    # Sensor budget constraint
    add_constraint(solver, PbEq([(y(s), 1) for s in non_goal_states], sensor_budget))
    #solver.set("timeout", TIMEOUT_MS)
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
    # Threshold arg: pass '[]' or 'none' to run in minimization mode.
    threshold_arg = sys.argv[4]
    if threshold_arg.lower() in ('none', '[]', ''):
        threshold_terms = None
    else:
        threshold_terms = tuple(int(x) for x in threshold_arg[1:-1].split(','))
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