"""
Z3 Solving Result Data
=======================

Solving metrics & SMT model/reward for location tpMCs and POMDPs in the OOP framework.
"""

from typing import Optional
from dataclasses import dataclass

from z3 import CheckSatResult, ModelRef, ArithRef


@dataclass
class Z3SolverResult:
    """Results from solving a location tpMC/POMDP for OOP instances based on Z3 backend."""
    solve_time: float
    # setup_time: float
    # memory_used: int  # bytes
    result: CheckSatResult
    model: Optional[ModelRef] = None
    reward: Optional[float] = None
    reward_frac: Optional[ArithRef] = None
    obs: Optional[dict[str, int]] = None
    # constraint_count: int = 0
