from typing import List
from pathlib import Path
import sys

from z3 import *


# Make sibling modules in ../ importable when running this file directly.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from MDP import MDP
from MDPVariants import line_n, maze_n
import time

x_vars = dict()
pi_vars = dict()
y_vars = dict()
bot = 'bot'
TIMEOUT = 1000 * 60 * 5 #the last digit it the number of miniuts

min_exp_rew = Real('min_exp_rew')

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
            x_vars[o,a] = Real(f'x_{o}_{a}')

    for a in mdp.actions():
        x_vars[bot,a] = Real(f'x_{bot}_{a}')

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
    minimize_mode = not threshold_terms
    solver = Optimize() if minimize_mode else Solver()
    
    states = list(mdp.states())
    goals = set(mdp.goals())
    non_goal_states = [s for s in states if s not in goals]
    initial_states = list(mdp.initial_states())

    init_variables(mdp)

    #We cannot do better than the fully observable case
    for s in mdp.states():
        add_constraint(solver, pi(s) >= mdp.optimal_cost(s))


    
    # We want to check if the minimal expected cost is below some threshold
    add_constraint(solver, min_exp_rew == Sum([pi(s) for s in initial_states]) *  Q(1, len(initial_states)))

    if minimize_mode:
        solver.minimize(min_exp_rew)
    else:
        threshold = Q(threshold_terms[0], threshold_terms[1]) if len(threshold_terms) > 1 else threshold_terms[0]
        add_constraint(solver, min_exp_rew <= threshold)


    # Expected cost/reward equations
    for s in mdp.states():

        if s in goals:
            add_constraint(solver, pi(s) == 0)
        else:
            # If @s is activated
            z = Sum([pi(s2) * x(s,a) * mdp.transition(s, a, s2) for s2 in mdp.states() for a in mdp.actions()])

            add_constraint(solver, Implies(y(s), pi(s) >= mdp.reward(s) + z))

            # If @s is not activated (default observation)
            z2 = Sum([pi(s2) * x(bot,a) * mdp.transition(s, a, s2) for s2 in mdp.states() for a in mdp.actions()])
            add_constraint(solver, Implies(Not(y(s)), pi(s) >= mdp.reward(s) + z2))


    #x_o_a -> [0,1]
    for o in list(range(len(states))):
        for a in mdp.actions():
            add_constraint(solver, And(x(o,a) >= 0, x(o,a) <= 1))
        add_constraint(solver, Sum([x(o,a) for a in mdp.actions()]) == 1)

    for a in mdp.actions():
        add_constraint(solver, x(bot,a) >= 0)
        add_constraint(solver, x(bot,a) <= 1)
    add_constraint(solver, Sum([x(bot,a) for a in mdp.actions()]) == 1)

    # Sensor budget constraint
    add_constraint(solver, PbEq([(y(s), 1) for s in non_goal_states], sensor_budget))

    #solver.set("timeout", TIMEOUT)
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

    n = 9

    #mdp = line_n(n)
    mdp = maze_n(n)

    main(mdp = mdp, sensor_budget=0, threshold_terms=[302])