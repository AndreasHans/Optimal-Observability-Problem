from typing import Unpack

from previous_work.dynamic_solvers.builders.pop.POPSpec import POPSpec
from previous_work.dynamic_solvers.builders.worlds import Grid
from previous_work.dynamic_solvers.builders.typedicts import OperationKWArgs
from previous_work.dynamic_solvers.utils import get_observation_marker


class GridTPMC(Grid, POPSpec):
    def __init__(self, budget: int, goal: int, width: int, height: int,
                 determinism: bool = False, **kwargs: Unpack[OperationKWArgs]):
        """Create a Grid POP instance.

        Args:
            budget: Budget constraint (number of observation classes allowed).
            goal: Goal state index.
            width: Width of the grid.
            height: Height of the grid.
            determinism: Use deterministic strategies (default: False).
            **kwargs: Additional parameters (ctx, verbose, bellman_format).
                See OOPSpec.__init__ for details.
        """
        Grid.__init__(self, width, height, goal)
        POPSpec.__init__(self, budget, goal, determinism, **kwargs)

    def draw_model(self, model: dict, goal_state: int, budget: int, use_color: bool = True) -> str:
        """Draw grid world with observation classes marked in the POP setting."""
        lines = []
        lines.append(f"Grid World ({self.width}x{self.height}) (POP):")
        lines.append("")

        # Calculate width needed for state numbers
        max_state = self.size - 1
        num_width = len(str(max_state))
        cell_width = num_width + 3  # 1 leading space + num_width + 2 trailing spaces

        for y in range(self.height):
            state_line = ""
            obs_line = ""

            for x in range(self.width):
                state = y * self.width + x

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

            lines.append(state_line)
            lines.append(obs_line)
            lines.append("")

        # Build legend
        legend = "Legend: ✓=goal"
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

        tpMC = GridTPMC(budget, goal, size, size, determinism=det == 1)

        tpMC.declare_variables()
        tpMC.collect_constraints(threshold)
