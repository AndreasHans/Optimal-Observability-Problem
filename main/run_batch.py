"""Batch runner for the BMSSP solvers.

Reads a CSV config file, runs each row in a fresh subprocess via
``_run_one.py``, and writes results to ``main/output/<input-stem>.csv``.

Usage:
    python main/run_batch.py <config.csv>

See ``main/plan.md`` for the full specification.
"""
import argparse
import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

TIMEOUT_SECONDS = 180  # 3 minutes per instance
INPUT_COLUMNS = ['family', 'type', 'size', 'budget', 'memory', 'threshold']
OUTPUT_COLUMNS = ['family', 'type', 'size', 'budget', 'memory', 'threshold',
                  'time', 'status', 'reward']
VALID_FAMILIES = {'deterministic', 'randomized', 'memory','restricted', 'forced', 'heuristic'}
VALID_TYPES = {'line', 'grid', 'maze'}

WORKER = Path(__file__).resolve().parent / '_run_one.py'
OUTPUT_DIR = Path(__file__).resolve().parent / 'output'


@dataclass
class ConfigRow:
    family: str
    mdp_type: str
    size: int
    budget: int
    memory: int
    threshold_raw: str


def validate_threshold(raw: str) -> None:
    """Raise ValueError if the threshold string is malformed.

    Empty string ⇒ minimization mode, accepted.
    """
    text = raw.strip()
    if not text:
        return
    if text.startswith('<='):
        value = text[2:].strip()
    elif text.startswith('<'):
        value = text[1:].strip()
    else:
        raise ValueError(f"threshold must start with '<' or '<=': {raw!r}")
    if '/' in value:
        num_str, den_str = value.split('/', 1)
        int(num_str.strip())
        den = int(den_str.strip())
        if den == 0:
            raise ValueError(f"zero denominator in threshold: {raw!r}")
    else:
        int(value)


def parse_row(raw: dict) -> ConfigRow:
    family = (raw.get('family') or '').strip().lower()
    if family not in VALID_FAMILIES:
        raise ValueError(f"unknown family: {raw.get('family')!r}")

    mdp_type = (raw.get('type') or '').strip().lower()
    if mdp_type not in VALID_TYPES:
        raise ValueError(f"unknown type: {raw.get('type')!r}")

    size = int((raw.get('size') or '').strip())
    budget = int((raw.get('budget') or '').strip())
    memory = int((raw.get('memory') or '').strip())

    threshold_raw = (raw.get('threshold') or '').strip()
    validate_threshold(threshold_raw)

    return ConfigRow(
        family=family,
        mdp_type=mdp_type,
        size=size,
        budget=budget,
        memory=memory,
        threshold_raw=threshold_raw,
    )


def threshold_slug(raw: str) -> str:
    text = raw.strip()
    if not text:
        return 'min'
    if text.startswith('<='):
        prefix, rest = 'le', text[2:]
    elif text.startswith('<'):
        prefix, rest = 'lt', text[1:]
    else:
        prefix, rest = '', text
    return prefix + rest.strip().replace('/', '_')


def dump_path(run_dir: Path, input_stem: str, cfg: ConfigRow) -> Path:
    name = (
        f"{cfg.family}-{cfg.mdp_type}"
        f"-n{cfg.size}-b{cfg.budget}-m{cfg.memory}"
        f"-t{threshold_slug(cfg.threshold_raw)}.txt"
    )
    return run_dir / name


