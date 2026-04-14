#!/usr/bin/env bash
# Glimmer — Verification pack runner
#
# Usage:
#   ./tests/tools/run_pack.sh smoke
#   ./tests/tools/run_pack.sh release
#   ./tests/tools/run_pack.sh workstream_f
#   ./tests/tools/run_pack.sh all
#   ./tests/tools/run_pack.sh browser   # runs Playwright tests
#
# WORKG:WG3 — Smoke pack execution
# WORKG:WG6 — Release-pack execution routine

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TESTS_DIR="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$(dirname "$TESTS_DIR")"
WEB_DIR="$SRC_DIR/apps/web"

PACK="${1:-}"

if [ -z "$PACK" ]; then
    echo "Usage: $0 <pack_name>"
    echo ""
    echo "Available packs:"
    echo "  smoke          - Baseline startup and reachability"
    echo "  workstream_a   - Foundation"
    echo "  workstream_b   - Domain and Memory"
    echo "  workstream_c   - Connectors"
    echo "  workstream_d   - Triage and Prioritization"
    echo "  workstream_e   - Drafting and UI"
    echo "  workstream_f   - Voice and Companion"
    echo "  data_integrity - Cross-cutting memory spine protection"
    echo "  release        - Representative cross-system confidence"
    echo "  all            - Full test suite"
    echo "  browser        - Playwright browser tests"
    echo ""
    echo "For evidence report, use:"
    echo "  python tests/tools/evidence_report.py <pack_name>"
    exit 1
fi

cd "$SRC_DIR"

case "$PACK" in
    browser)
        echo "=== Running Playwright browser tests ==="
        cd "$WEB_DIR"
        npx playwright test --reporter=list
        ;;
    all)
        echo "=== Running full test suite ==="
        python -m pytest tests/ -v --tb=short
        ;;
    smoke|workstream_a|workstream_b|workstream_c|workstream_d|workstream_e|workstream_f|data_integrity|release)
        echo "=== Running pack: $PACK ==="
        python -m pytest tests/ -m "$PACK" -v --tb=short
        ;;
    *)
        echo "Unknown pack: $PACK"
        exit 1
        ;;
esac

echo ""
echo "=== Pack $PACK completed ==="

