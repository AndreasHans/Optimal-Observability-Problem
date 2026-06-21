# World specific heuristics
In this section we develop heuristics that are specific to each world type: Line, Grid and Maze. We search for optimal solutions in small instances with goal of identifying patterns that we can then generalize and apply as heuristic to solve larger instances.

## Methodology
How we have done the experiment.

## Empirical observations

### Line

For the line we have observed the following:
* There is no solution with 0 sensors unless we have n/2+1 memory. In that case the agent goes one way until it will have hit the corner/goal, then it goes the other way.
* For B=1. The best way to place the sensor is at around state (m-2) until m=n/4 where the sensor is placed in the middle of one of the sides. The strategy is to go right/left until you would have hit the sensor and then go the other way if you did not hit the sensor.
* For B>1 it does not seem like the min exp rew can be improved by using more than memory 2. All sensors are placed evenly on the same side of the goal. The overall strategy is to go left until you hit a sensor, then go right.


Examples with Line(21):

B=1, M=2
```
+---+---+---+---+---+---+---+---+---+---+---+
| X |   |   |   |   |   |   |   |   |   | G |.. 
+---+---+---+---+---+---+---+---+---+---+---+
```

B=1, M=4
```
+---+---+---+---+---+---+---+---+---+---+---+
|   |   | X |   |   |   |   |   |   |   | G |.. 
+---+---+---+---+---+---+---+---+---+---+---+
```

B=1, M=6+
```
+---+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   | X |   |   |   |   |   | G |.. 
+---+---+---+---+---+---+---+---+---+---+---+
```

B=3, M=2+
```
+---+---+---+---+---+---+---+---+---+---+---+
| X |   |   | X |   |   | X |   |   |   | G |.. 
+---+---+---+---+---+---+---+---+---+---+---+
```

### Grid

For the grid we have observed the following:


Grid = Place on the last column or row. Dont place sensors next to each other. Place same amount of sensors on the row and column.

```
+---+---+---+---+---+
|   |   |   |   | 4 |
+---+---+---+---+---+
|   |   |   |   |   |
+---+---+---+---+---+
|   |   |   |   | 2 |
+---+---+---+---+---+
|   |   |   |   |   |
+---+---+---+---+---+
| 3 |   | 1 |   | G |
+---+---+---+---+---+
```


### Maze
Maze = Place starting from top left, go right, then down middle arm, then continue along the line. Then finally the two arms in some order.

## Conjectured patterns
Summarize the observed patterns into precise, testable conjectures for each world type. For each conjecture, state the world, the budget/memory regime, the claimed optimal placement rule, and the predicted minimum expected reward scaling.

## Heuristic design
Translate each conjecture into a concrete placement algorithm. For each world type, describe the heuristic as a step-by-step procedure that takes (n, B, M) as input and outputs a sensor placement. Include pseudocode where appropriate.

## Heuristic evaluation

### Experimental Setup
Describe the larger instances used to evaluate the heuristics, the baselines they are compared against (e.g., random placement, greedy), and the metrics reported (min expected reward, gap to optimal where known, runtime).

### Experimental Results
Present tables/figures comparing heuristic placement vs. baselines across instance sizes. Show how the gap between heuristic and optimal evolves as instances grow.

### Discussion
Analyze where each heuristic performs well and where it breaks down. Identify boundary cases or world sizes where the conjectured patterns no longer hold. Note open questions (e.g., grid and maze memory thresholds).

## Conclusion

