from typing import List
from pathlib import Path
import sys

from z3 import *

# Make sibling modules in ../ importable when running this file directly.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from MDP import MDP
from MDPVariants import line_n
import time

x_vars = dict()
pi_vars = dict()
y_vars = dict()
bot = 'bot'

def init_variables(mdp:MDP) -> None:
    y_vars.clear()
    pi_vars.clear()
    x_vars.clear()

    num_states = len(list(mdp.states()))

    for s in mdp.states():
        y_vars[s] = Bool(f'y_{s}')

    for s in mdp.states():
        pi_vars[s] = Real(f'pi_{s}')

    for o in range(num_states):
        for a in mdp.actions():
            x_vars[o,a] = Bool(f'x_{o}_{a}')

    for a in mdp.actions():
        x_vars[bot,a] = Bool(f'x_{bot}_{a}')

def y(s:int):
    return y_vars[s]

def pi(s:int):
    return pi_vars[s]

def x(o:int, a:str):
    return x_vars[o,a]

def add_constraint(solver: Solver, constraint):
    #print(constraint)
    solver.add(constraint)

def main(mdp: MDP, sensor_budget: int, threshold_terms: List[int]):
    solver = Solver()
    
    states = list(mdp.states())
    goals = set(mdp.goals())
    non_goal_states = [s for s in states if s not in goals]
    initial_states = list(mdp.initial_states())

    init_variables(mdp)

    #We cannot do better than the fully observable case
    for s in mdp.states():
        add_constraint(solver, pi(s) >= mdp.optimal_cost(s))

    threshold = Q(threshold_terms[0], threshold_terms[1]) if len(threshold_terms) > 1 else threshold_terms[0]

    # We want to check if the minimal expected cost is below some threshold
    add_constraint(solver, Sum([pi(s) for s in initial_states]) *  Q(1, len(initial_states)) <= threshold)

    # Expected cost/reward equations
    for s in mdp.goals():
        add_constraint(solver, pi(s) == 0)

    for s in non_goal_states:
        for a in mdp.actions():
            lhs = Or(And(y(s), x(s,a)), And(Not(y(s)), x(bot,a)))
            rhs = pi(s) == mdp.reward(s) + Sum([pi(t) * mdp.transition(s, a, t) for t in mdp.post(s, a)])
            add_constraint(solver, Implies(lhs, rhs))

    for o in list(range(len(states))):
        add_constraint(solver, PbEq([(x(o,a), 1) for a in mdp.actions()], 1))

    add_constraint(solver, PbEq([(x(bot,a), 1) for a in mdp.actions()], 1))


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
        print('This is a solution:')
        print(m)
    elif result == unsat:
        print('No solution!!!')
    else:
        print('Unknown')

if __name__ == "__main__":

    n = 1001
    b = n//2
    t = [n//2+1, 2]
    mdp = line_n(n)

    main(mdp = mdp, sensor_budget=b, threshold_terms=t)