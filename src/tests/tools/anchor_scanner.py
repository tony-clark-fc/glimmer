"""TEST: anchor traceability scanner — WG2.

Scans test files for TEST: anchor references and maps them against
the canonical test catalog. Produces a coverage/traceability report.

Usage:
    python tests/tools/anchor_scanner.py

WORKG:WG2 — TEST: anchor traceability support
"""

from __future__ import annotations

import os
import re
from pathlib import Path

# Paths relative to the repo src/ root
TESTS_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = TESTS_DIR.parent
CATALOG_PATH = SRC_DIR / "4. Verification" / "test_catalog.md"
# Additional directories containing test files (e.g. Playwright e2e)
E2E_DIR = SRC_DIR / "apps" / "web" / "e2e"


def scan_catalog(catalog_path: Path) -> set[str]:
    """Extract all TEST: anchors defined in the test catalog.

    Only scans the §7 "Catalog Entries" section to avoid picking up
    example anchors from maintenance rules (§8) like TEST:Planner.Fix2.
    """
    anchors: set[str] = set()
    if not catalog_path.exists():
        print(f"WARNING: Catalog not found at {catalog_path}")
        return anchors

    content = catalog_path.read_text()

    # Restrict to §7 Catalog Entries section only
    section_start = content.find("## 7. Catalog Entries")
    section_end = content.find("## 8. Catalog Maintenance Rules")
    if section_start == -1:
        # Fallback: scan entire file
        section = content
    elif section_end == -1:
        section = content[section_start:]
    else:
        section = content[section_start:section_end]

    # Match ### `TEST:Something.Something`
    for match in re.finditer(r"`(TEST:[A-Za-z0-9_.]+)`", section):
        anchors.add(match.group(1))
    return anchors


def scan_test_files(*scan_dirs: Path) -> dict[str, list[str]]:
    """Scan test files for TEST: anchor references.

    Accepts one or more directories. Returns {anchor: [file_path, ...]} mapping.
    Paths are relative to `SRC_DIR` for readability.
    """
    anchor_files: dict[str, list[str]] = {}

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for root, _dirs, files in os.walk(scan_dir):
            # Skip tools directory (contains scanner itself with example anchors)
            if os.path.basename(root) == "tools":
                continue
            for fname in files:
                if not fname.endswith(".py") and not fname.endswith(".ts"):
                    continue
                if fname.startswith("__"):
                    continue

                fpath = Path(root) / fname
                content = fpath.read_text()

                # Find TEST: references in docstrings, comments, and inline markers
                for match in re.finditer(r"(TEST:[A-Za-z0-9_.]+)", content):
                    anchor = match.group(1)
                    rel_path = str(fpath.relative_to(SRC_DIR))
                    if anchor not in anchor_files:
                        anchor_files[anchor] = []
                    if rel_path not in anchor_files[anchor]:
                        anchor_files[anchor].append(rel_path)

    return anchor_files


def generate_report(
    catalog_anchors: set[str],
    test_anchors: dict[str, list[str]],
) -> str:
    """Generate a Markdown traceability report."""
    lines: list[str] = []
    lines.append("# Glimmer — TEST: Anchor Traceability Report")
    lines.append("")
    lines.append(f"**Catalog anchors defined:** {len(catalog_anchors)}")
    lines.append(f"**Anchors referenced in tests:** {len(test_anchors)}")

    # Covered anchors
    covered = catalog_anchors & set(test_anchors.keys())
    missing = catalog_anchors - set(test_anchors.keys())
    extra = set(test_anchors.keys()) - catalog_anchors

    lines.append(f"**Covered by tests:** {len(covered)}")
    lines.append(f"**Missing from tests:** {len(missing)}")
    lines.append(f"**In tests but not in catalog:** {len(extra)}")
    lines.append("")

    # Coverage table
    lines.append("## Covered Anchors")
    lines.append("")
    lines.append("| Anchor | Test Files |")
    lines.append("|---|---|")
    for anchor in sorted(covered):
        files = ", ".join(test_anchors[anchor])
        lines.append(f"| `{anchor}` | {files} |")
    lines.append("")

    # Missing from tests
    if missing:
        lines.append("## Missing from Tests")
        lines.append("")
        lines.append("These anchors are defined in the catalog but have no implementing test:")
        lines.append("")
        for anchor in sorted(missing):
            lines.append(f"- `{anchor}`")
        lines.append("")

    # Extra in tests
    if extra:
        lines.append("## In Tests but Not in Catalog")
        lines.append("")
        lines.append("These anchors appear in tests but are not in the canonical catalog:")
        lines.append("")
        for anchor in sorted(extra):
            files = ", ".join(test_anchors[anchor])
            lines.append(f"- `{anchor}` → {files}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    catalog_anchors = scan_catalog(CATALOG_PATH)
    test_anchors = scan_test_files(TESTS_DIR, E2E_DIR)
    report = generate_report(catalog_anchors, test_anchors)

    # Write to evidence directory
    evidence_dir = TESTS_DIR / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    out_path = evidence_dir / "anchor_traceability_report.md"
    out_path.write_text(report)

    print(report)
    print(f"\nReport written to: {out_path}")


if __name__ == "__main__":
    main()

