from sympy import symbols, solve, simplify

# Define symbolic variables
pi0, pi1, pi2, pi3, p = symbols('pi0 pi1 pi2 pi3 p')
pi4, pi5, pi6, pi7, pi8, pi9 = symbols('pi4 pi5 pi6 pi7 pi8 pi9')
pi10, pi11, pi12, pi13, pi14 = symbols('pi10 pi11 pi12 pi13 pi14')

# Define the equations
eq1 = pi0 - (1 + p * pi0 + (1 - p) * pi1)
eq2 = pi1 - (1 + pi2)
eq3 = pi2 - (1 + p * pi1 + (1 - p) * pi3)
eq4 = pi3 - (1 + pi4)
eq5 = pi4 - (1 + p * pi3 + (1 - p) * pi5)
eq6 = pi5 - (1 + pi6)
eq7 = pi6 - (1 + pi7)
eq8 = pi7 - 0
eq9 = pi8 - (1 + p * pi7 + (1 - p) * pi9)
eq10 = pi9 - (1 + p * pi8 + (1 - p) * pi10)
eq11 = pi10 - (1 + p * pi9 + (1 - p) * pi11)
eq12 = pi11 - (1 + p * pi10 + (1 - p) * pi12)
eq13 = pi12 - (1 + p * pi11 + (1 - p) * pi13)
eq14 = pi13 - (1 + p * pi12 + (1 - p) * pi14)
eq15 = pi14 - (1 + p * pi13 + (1 - p) * pi14)

# Solve for pi0 and pi1 in terms of p and x
solution = solve(
    [eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8, eq9, eq10, eq11, eq12, eq13, eq14, eq15], 
    [pi0, pi1, pi2, pi3, pi4, pi5, pi6, pi7, pi8, pi9, pi10, pi11, pi12, pi13, pi14])

# Calculate the sum
sum_expr = simplify(
    solution[pi0] + solution[pi1] + solution[pi2] + solution[pi3] +
    solution[pi4] + solution[pi5] + solution[pi6] + solution[pi7] +
    solution[pi8] + solution[pi9] + solution[pi10] + solution[pi11] +
    solution[pi12] + solution[pi13] + solution[pi14]
)
print(f"\ntotal sum = {sum_expr}")