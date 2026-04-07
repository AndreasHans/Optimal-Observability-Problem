from z3 import *
from BMSSPResult import BMSSPResult
from Z3Result import Z3Result

bot = 'bot'

class ParseModel:

    def parse_observation(token: str):
        if token == bot:
            return bot
        return int(token)
    
    def parse_min_exp_rew(value):
        ls = [int(x) for x in str(value).split('/')]
        return ls

    def parse_model(z3result: Z3Result) -> BMSSPResult:
        result = BMSSPResult()

        result.solve_time = z3result.solve_time
        model = z3result.model

        for d in model.decls():
            value = model[d]
            name = d.name()

            if name == 'min_exp_rew':
                result.min_exp_rew = ParseModel.parse_min_exp_rew(value)
                continue

            if name.startswith('y_'):
                parts = name.split('_')
                if len(parts) == 2:
                    s = int(parts[1])
                    result.y_vars[s] = value
                continue

            if name.startswith('pi_'):
                parts = name.split('_')
                if len(parts) == 3:
                    s = int(parts[1])
                    c = int(parts[2])
                    result.pi_vars[s, c] = value
                continue

            if name.startswith('theta_'):
                parts = name.split('_')
                if len(parts) >= 4:
                    c = int(parts[1])
                    o = ParseModel.parse_observation(parts[2])
                    a = '_'.join(parts[3:])
                    result.theta_vars[c, o, a] = value
                continue

            if name.startswith('delta_'):
                parts = name.split('_')
                if len(parts) == 4:
                    c = int(parts[1])
                    o = ParseModel.parse_observation(parts[2])
                    c2 = int(parts[3])
                    result.delta_vars[c, o, c2] = value
                continue

        return result