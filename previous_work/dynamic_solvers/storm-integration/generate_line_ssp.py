import sys

#!/usr/bin/env python3

def main():
    # Usage: python generate.py N
    N = int(sys.argv[1]) if len(sys.argv) > 1 else -1
    if N <= 2:
        raise SystemExit("N must be >= 3")
    B = int(sys.argv[2]) if len(sys.argv) > 1 else -1
    if B < 0 or B >= N:
        raise SystemExit("B must be between 0 and N-1")

    print("pomdp\n")
    print("const LENGTH;")
    print("const GOAL;")
    print("const BUDGET;\n")

    # Define observation position constants
    for x in range(1, B+1):
        print(f"const POS{x};");

    # Observable declarations
    print("observable \"goal\" = (position=GOAL);")
    print("observable \"started\" = (started);\n")
    for x in range(1, B+1):
        print(f"observable \"flag{x}\" = (({x}<=BUDGET)?(position=POS{x}):false);");

    print("\nmodule LINE\n")

    print("chosen : bool init false;")
    print("started : bool init false;")
    print("position : [0..LENGTH-1];")

    # Uniform distribution of initial position across non-goal states
    print("\n[start] !chosen -> ")
    print(f"  ((0>=LENGTH | GOAL=0)?0:1)/(LENGTH-1):(started'=0<LENGTH)&(position'=(0<LENGTH?0:GOAL))&(chosen'=true)")
    for x in range(1, N):
        print(f"+ (({x}>=LENGTH | GOAL={x})?0:1)/(LENGTH-1):(started'={x}<LENGTH)&(position'=({x}<LENGTH?{x}:GOAL))&(chosen'=true)")
    print(";\n")

    # Navigation actions with boundary checks
    print("[left]  started -> 1.0:(position'=max(0,position-1));")
    print("[right] started -> 1.0:(position'=min(LENGTH-1,position+1));")
    print("[stop] (position = GOAL) -> true;")
    print("endmodule\n")

    # Goal label
    print("label \"gameover\" = (position=GOAL);\n")

    # Rewards for each action
    print("rewards")
    print("[left] true : 1 ;")
    print("[right] true : 1 ;")
    print("endrewards\n")

    print(f"// storm-pomdp -const LENGTH=7,BUDGET=3,", end='')
    for x in range(1, B+1):
        print(f"POS{x}=0,", end='')
    print("GOAL=3", end='')
    print(" --prism line.prism --prop \"Rmin=?[F \\\"gameover\\\"]\" --buildfull --belief-exploration --exact --memorybound 1", end='')
    print()
if __name__ == "__main__":
    main()
