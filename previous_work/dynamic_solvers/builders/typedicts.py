"""Type definitions for TPMC parameter passing.

This module contains TypedDict definitions used across the TPMC factory and leaf-instance constructors.

External API (TPMCParams): Accepts strings from CLI
Internal API (OperationKWArgs): Uses enums after Factory conversion
"""

from typing import TypedDict, Optional, Required, NotRequired, List, Literal
from z3 import Context

from previous_work.dynamic_solvers.builders.enums import BellmanFormat, Precision


class DimensionKWArgs(TypedDict, total=False):
    """World dimension parameters as kwargs to World constructors.

    Attributes:
        length (int): Length of the world (Line).
        width (int): Width of the world (Grid/Maze).
        height (int): Height of the world (Grid, mapped to 'depth' for Maze internally).
        depth (int): Depth of the world (Maze, mapped from 'height' for Maze internally).
    """
    length: Optional[int]
    width: Optional[int]
    height: Optional[int]
    depth: Optional[int]


class OperationKWArgs(TypedDict, total=False):
    """Internal operational parameters passed to instance constructors as kwargs.
    These parameters control solver behavior and output, not problem definition.

    Attributes:
        ctx (Optional[Context]): Z3 context to use (default: None, creates fresh context).
        verbose (bool): Enable verbose output (default: False).
        bellman_format (Optional[BellmanFormat]): Format for Bellman equations (enum)
        precision (Optional[Precision]): Constraint precision mode (enum)
        bool_encoding (Optional[bool]): Activate boolean encoding (`bitblast`) rather than real encoding
        order_constraints (Optional[List[int]]): Order of assertion of constraints for TPMC solver.
    """
    ctx: Optional[Context]
    verbose: bool
    bellman_format: Optional[BellmanFormat]
    precision: Optional[Precision]
    bool_encoding: Optional[bool]
    order_constraints: Optional[List[int]]
    budget_repair: bool


class ExtOperationParams(TypedDict, total=False):
    """External operational parameters accepted by Factory API.
    String types are converted to enums by the Factory.

    Attributes:
        ctx (Optional[Context]): Z3 context to use (default: None, creates fresh context).
        verbose (bool): Enable verbose output (default: False).
        bellman_format (str): Format for Bellman equations ('default', 'common', 'adapted')
        precision (str): Constraint precision mode ('strict', 'relaxed')
        bool_encoding (Optional[bool]): Activate boolean encoding (`bitblast`) rather than real encoding
        order_constraints (Optional[List[int]]): Order of assertion of constraints for TPMC solver
        cluster: (Optional[bool]): Whether to use a clustering algorithm as the solver (only applicable to POP instances)
    """
    ctx: Optional[Context]
    verbose: bool
    bellman_format: Optional[Literal['default', 'common', 'adapted']]
    precision: Optional[Literal['strict', 'relaxed']]
    bool_encoding: Optional[bool]
    order_constraints: Optional[List[int]]
    cluster: Optional[bool]
    budget_repair: bool


class TPMCParams(DimensionKWArgs, ExtOperationParams):
    """Combined external kwargs set for TPMC factory (dimensions + operations + core).
    This is the public API to the builders - accepts strings from CLI.

    Attributes:
        budget (int): Budget constraint (number of observation classes allowed).
        goal (int): Goal state index.
        determinism (bool): Restrict to deterministic strategies (default: False).
    """
    # Core (mandatory) problem settings
    budget: Required[int]
    goal: Required[int]
    determinism: NotRequired[bool] # Can be inferred as False if missing
