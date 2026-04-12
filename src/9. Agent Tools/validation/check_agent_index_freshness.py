#!/usr/bin/env python3
"""Validate whether AGENT_INDEX.json is missing or stale."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def default_index_path(root: Path) -> Path:
    return root / "src" / "9. Agent Tools" / "indexing" / "AGENT_INDEX.json"


def load_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Index file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_index(index_path: Path, index_data: dict[str, Any]) -> dict[str, Any]:
    repo_root = Path(index_data["repository_root"])
    index_mtime = index_path.stat().st_mtime
    newer_files: list[str] = []
    missing_files: list[str] = []

    for document in index_data.get("documents", []):
        file_path = repo_root / document["path"]
        if not file_path.exists():
            missing_files.append(document["path"])
            continue
        if file_path.stat().st_mtime > index_mtime:
            newer_files.append(document["path"])

    return {
        "index_path": str(index_path),
        "repository_root": str(repo_root),
        "document_count": len(index_data.get("documents", [])),
        "missing_files": missing_files,
        "newer_files": newer_files,
        "is_fresh": not missing_files and not newer_files,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether AGENT_INDEX.json is missing or stale.")
    parser.add_argument("--index", default=None, help="Path to AGENT_INDEX.json.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root_from_script()
    index_path = Path(args.index).resolve() if args.index else default_index_path(root)
    index_data = load_index(index_path)
    result = validate_index(index_path, index_data)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["is_fresh"]:
            print(f"Fresh: {result['index_path']} ({result['document_count']} indexed documents)")
        else:
            print(f"Stale: {result['index_path']}")
            if result["missing_files"]:
                print("Missing files:")
                for path in result["missing_files"][:10]:
                    print(f"- {path}")
            if result["newer_files"]:
                print("Newer files:")
                for path in result["newer_files"][:10]:
                    print(f"- {path}")

    return 0 if result["is_fresh"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

