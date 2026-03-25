from typing import List

from z3 import *
from MDP import MDP
from MDPVariants import grid_center, grid_corner_n, line_n
import time
from ModelPrinter import ModelPrinter

theta_vars = dict()
delta_vars = dict()
pi_vars = dict()
y_vars = dict()
bot = 'bot'

min_exp_rew = Real('min_exp_rew')

def init_variables(mdp:MDP, memory_budget: Int) -> None:
    y_vars.clear()
    pi_vars.clear()
    theta_vars.clear()
    delta_vars.clear()

    states = list(mdp.states())

    for s in mdp.states():
        y_vars[s] = Bool(f'y_{s}')

    for s in mdp.states():
         for c in range(memory_budget):
            pi_vars[s,c] = Real(f'pi_{s}_{c}')

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


def y(s:int):
    return y_vars[s]

def pi(s:int, c:int):
    return pi_vars[s,c]

def theta(c:int, o:int, a:str):
    return theta_vars[c,o,a]

def delta(c:int, o:int, c2:int):
    return delta_vars[c,o,c2]

def add_constraint(solver: Solver, constraint):
    #print(constraint)
    solver.add(constraint)

def main(mdp: MDP, sensor_budget: int, threshold_terms: List[int], memory_budget: int, strict_less: bool = True):
    solver = Solver()
    
    states = list(mdp.states())
    goals = set(mdp.goals())
    non_goal_states = [s for s in states if s not in goals]
    initial_states = list(mdp.initial_states())

    init_variables(mdp, memory_budget)

    #We cannot do better than the fully observable case
    for s in mdp.states():
        for c in range(memory_budget):
            add_constraint(solver, pi(s, c) >= mdp.optimal_cost(s))

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
            add_constraint(solver, pi(s, c) == 0)

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
                        y_terms.append(If(And(theta(c, s, a), delta(c, s, c2)), succ_cost, RealVal(0)))
                        not_y_terms.append(If(And(theta(c, bot, a), delta(c, bot, c2)), succ_cost, RealVal(0)))

                eq1 = Sum(y_terms) if y_terms else RealVal(0)
                eq2 = Sum(not_y_terms) if not_y_terms else RealVal(0)

                add_constraint(
                    solver,
                    Or(pi(s, c) == mdp.reward(s) + If(y(s), eq1, eq2), pi(s, c) == 9999)
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

    cpu_start = time.process_time()
    result = solver.check()
    cpu_end = time.process_time()
    solve_time = cpu_end - cpu_start

    print("Time:",solve_time, "s")
    file_solver = open("solver.txt", "w")
    file_solver.write(str(solver.sexpr()))
    file_solver.close()

    if result == sat:
        m = solver.model()
        #print('This is a solution:')
        #print(m)

        model_printer = ModelPrinter(m)
        model_printer.print_model()

    elif result == unsat:
        print('No solution!!!')
    else:
        print('Unknown')

if __name__ == "__main__":
    mdp = line_n(15)
    b = 1
    t = [46,7]
    m = 5

    main(mdp = mdp, sensor_budget=b, threshold_terms=t, memory_budget=m, strict_less=True)

    print("Done")