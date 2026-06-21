class Z3Result:
    
    def __init__(self, result, model=None, solve_time=None):
        self.result = result
        self.model = model
        self.solve_time = solve_time