def run_one(cfg: ConfigRow, run_dir: Path, input_stem: str) -> dict:
    """Run a single solver instance and return a dict of result fields."""
    cmd = [
        sys.executable,
        str(WORKER),
        cfg.family,
        cfg.mdp_type,
        str(cfg.size),
        str(cfg.budget),
        str(cfg.memory),
        cfg.threshold_raw,
        '--dump', str(dump_path(run_dir, input_stem, cfg)),
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {'time': '', 'status': 'timeout', 'reward': ''}

    if proc.returncode != 0:
        return {'time': '', 'status': 'error', 'reward': ''}

    # Last non-empty stdout line is the JSON payload.
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if not lines:
        return {'time': '', 'status': 'error', 'reward': ''}

    try:
        payload = json.loads(lines[-1])
    except json.JSONDecodeError:
        return {'time': '', 'status': 'error', 'reward': ''}

    status = payload.get('status', 'error')
    time_val = payload.get('time')
    time_str = f"{time_val:.6f}" if isinstance(time_val, (int, float)) else ''
    reward = payload.get('reward', '') if status == 'sat' else ''

    return {'time': time_str, 'status': status, 'reward': reward}


def iter_config_rows(path: Path):
    """Yield (raw_dict, line_number) pairs, skipping blanks and '#' comments."""
    with path.open('r', encoding='utf-8', newline='') as fh:
        # Filter out blank lines and '#' comment lines before CSV parses them.
        def _filtered():
            for idx, line in enumerate(fh, start=1):
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                yield line

        reader = csv.DictReader(_filtered(), fieldnames=None)
        if reader.fieldnames is None:
            return
        # Header validation (advisory only; order is fixed).
        expected = [c.lower() for c in INPUT_COLUMNS]
        actual = [c.strip().lower() for c in reader.fieldnames]
        if actual[:len(expected)] != expected:
            print(
                f"Warning: header {actual} does not match expected {expected}; "
                f"proceeding by column position.",
                file=sys.stderr,
            )
        for row in reader:
            yield row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=Path)
    args = parser.parse_args()

    if not args.config.is_file():
        print(f"Config file not found: {args.config}", file=sys.stderr)
        sys.exit(2)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    input_stem = args.config.stem
    run_dir = OUTPUT_DIR / input_stem
    run_dir.mkdir(parents=True, exist_ok=True)
    output_path = run_dir / f"{input_stem}.csv"

    counts = {'total': 0, 'sat': 0, 'unsat': 0, 'unknown': 0,
              'timeout': 0, 'error': 0}

    with output_path.open('w', encoding='utf-8', newline='') as out_fh:
        writer = csv.DictWriter(out_fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        out_fh.flush()

        for raw in iter_config_rows(args.config):
            counts['total'] += 1
            try:
                cfg = parse_row(raw)
            except (ValueError, KeyError, TypeError) as exc:
                print(f"Row parse error: {exc}", file=sys.stderr)
                writer.writerow({
                    'family': (raw.get('family') or '').strip(),
                    'type': (raw.get('type') or '').strip(),
                    'size': (raw.get('size') or '').strip(),
                    'budget': (raw.get('budget') or '').strip(),
                    'memory': (raw.get('memory') or '').strip(),
                    'threshold': (raw.get('threshold') or '').strip(),
                    'time': '',
                    'status': 'error',
                    'reward': '',
                })
                counts['error'] += 1
                out_fh.flush()
                continue

            print(
                f"[{counts['total']}] running {cfg.family} {cfg.mdp_type} "
                f"n={cfg.size} b={cfg.budget} m={cfg.memory} "
                f"t={cfg.threshold_raw or '(min)'}",
                flush=True,
            )

            result = run_one(cfg, run_dir, input_stem)
            counts[result['status']] = counts.get(result['status'], 0) + 1

            writer.writerow({
                'family': cfg.family,
                'type': cfg.mdp_type,
                'size': cfg.size,
                'budget': cfg.budget,
                'memory': cfg.memory,
                'threshold': cfg.threshold_raw,
                'time': result['time'],
                'status': result['status'],
                'reward': result['reward'],
            })
            out_fh.flush()

    print(
        f"Done. total={counts['total']} sat={counts['sat']} "
        f"unsat={counts['unsat']} unknown={counts['unknown']} "
        f"timeout={counts['timeout']} error={counts['error']}"
    )
    print(f"Output: {output_path}")


if __name__ == '__main__':
    main()
