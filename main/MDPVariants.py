from MDP import MDP

def grid_center(n:int, m:int):
    if n % 2 == 0 or m % 2 == 0:
        raise ValueError("n and m must be odd")
    print(f"Creating grid MDP with {n} rows and {m} columns")

    mdp = MDP(_states=n*m, _initial_states=[(j*n + i) for i in range(n) for j in range(m) if (i != n//2 and j != m//2)], _goals=[(m//2) * n + (n//2)], _actions=["left", "right", "up", "down"])
    # make transitions
    for s in mdp.states():
        if s-1 % n == 0:
            mdp.set_transition(s, "right", s+1, 1.0)
            mdp.set_transition(s, "left", s, 1.0)
        elif s-(n-1) % n == 0:
            mdp.set_transition(s, "right", s, 1.0)
            mdp.set_transition(s, "left", s-1, 1.0)
        else:
            mdp.set_transition(s, "right", s+1, 1.0)
            mdp.set_transition(s, "left", s-1, 1.0)

        if s < n:
            mdp.set_transition(s, "down", s+n, 1.0)
            mdp.set_transition(s, "up", s, 1.0)
        elif s >= n*(m-1):
            mdp.set_transition(s, "down", s, 1.0)
            mdp.set_transition(s, "up", s-n, 1.0)
        else:
            mdp.set_transition(s, "down", s+n, 1.0)
            mdp.set_transition(s, "up", s-n, 1.0)

    # set rewards
    for s in mdp.states():
        mdp.set_reward(s, 1.0)
    
    for s in mdp.goals():
        mdp.set_reward(s, 0.0)

    #set optimal costs
    for s in mdp.states():
        row = s // n
        col = s % n
        mdp.set_optimal_cost(s, abs(row - m//2) + abs(col - n//2))
    
    return mdp
    
     

def line_n(n:int):
    if n % 2 == 0:
        raise ValueError("n must be odd")
    print(f"Creating line MDP with {n} states")

    mdp = MDP(_states=n, _initial_states=[i for i in range(n) if i != n//2 ], _goals=[n//2], _actions=["left", "right"])

    for s in mdp.states():
        if s == 0:
            mdp.set_transition(s, "right", s+1, 1.0)
            mdp.set_transition(s, "left", s, 1.0)
        elif s == n-1:
            mdp.set_transition(s, "right", s, 1.0)
            mdp.set_transition(s, "left", s-1, 1.0)
        else:
            mdp.set_transition(s, "right", s+1, 1.0)
            mdp.set_transition(s, "left", s-1, 1.0)


    for s in mdp.states():
        mdp.set_reward(s, 1.0)
    
    for s in mdp.goals():
        mdp.set_reward(s, 0.0)

    for s in mdp.states():
        mdp.set_optimal_cost(s, abs(s - n//2))

    return mdp


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

    mdp.set_optimal_cost(0,2)
    mdp.set_optimal_cost(1,1)
    mdp.set_optimal_cost(2,0)
    mdp.set_optimal_cost(3,1)
    mdp.set_optimal_cost(4,2)

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

    mdp.set_optimal_cost(0,3)
    mdp.set_optimal_cost(1,2)
    mdp.set_optimal_cost(2,1)
    mdp.set_optimal_cost(3,0)
    mdp.set_optimal_cost(4,1)
    mdp.set_optimal_cost(5,2)
    mdp.set_optimal_cost(6,3)

    return mdp