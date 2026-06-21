#!/usr/bin/env bash
set -euo pipefail

# Entrypoint for the dynamic_solvers container.
# Builds a safe argv array and execs the benchmark runner.

# Defaults (can be overridden by environment variables)
CONFIG_CSV=${CONFIG_CSV:-/configs/runtime-variance.csv}
OUTPUT_CSV=${OUTPUT_CSV:-benchmark_results.csv}

# Boolean env vars expected to be "true" to enable behaviour
# VERBOSE -> adds --verbose
# REAL_ENCODING -> adds -re (real encoding)
# ORDER_ENABLED -> when "true", adds -order with ORDER_VALUE

args=(python3 -m dynamic_solvers.benchmark "$CONFIG_CSV" --output "$OUTPUT_CSV")

# verbose flag
if [[ "${VERBOSE:-}" = "true" ]]; then
  args+=(--verbose)
fi

# real encoding flag
if [[ "${REAL_ENCODING:-}" = "true" ]]; then
  args+=(-re)
fi

# bellman format (always add, use default if unset)
args+=(${BF:+-bf $BF})

# optional order constraint argument: only add when explicitly enabled
args+=(${ORDER:+-order $ORDER})

# optional trials argument: only add when TRIALS is set
if [[ -n "${TRIALS:-}" ]]; then
  args+=(-t "$TRIALS")
fi

echo "Running: ${args[*]}" >&2

exec "${args[@]}"
