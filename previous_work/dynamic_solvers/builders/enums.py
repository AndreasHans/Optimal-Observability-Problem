from enum import Enum, auto


class OOPVariant(Enum):
    """OOP problem variant types."""
    POP = auto(),
    SSP = auto()

    @classmethod
    def from_string(cls, s: str) -> 'OOPVariant':
        """Convert string argument to OOPVariant enum.

        Args:
            s: String representation ('ssp', 'pop')

        Returns:
            Corresponding OOPVariant enum value

        Raises:
            ValueError: If string doesn't match any variant
        """
        mapping = {
            'ssp': cls.SSP,
            'pop': cls.POP
        }
        s_lower = s.lower().strip()
        if s_lower not in mapping:
            raise ValueError(f"Invalid variant: {s}. Choose from: {list(mapping.keys())}")
        return mapping[s_lower]


class PuzzleType(Enum):
    """World/puzzle type variants."""
    LINE = auto(),
    GRID = auto(),
    MAZE = auto()

    @classmethod
    def from_string(cls, s: str) -> 'PuzzleType':
        """Convert string argument to PuzzleType enum.

        Args:
            s: String representation ('line', 'grid', 'maze')

        Returns:
            Corresponding PuzzleType enum value

        Raises:
            ValueError: If string doesn't match any puzzle type
        """
        mapping = {
            'line': cls.LINE,
            'grid': cls.GRID,
            'maze': cls.MAZE
        }
        s_lower = s.lower().strip()
        if s_lower not in mapping:
            raise ValueError(f"Invalid puzzle type: {s}. Choose from: {list(mapping.keys())}")
        return mapping[s_lower]


class BellmanFormat(Enum):
    """Bellman equation format variants."""
    DEFAULT = auto()  # Variant-specific default format
    COMMON = auto()   # Common format with stay-in-place cost
    ADAPTED = auto()  # Adapted format without stay-in-place cost

    @classmethod
    def from_string(cls, s: str) -> 'BellmanFormat':
        """Convert string to BellmanFormat enum.

        Args:
            s: String representation ('default', 'common', 'adapted')

        Returns:
            Corresponding BellmanFormat enum value

        Raises:
            ValueError: If string doesn't match any format
        """
        mapping = {
            'default': cls.DEFAULT,
            'common': cls.COMMON,
            'adapted': cls.ADAPTED
        }
        s_lower = s.lower().strip()
        if s_lower not in mapping:
            raise ValueError(f"Invalid bellman_format: {s}. Must be one of {list(mapping.keys())}")
        return mapping[s_lower]


class Precision(Enum):
    """Constraint precision mode."""
    STRICT = auto()   # Use equality constraints (==) for precise optimal solutions
    RELAXED = auto()  # Use inequality constraints (>= for Bellman, <= for budget) for approximate solutions (invariant)

    @classmethod
    def from_string(cls, s: str) -> 'Precision':
        """Convert string to Precision enum.

        Args:
            s: String representation ('strict', 'relaxed')

        Returns:
            Corresponding Precision enum value

        Raises:
            ValueError: If string doesn't match any precision mode
        """
        mapping = {
            'strict': cls.STRICT,
            'relaxed': cls.RELAXED
        }
        s_lower = s.lower().strip()
        if s_lower not in mapping:
            raise ValueError(f"Invalid precision: {s}. Must be one of {list(mapping.keys())}")
        return mapping[s_lower]
