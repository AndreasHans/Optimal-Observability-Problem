from typing import Unpack

from previous_work.dynamic_solvers.builders.ssp.SSPSpec import SSPSpec
from previous_work.dynamic_solvers.builders.worlds import Maze
from previous_work.dynamic_solvers.utils import get_observation_marker
from previous_work.dynamic_solvers.builders.typedicts import OperationKWArgs


class MazeTPMC(Maze, SSPSpec):
    def __init__(self, budget: int, goal: int, width: int, depth: int,
                 determinism: bool = False, **kwargs: Unpack[OperationKWArgs]):
        """Create a Maze SSP instance.

        Args:
            budget: Budget constraint (number of sensors allowed).
            goal: Goal state index.
            width: Width of the maze.
            depth: Depth of the maze.
            determinism: Use deterministic strategies (default: False).
            **kwargs: Additional parameters (ctx, verbose, bellman_format).
                See OOPSpec.__init__ for details.
        """
        Maze.__init__(self, width, depth, goal)
        SSPSpec.__init__(self, budget, goal, determinism, **kwargs)

    def draw_model(self, model: dict, goal_state: int, budget: int, use_color: bool = True) -> str:
        """Draw maze world with sensor placements marked in the SSP setting."""
        lines = []
        lines.append(f"Maze World (width={self.width}, depth={self.depth}) (SSP):")
        lines.append("")

        # Calculate width needed for state numbers
        max_state = self.size - 1
        num_width = len(str(max_state))
        cell_width = num_width + 2  # Add padding

        # Top row (states 0 to width-1)
        top_state_line = ""
        top_sensor_line = ""
        for state in range(self.width):
            if state == goal_state:
                top_state_line += f" {state:{num_width}}  "
                padding = (cell_width - 1) // 2
                top_sensor_line += " " * padding + "✓" + " " * (cell_width - padding)
            else:
                top_state_line += f" {state:{num_width}}  "
                sensor_on = self.is_obs_selected(model, f'ys{state}')
                symbol = get_observation_marker(1 if sensor_on else 0, use_color, binary=True)
                padding = (cell_width - 1) // 2
                top_sensor_line += " " * padding + symbol + " " * (cell_width - padding)

        lines.append(top_state_line)
        lines.append(top_sensor_line)
        lines.append("")

        # Subsequent rows (3 states per row, starting from state 'width')
        # The 3 pillars should align under states: 0, (width-1)//2, and (width-1)
        pillar_positions = [0, (self.width - 1) // 2, self.width - 1]

        # Actual cell width in output (1 space + num_width digits + 2 spaces)
        actual_cell_width = num_width + 3

        state = self.width
        for depth_level in range(self.depth - 1):
            row_state_line = ""
            row_sensor_line = ""

            for col in range(3):
                if state >= self.size:
                    break

                # Add spacing to align this column under the correct position from top row
                if col == 0:
                    spacing = pillar_positions[0] * actual_cell_width
                else:
                    # Space from end of previous column to start of this column
                    spacing = (pillar_positions[col] - pillar_positions[col - 1] - 1) * actual_cell_width

                row_state_line += " " * spacing
                row_sensor_line += " " * spacing

                if state == goal_state:
                    row_state_line += f" {state:{num_width}}  "
                    padding = (cell_width - 1) // 2
                    row_sensor_line += " " * padding + "✓" + " " * (cell_width - padding)
                else:
                    row_state_line += f" {state:{num_width}}  "
                    sensor_on = self.is_obs_selected(model, f'ys{state}')
                    symbol = get_observation_marker(1 if sensor_on else 0, use_color, binary=True)
                    padding = (cell_width - 1) // 2
                    row_sensor_line += " " * padding + symbol + " " * (cell_width - padding)

                state += 1

            lines.append(row_state_line)
            lines.append(row_sensor_line)
            lines.append("")

        lines.append(f"Legend: ✓=goal, "
                     f"{get_observation_marker(0, use_color, binary=True)}=sensor off, "
                     f"{get_observation_marker(1, use_color, binary=True)}=sensor on")

        return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 7:
        width = int(sys.argv[1])
        depth = int(sys.argv[2])
        goal = int(sys.argv[3])
        budget = int(sys.argv[4])
        threshold = sys.argv[5]
        det = int(sys.argv[6])

        tpMC = MazeTPMC(budget, goal, width, depth, determinism=det == 1)

        tpMC.declare_variables()
        tpMC.collect_constraints(threshold)
