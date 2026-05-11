from MDP import MDP

def grid_center_n(n:int):
    """
    N x N grid MDP where the goal is in the center.
    """
    if n < 3:
        raise ValueError("n must be at least 3")
    
    goal = n * n // 2 

    mdp = MDP(variant = "grid", size = n, _states=n*n, _initial_states=[i for i in range(n*n) if i != goal], _goals=[goal], _actions=["left", "right", "up", "down"])

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

    for s in mdp.goals():
        for a in mdp.actions():
            for s2 in mdp.states():
                if s2 != s:
                    mdp.set_transition(s, a, s2, 0.0)
                else:
                    mdp.set_transition(s, a, s2, 1.0)


    for s in mdp.states():
        row = s // n
        col = s % n
        mdp.set_optimal_cost(s, abs(n // 2 - row) + abs(n // 2 - col))

    return mdp

def maze_n(n:int):
    return maze(n, ((n-1)//2))

def maze(columns:int, rows:int):
    if columns % 2 == 0:
        raise ValueError("columns must be odd")
    print(f"Creating maze MDP with {columns} columns and {rows} rows")
    num_states = columns+3*rows
    goal = num_states - rows - 1
    mid = (columns - 1) // 2

    mdp = MDP(variant = "maze", size = columns, _states=num_states, _initial_states=[s for s in range(num_states) if (s != goal)], _goals=[goal], _actions=["left", "right", "up", "down"])

    def set_vertical_leg_transitions(start:int, up_target:int):
        end = start + rows
        for s in range(start, end):
            if s == start:
                mdp.set_transition(s, "up", up_target, 1.0)
                mdp.set_transition(s, "down", s+1, 1.0)
            elif s == end - 1:
                mdp.set_transition(s, "up", s-1, 1.0)
                mdp.set_transition(s, "down", s, 1.0)
            else:
                mdp.set_transition(s, "up", s-1, 1.0)
                mdp.set_transition(s, "down", s+1, 1.0)

            mdp.set_transition(s, "left", s, 1.0)
            mdp.set_transition(s, "right", s, 1.0)

    # All transitions for the line part
    for s in range(columns):
        if s == 0:
            mdp.set_transition(s, "right", s+1, 1.0)
            mdp.set_transition(s, "left", s, 1.0)
            mdp.set_transition(s, "down", columns, 1.0)
            mdp.set_transition(s, "up", s, 1.0)
        elif s == mid:
            mdp.set_transition(s, "right", s+1, 1.0)
            mdp.set_transition(s, "left", s-1, 1.0)
            mdp.set_transition(s, "down", columns + rows, 1.0)
            mdp.set_transition(s, "up", s, 1.0)
        elif s == columns-1:
            mdp.set_transition(s, "right", s, 1.0)
            mdp.set_transition(s, "left", s-1, 1.0)
            mdp.set_transition(s, "down", (2* rows + columns), 1.0)
            mdp.set_transition(s, "up", s, 1.0)
        else:
            mdp.set_transition(s, "right", s+1, 1.0)
            mdp.set_transition(s, "left", s-1, 1.0)
            mdp.set_transition(s, "down", s, 1.0)
            mdp.set_transition(s, "up", s, 1.0)

    set_vertical_leg_transitions(columns, 0)
    set_vertical_leg_transitions(columns + rows, mid)
    set_vertical_leg_transitions(columns + 2 * rows, columns-1)


                
    #set reward
    for s in mdp.states():
        mdp.set_reward(s, 1.0)
    
    for s in mdp.goals():
        mdp.set_reward(s, 0)

    #set minimum cost
    mid = columns//2 
    for s in mdp.states():

        if s < columns:
            #the line
            mdp.set_optimal_cost(s, abs(s-mid) + rows)
        elif s < columns + rows:
            mdp.set_optimal_cost(s, mid + rows + s - columns + 1)
        elif s < (columns + 2 * rows):
            mdp.set_optimal_cost(s, goal - s)  
        else:
            mdp.set_optimal_cost(s, mid + rows + s - (columns + 2 * rows) + 1)

    for s in mdp.goals():
        for a in mdp.actions():
            for s2 in mdp.states():
                if s2 != s:
                    mdp.set_transition(s, a, s2, 0.0)
                else:
                    mdp.set_transition(s, a, s2, 1.0)
  
   
   
    return mdp

            
        
    

def line_n(n:int):
    if n % 2 == 0:
        raise ValueError("n must be odd")
    print(f"Creating line MDP with {n} states")

    mdp = MDP(variant = "line", size = n, _states=n, _initial_states=[i for i in range(n) if i != n//2 ], _goals=[n//2], _actions=["left", "right"])

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

    for s in mdp.goals():
        for a in mdp.actions():
            for s2 in mdp.states():
                if s2 != s:
                    mdp.set_transition(s, a, s2, 0.0)
                else:
                    mdp.set_transition(s, a, s2, 1.0)


    return mdp


def grid_corner_n(n:int):
    """
    N x N grid MDP where the goal is in the bottom right corner.
    """
    if n < 3:
        raise ValueError("n must be at least 3")
    
    goal = n*n - 1

    mdp = MDP(variant = "grid", size = n, _states=n*n, _initial_states=[i for i in range(n*n) if i != goal], _goals=[goal], _actions=["left", "right", "up", "down"])

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

    for s in mdp.goals():
        for a in mdp.actions():
            for s2 in mdp.states():
                if s2 != s:
                    mdp.set_transition(s, a, s2, 0.0)
                else:
                    mdp.set_transition(s, a, s2, 1.0)


    return mdp