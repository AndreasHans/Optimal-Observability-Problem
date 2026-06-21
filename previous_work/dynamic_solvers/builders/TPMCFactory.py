from typing import Unpack

import previous_work.dynamic_solvers.builders.pop as pop
import previous_work.dynamic_solvers.builders.ssp as ssp
from previous_work.dynamic_solvers.builders.OOPSpec import OOPSpec
from previous_work.dynamic_solvers.builders.enums import OOPVariant, PuzzleType, BellmanFormat, Precision
from previous_work.dynamic_solvers.builders.ssp.SSPSpec import SSPSpec
from previous_work.dynamic_solvers.builders.pop.POPSpec import POPSpec
from previous_work.dynamic_solvers.builders.typedicts import DimensionKWArgs, OperationKWArgs, TPMCParams


class TPMCFactory:
    """Factory for creating dynamic TPMC problem instances with context builders.
    The creational method accepts keyword arguments declared by `TPMCParams`."""

    @staticmethod
    def create(oop_variant: str, puzzle_type: str, **kwargs: Unpack[TPMCParams]) -> SSPSpec | POPSpec:
        """
        Factory method that handles parameter selection and object creation based on variant and world.
        Client only needs to pass all available parameters; factory filters what's needed.

        This is the public API boundary - accepts strings from CLI and converts to internal enum types.

        Uses **kwargs pattern for flexible parameter passing without explicit listing.
        Type-safety is ensured by modern typed-dictionary unpacking.

        Args:
            oop_variant (str): Selected OOP variant ('ssp', 'pop')
            puzzle_type (str): Selected puzzle type ('line', 'grid', 'maze')
            **kwargs (Unpacked[TPMCParams]): Additional parameters declared by TypedDict `TPMCParams`

        Keyword Args:
            Core Problem Settings:
                budget (int): Budget constraint (number of observation classes allowed).
                goal (int): Goal state index.
                determinism (bool): Restrict to deterministic strategies (default: False).

            World-specific Dimension Parameters:
                length (int): Length of the world (Line).
                width (int): Width of the world (Grid/Maze).
                height (int): Height of the world (Grid) or Depth of the world (Maze).
                depth (int): Depth of the world (Maze) [internally mapped from `height`].

            Operational Parameters:
                ctx (Optional[Context]): Z3 context to use (default: None, creates fresh context).
                verbose (bool): Enable verbose output (default: False).
                bellman_format (str): Format for Bellman equations ('default', 'common', 'adapted')
                precision (str): Constraint precision for optimality ('strict', 'relaxed')
                bool_encoding (bool): Use boolean encoding instead of real encoding
                order_constraints (List[int]): Order of constraint assertion

        Returns:
            OOPSpec : configured instance specification for OOP
        """
        # Convert string parameters to enums at Factory boundary
        oop_variant = OOPVariant.from_string(oop_variant)
        puzzle_type = PuzzleType.from_string(puzzle_type)

        op_params = TPMCFactory._extract_operation_params(**kwargs)
        dim_params = TPMCFactory._extract_dimension_params(puzzle_type, kwargs)

        # Dispatch to the appropriate constructor based on problem variant and then puzzle type
        constructors = {
            OOPVariant.POP: {
                PuzzleType.LINE: pop.LineTPMC,
                PuzzleType.GRID: pop.GridTPMC,
                PuzzleType.MAZE: pop.MazeTPMC,
            },
            OOPVariant.SSP: {
                PuzzleType.LINE: ssp.LineTPMC,
                PuzzleType.GRID: ssp.GridTPMC,
                PuzzleType.MAZE: ssp.MazeTPMC,
            },
        }
        return constructors[oop_variant][puzzle_type](
            # Explicit parameter passing for core settings
            budget=kwargs["budget"],
            goal=kwargs["goal"],
            determinism=kwargs.get("determinism", False),
            **dim_params,
            **op_params,
        )

    @staticmethod
    def _extract_operation_params(**kwargs: TPMCParams) -> OperationKWArgs:
        """Extract operational parameters common to all constructors.
        Converts string parameters to enums at the Factory boundary.

        Args:
            **kwargs: External parameters (strings from CLI)

        Returns:
            Internal parameters (enums for constructors)
        """
        res: OperationKWArgs = {}
        op_params = set(OperationKWArgs.__annotations__.keys())
        res.update({key: kwargs[key] for key in op_params if key in kwargs})

        # Convert string parameters to enums
        if 'bellman_format' in kwargs and kwargs['bellman_format'] is not None:
            res['bellman_format'] = BellmanFormat.from_string(str(kwargs['bellman_format']))

        if 'precision' in kwargs and kwargs['precision'] is not None:
            res['precision'] = Precision.from_string(str(kwargs['precision']))

        return res

    @staticmethod
    def _extract_dimension_params(puzzle_type: PuzzleType, kwargs: TPMCParams) -> DimensionKWArgs:
        """Extract dimension-specific parameters based on world type.

        Args:
            puzzle_type: Puzzle type enum (already converted from string)
            kwargs: External parameters

        Returns:
            Dimension parameters for the specific world type
        """
        if puzzle_type == PuzzleType.LINE:
            return {'length': kwargs['length']}
        elif puzzle_type == PuzzleType.GRID:
            return {'width': kwargs['width'], 'height': kwargs['height']}
        else:  # PuzzleType.MAZE
            # Maze uses 'depth' internally instead of 'height'
            return {'width': kwargs['width'], 'depth': kwargs['height']}
