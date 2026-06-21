from previous_work.dynamic_solvers.builders.worlds import World


def main(world: World, goal_state: int) -> None:
    distances = 0
    for state in range(world.size):
        if state == goal_state:
            continue
        distances += world.dist(state, goal_state)
    exp_rew = distances / (world.size - 1)
    print(f"World size: {world.size} | Total distances: {distances}")
    print(f"MDP Expected reward: {exp_rew}")
    print(f"MDP Goal: {goal_state}")
    print(f"Q({distances},{world.size - 1})")


if __name__ == "__main__":
    import sys
    from previous_work.dynamic_solvers.builders.worlds import Line, Grid, Maze

    try:
        world_type = sys.argv[1]

        if world_type == "line":
            length = int(sys.argv[2])
            if len(sys.argv) > 3:
                goal_state = int(sys.argv[3])
            else:
                goal_state = length//2
            world = Line(length=length, goal=goal_state)
        elif world_type == "grid":
            width, height = map(int, sys.argv[2:4])
            if len(sys.argv) > 4:
                goal_state = int(sys.argv[4])
            else:
                goal_state = (width**2 - 1)//2
            world = Grid(width=width, height=height, goal=goal_state)
        elif world_type == "maze":
            width, depth = map(int, sys.argv[2:4])
            if len(sys.argv) > 4:
                goal_state = int(sys.argv[4])
            else:
                goal_state = width + 1 + 3*((depth - 2)//2)
            world = Maze(width=width, depth=depth, goal=goal_state)
        else:
            raise ValueError(f"Unknown world type: {world_type}")
        main(world, goal_state)
    except Exception as e:
        print(f"Error creating world: {e}")
        print("\nUsage: python generate_world.py <world_type> <dimensions> [goal_state?]\n"
              "where <dimensions> are the dimensions of the world:\n"
              "- for line: <length>\n"
              "- for grid: <width> <height>\n"
              "- for maze: <width> <height>\n"
              "and [goal_state?] is an optional goal state index (default is center state).")
