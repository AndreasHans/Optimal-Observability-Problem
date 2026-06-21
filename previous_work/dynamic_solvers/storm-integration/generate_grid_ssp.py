#!/usr/bin/env python3

import sys

def main():
    # Usage: python generate_grid_ssp.py WIDTH HEIGHT BUDGET
    if len(sys.argv) < 4:
        print("Usage: python generate_grid_ssp.py WIDTH HEIGHT BUDGET")
        sys.exit(1)

    WIDTH = int(sys.argv[1])
    HEIGHT = int(sys.argv[2])
    BUDGET = int(sys.argv[3])

    GRID_SIZE = WIDTH * HEIGHT

    if WIDTH < 2 or HEIGHT < 2:
        raise SystemExit("WIDTH and HEIGHT must be >= 2")
    if BUDGET < 0 or BUDGET >= GRID_SIZE:
        raise SystemExit(f"BUDGET must be between 0 and {GRID_SIZE - 1}")

    print("pomdp\n")
    print("const WIDTH;")
    print("const HEIGHT;")
    print("const GOAL;")
    print("const BUDGET;\n")

    # Define observation position constants (as linearized indices)
    for i in range(1, BUDGET + 1):
        print(f"const POS{i};")

    # Observable declarations
    print("\nobservable \"goal\" = (position=GOAL);")
    print("observable \"started\" = (started);\n")
    for i in range(1, BUDGET + 1):
        print(f"observable \"flag{i}\" = (({i}<=BUDGET)?(position=POS{i}):false);")

    # Main grid module with linearized state space
    print("\nmodule GRID\n")
    print("chosen : bool init false;")
    print("started : bool init false;")
    print(f"position : [0..WIDTH*HEIGHT-1];")

    # Start action - uniformly distribute initial position across non-goal states
    print("\n[start] !chosen -> ")
    for s in range(GRID_SIZE):
        separator = ";" if s == GRID_SIZE - 1 else ""
        print(f"  (({s}>=WIDTH*HEIGHT | GOAL={s})?0:1)/(WIDTH*HEIGHT-1):(started'={s}<WIDTH*HEIGHT)&(position'=({s}<WIDTH*HEIGHT?{s}:GOAL))&(chosen'=true){separator}")
        if s < GRID_SIZE - 1:
            print("+", end=" ")

    print("\n// Movement: up decreases by WIDTH, down increases by WIDTH")
    print("// left decreases by 1, right increases by 1")
    print("// x = position mod WIDTH, y = position div WIDTH")

    # Movement actions with boundary checks
    # Up: move to position - WIDTH if not in top row (y > 0)

    print("\n[up]    started & (position >= WIDTH) -> 1.0:(position'=position-WIDTH);")
    print("[up]    started & (position < WIDTH) -> 1.0:true;")  # Stay if in top row

    # Down: move to position + WIDTH if not in bottom row (y < HEIGHT-1)
    print("[down]  started & (position < WIDTH*(HEIGHT-1)) -> 1.0:(position'=position+WIDTH);")
    print("[down]  started & (position >= WIDTH*(HEIGHT-1)) -> 1.0:true;")  # Stay if in bottom row

    # Left: move to position - 1 if not in leftmost column (x > 0)
    print("[left]  started & (mod(position,WIDTH) > 0) -> 1.0:(position'=position-1);")
    print("[left]  started & (mod(position,WIDTH) = 0) -> 1.0:true;")  # Stay if in left column

    # Right: move to position + 1 if not in rightmost column (x < WIDTH-1)
    print("[right] started & (mod(position,WIDTH) < WIDTH-1) -> 1.0:(position'=position+1);")
    print("[right] started & (mod(position,WIDTH) = WIDTH-1) -> 1.0:true;")  # Stay if in right column

    print("[stop]  (position = GOAL) -> true;")
    print("\nendmodule\n")

    # Goal label
    print("label \"gameover\" = (position=GOAL);\n")

    # Rewards for each action
    print("rewards")
    print("[up]    true : 1;")
    print("[down]  true : 1;")
    print("[left]  true : 1;")
    print("[right] true : 1;")
    print("endrewards")

    # Example storm-pomdp command with sample values
    goal_example = GRID_SIZE // 2  # Middle of the grid
    print(f"// storm-pomdp --prism grid.prism -const WIDTH={WIDTH},HEIGHT={HEIGHT},BUDGET={BUDGET},", end='')
    for i in range(1, BUDGET + 1):
        print(f"POS{i}=0,", end='')
    print(f"GOAL={goal_example}", end='')
    print(" --prop \"Rmin=?[F \\\"gameover\\\"]\" --buildfull --belief-exploration --exact --memorybound 1")

if __name__ == "__main__":
    main()
