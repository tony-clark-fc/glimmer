"""Evidence collection and reporting — WG7.

Runs a verification pack via pytest, captures JUnit XML results, and
generates a human-readable Markdown evidence summary.

Usage:
    python tests/tools/evidence_report.py smoke
    python tests/tools/evidence_report.py release
    python tests/tools/evidence_report.py workstream_f
    python tests/tools/evidence_report.py all

WORKG:WG7 — Evidence collection and reporting support
"""

from __future__ import annotations

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = TESTS_DIR.parent
EVIDENCE_DIR = TESTS_DIR / "evidence"

VALID_PACKS = [
    "smoke",
    "workstream_a",
    "workstream_b",
    "workstream_c",
    "workstream_d",
    "workstream_e",
    "workstream_f",
    "data_integrity",
    "release",
    "all",
]


def run_pack(pack_name: str) -> Path:
    """Run a verification pack and return path to JUnit XML."""
    EVIDENCE_DIR.mkdir(exist_ok=True)
    xml_path = EVIDENCE_DIR / f"{pack_name}_results.xml"

    cmd = [
        sys.executable, "-m", "pytest",
        str(TESTS_DIR),
        f"--junitxml={xml_path}",
        "-q",
        "--tb=short",
    ]
    if pack_name != "all":
        cmd.extend(["-m", pack_name])

    print(f"Running pack: {pack_name}")
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SRC_DIR))

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return xml_path


def parse_junit_xml(xml_path: Path) -> dict:
    """Parse JUnit XML into a structured result dict."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Handle both <testsuites> and <testsuite> root
    if root.tag == "testsuites":
        suites = list(root)
    else:
        suites = [root]

    total = 0
    passed = 0
    failed = 0
    errors = 0
    skipped = 0
    tests: list[dict] = []

    for suite in suites:
        for testcase in suite.findall("testcase"):
            total += 1
            name = testcase.get("name", "unknown")
            classname = testcase.get("classname", "")
            time_s = float(testcase.get("time", "0"))

            failure = testcase.find("failure")
            error = testcase.find("error")
            skip = testcase.find("skipped")

            if failure is not None:
                status = "FAILED"
                failed += 1
            elif error is not None:
                status = "ERROR"
                errors += 1
            elif skip is not None:
                status = "SKIPPED"
                skipped += 1
            else:
                status = "PASSED"
                passed += 1

            tests.append({
                "name": name,
                "classname": classname,
                "status": status,
                "time": time_s,
            })

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "tests": tests,
    }


def load_manual_deferred() -> list[dict]:
    """Load manual/deferred scenarios from the registry."""
    registry_path = Path(__file__).parent / "manual_deferred.yaml"
    if not registry_path.exists():
        return []

    items: list[dict] = []
    current: dict = {}
    for line in registry_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("- anchor:"):
            if current:
                items.append(current)
            current = {"anchor": line.split(":", 1)[1].strip()}
        elif line.startswith("status:") and current:
            current["status"] = line.split(":", 1)[1].strip()
        elif line.startswith("reason:") and current:
            current["reason"] = line.split(":", 1)[1].strip()
    if current:
        items.append(current)
    return items


def generate_evidence_report(pack_name: str, results: dict) -> str:
    """Generate a Markdown evidence report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []

    lines.append(f"# Glimmer — Verification Evidence: {pack_name}")
    lines.append("")
    lines.append(f"**Pack:** `{pack_name}`")
    lines.append(f"**Executed:** {now}")
    lines.append(f"**Environment:** Local development (macOS)")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|---|---|")
    lines.append(f"| Total | {results['total']} |")
    lines.append(f"| Passed | {results['passed']} |")
    lines.append(f"| Failed | {results['failed']} |")
    lines.append(f"| Errors | {results['errors']} |")
    lines.append(f"| Skipped | {results['skipped']} |")

    verdict = "✅ PASS" if results["failed"] == 0 and results["errors"] == 0 else "❌ FAIL"
    lines.append(f"| **Verdict** | **{verdict}** |")
    lines.append("")

    # Failed tests detail
    failures = [t for t in results["tests"] if t["status"] in ("FAILED", "ERROR")]
    if failures:
        lines.append("## Failures")
        lines.append("")
        for t in failures:
            lines.append(f"- **{t['status']}**: `{t['classname']}::{t['name']}`")
        lines.append("")

    # Per-test table (abbreviated)
    lines.append("## Test Results")
    lines.append("")
    lines.append("| Status | Class | Test | Time |")
    lines.append("|---|---|---|---|")
    for t in results["tests"]:
        emoji = {"PASSED": "✅", "FAILED": "❌", "ERROR": "💥", "SKIPPED": "⏭"}.get(t["status"], "?")
        lines.append(f"| {emoji} {t['status']} | `{t['classname']}` | `{t['name']}` | {t['time']:.3f}s |")
    lines.append("")

    # Manual/deferred section
    manual_items = load_manual_deferred()
    if manual_items:
        lines.append("## Manual / Deferred Scenarios")
        lines.append("")
        lines.append("| Anchor | Status | Reason |")
        lines.append("|---|---|---|")
        for item in manual_items:
            lines.append(
                f"| `{item.get('anchor', '?')}` "
                f"| {item.get('status', 'Unknown')} "
                f"| {item.get('reason', '')} |"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <pack_name>")
        print(f"Valid packs: {', '.join(VALID_PACKS)}")
        sys.exit(1)

    pack_name = sys.argv[1]
    if pack_name not in VALID_PACKS:
        print(f"Unknown pack: {pack_name}")
        print(f"Valid packs: {', '.join(VALID_PACKS)}")
        sys.exit(1)

    xml_path = run_pack(pack_name)

    if not xml_path.exists():
        print(f"ERROR: JUnit XML not generated at {xml_path}")
        sys.exit(1)

    results = parse_junit_xml(xml_path)
    report = generate_evidence_report(pack_name, results)

    report_path = EVIDENCE_DIR / f"{pack_name}_evidence.md"
    report_path.write_text(report)

    print(f"\n{'=' * 60}")
    print(f"Evidence report written to: {report_path}")
    print(f"Pack: {pack_name} — {results['passed']}/{results['total']} passed")
    if results["failed"] > 0 or results["errors"] > 0:
        print(f"⚠️  {results['failed']} failures, {results['errors']} errors")


if __name__ == "__main__":
    main()

