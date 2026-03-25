from z3 import *
from MDP import MDP
from MDPVariants import line_n
import time

# coombines the delta only and repeat node approach

delta_vars = dict()
pi_vars = dict()
y_vars = dict()

def init_variables(mdp:MDP, memory_budget:int) -> None:
    y_vars.clear()
    pi_vars.clear()
    delta_vars.clear()

    num_states = len(list(mdp.states()))

    for s in mdp.states():
        y_vars[s] = Int(f'y_{s}')

    for s in mdp.states():
         for c in range(memory_budget):
            pi_vars[s,c] = Real(f'pi_{s}_{c}')

  
    for c in range(memory_budget):
        for o in range(num_states):
            for a in mdp.actions():
                for c2 in range(memory_budget):
                    delta_vars[c,o,a,c2] = Int(f'delta_{c}_{o}_{a}_{c2}')

        for a in mdp.actions():
            for c2 in range(memory_budget):
                delta_vars[c,'bot',a,c2] = Int(f'delta_{c}_bot_{a}_{c2}')

def y(s:int):
    return y_vars[s]

def pi(s:int, c:int):
    return pi_vars[s,c]

def delta(c:int, o:int, a:str, c2:int):
    return delta_vars[c,o,a,c2]

def distribution(variables):
    return And(
        Sum(variables) == 1,
        *[Or(v == 0, v == 1) for v in variables],
    )

def main(mdp: MDP, sensor_budget: int, memory_budget: int, threshold: float):
    solver = Solver()

    bot = 'bot'

    states = list(mdp.states())
    goals = set(mdp.goals())
    non_goal_states = [s for s in states if s not in goals]
    initial_states = list(mdp.initial_states())

    init_variables(mdp, memory_budget)

    #We cannot do better than the fully observable case
    for s in mdp.states():
        for c in range(memory_budget):
            solver.add(pi(s,c) >= mdp.optimal_cost(s))

    # Expected cost/reward equations
    infinitySimulator = 999999
    for s in mdp.states():        
        for c in range(memory_budget):
            if s in mdp.goals():
                solver.add(pi(s,c) == 0)
            else:
                eq1 = RealVal(0)
                for c2 in range(memory_budget):
                    for s2 in mdp.states():
                        for a in mdp.actions():
                            p_sas2 = mdp.transition(s, a, s2)
                            if p_sas2 > 0:
                                p_obs = y(s) * delta(c, s, a, c2) * p_sas2
                                p_bot = (1 - y(s)) * delta(c, bot, a, c2) * p_sas2
                                if s == s2 and c == c2: #if we stay in the same node and controller, we can do that without any observation
                                    eq1 = eq1 + (infinitySimulator) * (p_obs + p_bot)   
                                else:
                                    eq1 = eq1 + (mdp.reward(s) + pi(s2, c2)) * (p_obs + p_bot)

                solver.add(pi(s, c) == eq1)
          

    # We want to check if the minimal expected cost is below some threshold
    solver.add(sum(pi(s,0) for s in initial_states) / len(initial_states) <= threshold)

    

    # delta(c,o,a) -> c'
    for c in range(memory_budget):
        for o in non_goal_states:
                solver.add(distribution([delta(c,o,a,c2) for c2 in range(memory_budget) for a in mdp.actions()]))
        solver.add(distribution([delta(c,bot,a,c2) for c2 in range(memory_budget) for a in mdp.actions()]))


    # Sensor enabled or disabled constraints
    for s in non_goal_states:
        solver.add(Or(y(s) == 0, y(s) == 1))

    # Sensor budget constraint
    solver.add(sum(y(s) for s in non_goal_states) == sensor_budget)

    cpu_start = time.process_time()
    result = solver.check()
    cpu_end = time.process_time()
    solve_time = cpu_end - cpu_start

    print("Time:",solve_time, "s")

    if result == sat:
        m = solver.model()
        print('This is a solution:')
        print(m)
    elif result == unsat:
        print('No solution!!!')
    else:
        print('Unknown')

if __name__ == "__main__":

    n =101

    mdp = line_n(n)

    main(mdp = mdp, sensor_budget=1, memory_budget=2, threshold=(n-1)/2)



"""
stats:
Line(5): time: 0.3s, threshold 2
Line(7): time 0.6s, threshold 3
Line(9): time 0.7s, threshold 4
Line(11): 2.9, threshold 5
line(13): 5.2s, threshold 6
line(15): time 2.7s, threshold 7
line(17): time 1.2s, threshold 8
line(19): time 20s, threshold 9
line(21): time 3.8s, threshold 10
line(23): time 15s, threshold 11
line(25): time 8s, threshold 12
line(27): time 8s, threshold 13
line(29): time 129s, threshold 19
line(31): time 91s, threshold 20
line(33): time 53s, threshold 21
line(35): time 30s, threshold 22
line(37): time 81s, threshold 23
line(39): time 70s, threshold 19
line(41): time 137s, threshold 20

line(49): 46s, threshold 24

Line(69): time 60s,
"""