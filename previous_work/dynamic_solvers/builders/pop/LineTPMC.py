from typing import Unpack

from previous_work.dynamic_solvers.builders.pop.POPSpec import POPSpec
from previous_work.dynamic_solvers.builders.worlds import Line
from previous_work.dynamic_solvers.builders.typedicts import OperationKWArgs
from previous_work.dynamic_solvers.utils import get_observation_marker


class LineTPMC(Line, POPSpec):
    def __init__(self, budget: int, goal: int, length: int,
                 determinism: bool = False, **kwargs: Unpack[OperationKWArgs]):
        """Create a Line POP instance.

        Args:
            budget: Budget constraint (number of observation classes allowed).
            goal: Goal state index.
            length: Length of the line world.
            determinism: Use deterministic strategies (default: False).
            **kwargs: Additional parameters (ctx, verbose, bellman_format).
                See OOPSpec.__init__ for details.
        """
        Line.__init__(self, length, goal)
        POPSpec.__init__(self, budget, goal, determinism, **kwargs)

    def draw_model(self, model: dict, goal_state: int, budget: int, use_color: bool = True) -> str:
        """Draw line world with observation classes marked in the POP setting."""
        lines = []

        # Calculate width needed for state numbers
        max_state = self.length - 1
        num_width = len(str(max_state))
        cell_width = num_width + 3  # 1 leading space + num_width + 2 trailing spaces

        # State numbers
        state_line = ""
        obs_line = ""

        for state in range(self.length):
            if state == goal_state:
                state_line += f" {state:{num_width}}  "
                # Center the symbol in the cell
                padding = (cell_width - 1) // 2
                obs_line += " " * padding + "✓" + " " * (cell_width - padding - 1)
            else:
                state_line += f" {state:{num_width}}  "
                # Find which observation class this state belongs to
                obs_class = 0
                for o in range(1, budget + 1):
                    if self.is_obs_selected(model, f'ys{state}o{o}'):
                        obs_class = o
                        break
                symbol = get_observation_marker(obs_class, use_color)
                # Center the symbol in the cell (ANSI colors don't affect width)
                padding = (cell_width - 1) // 2
                obs_line += " " * padding + symbol + " " * (cell_width - padding - 1)

        lines.append(f"Line World ({self.length}) (POP):")
        lines.append(state_line)
        lines.append(obs_line)

        # Build legend
        legend = "\nLegend: ✓=goal"
        for o in range(1, budget + 1):
            legend += f", {get_observation_marker(o, use_color)}=obs {o}"
        lines.append(legend)

        return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 6:
        size = int(sys.argv[1])
        goal = int(sys.argv[2])
        budget = int(sys.argv[3])
        threshold = sys.argv[4]
        det = int(sys.argv[5])

        tpMC = LineTPMC(budget, goal, size, determinism=det == 1)

        tpMC.declare_variables()
        tpMC.collect_constraints(threshold)
