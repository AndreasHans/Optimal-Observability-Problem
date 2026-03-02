from z3 import *

# Expected cost/reward of reaching the goal.
pi_s0_c1 = Real('pi_s0_c1')
pi_s1_c1 = Real('pi_s1_c1')
pi_s2_c1 = Real('pi_s2_c1')
pi_s3_c1 = Real('pi_s3_c1')
pi_s4_c1 = Real('pi_s4_c1')

pi_s0_c2 = Real('pi_s0_c2')
pi_s1_c2 = Real('pi_s1_c2')
pi_s2_c2 = Real('pi_s2_c2')
pi_s3_c2 = Real('pi_s3_c2')
pi_s4_c2 = Real('pi_s4_c2')


# Choice of observations
y0 = Real('y0')
y1 = Real('y1')
y2 = Real('y2')
y3 = Real('y3')
y4 = Real('y4')

# Rates of theta(c,o) -> a
x_c1_o0_l = Real('x_c1_o0_l')
x_c1_o0_r = Real('x_c1_o0_r')
x_c2_o0_l = Real('x_c2_o0_l')
x_c2_o0_r = Real('x_c2_o0_r')

x_c1_o1_l = Real('x_c1_o1_l')
x_c1_o1_r = Real('x_c1_o1_r')
x_c2_o1_l = Real('x_c2_o1_l')
x_c2_o1_r = Real('x_c2_o1_r')

x_c1_o3_l = Real('x_c1_o3_l')
x_c1_o3_r = Real('x_c1_o3_r')
x_c2_o3_l = Real('x_c2_o3_l')
x_c2_o3_r = Real('x_c2_o3_r')

x_c1_o4_l = Real('x_c1_o4_l')
x_c1_o4_r = Real('x_c1_o4_r')
x_c2_o4_l = Real('x_c2_o4_l')
x_c2_o4_r = Real('x_c2_o4_r')

x_c1_o_l = Real('x_c1_o_l')
x_c1_o_r = Real('x_c1_o_r')
x_c2_o_l = Real('x_c2_o_l')
x_c2_o_r = Real('x_c2_o_r')

# Rates of delta(c,o,a) -> c'
x_c1_o0_l_c1 = Real('x_c1_o0_l_c1')
x_c1_o0_l_c2 = Real('x_c1_o0_l_c2')
x_c1_o0_r_c1 = Real('x_c1_o0_r_c1')
x_c1_o0_r_c2 = Real('x_c1_o0_r_c2')

x_c1_o1_l_c1 = Real('x_c1_o1_l_c1')
x_c1_o1_l_c2 = Real('x_c1_o1_l_c2')
x_c1_o1_r_c1 = Real('x_c1_o1_r_c1')
x_c1_o1_r_c2 = Real('x_c1_o1_r_c2')

x_c1_o3_l_c1 = Real('x_c1_o3_l_c1')
x_c1_o3_l_c2 = Real('x_c1_o3_l_c2')
x_c1_o3_r_c1 = Real('x_c1_o3_r_c1')
x_c1_o3_r_c2 = Real('x_c1_o3_r_c2')

x_c1_o4_l_c1 = Real('x_c1_o4_l_c1')
x_c1_o4_l_c2 = Real('x_c1_o4_l_c2')
x_c1_o4_r_c1 = Real('x_c1_o4_r_c1')
x_c1_o4_r_c2 = Real('x_c1_o4_r_c2')

x_c1_o_l_c1 = Real('x_c1_o_l_c1')
x_c1_o_l_c2 = Real('x_c1_o_l_c2')
x_c1_o_r_c1 = Real('x_c1_o_r_c1')
x_c1_o_r_c2 = Real('x_c1_o_r_c2')

x_c2_o0_l_c1 = Real('x_c2_o0_l_c1')
x_c2_o0_l_c2 = Real('x_c2_o0_l_c2')
x_c2_o0_r_c1 = Real('x_c2_o0_r_c1')
x_c2_o0_r_c2 = Real('x_c2_o0_r_c2')

x_c2_o1_l_c1 = Real('x_c2_o1_l_c1')
x_c2_o1_l_c2 = Real('x_c2_o1_l_c2')
x_c2_o1_r_c1 = Real('x_c2_o1_r_c1')
x_c2_o1_r_c2 = Real('x_c2_o1_r_c2')

x_c2_o3_l_c1 = Real('x_c2_o3_l_c1')
x_c2_o3_l_c2 = Real('x_c2_o3_l_c2')
x_c2_o3_r_c1 = Real('x_c2_o3_r_c1')
x_c2_o3_r_c2 = Real('x_c2_o3_r_c2')

