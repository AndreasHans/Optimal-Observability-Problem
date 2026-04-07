
from z3 import *
from MDPVariants import grid_corner_n, line_n, maze_n
import sys
from ParseModel import ParseModel
import BMSSP_solver_deterministic
from BMSSPResult import BMSSPResult


def loop():
    threshold_terms = (999,1)
    curr_best = None

    z3result = BMSSP_solver_deterministic.main(mdp, sensor_budget, threshold_terms, memory_budget, True)

    if not z3result.result == sat:
        return None

    curr_best = ParseModel.parse_model(z3result)


    while True:
        threshold_terms = curr_best.min_exp_rew
        
        z3result = BMSSP_solver_deterministic.main(mdp, sensor_budget, threshold_terms, memory_budget, True)

        if not z3result.result == sat:
            return curr_best

        curr_best:BMSSPResult = ParseModel.parse_model(z3result)






if __name__ == "__main__":

    print("Parsing arguments...")

    type = sys.argv[1]
    n = int(sys.argv[2])
    sensor_budget = int(sys.argv[3])
    memory_budget = int(sys.argv[4])

    print("Parsed arguments:")
    print(f"Type: {type}, n: {n}, sensor_budget: {sensor_budget}, memory_budget: {memory_budget}")

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

    result = loop()

    if result:
        print("Success")
        result.print()
    else:
        print('No solution')