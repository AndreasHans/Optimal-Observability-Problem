from z3 import *

class BMSSPResult:
    def __init__(self, solve_time=None, min_exp_rew=(int,int), y_vars=dict(), pi_vars=dict(), theta_vars=dict(), delta_vars=dict()):
        self.solve_time = solve_time
        self.min_exp_rew = min_exp_rew
        self.y_vars = y_vars
        self.pi_vars = pi_vars
        self.theta_vars = theta_vars
        self.delta_vars = delta_vars
        self.bot = 'bot'

    def print(self):

        print(f"Solve time: {self.solve_time} seconds")

       

        enabled_sensors = [s for s in self.y_vars if is_true(self.y_vars[s])]

        for s in enabled_sensors:
            val = f"y({s})"
            print(val)

        for s, c in self.pi_vars:
            if c == 0:
                val = f"pi({s}, {c}) = {self.pi_vars[s, c]}"
                print(val)


        for c, o, a in self.theta_vars:
            if o in enabled_sensors or o == self.bot:
                v = self.theta_vars[c, o, a]
                if is_true(v):
                    print(f"theta({c}, {o}, {a})")
                elif is_rational_value(v) and v.numerator_as_long() != 0:
                    print(f"theta({c}, {o}, {a}) = {v}")

        for c, o, c2 in self.delta_vars:
            if o in enabled_sensors or o == self.bot:
                v = self.delta_vars[c, o, c2]
                if is_true(v):
                    val = f"delta({c}, {o}, {c2})"
                    print(val)
                elif is_rational_value(v) and v.numerator_as_long() != 0:
                    val = f"delta({c}, {o}, {c2}) = {v}"
                    print(val)
                    
        if len(self.min_exp_rew) == 2:
            print(f"min_exp_rew = {self.min_exp_rew[0]}/{self.min_exp_rew[1]}")
        else:
            print(f"min_exp_rew = {self.min_exp_rew[0]}")
