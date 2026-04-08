import stormpy
import stormpy.examples
import stormpy.examples.files
from MDPVariants import line_n
from MDP import MDP

#goal: take an MDP, convert it to storm workable, and iterate over observation functions, trying to find one with a low enough treshold. 


def main(mdp: MDP, sensor_budget: int, threshold_terms: list[int], memory_budget: int,):
    #step 1: unfold mdp: (this is equivilant to creating a fsc)
    unfolded = mdp_unfolder(mdp, memory_budget)

    #step 2: iterate over obs functions, until solution in threshold is found
    prismModel = mdp_to_prism(unfolded)

    #step 3: convert it to prism, which storm can read

    print("done")
 
def pomdp_to_prism(mpd: MDP, obs:list[int], memory: int):
    #obs is a list of ints, where each int is a state that is observed, and every other state is not observed: the length of the obs should be no longer than budget
    POMDPtoPrism(mdp, "target", obs, memory)
    
  
    return model

def mdp_unfolder(mdp: MDP, memory: int):
    goals = []
    for goal in mdp.goals():
        for mem in range(memory):
            goals.append(goal*mem)

    actions = []
    actionBlocks = [] # each block is all variants of the same action
    orgActions = []
    for action in mdp.actions():
        block = []
        orgActions.append(action)
        for mem in range(memory):
            actions.append(action+str(mem))
            block.append(action+str(mem))
        actionBlocks.append(block)

    result = MDP(mdp._states*memory, MDP.initial_states,goals, actions)
    #we now have an mdp with the right amount of actions and and states, but needs to do the transitions, optimal costs and rewards
    
    for state in mdp.states():
        for mem in range(memory):
            stateNr = state + mem * mdp._states
            result.set_optimal_cost(stateNr,mdp.optimal_cost(state))
            result.set_reward(stateNr,mdp.reward(state))
            #set transtitions:
            for i in range(len(actionBlocks)):
                for mem2 in range(memory):
                    next = 0
                    for j in mdp.post(state,orgActions[i]):
                        next = j
                    result.set_transition(stateNr, actionBlocks[i][mem2],next + mem2*mdp._states,1)
    #TODO: verify it works corretly
    return result

if __name__ == "__main__":

    n = 9
    m = 3
    b = n//2
    t = [n//2+1, 2]
    mdp = line_n(n)

    main(mdp = mdp, sensor_budget=b, memory_budget=m, threshold_terms=t)
    
