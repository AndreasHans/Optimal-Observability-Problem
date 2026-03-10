from math import pi
import sys
from turtle import left

def create_line_bmssp(budget, memory, target, size, threshold, det, pre):
    
    strat_type = "det" if det == 1 else "ran"
    file = open(f'bmssp_line_{size}_{strat_type}_z3.py', 'w')

    actions = ['l', 'r']

    file.write('from z3 import *\n\n')
    file.write('# Expected cost/reward of reaching the goal.\n')
    reward_vars = []
    for s in range(size):
        for m in range(1,memory+1):
            reward_vars.append(f'pi_s{s}_c{m} = Real(\'pi_s{s}_c{m}\')')
    file.write('\n'.join(reward_vars) + '\n')


    file.write('\n# Choice of observations\n')

    # Generate sensor variables - one per non-target state
    sensor_vars = []
    sensor_states = [] 
    for s in range(size):
        if s != target:
            sensor_vars.append(f'y{s} = Real(\'y{s}\')')
            sensor_states.append(s)
    file.write('\n'.join(sensor_vars) + '\n')

    #generate the theta functions
    file.write('\n# theta functions\n')
    theta_vars = []
    for s in sensor_states:
        for m in range(1,memory+1):
            for act in actions:
                theta_vars.append(f'x_c{m}_o{s}_{act} = Real(\'x_c{m}_o{s}_{act}\')')
    
    #default theta functions (when no sensor observes - unknown state)
    for m in range(1,memory+1):
            for act in actions:
                theta_vars.append(f'x_c{m}_o_{act} = Real(\'x_c{m}_o_{act}\')')
    
    file.write('\n'.join(theta_vars) + '\n')

    
    
    file.write('\n# delta functions\n')
    # generata the delta functions
    file.write('\n# delta functions\n')
    delta_vars = []
    for s in sensor_states:
        for m in range(1,memory+1):
            for act in actions:
                for n in range(1,memory+1):
                    delta_vars.append(f'x_c{m}_o{s}_{act}_c{n} = Real(\'x_c{m}_o{s}_{act}_c{n}\')')
    
    #generate default delta functions (when no sensor observes - unknown state)
    for m in range(1,memory+1):
        for act in actions:
            for n in range(1,memory+1):
                delta_vars.append(f'x_c{m}_o_{act}_c{n} = Real(\'x_c{m}_o_{act}_c{n}\')')
    

    file.write('\n'.join(delta_vars) + '\n')

    file.write('solver = Solver()\n\n\n')

    file.write('solver.add(\n')
    file.write('#We cannot do better than the fully observable case\n')
    for m in range(1,memory+1):
        bounds = ', '.join([f'pi_s{s}_c{m}>={abs(target - s)}' for s in range(size)])
        file.write(f'{bounds}, \n')
    file.write('# Expected cost/reward equations\n')

    #genreate the cost equations

    for s in range(size):
        for m in range(1,memory+1):#left hand side of the equation
            if s == target:
                file.write(f'pi_s{s}_c{m} == 0, \n')
            else:
                # For sensor selection: if sensor y_s is on, use x_c{m}_o{s}_{act}, else use default x_c{m}_o_{act}
                left_next = max(s-1, 0)
                right_next = min(s+1, size-1)
                directions = [left_next, right_next]
                equation = f'pi_s{s}_c{m} == '
                for idx, act in enumerate(actions):
                    next = directions[idx] 
                    for n in range(1, memory+1):
                        if act == actions[0] and n == 1 and next == directions[0]: #first term in the equation
                            equation += f'(1 + pi_s{next}_c{n}) * (y{s} * x_c{m}_o{s}_{act} * x_c{m}_o{s}_{act}_c{n} + (1 - y{s}) * x_c{m}_o_{act} * x_c{m}_o_{act}_c{n}) \n'
                        else:
                            equation += f'+ (1 + pi_s{next}_c{n}) * (y{s} * x_c{m}_o{s}_{act} * x_c{m}_o{s}_{act}_c{n} + (1 - y{s}) * x_c{m}_o_{act} * x_c{m}_o_{act}_c{n}) \n'
                file.write(equation + ',\n')
    
    file.write(f'# We are dropped uniformly in the line\n# We want to check if the minimal expected cost is below some threshold {threshold}\n')
    pi_terms = [f'pi_s{s}_c1' for s in range(size) if s != target]
    pi_sum = '+'.join(pi_terms)
    threshold_constraint = f'({pi_sum}) * Q(1,{size-1}) <= {threshold},'

    #may need later
    e = f'({pi_sum}) * Q(1,{size-1}) '

    file.write(threshold_constraint + '\n')

    file.write('#randomized strategy theta \n')
    theta_strategy_constraints = []
    for s in sensor_states:
        for m in range(1,memory+1):
            thetaSum = ""
            for act in actions:
                theta_strategy_constraints.append(f'x_c{m}_o{s}_{act} >= 0')
                theta_strategy_constraints.append(f'x_c{m}_o{s}_{act} <= 1')
                thetaSum += f'x_c{m}_o{s}_{act} + '
            thetaSum = thetaSum[:-3]
            theta_strategy_constraints.append(f'{thetaSum} == 1')

    #add defult strategy constraints

    for m in range(1,memory+1):
        thetaSum = ""
        for act in actions:
            theta_strategy_constraints.append(f'x_c{m}_o_{act} >= 0')
            theta_strategy_constraints.append(f'x_c{m}_o_{act} <= 1')
            thetaSum += f'x_c{m}_o_{act} + '
        thetaSum = thetaSum[:-3]
        theta_strategy_constraints.append(f'{thetaSum} == 1')                    
    file.write(',\n'.join(theta_strategy_constraints) + ',\n')

    file.write('#randomized strategy delta \n')
   
 
    implications = []
    for s in sensor_states:
        for m in range(1,memory+1):
            for act in actions:
                for n in range(1,memory+1):
                    implications.append(f'Implies (y{s} == 0, x_c{m}_o{s}_{act}_c{n} == 0)')
        implications[-1] = implications[-1] + "\n"

    
    file.write(',\n'.join(implications) + ',\n')
      

    delta_strategy_constraints = []
    
    for m in range(1,memory+1):
        for s in sensor_states:
            for act in actions:
                deltaSum = ""
                for n in range(1,memory+1):
                    delta_strategy_constraints.append(f'x_c{m}_o{s}_{act}_c{n} >= 0')
                    delta_strategy_constraints.append(f'x_c{m}_o{s}_{act}_c{n} <= 1')
                    deltaSum += f'x_c{m}_o{s}_{act}_c{n} + '
                deltaSum = deltaSum[:-3]
                delta_strategy_constraints.append(f'Or ({deltaSum} == 1, {deltaSum} + y{s} == 0)') 
                #delta_strategy_constraints.append(f'{deltaSum} == 1')

    #add defult delta strategy constraints
    for m in range(1,memory+1):
        for n in range(1,memory+1):
            deltaSum = ""
            for act in actions:
                
                delta_strategy_constraints.append(f'x_c{m}_o_{act}_c{n} >= 0')
                delta_strategy_constraints.append(f'x_c{m}_o_{act}_c{n} <= 1')
                deltaSum += f'x_c{m}_o_{act}_c{n} + '
            deltaSum = deltaSum[:-3]
            delta_strategy_constraints.append(f'{deltaSum} == 1') 
    
    file.write(',\n'.join(delta_strategy_constraints) + ',\n')
    
    #needs to add section on deterministic strategies if det == 1

    file.write('# y is a function that should map every state N to some observable class M\n')
    sensor_binary_constraints = [f'Or (y{s} == 0, y{s} == 1),' for s in sensor_states]
    file.write('\n'.join(sensor_binary_constraints) + '\n') 
    sensor_sum = ' + '.join([f'y{s}' for s in sensor_states])    
    file.write(f'{sensor_sum} == {budget}')           

    file.write('\n)\n')

    file.write('set_option(max_args=1000000, max_lines=100000000)\n')

    file.write('file_results = open(\'results.txt\', \'w\')\n')

    file.write('file_reward = open(\'reward.txt\', \'w\')\n')

    file.write('result = solver.check()\n'
               'if result == sat:\n\t'
               'm = solver.model()\n\t'
               'print(\'Solution found\')\n\t'
               'file_results.write(str(m))\n\t'
               'file_reward.write(str(m.eval(' + str(e) + ')))\n'
               'elif result == unsat:\n\t'
               'print(\'No solution!!!\')\n\t'
               'file_reward.write(\'N/A\')\n'
               'else:\n\t'
               'print(\'Unknown\')')

budget = int(sys.argv[1])
memory = int(sys.argv[2])
target = int(sys.argv[3])
size = int(sys.argv[4])
threshold = sys.argv[5]
det = int(sys.argv[6])
pre = sys.argv[7]


if pre == 'predefined.txt':
    file = open(pre, 'r')
    pre = file.readlines()[0].strip('\'')   
    
create_line_bmssp(budget, memory, target, size, threshold, det, pre)
