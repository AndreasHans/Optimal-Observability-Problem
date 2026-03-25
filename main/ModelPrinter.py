from z3 import *

class ModelPrinter:
    def __init__(self, model: ModelRef):
        self.model = model
        self.theta_vars = dict()
        self.delta_vars = dict()
        self.pi_vars = dict()
        self.y_vars = dict()
        self.bot = 'bot'
        self.min_exp_rew = None

    def map_model_to_dicts(self):
        self.y_vars.clear()
        self.pi_vars.clear()
        self.theta_vars.clear()
        self.delta_vars.clear()
        self.min_exp_rew = None

        for d in self.model.decls():
            value = self.model[d]
            name = d.name()

            if name == 'min_exp_rew':
                self.min_exp_rew = value
                continue

            if name.startswith('y_'):
                parts = name.split('_')
                if len(parts) == 2:
                    s = int(parts[1])
                    self.y_vars[s] = value
                continue

            if name.startswith('pi_'):
                parts = name.split('_')
                if len(parts) == 3:
                    s = int(parts[1])
                    c = int(parts[2])
                    self.pi_vars[s, c] = value
                continue

            if name.startswith('theta_'):
                parts = name.split('_')
                if len(parts) >= 4:
                    c = int(parts[1])
                    o = self._parse_observation(parts[2])
                    a = '_'.join(parts[3:])
                    self.theta_vars[c, o, a] = value
                continue

            if name.startswith('delta_'):
                parts = name.split('_')
                if len(parts) == 4:
                    c = int(parts[1])
                    o = self._parse_observation(parts[2])
                    c2 = int(parts[3])
                    self.delta_vars[c, o, c2] = value
                continue

        return {
            'y_vars': self.y_vars,
            'pi_vars': self.pi_vars,
            'theta_vars': self.theta_vars,
            'delta_vars': self.delta_vars,
            'min_exp_rew': self.min_exp_rew,
        }

    def _parse_observation(self, token: str):
        if token == self.bot:
            return self.bot
        return int(token)

    def print_model(self):
        self.map_model_to_dicts()

        file_solution = open("solution.txt", "w")

        print(f"min_exp_rew = {self.min_exp_rew}")
        file_solution.write(f"min_exp_rew = {self.min_exp_rew}\n")

        enabled_sensors = [s for s in self.y_vars if is_true(self.y_vars[s])]

        for s in enabled_sensors:
            val = f"y({s})"
            print(val)
            file_solution.write(val + "\n")

        for s, c in self.pi_vars:
            if c == 0:
                val = f"pi({s}, {c}) = {self.pi_vars[s, c]}"
                print(val)
                file_solution.write(val + "\n")


        for c, o, a in self.theta_vars:
            if o in enabled_sensors or o == self.bot:
                if is_true(self.theta_vars[c, o, a]):
                    val = f"theta({c}, {o}, {a})"
                    print(val)
                    file_solution.write(val + "\n")

        for c, o, c2 in self.delta_vars:
            if o in enabled_sensors or o == self.bot:
                if is_true(self.delta_vars[c, o, c2]):
                    val = f"delta({c}, {o}, {c2})"
                    print(val)
                    file_solution.write(val + "\n")

        file_solution.close()
    