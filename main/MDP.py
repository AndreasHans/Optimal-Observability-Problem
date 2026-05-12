from typing import Iterable, List


class MDP:

    def __init__(self, variant: str, size: int, _states:int, _initial_states:List[int], _goals:List[int], _actions:List[str]):
        self.variant = variant
        self._states = _states
        self._initial_states = _initial_states
        self._goal_states = _goals
        self._actions = _actions
        self._optimals = [0 for _ in range(_states)]
        self._type = "fishsayce"
        self._size = size
        # p(s,a,s') = 0 for all s,a,s'
        self.transition_probabilities = {
            state: {
                action: {state2: 0.0 for state2 in range(_states)}
                for action in _actions
            }
            for state in range(_states)
        }

        # rew(s) = 1 for all states except the goal states, where rew(s) = 0
        self.rewards = [1.0 for _ in range(_states)]
        for goal in _goals:
            self.rewards[goal] = 0.0

    def states(self) -> Iterable[int]:
        for i in range(self._states):
            yield i
        
    def post(self, state:int, action:str) -> Iterable[int]:
        for state2 in range(self._states):
            if self.transition_probabilities[state][action][state2] > 0:
                yield state2

    def actions(self) -> Iterable[str]:
        for a in self._actions:
            yield a
            
    def initial_states(self) -> Iterable[int]:
        for s in self._initial_states:
            yield s

    def initial_states_len(self) -> int:
        return len(self._initial_states)

    def goals(self) -> Iterable[int]:
        for g in self._goal_states:
            yield g

    def optimal_cost(self, state:int) -> float:
        return self._optimals[state]

    def set_optimal_cost(self, state:int, optimal:float) -> None:
        self._optimals[state] = optimal

    def set_reward(self, state:int, reward:float) -> None:
        self.rewards[state] = reward

    def reward(self, state:int) -> float:
        return self.rewards[state]

    def set_transition(self, state:int, action:str, state2:int, probability:float) -> None:
        self.transition_probabilities[state][action][state2] = probability

    def transition(self, state:int, action:str, state2:int) -> float:
        return self.transition_probabilities[state][action][state2]
        
    def set_size(self, size: int):
        self._size = size

    def size(self) -> int:
        return self._size
    
    def set_type(self, type: str):
        self._type = type

    def type(self) -> str:
        return self._type