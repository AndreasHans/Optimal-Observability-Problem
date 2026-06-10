from math import floor
import subprocess
from typing import List, Optional

from z3 import *
from MDP import MDP
from MDPVariants import grid_corner_n, line_n, maze_n
import time
import sys

from Z3Result import Z3Result
from BMSSPResult import BMSSPResult
from ParseModel import ParseModel
from WorldSpecificHeuristics import add_trend_1, add_trend_2,add_trend_6, add_trend_9
#from dynamic_solvers.benchmark import TIMEOUT

theta_vars = dict()
delta_vars = dict()
pi_vars = dict()
y_vars = dict()
reachable_vars = dict()
used_memory_state_vars = dict()
bot = 'bot'
TIMEOUT_MS =   1000 * 120 #timeout for individual runs. Second part of equation is in seconds


enabled_world_specific_heuristics =[] # [ 'line special', 'grid sensor', , 'maze memory', ]
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

def add_memory_symmetry_heuristic(solver, states, memory_budget):
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

def add_general_heuristics(solver, mdp, memory_budget, states):
    #adds heuristics for specific problems
    if mdp.type() == "line":
        for n in range(memory_budget):
            for c in range(memory_budget): 
                add_constraint(solver, Implies(y(n), theta(c,n,"right") == True))
    elif mdp.type() == "maze":
        for n in range(floor( mdp.size() / 2)):
            for c in range(memory_budget):
                add_constraint(solver, Implies(y(n), theta(c,n,"right") == True))
        for c in range(memory_budget):
            add_constraint(solver, Implies(y(floor(mdp.size()/2)), theta(c,floor(mdp.size()/2),"down")== True))
        for n in range(floor(mdp.size()/2)+1, mdp.size()):
            for c in range(memory_budget):
                add_constraint(solver, Implies(y(n), theta(c,n,"left")== True))
    elif mdp.type() == "grid":
        
        for z in range(1,mdp.size()+1):
            for x in range(z,mdp.size()):
                location = (z-1)*mdp.size() + x
                for c in range(memory_budget):
                    add_constraint(solver, Implies(y(location), theta(c, location,"down") == True))
        for z in range(mdp.size()):
            for x in range(z+1):
                location = z * mdp.size() + x
                for c in range(memory_budget):
                    add_constraint(solver, Implies(y(location), theta(c,location,"right") == True))


def main(mdp: MDP, sensor_budget: int, threshold_terms: Optional[List[int]], memory_budget: int, strict_less: bool, sps: String) -> Z3Result:
    # If threshold_terms is None/empty, run in minimization mode using Optimize();
    # otherwise run in threshold-check mode using Solver().
    print("Adding constraints...")
    n = mdp.size()
    minimize_mode = not threshold_terms
    solver = Optimize() if minimize_mode else Solver()

    print("Updated memory budget: ", memory_budget)

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

    # Compute the minimum expected reward
    add_constraint(solver, min_exp_rew == Sum([pi(s, 0) for s in initial_states]) *  Q(1, len(initial_states)))

    if minimize_mode:
        solver.minimize(min_exp_rew)
    else:
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
            add_constraint(solver, min_exp_rew < threshold)
        else:
            add_constraint(solver, min_exp_rew <= threshold)

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

    # Add general heuristics (e.g. symmetry breaking)
    add_memory_symmetry_heuristic(solver, states, memory_budget)
    add_general_heuristics(solver, mdp, memory_budget, states)

    # add world specific heuristics (e.g. for line, grid, maze worlds)
    if sps == 'line':
        add_trend_1(solver, mdp, memory_budget, sensor_budget, add_constraint, y, theta, delta, states, n, bot)

    

    if sps == 'grid' :   
        add_trend_6(solver, mdp, memory_budget, sensor_budget, add_constraint, y, theta, delta, states, n, bot)



    print("Running solver...")
   
    solver.set("timeout", TIMEOUT_MS)

    cpu_start = time.process_time()
    result = solver.check()
    cpu_end = time.process_time()
    solve_time = cpu_end - cpu_start
    return Z3Result(result, solver.model() if result == sat else None, solve_time)

def all_equal_theta(memory, o, a):
    return And([theta(c,o,a) == theta(0,o,a) for c in range(1,memory)])

def all_equal_delta(c2, o, mem):
    return And([delta(0,o,c2) == delta(c,o,c2) for c in range(1,mem)])

def result(z3result):
    if z3result.result == sat:
        print("Success")
        bmssp_result = ParseModel.parse_model(z3result)
        bmssp_result.print()
    elif z3result.result == unsat:
        print('No solution')
    else:
        print('Unknown')
    print("Time taken: ", z3result.solve_time, " seconds")
    print("Done!")
    sys.exit()
    print("evertything is gone")

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
    
    if threshold_terms: #main algo can only run for non optimization challenge
        if type == "line":
            if sensor_budget >= floor(n/2):#step 1
                 print("attempting ML")
                 z3result = main(mdp, sensor_budget, threshold_terms, 1, strict_less, "")
                 if z3result.result == sat:
                     result(z3result)
            if sensor_budget >= 2 and memory_budget >= 2: # step 2
                print("attempting SM SPS")
                z3result = main(mdp, sensor_budget, threshold_terms, 2, strict_less, "line")
                if z3result.result == sat:
                     result(z3result)
            if sensor_budget >= 2 and memory_budget >= 2: # step 3
                print("attempting SM")
                z3result = main(mdp, sensor_budget, threshold_terms, 2, strict_less, "")
                if z3result.result == sat:
                     result(z3result)
            print("attempting SPS")         
            z3result = main(mdp, sensor_budget, threshold_terms, memory_budget, strict_less, "line") #step 4
            if z3result.result == sat:
                result(z3result) 
        elif type == "grid":
            if sensor_budget >= n-1:#step 1
                 print("attempting ML")
                 z3result = main(mdp, sensor_budget, threshold_terms, 1, strict_less, "")
                 if z3result.result == sat:
                     result(z3result)
            if memory_budget >= 2: # step 2
                print("attempting SM SPS")
                z3result = main(mdp, sensor_budget, threshold_terms, 2, strict_less, "grid")
                if z3result.result == sat:
                     result(z3result)
            if memory_budget >= 2: # step 3
                print("attempting SM")
                z3result = main(mdp, sensor_budget, threshold_terms, 2, strict_less, "")
                if z3result.result == sat:
                     result(z3result)
            print("attempting SPS")         
            z3result = main(mdp, sensor_budget, threshold_terms, memory_budget, strict_less, "grid") #step 4
            if z3result.result == sat:
                result(z3result)
        elif type == "maze":
            if sensor_budget >= (3/2)*(n-1):#step 1
                print("attempting ML")
                z3result = main(mdp, sensor_budget, threshold_terms, 1, strict_less, "")
                if z3result.result == sat:
                    result(z3result)
            if sensor_budget >= 1 and memory_budget >= 4: # step 3
                print("attempting SM")
                z3result = main(mdp, sensor_budget, threshold_terms, 4, strict_less, "")
                if z3result.result == sat:
                     result(z3result)
    z3result = main(mdp, sensor_budget, threshold_terms, memory_budget, strict_less, "") #step 5   
    result(z3result)



   
    

