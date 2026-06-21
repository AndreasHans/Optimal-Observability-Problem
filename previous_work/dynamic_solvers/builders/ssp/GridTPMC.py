from typing import Unpack

from previous_work.dynamic_solvers.builders.ssp.SSPSpec import SSPSpec
from previous_work.dynamic_solvers.builders.worlds import Grid
from previous_work.dynamic_solvers.builders.typedicts import OperationKWArgs
from previous_work.dynamic_solvers.utils import get_observation_marker


class GridTPMC(Grid, SSPSpec):
    def __init__(self, budget: int, goal: int, width: int, height: int,
                 determinism: bool = False, **kwargs: Unpack[OperationKWArgs]):
        """Create a Grid SSP instance.

        Args:
            budget: Budget constraint (number of sensors allowed).
            goal: Goal state index.
            width: Width of the grid.
            height: Height of the grid.
            determinism: Use deterministic strategies (default: False).
            **kwargs: Additional parameters (ctx, verbose, bellman_format).
                See OOPSpec.__init__ for details.
        """
        Grid.__init__(self, width, height, goal)
        SSPSpec.__init__(self, budget, goal, determinism, **kwargs)

    def draw_model(self, model: dict, goal_state: int, budget: int, use_color: bool = True) -> str:
        """Draw grid world with sensor placements marked in the SSP setting."""
        lines = []
        lines.append(f"Grid World ({self.width}x{self.height}) (SSP):")
        lines.append("")

        # Calculate width needed for state numbers
        max_state = self.size - 1
        num_width = len(str(max_state))
        cell_width = num_width + 2  # Add padding

        for y in range(self.height):
            state_line = ""
            sensor_line = ""

            for x in range(self.width):
                state = y * self.width + x

                if state == goal_state:
                    state_line += f" {state:{num_width}}  "
                    # Center the symbol in the cell
                    padding = (cell_width - 1) // 2
                    sensor_line += " " * padding + "✓" + " " * (cell_width - padding)
                else:
                    state_line += f" {state:{num_width}}  "
                    sensor_on = self.is_obs_selected(model, f'ys{state}')
                    symbol = get_observation_marker(1 if sensor_on else 0, use_color, binary=True)
                    # Center the symbol in the cell
                    padding = (cell_width - 1) // 2
                    sensor_line += " " * padding + symbol + " " * (cell_width - padding)

            lines.append(state_line)
            lines.append(sensor_line)
            lines.append("")

        lines.append(f"Legend: ✓=goal, "
                     f"{get_observation_marker(0, use_color, binary=True)}=sensor off, "
                     f"{get_observation_marker(1, use_color, binary=True)}=sensor on")

        return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 6:
        size_x = int(sys.argv[1])
        size_y = int(sys.argv[2])
        goal = int(sys.argv[3])
        budget = int(sys.argv[4])
        threshold = sys.argv[5]
        det = int(sys.argv[6])

        tpMC = GridTPMC(budget, goal, size_x, size_y, determinism=det == 1)

        tpMC.declare_variables()
        tpMC.collect_constraints(threshold)
