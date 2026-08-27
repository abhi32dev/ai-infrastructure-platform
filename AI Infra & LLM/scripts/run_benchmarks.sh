#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}/.."
source "${PROJECT_DIR}/.venv/bin/activate"

echo "=== Launching AI Infra load tests & sweeps ==="
python "${PROJECT_DIR}/src/benchmarks/runner.py" "$@"
echo "=== Sweep completed ==="
