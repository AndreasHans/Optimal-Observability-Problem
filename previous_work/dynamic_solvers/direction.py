from enum import Enum
from typing import Optional, Set


class Direction(Enum):
    N  = ("N",  {"u"})
    S  = ("S",  {"d"})
    W  = ("W",  {"l"})
    E  = ("E",  {"r"})
    NE = ("NE", {"u", "r"})
    SE = ("SE", {"d", "r"})
    SW = ("SW", {"d", "l"})
    NW = ("NW", {"u", "l"})

    def __init__(self, symbol, actions):
        self.symbol = symbol
        self.actions = actions

    @staticmethod
    def action_to_dir(actions: Set[str]) -> Optional['Direction']:
        """
        Find the Direction enum case that matches the given action set.

        Args:
            actions: A set of action strings

        Returns:
            The matching Direction enum, or None if no match is found.
        """
        for direction in Direction:
            if direction.actions == actions:
                return direction
        return None

    def opposite(self):
        match self.symbol:
            case "N": return self.S
            case "S": return self.N
            case "W": return self.E
            case "E": return self.W
            case "NE": return self.SW
            case "SW": return self.NE
            case "NW": return self.SE
            case "SE": return self.NW
        return None
