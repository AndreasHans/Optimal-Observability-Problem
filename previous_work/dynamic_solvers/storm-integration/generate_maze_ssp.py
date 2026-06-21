#!/usr/bin/env python3

import sys

def xy_to_state(x, y, width):
    """Convert (x, y) maze coordinates to linearized state index.

    State space layout:
    - Row 0 (horizontal corridor): states 0 to WIDTH-1
    - Row y > 0 (vertical corridors): states WIDTH + 3*(y-1) + corridor_idx
      where corridor_idx: 0 (x=0), 1 (x=WIDTH/2), 2 (x=WIDTH-1)
    """
    if y == 0:
        return x
    else:
        # Map x to corridor index
        if x == 0:
            corridor_idx = 0
        elif x == width // 2:
            corridor_idx = 1
        elif x == width - 1:
            corridor_idx = 2
        else:
            raise ValueError(f"Invalid x={x} for vertical corridor")

        return width + 3 * (y - 1) + corridor_idx

def state_to_xy(state, width):
    """Convert linearized state index to (x, y) maze coordinates."""
    if state < width:
        return state, 0
    else:
        # Vertical corridor
        offset = state - width
        y = offset // 3 + 1
        corridor_idx = offset % 3

        if corridor_idx == 0:
            x = 0
        elif corridor_idx == 1:
            x = width // 2
        else:  # corridor_idx == 2
            x = width - 1

        return x, y

