
from z3 import *
import time

# Expected cost/reward of reaching the goal.
pi_s0_c1 = Real('pi_s0_c1')
pi_s1_c1 = Real('pi_s1_c1')
pi_s2_c1 = Real('pi_s2_c1')
pi_s3_c1 = Real('pi_s3_c1')
pi_s4_c1 = Real('pi_s4_c1')
pi_s5_c1 = Real('pi_s5_c1')
pi_s6_c1 = Real('pi_s6_c1')

pi_s0_c2 = Real('pi_s0_c2')
pi_s1_c2 = Real('pi_s1_c2')
pi_s2_c2 = Real('pi_s2_c2')
pi_s3_c2 = Real('pi_s3_c2')
pi_s4_c2 = Real('pi_s4_c2')
pi_s5_c2 = Real('pi_s5_c2')
pi_s6_c2 = Real('pi_s6_c2')

# Choice of observations
y_0 = Real('y_0')
y_1 = Real('y_1')
y_2 = Real('y_2')
y_3 = Real('y_3')
y_4 = Real('y_4')
y_5 = Real('y_5')
y_6 = Real('y_6')

# Rates of theta(c,o) -> a
x_c1_o0_l = Real('x_c1_o0_l')
x_c1_o0_r = Real('x_c1_o0_r')
x_c2_o0_l = Real('x_c2_o0_l')
x_c2_o0_r = Real('x_c2_o0_r')

x_c1_o1_l = Real('x_c1_o1_l')
x_c1_o1_r = Real('x_c1_o1_r')
x_c2_o1_l = Real('x_c2_o1_l')
x_c2_o1_r = Real('x_c2_o1_r')


x_c1_o2_l = Real('x_c1_o2_l')
x_c1_o2_r = Real('x_c1_o2_r')
x_c2_o2_l = Real('x_c2_o2_l')
x_c2_o2_r = Real('x_c2_o2_r')

x_c1_o4_l = Real('x_c1_o4_l')
x_c1_o4_r = Real('x_c1_o4_r')
x_c2_o4_l = Real('x_c2_o4_l')
x_c2_o4_r = Real('x_c2_o4_r')

x_c1_o5_l = Real('x_c1_o5_l')
x_c1_o5_r = Real('x_c1_o5_r')
x_c2_o5_l = Real('x_c2_o5_l')
x_c2_o5_r = Real('x_c2_o5_r')

x_c1_o6_l = Real('x_c1_o6_l')
x_c1_o6_r = Real('x_c1_o6_r')
x_c2_o6_l = Real('x_c2_o6_l')
x_c2_o6_r = Real('x_c2_o6_r')
    
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

x_c1_o2_l_c1 = Real('x_c1_o2_l_c1')
x_c1_o2_l_c2 = Real('x_c1_o2_l_c2')
x_c1_o2_r_c1 = Real('x_c1_o2_r_c1')
x_c1_o2_r_c2 = Real('x_c1_o2_r_c2')

x_c1_o4_l_c1 = Real('x_c1_o4_l_c1')
x_c1_o4_l_c2 = Real('x_c1_o4_l_c2')
x_c1_o4_r_c1 = Real('x_c1_o4_r_c1')
x_c1_o4_r_c2 = Real('x_c1_o4_r_c2')

x_c1_o5_l_c1 = Real('x_c1_o5_l_c1')
x_c1_o5_l_c2 = Real('x_c1_o5_l_c2')
x_c1_o5_r_c1 = Real('x_c1_o5_r_c1')
x_c1_o5_r_c2 = Real('x_c1_o5_r_c2')

x_c1_o6_l_c1 = Real('x_c1_o6_l_c1')
x_c1_o6_l_c2 = Real('x_c1_o6_l_c2')
x_c1_o6_r_c1 = Real('x_c1_o6_r_c1')
x_c1_o6_r_c2 = Real('x_c1_o6_r_c2')

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

