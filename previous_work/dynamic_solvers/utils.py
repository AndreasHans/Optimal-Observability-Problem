import re
from typing import Tuple, Callable, List, Generator, Iterable

from z3 import Bool, Real, Context, z3

from previous_work.dynamic_solvers.builders.worlds import World
from previous_work.dynamic_solvers.direction import Direction


def parse_threshold(arg: str) -> Tuple[List[int], Callable[[int, int], bool]]:
    sign_idx = arg.find('<')
    if sign_idx == -1:
        raise ValueError("No sign in threshold")
    sign = (lambda x, y: x <= y) if arg[sign_idx + 1] == '=' else (lambda x, y: x < y)

    terms = list(map(int, re.findall(r"\d+", arg)))
    assert len(terms) > 0
    return terms, sign


def init_var_type(condition: bool) -> Callable[[str, Context], z3.ArithRef | z3.BoolRef]:
    """Typed (first-class) constructor selector for Z3 variables based on conditional mode."""
    return Bool if condition else Real


def get_observation_marker(obs_class: int, use_color: bool = True, binary: bool = False) -> str:
    """Get colored circle or digit for observation class using ANSI colors when appropriate.

    Args:
        obs_class: The observation class number (1-9)
        use_color: If True, use ANSI colors. If False, use plain symbols.
        binary: If True, use on/off symbols instead of digits.
    """
    if use_color:
        # ANSI color codes: red, green, blue, yellow, magenta, cyan, white, bright_black, bright_white
        colors = [
            '\033[91m●\033[0m',  # Bright red
            '\033[92m●\033[0m',  # Bright green
            '\033[94m●\033[0m',  # Bright blue
            '\033[93m●\033[0m',  # Bright yellow
            '\033[95m●\033[0m',  # Bright magenta
            '\033[96m●\033[0m',  # Bright cyan
            '\033[97m●\033[0m',  # Bright white
            '\033[90m●\033[0m',  # Bright black (gray)
            '\033[37m●\033[0m',  # White
        ]
        if binary:
            return colors[0] if obs_class == 0 else colors[1]
        if obs_class <= 0 or obs_class > len(colors):
            return '○'  # Default for invalid classes
        return colors[obs_class - 1]
    else:
        if binary:
            return "○" if obs_class == 0 else "●"
        # Plain ASCII numbers for file output (monospace)
        if obs_class <= 0 or obs_class > 9:
            return '#'  # Default for invalid classes
        return str(obs_class)


def convert_text_to_html(text: str, title: str = "World Visualization") -> str:
    """Convert ANSI-colored text to HTML.

    Args:
        text: Text with ANSI color codes
        title: HTML page title

    Returns:
        Complete HTML document as string
    """
    # Map ANSI color codes to CSS colors
    ansi_to_css = {
        '91': '#ff5555',  # Bright red
        '92': '#50fa7b',  # Bright green
        '94': '#8be9fd',  # Bright blue
        '93': '#f1fa8c',  # Bright yellow
        '95': '#ff79c6',  # Bright magenta
        '96': '#8be9fd',  # Bright cyan
        '97': '#f8f8f2',  # Bright white
        '90': '#6272a4',  # Bright black (gray)
        '37': '#f8f8f2',  # White
    }

    # Convert ANSI codes to HTML spans
    def replace_ansi(match):
        code = match.group(1)
        content = match.group(2)
        color = ansi_to_css.get(code, '#ffffff')
        return f'<span style="color: {color}; font-weight: bold;">{content}</span>'

    # Pattern: \033[XXm CONTENT \033[0m
    html_text = re.sub(r'\033\[(\d+)m([^\033]+)\033\[0m', replace_ansi, text)

    # Escape any remaining HTML characters
    html_text = html_text.replace('&', '&amp;').replace('<span', '###SPAN###').replace('</span>', '###/SPAN###')
    html_text = html_text.replace('###SPAN###', '<span').replace('###/SPAN###', '</span>')

    # Build complete HTML document
    html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{
                    background-color: #282a36;
                    color: #f8f8f2;
                    font-family: 'Courier New', Consolas, monospace;
                    padding: 20px;
                    margin: 0;
                }}
                pre {{
                    background-color: #1e1f29;
                    padding: 20px;
                    border-radius: 5px;
                    overflow-x: auto;
                    line-height: 1.4;
                }}
            </style>
        </head>
        <body>
            <pre>{html_text}</pre>
        </body>
        </html>"""
    return html


def stirling_partitions(n, k) -> Generator[list[list[int]]]:
    """Generate all partitions of {0...n-1} into k unlabeled nonempty subsets."""
    items = list(range(n))

    def backtrack(i: int, curr: list[list[int]], used: int):
        if i == n:
            if used == k:
                # Yield a sorted normalized form (unlabeled buckets)
                yield list(sorted(list(sorted(b)) for b in curr[:used]))
            return

        # Option 1: put item i into an existing bucket
        for b in range(used):
            curr[b].append(items[i])
            yield from backtrack(i + 1, curr, used)
            curr[b].pop()

        # Option 2: create a new bucket (only if we have room)
        if used < k:
            curr[used].append(items[i])
            yield from backtrack(i + 1, curr, used + 1)
            curr[used].pop()

    curr = [[] for _ in range(k)]
    yield from backtrack(0, curr, 0)


def minimal_positional_budget(world: World) -> int:
    """
    Compute the Minimal Positional Budget (MPB) for the general (non-cardinal) world.

    The MPB is the minimum number of observation classes needed such that states
    can be grouped while maintaining optimality. States can be grouped together
    if their atomic groups share at least one common optimal action.

    Returns:
        int: The minimal positional budget.
    """
    n = len(world.clusters)
    if n <= 1:
        return n

    def _partition_is_valid(partition: list[list[int]], atomic_groups: list[Direction]) -> bool:
        """
        Check if a partition is valid: each block must have atomic groups with strictly overlapping actions.

        Args:
            partition: List of blocks, where each block contains indices of atomic groups.
            atomic_groups: List of Direction enum values representing the atomic groups.

        Returns:
            bool: True if all blocks have non-empty action intersection, False otherwise.
        """
        for block in partition:
            action_sets = [atomic_groups[idx].actions for idx in block]
            common_actions = set.intersection(*action_sets)
            if len(common_actions) == 0:
                return False
        return True

    atomic_groups = list(world.clusters.keys())

    # Try partition sizes from 2 up to min(4, n)
    for budget in range(2, n):
        for partition in stirling_partitions(n, budget):
            if _partition_is_valid(partition, atomic_groups):
                return budget

    # Fallback: each cluster needs its own observation class
    return n


def prettify(obj: object | Iterable, prefix: str):
    """
    Recursively traverses an object or iterable and adds a specified prefix to each element.

    Parameters:
        obj (object | Iterable): The object or iterable whose elements will be prefixed.
        prefix (str): The string to prepend to each element.

    Returns:
        object | Iterable: A new object or iterable with the same structure as the input,
        where each element has the prefix added.
    """

    if isinstance(obj, Iterable):
        container_type = type(obj)
        return container_type(prettify(item, prefix) for item in obj)
    else:
        return f"{prefix}{str(obj)}"