def get_all_states(width, height):
    """Get all valid states in the maze."""
    states = []

    # Row 0: horizontal corridor
    for x in range(width):
        states.append(xy_to_state(x, 0, width))

    # Rows 1 to HEIGHT-1: vertical corridors
    for y in range(1, height):
        for corridor_idx, x in enumerate([0, width // 2, width - 1]):
            states.append(xy_to_state(x, y, width))

    return states

def main():
    # Usage: python generate_maze_ssp.py WIDTH HEIGHT BUDGET
    if len(sys.argv) < 4:
        print("Usage: python generate_maze_ssp.py WIDTH HEIGHT BUDGET")
        sys.exit(1)

    WIDTH = int(sys.argv[1])
    HEIGHT = int(sys.argv[2])
    BUDGET = int(sys.argv[3])

    if WIDTH < 3:
        raise SystemExit("WIDTH must be >= 3 (to accommodate 3 vertical corridors)")
    if HEIGHT < 2:
        raise SystemExit("HEIGHT must be >= 2")

    num_states = WIDTH + 3 * (HEIGHT - 1)

    if BUDGET < 0 or BUDGET >= num_states:
        raise SystemExit(f"BUDGET must be between 0 and {num_states - 1}")

    print("pomdp\n")
    print("const WIDTH;")
    print("const HEIGHT;")
    print("const GOAL;")
    print("const BUDGET;\n")

    # Define observation position constants
    for i in range(1, BUDGET + 1):
        print(f"const POS{i};")

    # Observable declarations
    print("\nobservable \"goal\" = (position=GOAL);")
    print("observable \"started\" = (started);\n")
    for i in range(1, BUDGET + 1):
        print(f"observable \"flag{i}\" = (({i}<=BUDGET)?(position=POS{i}):false);")

    # Main maze module
    print("\nmodule MAZE\n")
    print("chosen : bool init false;")
    print("started : bool init false;")
    print(f"position : [0..WIDTH+3*(HEIGHT-1)-1];")

    # Start action - uniformly distribute across non-goal valid positions
    print("// State space: WIDTH + 3*(HEIGHT-1) states")
    print("// Row 0: states 0 to WIDTH-1 (horizontal corridor)")
    print("// Row y>0: states WIDTH+3*(y-1) to WIDTH+3*(y-1)+2 (3 vertical corridors)")
    print("\n[start] !started -> ")

    all_states = get_all_states(WIDTH, HEIGHT)
    for idx, state in enumerate(all_states):
        separator = ";" if idx == len(all_states) - 1 else ""
        print(f"  (({state}>=WIDTH+3*(HEIGHT-1) | GOAL={state})?0:1)/(WIDTH+3*(HEIGHT-1)-1):(started'={state}<WIDTH+3*(HEIGHT-1))&(position'=({state}<WIDTH+3*(HEIGHT-1)?{state}:GOAL))&(chosen'=true){separator}")
        if idx < len(all_states) - 1:
            print("+", end=" ")

    # Left action - only works in horizontal corridor (position < WIDTH)
    print("\n// Left: only works in horizontal corridor (position < WIDTH)")
    print("[left]  started & (position < WIDTH) -> 1.0:(position'=max(0,position-1));")
    print("[left]  started & (position >= WIDTH) -> 1.0:true;")

    # Right action - only works in horizontal corridor (position < WIDTH)
    print("\n// Right: only works in horizontal corridor (position < WIDTH)")
    print("[right] started & (position < WIDTH) -> 1.0:(position'=min(WIDTH-1,position+1));")
    print("[right] started & (position >= WIDTH) -> 1.0:true;")

    # Up action
    print("\n// Up: move up in vertical corridors")
    print("// From row 1 to row 0: depends on corridor index")
    print(f"[up]    started & (position = WIDTH+0) -> 1.0:(position'=0);")  # corridor 0 -> x=0
    print(f"[up]    started & (position = WIDTH+1) -> 1.0:(position'=floor(WIDTH/2);")  # corridor 1 -> x=WIDTH // 2
    print(f"[up]    started & (position = WIDTH+2) -> 1.0:(position'=WIDTH-1);")  # corridor 2 -> x=WIDTH-1
    print("// From row y>1 to row y-1: subtract 3")
    print("[up]    started & (position > WIDTH+2) -> 1.0:(position'=position-3);")
    print("// Already in row 0: stay")
    print("[up]    started & (position < WIDTH) -> 1.0:true;")

    # Down action
    print("\n// Down: move down in vertical corridors")
    print("// From row 0 to row 1: only from corridor positions")
    print(f"[down]  started & (position = 0) -> 1.0:(position'=WIDTH+0);")  # x=0 -> corridor 0
    print(f"[down]  started & (position = floor(WIDTH/2)) -> 1.0:(position'=WIDTH+1);")  # x=WIDTH // 2 -> corridor 1
    print(f"[down]  started & (position = WIDTH-1) -> 1.0:(position'=WIDTH+2);")  # x=WIDTH-1 -> corridor 2
    print("// From row 0 non-corridor positions: stay")
    print("[down]  started & (position < WIDTH) & (position != 0 & position != floor(WIDTH/2) & position != WIDTH-1) -> 1.0:true;")
    print("// From row y to row y+1 (if not at bottom): add 3")
    print(f"[down]  started & (position >= WIDTH) & (position < WIDTH+3*(HEIGHT-1)-3) -> 1.0:(position'=position+3);")
    print("// Already at bottom row: stay")
    print(f"[down]  started & (position >= WIDTH+3*(HEIGHT-1)-3) & (position < WIDTH+3*(HEIGHT-1)) -> 1.0:true;")

    print("[stop]  (position = GOAL) -> true;")
    print("\nendmodule\n")

    # Goal label
    print("label \"gameover\" = (position=GOAL);\n")

    # Rewards
    print("rewards")
    print("[up]    true : 1;")
    print("[down]  true : 1;")
    print("[left]  true : 1;")
    print("[right] true : 1;")
    print("endrewards")

    # Example storm-pomdp command
    goal_example = xy_to_state(WIDTH // 2, HEIGHT - 1, WIDTH)  # Bottom of middle corridor
    print(f"// Example: WIDTH={WIDTH}, HEIGHT={HEIGHT}, {num_states} states total")
    print(f"// storm-pomdp --prism maze.prism -const WIDTH={WIDTH},HEIGHT={HEIGHT},BUDGET={BUDGET},", end='')
    for i in range(1, BUDGET + 1):
        print(f"POS{i}=0,", end='')
    print(f"GOAL={goal_example}", end='')
    print(" --prop \"Rmin=?[F \\\"gameover\\\"]\" --buildfull --belief-exploration --exact --memorybound 1")

if __name__ == "__main__":
    main()