x_c2_o2_l_c1 = Real('x_c2_o2_l_c1')
x_c2_o2_l_c2 = Real('x_c2_o2_l_c2')
x_c2_o2_r_c1 = Real('x_c2_o2_r_c1')
x_c2_o2_r_c2 = Real('x_c2_o2_r_c2')

x_c2_o4_l_c1 = Real('x_c2_o4_l_c1')
x_c2_o4_l_c2 = Real('x_c2_o4_l_c2')
x_c2_o4_r_c1 = Real('x_c2_o4_r_c1')
x_c2_o4_r_c2 = Real('x_c2_o4_r_c2')

x_c2_o5_l_c1 = Real('x_c2_o5_l_c1')
x_c2_o5_l_c2 = Real('x_c2_o5_l_c2')
x_c2_o5_r_c1 = Real('x_c2_o5_r_c1')
x_c2_o5_r_c2 = Real('x_c2_o5_r_c2')

x_c2_o6_l_c1 = Real('x_c2_o6_l_c1')
x_c2_o6_l_c2 = Real('x_c2_o6_l_c2')
x_c2_o6_r_c1 = Real('x_c2_o6_r_c1')
x_c2_o6_r_c2 = Real('x_c2_o6_r_c2')

x_c2_o_l_c1 = Real('x_c2_o_l_c1')
x_c2_o_l_c2 = Real('x_c2_o_l_c2')
x_c2_o_r_c1 = Real('x_c2_o_r_c1')
x_c2_o_r_c2 = Real('x_c2_o_r_c2')

solver = Solver()


