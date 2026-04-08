from mimetypes import init
import string
from MDP import MDP

def POMDPtoPrism(mdp:MDP, target: string, obs:list[int], memory: int):
    #makes a pomdp into a prim file
    file = open(f'{target}.prism',"w")
    file.write('pomdp\n')
    file.write('observables\n o\n endobservables\n\n')

    file.write('module graph\n\n')
    file.write(f'    s : [-1..{mdp._states}];\n')
   
    observations = ((len(obs)+1) * memory)#-1 is initial state, 0 is the goal the last mem numbers are bot 
    file.write(f'    o : [-1..{observations}];\n\n')
    
    

    #creation of observation dict: the state nr is key, the value is the observation
    obsDict = observationDict(mdp, obs, memory)


    #initilization:
    init = "    [] s=-1 ->"
    initialStateNumber = len(mdp._initial_states)
    for state in mdp.initial_states():
        param = f'1/{initialStateNumber} : (s\'={state}) & (o\'={obsDict[state]})'
        init += param
        if state != initialStateNumber:
            init += ' + '

    file.write(init + ";\n\n\n")

    #moving around the graph
    moving = ""
    for state in mdp.states():
        if not (state in mdp._goal_states):
            for action in mdp.actions():
                forward = []
                for post in mdp.post(state,action):
                    forward.append(post)
                if len(forward) < 2:
                    moving += f'    [{action}] s={state} -> (s\'={forward[0]}) & (o\'= {obsDict[forward[0]]});\n'
            moving += "\n"
    
    file.write(moving)
    done = ""
    for goal in mdp.goals():
        done += f"   [done] s={goal} -> true;\n"

    file.write(done)
    file.write("endmodule\n\n")
    file.write("rewards\n")

    rewards = ""
    for action in mdp.actions():
        rewards += f'   [{action}] true : 1;\n'


    file.write(rewards)
    file.write("endrewards\n\n")

    label = "label \"goal\" = o=["
    for state in mdp.goals():
        label += f'{state},'
    label = label[:-1]
    label += "];"

    file.close()


def observationDict(mdp: MDP, obs: list[int], memory: int):
    #form: each key is a int, that corrosponds to a state: each value is a observation
    obsDict = {}
    obsNr = 0
    botNrStart = len(obs)*memory + 1
    originalStateCount = len(mdp._initial_states) + len(mdp._goal_states)//memory
    for state in mdp.states():
        if state in mdp._goal_states:
            #print(f'{state} goal')
            obsDict[state] = 0
        elif state < originalStateCount: #mem = 1
            if state in obs:
                obsNr += 1
                obsDict[state] = obsNr
            else:
                obsDict[state] = botNrStart
        else:
            mem = 0 # the level of memory we are on
            originalState = state
            while originalState >= originalStateCount: #finds the state this state is a copy of 
                originalState -= originalStateCount
                mem += 1
            if originalState in obs:
                print(state)
                obsNr += 1
                obsDict[state] = obsNr
            else:
                obsDict[state] = botNrStart + mem
    print(obsDict)

    for entry in obsDict:
        print(f"{entry}: {obsDict[entry]}")
    return obsDict



            


