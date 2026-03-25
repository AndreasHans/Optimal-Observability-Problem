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


def grid_corner_n(n:int):
    """
    N x N grid MDP where the goal is in the bottom right corner.
    """
    if n < 3:
        raise ValueError("n must be at least 3")
    
    goal = n*n - 1

    mdp = MDP(_states=n*n, _initial_states=[i for i in range(n*n) if i != goal], _goals=[goal], _actions=["left", "right", "up", "down"])

    for s in mdp.states():
        mdp.set_reward(s, 1.0)

    for s in mdp.goals():
        mdp.set_reward(s, 0.0)

    for s in mdp.states():
        col = s % n
        row = s // n

        if col == 0:
            mdp.set_transition(s, "right", s+1, 1.0)
            mdp.set_transition(s, "left", s, 1.0)
        elif col == n-1:
            mdp.set_transition(s, "right", s, 1.0)
            mdp.set_transition(s, "left", s-1, 1.0)
        else:
            mdp.set_transition(s, "right", s+1, 1.0)
            mdp.set_transition(s, "left", s-1, 1.0)

        if row == 0:
            mdp.set_transition(s, "down", s+n, 1.0)
            mdp.set_transition(s, "up", s, 1.0)
        elif row == n-1:
            mdp.set_transition(s, "down", s, 1.0)
            mdp.set_transition(s, "up", s-n, 1.0)
        else:
            mdp.set_transition(s, "down", s+n, 1.0)
            mdp.set_transition(s, "up", s-n, 1.0)

    for s in mdp.states():
        row = s // n
        col = s % n
        mdp.set_optimal_cost(s, (n - 1 - row) + (n - 1 - col))


    return mdp