solver.add(
#We cannot do better than the fully observable case
pi_s0_c1>=3, pi_s1_c1>=2, pi_s2_c1>=1, pi_s3_c1>=0, pi_s4_c1>=1, pi_s5_c1>=2, pi_s6_c1>=3, 
pi_s0_c2>=3, pi_s1_c2>=2, pi_s2_c2>=1, pi_s3_c2>=0, pi_s4_c2>=1, pi_s5_c2>=2, pi_s6_c2>=3,

# Expected cost/reward equations
pi_s0_c1 == (1 + pi_s0_c1) * (y_0 * x_c1_o0_l * x_c1_o0_l_c1 + (1 - y_0)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s0_c2) * (y_0 * x_c1_o0_l * x_c1_o0_l_c2 + (1 - y_0)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s1_c1) * (y_0 * x_c1_o0_r * x_c1_o0_r_c1 + (1 - y_0)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s1_c2) * (y_0 * x_c1_o0_r * x_c1_o0_r_c2 + (1 - y_0)*x_c1_o_r * x_c1_o_r_c2),

Or(
pi_s0_c2 == (1 + pi_s0_c1) * (y_0 * x_c2_o0_l * x_c2_o0_l_c1 + (1 - y_0)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s0_c2) * (y_0 * x_c2_o0_l * x_c2_o0_l_c2 + (1 - y_0)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s1_c1) * (y_0 * x_c2_o0_r * x_c2_o0_r_c1 + (1 - y_0)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s1_c2) * (y_0 * x_c2_o0_r * x_c2_o0_r_c2 + (1 - y_0)*x_c2_o_r * x_c2_o_r_c2),
pi_s0_c2 == 99999
),

pi_s1_c1 == (1 + pi_s0_c1) * (y_1 * x_c1_o1_l * x_c1_o1_l_c1 + (1 - y_1)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s0_c2) * (y_1 * x_c1_o1_l * x_c1_o1_l_c2 + (1 - y_1)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s2_c1) * (y_1 * x_c1_o1_r * x_c1_o1_r_c1 + (1 - y_1)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s2_c2) * (y_1 * x_c1_o1_r * x_c1_o1_r_c2 + (1 - y_1)*x_c1_o_r * x_c1_o_r_c2),


Or(
pi_s1_c2 == (1 + pi_s0_c1) * (y_1 * x_c2_o1_l * x_c2_o1_l_c1 + (1 - y_1)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s0_c2) * (y_1 * x_c2_o1_l * x_c2_o1_l_c2 + (1 - y_1)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s2_c1) * (y_1 * x_c2_o1_r * x_c2_o1_r_c1 + (1 - y_1)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s2_c2) * (y_1 * x_c2_o1_r * x_c2_o1_r_c2 + (1 - y_1)*x_c2_o_r * x_c2_o_r_c2),
pi_s1_c2 == 99999
),

		  
pi_s2_c1 == (1 + pi_s1_c1) * (y_2 * x_c1_o2_l * x_c1_o2_l_c1 + (1 - y_2)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s1_c2) * (y_2 * x_c1_o2_l * x_c1_o2_l_c2 + (1 - y_2)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s3_c1) * (y_2 * x_c1_o2_r * x_c1_o2_r_c1 + (1 - y_2)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s3_c2) * (y_2 * x_c1_o2_r * x_c1_o2_r_c2 + (1 - y_2)*x_c1_o_r * x_c1_o_r_c2),


Or(
pi_s2_c2 == (1 + pi_s1_c1) * (y_2 * x_c2_o2_l * x_c2_o2_l_c1 + (1 - y_2)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s1_c2) * (y_2 * x_c2_o2_l * x_c2_o2_l_c2 + (1 - y_2)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s3_c1) * (y_2 * x_c2_o2_r * x_c2_o2_r_c1 + (1 - y_2)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s3_c2) * (y_2 * x_c2_o2_r * x_c2_o2_r_c2 + (1 - y_2)*x_c2_o_r * x_c2_o_r_c2),
pi_s2_c2 == 99999

),

pi_s3_c1 == 0,
pi_s3_c2 == 0,

pi_s4_c1 == (1 + pi_s3_c1) * (y_4 * x_c1_o4_l * x_c1_o4_l_c1 + (1 - y_4)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s3_c2) * (y_4 * x_c1_o4_l * x_c1_o4_l_c2 + (1 - y_4)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s5_c1) * (y_4 * x_c1_o4_r * x_c1_o4_r_c1 + (1 - y_4)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s5_c2) * (y_4 * x_c1_o4_r * x_c1_o4_r_c2 + (1 - y_4)*x_c1_o_r * x_c1_o_r_c2),

Or(
pi_s4_c2 == (1 + pi_s3_c1) * (y_4 * x_c2_o4_l * x_c2_o4_l_c1 + (1 - y_4)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s3_c2) * (y_4 * x_c2_o4_l * x_c2_o4_l_c2 + (1 - y_4)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s5_c1) * (y_4 * x_c2_o4_r * x_c2_o4_r_c1 + (1 - y_4)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s5_c2) * (y_4 * x_c2_o4_r * x_c2_o4_r_c2 + (1 - y_4)*x_c2_o_r * x_c2_o_r_c2),
pi_s4_c2 == 99999
),

pi_s5_c1 == (1 + pi_s4_c1) * (y_5 * x_c1_o5_l * x_c1_o5_l_c1 + (1 - y_5)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s4_c2) * (y_5 * x_c1_o5_l * x_c1_o5_l_c2 + (1 - y_5)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s6_c1) * (y_5 * x_c1_o5_r * x_c1_o5_r_c1 + (1 - y_5)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s6_c2) * (y_5 * x_c1_o5_r * x_c1_o5_r_c2 + (1 - y_5)*x_c1_o_r * x_c1_o_r_c2),

Or(
pi_s5_c2 == (1 + pi_s4_c1) * (y_5 * x_c2_o5_l * x_c2_o5_l_c1 + (1 - y_5)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s4_c2) * (y_5 * x_c2_o5_l * x_c2_o5_l_c2 + (1 - y_5)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s6_c1) * (y_5 * x_c2_o5_r * x_c2_o5_r_c1 + (1 - y_5)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s6_c2) * (y_5 * x_c2_o5_r * x_c2_o5_r_c2 + (1 - y_5)*x_c2_o_r * x_c2_o_r_c2),
pi_s5_c2 == 99999
),

pi_s6_c1 == (1 + pi_s5_c1) * (y_6 * x_c1_o6_l * x_c1_o6_l_c1 + (1 - y_6)*x_c1_o_l * x_c1_o_l_c1) 
          + (1 + pi_s5_c2) * (y_6 * x_c1_o6_l * x_c1_o6_l_c2 + (1 - y_6)*x_c1_o_l * x_c1_o_l_c2)
          + (1 + pi_s6_c1) * (y_6 * x_c1_o6_r * x_c1_o6_r_c1 + (1 - y_6)*x_c1_o_r * x_c1_o_r_c1)
          + (1 + pi_s6_c2) * (y_6 * x_c1_o6_r * x_c1_o6_r_c2 + (1 - y_6)*x_c1_o_r * x_c1_o_r_c2),

Or(
pi_s6_c2 == (1 + pi_s5_c1) * (y_6 * x_c2_o6_l * x_c2_o6_l_c1 + (1 - y_6)*x_c2_o_l * x_c2_o_l_c1) 
          + (1 + pi_s5_c2) * (y_6 * x_c2_o6_l * x_c2_o6_l_c2 + (1 - y_6)*x_c2_o_l * x_c2_o_l_c2)
          + (1 + pi_s6_c1) * (y_6 * x_c2_o6_r * x_c2_o6_r_c1 + (1 - y_6)*x_c2_o_r * x_c2_o_r_c1)
          + (1 + pi_s6_c2) * (y_6 * x_c2_o6_r * x_c2_o6_r_c2 + (1 - y_6)*x_c2_o_r * x_c2_o_r_c2),
pi_s6_c2 == 99999
),


# We are dropped uniformly in the line
# We want to check if the minimal expected cost is below some threshold <= 2
(pi_s0_c1+pi_s1_c1+pi_s2_c1+pi_s4_c1+pi_s5_c1+pi_s6_c1) * Q(1,6) <= 3,


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

x_c1_o2_l <= 1,
x_c1_o2_l >= 0,
x_c1_o2_r <= 1,
x_c1_o2_r >= 0,
x_c1_o2_l + x_c1_o2_r == 1,

x_c1_o4_l <= 1,
x_c1_o4_l >= 0,
x_c1_o4_r <= 1,
x_c1_o4_r >= 0,
x_c1_o4_l + x_c1_o4_r == 1,

x_c1_o5_l <= 1,
x_c1_o5_l >= 0,
x_c1_o5_r <= 1,
x_c1_o5_r >= 0,
x_c1_o5_l + x_c1_o5_r == 1,

x_c1_o6_l <= 1,
x_c1_o6_l >= 0,
x_c1_o6_r <= 1,
x_c1_o6_r >= 0,
x_c1_o6_l + x_c1_o6_r == 1,

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

x_c2_o2_l <= 1,
x_c2_o2_l >= 0,
x_c2_o2_r <= 1,
x_c2_o2_r >= 0,
x_c2_o2_l + x_c2_o2_r == 1,

x_c2_o4_l <= 1,
x_c2_o4_l >= 0,
x_c2_o4_r <= 1,
x_c2_o4_r >= 0,
x_c2_o4_l + x_c2_o4_r == 1,

x_c2_o5_l <= 1,
x_c2_o5_l >= 0,
x_c2_o5_r <= 1,
x_c2_o5_r >= 0,
x_c2_o5_l + x_c2_o5_r == 1,

x_c2_o6_l <= 1,
x_c2_o6_l >= 0,
x_c2_o6_r <= 1,
x_c2_o6_r >= 0,
x_c2_o6_l + x_c2_o6_r == 1,

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

x_c1_o2_l_c1 <= 1,
x_c1_o2_l_c1 >= 0,
x_c1_o2_l_c2 <= 1,
x_c1_o2_l_c2 >= 0,
x_c1_o2_l_c1 + x_c1_o2_l_c2 == 1,

x_c1_o2_r_c1 <= 1,
x_c1_o2_r_c1 >= 0,
x_c1_o2_r_c2 <= 1,
x_c1_o2_r_c2 >= 0,
x_c1_o2_r_c1 + x_c1_o2_r_c2 == 1,

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

x_c1_o5_l_c1 <= 1,
x_c1_o5_l_c1 >= 0,
x_c1_o5_l_c2 <= 1,
x_c1_o5_l_c2 >= 0,
x_c1_o5_l_c1 + x_c1_o5_l_c2 == 1,

x_c1_o5_r_c1 <= 1,
x_c1_o5_r_c1 >= 0,
x_c1_o5_r_c2 <= 1,
x_c1_o5_r_c2 >= 0,
x_c1_o5_r_c1 + x_c1_o5_r_c2 == 1,

x_c1_o6_l_c1 <= 1,
x_c1_o6_l_c1 >= 0,
x_c1_o6_l_c2 <= 1,
x_c1_o6_l_c2 >= 0,
x_c1_o6_l_c1 + x_c1_o6_l_c2 == 1,

x_c1_o6_r_c1 <= 1,
x_c1_o6_r_c1 >= 0,
x_c1_o6_r_c2 <= 1,
x_c1_o6_r_c2 >= 0,
x_c1_o6_r_c1 + x_c1_o6_r_c2 == 1,

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

x_c2_o2_l_c1 <= 1,
x_c2_o2_l_c1 >= 0,
x_c2_o2_l_c2 <= 1,
x_c2_o2_l_c2 >= 0,
x_c2_o2_l_c1 + x_c2_o2_l_c2 == 1,

x_c2_o2_r_c1 <= 1,
x_c2_o2_r_c1 >= 0,
x_c2_o2_r_c2 <= 1,
x_c2_o2_r_c2 >= 0,
x_c2_o2_r_c1 + x_c2_o2_r_c2 == 1,

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

x_c2_o5_l_c1 <= 1,
x_c2_o5_l_c1 >= 0,
x_c2_o5_l_c2 <= 1,
x_c2_o5_l_c2 >= 0,
x_c2_o5_l_c1 + x_c2_o5_l_c2 == 1,

x_c2_o5_r_c1 <= 1,
x_c2_o5_r_c1 >= 0,
x_c2_o5_r_c2 <= 1,
x_c2_o5_r_c2 >= 0,
x_c2_o5_r_c1 + x_c2_o5_r_c2 == 1,

x_c2_o6_l_c1 <= 1,
x_c2_o6_l_c1 >= 0,
x_c2_o6_l_c2 <= 1,
x_c2_o6_l_c2 >= 0,
x_c2_o6_l_c1 + x_c2_o6_l_c2 == 1,

x_c2_o6_r_c1 <= 1,
x_c2_o6_r_c1 >= 0,
x_c2_o6_r_c2 <= 1,
x_c2_o6_r_c2 >= 0,
x_c2_o6_r_c1 + x_c2_o6_r_c2 == 1,

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
Or (y_0 == 0 , y_0 == 1 ),
Or (y_1 == 0 , y_1 == 1 ),
Or (y_2 == 0 , y_2 == 1 ),
Or (y_4 == 0 , y_4 == 1 ),
Or (y_5 == 0 , y_5 == 1 ),
Or (y_6 == 0 , y_6 == 1 ),

y_0 + y_1 + y_2 + y_4 + y_5 + y_6 == 1
)

cpu_start = time.process_time()
result = solver.check()
cpu_end = time.process_time()
solve_time = cpu_end - cpu_start

print("Time:",solve_time, "s")
file_solver = open("solver.txt", "w")
file_solver.write(str(solver.sexpr()))
file_solver.close()

if result == sat:
    m = solver.model()
    print('This is a solution:')
    print(m)
elif result == unsat:
    print('No solution!!!')
else:
    print('Unknown')