x_c2_o4_l_c1 = Real('x_c2_o4_l_c1')
x_c2_o4_l_c2 = Real('x_c2_o4_l_c2')
x_c2_o4_r_c1 = Real('x_c2_o4_r_c1')
x_c2_o4_r_c2 = Real('x_c2_o4_r_c2')

x_c2_o_l_c1 = Real('x_c2_o_l_c1')
x_c2_o_l_c2 = Real('x_c2_o_l_c2')
x_c2_o_r_c1 = Real('x_c2_o_r_c1')
x_c2_o_r_c2 = Real('x_c2_o_r_c2')

solver = Solver()


solver.add(
#We cannot do better than the fully observable case
pi_s0_c1>=2, pi_s1_c1>=1, pi_s2_c1>=0, pi_s3_c1>=1, pi_s4_c1>=2, 
pi_s0_c2>=2, pi_s1_c2>=1, pi_s2_c2>=0, pi_s3_c2>=1, pi_s4_c2>=2,

# Expected cost/reward equations
#pi0 == (1 + pi0) * (y0*xo0l + (1 - y0)*xol) 
#     + (1 + pi1) * (y0*xo0r + (1 - y0)*xor), 

pi_s0_c1 == (1 + pi_s0_c1) * (y0 * x_c1_o0_l * x_c1_o0_l_c1 + (1 - y0)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s0_c2) * (y0 * x_c1_o0_l * x_c1_o0_l_c2 + (1 - y0)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s1_c1) * (y0 * x_c1_o0_r * x_c1_o0_r_c1 + (1 - y0)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s1_c2) * (y0 * x_c1_o0_r * x_c1_o0_r_c2 + (1 - y0)*x_c1_o_r * x_c1_o_r_c2),

pi_s0_c2 == (1 + pi_s0_c1) * (y0 * x_c2_o0_l * x_c2_o0_l_c1 + (1 - y0)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s0_c2) * (y0 * x_c2_o0_l * x_c2_o0_l_c2 + (1 - y0)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s1_c1) * (y0 * x_c2_o0_r * x_c2_o0_r_c1 + (1 - y0)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s1_c2) * (y0 * x_c2_o0_r * x_c2_o0_r_c2 + (1 - y0)*x_c2_o_r * x_c2_o_r_c2),

pi_s1_c1 == (1 + pi_s0_c1) * (y1 * x_c1_o1_l * x_c1_o1_l_c1 + (1 - y1)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s0_c2) * (y1 * x_c1_o1_l * x_c1_o1_l_c2 + (1 - y1)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s2_c1) * (y1 * x_c1_o1_r * x_c1_o1_r_c1 + (1 - y1)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s2_c2) * (y1 * x_c1_o1_r * x_c1_o1_r_c2 + (1 - y1)*x_c1_o_r * x_c1_o_r_c2),

pi_s1_c2 == (1 + pi_s0_c1) * (y1 * x_c2_o1_l * x_c2_o1_l_c1 + (1 - y1)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s0_c2) * (y1 * x_c2_o1_l * x_c2_o1_l_c2 + (1 - y1)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s2_c1) * (y1 * x_c2_o1_r * x_c2_o1_r_c1 + (1 - y1)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s2_c2) * (y1 * x_c2_o1_r * x_c2_o1_r_c2 + (1 - y1)*x_c2_o_r * x_c2_o_r_c2),

pi_s2_c1 == 0,
pi_s2_c2 == 0,

pi_s3_c1 == (1 + pi_s2_c1) * (y3 * x_c1_o3_l * x_c1_o3_l_c1 + (1 - y3)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s2_c2) * (y3 * x_c1_o3_l * x_c1_o3_l_c2 + (1 - y3)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s4_c1) * (y3 * x_c1_o3_r * x_c1_o3_r_c1 + (1 - y3)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s4_c2) * (y3 * x_c1_o3_r * x_c1_o3_r_c2 + (1 - y3)*x_c1_o_r * x_c1_o_r_c2),

pi_s3_c2 == (1 + pi_s2_c1) * (y3 * x_c2_o3_l * x_c2_o3_l_c1 + (1 - y3)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s2_c2) * (y3 * x_c2_o3_l * x_c2_o3_l_c2 + (1 - y3)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s4_c1) * (y3 * x_c2_o3_r * x_c2_o3_r_c1 + (1 - y3)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s4_c2) * (y3 * x_c2_o3_r * x_c2_o3_r_c2 + (1 - y3)*x_c2_o_r * x_c2_o_r_c2),

pi_s4_c1 == (1 + pi_s3_c1) * (y4 * x_c1_o4_l * x_c1_o4_l_c1 + (1 - y4)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s3_c2) * (y4 * x_c1_o4_l * x_c1_o4_l_c2 + (1 - y4)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s4_c1) * (y4 * x_c1_o4_r * x_c1_o4_r_c1 + (1 - y4)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s4_c2) * (y4 * x_c1_o4_r * x_c1_o4_r_c2 + (1 - y4)*x_c1_o_r * x_c1_o_r_c2),

pi_s4_c2 == (1 + pi_s3_c1) * (y4 * x_c2_o4_l * x_c2_o4_l_c1 + (1 - y4)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s3_c2) * (y4 * x_c2_o4_l * x_c2_o4_l_c2 + (1 - y4)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s4_c1) * (y4 * x_c2_o4_r * x_c2_o4_r_c1 + (1 - y4)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s4_c2) * (y4 * x_c2_o4_r * x_c2_o4_r_c2 + (1 - y4)*x_c2_o_r * x_c2_o_r_c2),

# We are dropped uniformly in the line
# We want to check if the minimal expected cost is below some threshold <= 2
(pi_s0_c1+pi_s1_c1+pi_s3_c1+pi_s4_c1) * Q(1,4) <= 2,


# Randomised strategies (proper probability distributions)

# theta(c,o) -> a

x_c1_o0_l <= 1,
x_c1_o0_l >= 0,
x_c1_o0_r <= 1,
x_c1_o0_r >= 0,
x_c1_o0_l + x_c1_o0_r == 1,

x_c1_o1_l <= 1,
x_c1_o1_l >= 0,
x_c1_o1_r <= 1,
x_c1_o1_r >= 0,
x_c1_o1_l + x_c1_o1_r == 1,

x_c1_o3_l <= 1,
x_c1_o3_l >= 0,
x_c1_o3_r <= 1,
x_c1_o3_r >= 0,
x_c1_o3_l + x_c1_o3_r == 1,

x_c1_o4_l <= 1,
x_c1_o4_l >= 0,
x_c1_o4_r <= 1,
x_c1_o4_r >= 0,
x_c1_o4_l + x_c1_o4_r == 1,

x_c1_o_l <= 1,
x_c1_o_l >= 0,
x_c1_o_r <= 1,
x_c1_o_r >= 0,
x_c1_o_l + x_c1_o_r == 1,

x_c2_o0_l <= 1,
x_c2_o0_l >= 0,
x_c2_o0_r <= 1,
x_c2_o0_r >= 0,
x_c2_o0_l + x_c2_o0_r == 1,

x_c2_o1_l <= 1,
x_c2_o1_l >= 0,
x_c2_o1_r <= 1,
x_c2_o1_r >= 0,
x_c2_o1_l + x_c2_o1_r == 1,

x_c2_o3_l <= 1,
x_c2_o3_l >= 0,
x_c2_o3_r <= 1,
x_c2_o3_r >= 0,
x_c2_o3_l + x_c2_o3_r == 1,

x_c2_o4_l <= 1,
x_c2_o4_l >= 0,
x_c2_o4_r <= 1,
x_c2_o4_r >= 0,
x_c2_o4_l + x_c2_o4_r == 1,

x_c2_o_l <= 1,
x_c2_o_l >= 0,
x_c2_o_r <= 1,
x_c2_o_r >= 0,
x_c2_o_l + x_c2_o_r == 1,


# delta(c,o,a) -> c'
x_c1_o0_l_c1 <= 1,
x_c1_o0_l_c1 >= 0,
x_c1_o0_l_c2 <= 1,
x_c1_o0_l_c2 >= 0,
x_c1_o0_l_c1 + x_c1_o0_l_c2 == 1,

x_c1_o0_r_c1 <= 1,
x_c1_o0_r_c1 >= 0,
x_c1_o0_r_c2 <= 1,
x_c1_o0_r_c2 >= 0,
x_c1_o0_r_c1 + x_c1_o0_r_c2 == 1,

x_c1_o1_l_c1 <= 1,
x_c1_o1_l_c1 >= 0,
x_c1_o1_l_c2 <= 1,
x_c1_o1_l_c2 >= 0,
x_c1_o1_l_c1 + x_c1_o1_l_c2 == 1,

x_c1_o1_r_c1 <= 1,
x_c1_o1_r_c1 >= 0,
x_c1_o1_r_c2 <= 1,
x_c1_o1_r_c2 >= 0,
x_c1_o1_r_c1 + x_c1_o1_r_c2 == 1,

x_c1_o3_l_c1 <= 1,
x_c1_o3_l_c1 >= 0,
x_c1_o3_l_c2 <= 1,
x_c1_o3_l_c2 >= 0,
x_c1_o3_l_c1 + x_c1_o3_l_c2 == 1,

x_c1_o3_r_c1 <= 1,
x_c1_o3_r_c1 >= 0,
x_c1_o3_r_c2 <= 1,
x_c1_o3_r_c2 >= 0,
x_c1_o3_r_c1 + x_c1_o3_r_c2 == 1,

x_c1_o4_l_c1 <= 1,
x_c1_o4_l_c1 >= 0,
x_c1_o4_l_c2 <= 1,
x_c1_o4_l_c2 >= 0,
x_c1_o4_l_c1 + x_c1_o4_l_c2 == 1,

x_c1_o4_r_c1 <= 1,
x_c1_o4_r_c1 >= 0,
x_c1_o4_r_c2 <= 1,
x_c1_o4_r_c2 >= 0,
x_c1_o4_r_c1 + x_c1_o4_r_c2 == 1,

x_c1_o_l_c1 <= 1,
x_c1_o_l_c1 >= 0,
x_c1_o_l_c2 <= 1,
x_c1_o_l_c2 >= 0,
x_c1_o_l_c1 + x_c1_o_l_c2 == 1,

x_c1_o_r_c1 <= 1,
x_c1_o_r_c1 >= 0,
x_c1_o_r_c2 <= 1,
x_c1_o_r_c2 >= 0,
x_c1_o_r_c1 + x_c1_o_r_c2 == 1,

x_c2_o0_l_c1 <= 1,
x_c2_o0_l_c1 >= 0,
x_c2_o0_l_c2 <= 1,
x_c2_o0_l_c2 >= 0,
x_c2_o0_l_c1 + x_c2_o0_l_c2 == 1,

x_c2_o0_r_c1 <= 1,
x_c2_o0_r_c1 >= 0,
x_c2_o0_r_c2 <= 1,
x_c2_o0_r_c2 >= 0,
x_c2_o0_r_c1 + x_c2_o0_r_c2 == 1,

x_c2_o1_l_c1 <= 1,
x_c2_o1_l_c1 >= 0,
x_c2_o1_l_c2 <= 1,
x_c2_o1_l_c2 >= 0,
x_c2_o1_l_c1 + x_c2_o1_l_c2 == 1,

x_c2_o1_r_c1 <= 1,
x_c2_o1_r_c1 >= 0,
x_c2_o1_r_c2 <= 1,
x_c2_o1_r_c2 >= 0,
x_c2_o1_r_c1 + x_c2_o1_r_c2 == 1,

x_c2_o3_l_c1 <= 1,
x_c2_o3_l_c1 >= 0,
x_c2_o3_l_c2 <= 1,
x_c2_o3_l_c2 >= 0,
x_c2_o3_l_c1 + x_c2_o3_l_c2 == 1,

x_c2_o3_r_c1 <= 1,
x_c2_o3_r_c1 >= 0,
x_c2_o3_r_c2 <= 1,
x_c2_o3_r_c2 >= 0,
x_c2_o3_r_c1 + x_c2_o3_r_c2 == 1,

x_c2_o4_l_c1 <= 1,
x_c2_o4_l_c1 >= 0,
x_c2_o4_l_c2 <= 1,
x_c2_o4_l_c2 >= 0,
x_c2_o4_l_c1 + x_c2_o4_l_c2 == 1,

x_c2_o4_r_c1 <= 1,
x_c2_o4_r_c1 >= 0,
x_c2_o4_r_c2 <= 1,
x_c2_o4_r_c2 >= 0,
x_c2_o4_r_c1 + x_c2_o4_r_c2 == 1,

x_c2_o_l_c1 <= 1,
x_c2_o_l_c1 >= 0,
x_c2_o_l_c2 <= 1,
x_c2_o_l_c2 >= 0,
x_c2_o_l_c1 + x_c2_o_l_c2 == 1,

x_c2_o_r_c1 <= 1,
x_c2_o_r_c1 >= 0,
x_c2_o_r_c2 <= 1,
x_c2_o_r_c2 >= 0,
x_c2_o_r_c1 + x_c2_o_r_c2 == 1,


# y is a function that should map every state N to some observable class M
Or (y0 == 0 , y0 == 1 ),
Or (y1 == 0 , y1 == 1 ),
Or (y3 == 0 , y3 == 1 ),
Or (y4 == 0 , y4 == 1 ),
y0 + y1 + y3 + y4 == 1
)


if solver.check() == sat:
	m = solver.model()
	print('This is a solution:')
	print(m)
elif solver.check() == unsat:
	print('No solution!!!')
else:
	print('Unknown')