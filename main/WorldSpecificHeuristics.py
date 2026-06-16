
from math import floor

from z3 import *


def add_trend_1(solver, mdp, memory_budget, sensor_budget, add_constraint, y, theta, delta, states, n, bot):
    if mdp.type() == "line" and sensor_budget >= 2 and memory_budget >= 2:
        U = []
        for i in range(0, min(sensor_budget- 1, floor((n/2)-1)) + 1):
            u = floor(i*(n-1)/(2*sensor_budget))
            U.append(u)

        for s in states:
            if s in U:
                add_constraint(solver, y(s) == True)
                add_constraint(solver, theta(0, s, "right") == True)
                add_constraint(solver, theta(1, s, "right") == True)
                add_constraint(solver, delta(0, s, 1) == True)
                add_constraint(solver, delta(1, s, 1) == True)
            else:                
                add_constraint(solver, y(s) == False)

        add_constraint(solver, theta(0, bot, "left") == True)
        add_constraint(solver, theta(1, bot, "right") == True)
        add_constraint(solver, delta(1, bot, 1) == True)
        add_constraint(solver, delta(0, bot, 0) == True)

def add_trend_2(solver, mdp, memory_budget, sensor_budget, add_constraint, y, theta, delta, states, n, bot):
    if mdp.type() == "line" and sensor_budget == 1 and memory_budget >= 2:
        u = min(memory_budget-2, floor(n/4))
        U = [s for s in [u-1,u,u+1] if s >= 0 and s < n]
        for s in states:
            if not s in U:
                add_constraint(solver, y(s) == False)
        add_constraint(solver, Or([y(s) for s in U]))

def add_trend_6(solver, mdp, memory_budget, sensor_budget, add_constraint, y, theta, delta, states, n, bot):
    if mdp.type() == "grid" and sensor_budget < n-1 and memory_budget >= 2:
        for i in range(1, sensor_budget + 1):
            if i % 2 == 0:
                u = n*n - i*n-1
            else:
                u = n*n - (i+2)
            add_constraint(solver, y(u))

def add_trend_9(solver, mdp, memory_budget, sensor_budget, add_constraint, y, theta, delta, states, n, bot):
    if mdp.type() == "maze":
        R = (n-1)//2
        U = []
        for i in range(1, sensor_budget + 1):
            if 1 <= i <= R + 1:
                u = i - 1
            elif R + 2 <= i <= 2*R:
                u = n+i-2
            elif 2*R+1 <= i <= 2*R+n-1:
                u = i - R
            else:
                u = i
            U.append(u)

        for s in states:
            if s in U:
                add_constraint(solver, y(s) == True)
            else:                
                add_constraint(solver, y(s) == False)

        if memory_budget == 1:
            add_constraint(solver, theta(0, bot, "up") == True)
            add_constraint(solver, delta(0, bot, 0) == True)
        elif memory_budget == 2:
            add_constraint(solver, theta(0, bot, "up") == True)
            add_constraint(solver, theta(1, bot, "left") == True)
            add_constraint(solver, delta(0, bot, 1) == True)
            add_constraint(solver, delta(1, bot, 0) == True)
        elif memory_budget == 3:
            add_constraint(solver, theta(0, bot, "up") == True)
            add_constraint(solver, theta(1, bot, "left") == True)
            add_constraint(solver, theta(2, bot, "down") == True)
            add_constraint(solver, delta(0, bot, 1) == True)
            add_constraint(solver, delta(1, bot, 0) == True)
            add_constraint(solver, delta(2, bot, 2) == True)
        elif memory_budget == 4:
            add_constraint(solver, theta(0, bot, "up") == True)
            add_constraint(solver, theta(1, bot, "left") == True)
            add_constraint(solver, theta(2, bot, "down") == True)
            add_constraint(solver, theta(3, bot, "right") == True)
            add_constraint(solver, delta(0, bot, 1) == True)
            add_constraint(solver, delta(1, bot, 0) == True)
            add_constraint(solver, delta(2, bot, 3) == True)
            add_constraint(solver, delta(3, bot, 2) == True)
