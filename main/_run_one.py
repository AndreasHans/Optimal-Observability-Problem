"""Worker script: run a single BMSSP solver instance and print a JSON result.

Invoked by ``run_batch.py`` as a subprocess so each instance gets a clean
Z3 state and can be bounded with a hard wall-clock timeout.

Usage:
    python main/_run_one.py <family> <type> <size> <budget> <memory> <threshold> [--dump <path>]

``<threshold>`` is either empty (minimization mode) or a string of the
form ``<k``, ``<=k``, ``<k/d``, or ``<=k/d``.
"""
import argparse
import contextlib
import json
import sys
import traceback

from z3 import sat, unsat

from MDPVariants import grid_corner_n, line_n, maze_n
from ParseModel import ParseModel

import BMSSP_solver_deterministic
import BMSSP_solver_randomized
import BMSSP_deterministic_memory_symmetry
import BMSSP_deterministic_MemoryRestrict
import BMSSP_det_forced_action
import BMSSP_det_forced_restricted
import BMSSP_deterministic_general_heuristics


def build_mdp(mdp_type: str, size: int):
    mdp_type = mdp_type.lower()
    if mdp_type == 'grid':
        return grid_corner_n(size)
    if mdp_type == 'line':
        return line_n(size)
    if mdp_type == 'maze':
        return maze_n(size)
    raise ValueError(f"Unknown MDP type: {mdp_type}")


def parse_threshold(raw: str):
    """Return (threshold_terms, strict_less).

    ``threshold_terms`` is ``None`` for minimization mode, else a tuple
    ``(num, den)``.
    """
    text = raw.strip()
    if not text:
        return None, True

    if text.startswith('<='):
        strict_less = False
        value = text[2:].strip()
    elif text.startswith('<'):
        strict_less = True
        value = text[1:].strip()
    else:
        raise ValueError(f"Threshold must start with '<' or '<=': {raw!r}")

    if '/' in value:
        num_str, den_str = value.split('/', 1)
        num = int(num_str.strip())
        den = int(den_str.strip())
        if den == 0:
            raise ValueError(f"Zero denominator in threshold: {raw!r}")
    else:
        num = int(value)
        den = 1

    return (num, den), strict_less


def format_reward(model, min_exp_rew_symbol) -> str:
    val = model.eval(min_exp_rew_symbol, model_completion=True)
    if val.is_int_value():
        return str(val.as_long())
    return f"{val.numerator_as_long()}/{val.denominator_as_long()}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('family')
    parser.add_argument('mdp_type')
    parser.add_argument('size', type=int)
    parser.add_argument('budget', type=int)
    parser.add_argument('memory', type=int)
    parser.add_argument('threshold')
    parser.add_argument('--dump', default=None)
    args = parser.parse_args()

    family = args.family.lower()
    if family == 'deterministic':
        solver_module = BMSSP_solver_deterministic
    elif family == 'randomized':
        solver_module = BMSSP_solver_randomized
    elif family == 'symmetry':#memory symmetry heurisitc.
        solver_module == BMSSP_deterministic_memory_symmetry
    elif family == 'memory':#reduced memory under observation heuristic
        solver_module = BMSSP_deterministic_MemoryRestrict
    elif family == 'restricted': #reduced memory under observation and optimal action heuristic
        solver_module = BMSSP_det_forced_restricted
    elif family == 'forced': #optimal action heuristic
        solver_module = BMSSP_det_forced_action 
    elif family == 'general heuristics': #use of the results of the heuristiscs
        solver_module = BMSSP_deterministic_general_heuristics
    else:
        raise ValueError(f"Unknown family: {args.family}")

    threshold_terms, strict_less = parse_threshold(args.threshold)

    mdp = build_mdp(args.mdp_type, args.size)

    z3result = solver_module.main(
        mdp,
        args.budget,
        threshold_terms,
        args.memory,
        strict_less,
    )

    out = {'time': z3result.solve_time}

    if z3result.result == sat:
        out['status'] = 'sat'
        out['reward'] = format_reward(z3result.model, solver_module.min_exp_rew)

        if args.dump:
            bmssp_result = ParseModel.parse_model(z3result)
            with open(args.dump, 'w', encoding='utf-8') as fh:
                with contextlib.redirect_stdout(fh):
                    bmssp_result.print()
    elif z3result.result == unsat:
        out['status'] = 'unsat'
    else:
        out['status'] = 'unknown'

    print(json.dumps(out))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
