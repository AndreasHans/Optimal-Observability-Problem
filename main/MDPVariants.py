from MDP import MDP


def line_5():

    mdp = MDP(_states=5, _initial_states=[0,1,3,4], _goals=[2], _actions=["left", "right"])

    # s0
    mdp.set_transition(0, "right", 1, 1.0)
    mdp.set_transition(0, "left", 0, 1.0)

    # s1
    mdp.set_transition(1, "right", 2, 1.0)
    mdp.set_transition(1, "left", 0, 1.0)

    # s2
    mdp.set_transition(2, "right", 2, 1.0)
    mdp.set_transition(2, "left", 2, 1.0)

    # s3
    mdp.set_transition(3, "right", 4, 1.0)
    mdp.set_transition(3, "left", 2, 1.0)

    # s4
    mdp.set_transition(4, "right", 4, 1.0)
    mdp.set_transition(4, "left", 3, 1.0)

    for s in mdp.states():
        mdp.set_reward(s, 1.0)
    
    for s in mdp.goals():
        mdp.set_reward(s, 0.0)

    return mdp

def line_7():
    mdp = MDP(_states=7, _initial_states=[0,1,2,4,5,6], _goals=[3], _actions=["left", "right"])

    # s0
    mdp.set_transition(0, "right", 1, 1.0)
    mdp.set_transition(0, "left", 0, 1.0)

    # s1
    mdp.set_transition(1, "right", 2, 1.0)
    mdp.set_transition(1, "left", 0, 1.0)

    # s2
    mdp.set_transition(2, "right", 3, 1.0)
    mdp.set_transition(2, "left", 1, 1.0)

    # s3
    mdp.set_transition(3, "right", 3, 1.0)
    mdp.set_transition(3, "left", 3, 1.0)

    # s4
    mdp.set_transition(4, "right", 5, 1.0)
    mdp.set_transition(4, "left", 3, 1.0)

    # s5
    mdp.set_transition(5, "right", 6, 1.0)
    mdp.set_transition(5, "left", 4, 1.0)

    # s6
    mdp.set_transition(6, "right", 6, 1.0)
    mdp.set_transition(6, "left", 5, 1.0)

    for s in mdp.states():
        mdp.set_reward(s, 1.0)
    
    for s in mdp.goals():
        mdp.set_reward(s, 0.0)

    return mdp