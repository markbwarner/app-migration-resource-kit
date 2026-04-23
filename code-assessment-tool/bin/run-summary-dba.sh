#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $(basename "$0") <input-directory> [custom-patterns-json] [output-directory]"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INPUT_DIR="$(cd "$1" && pwd)"
SCAN_NAME="$(basename "$INPUT_DIR")"
CUSTOM_PATTERNS="${2:-$REPO_ROOT/custom-patterns.example.json}"
OUTPUT_DIR="${3:-$REPO_ROOT/reports}"
STAMP="$(date +"%Y%m%d_%H%M%S")"
PYTHON_BIN="${PYTHON_BIN:-python}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

mkdir -p "$OUTPUT_DIR"

"$PYTHON_BIN" "$REPO_ROOT/app.py" "$INPUT_DIR" \
  --custom-patterns "$CUSTOM_PATTERNS" \
  --json-summary-out "$OUTPUT_DIR/${SCAN_NAME}_pii-impact-summary_${STAMP}.json" \
  --csv-out "$OUTPUT_DIR/${SCAN_NAME}_likely-change-targets_${STAMP}.csv" \
  --sql-out "$OUTPUT_DIR/${SCAN_NAME}_dba-planning_${STAMP}.sql"
