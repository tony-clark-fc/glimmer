#!/usr/bin/env python3
"""Generate a lightweight markdown retrieval index for the repository."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ANCHOR_PATTERN = re.compile(r"\b(?:REQ|ARCH|PLAN|TEST|ADR|OPS|DATA|SEC|API):[A-Za-z0-9._-]+")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
STATUS_PATTERN = re.compile(r"^-\s+\*\*Status:\*\*\s+(.*\S)\s*$", re.IGNORECASE)
DESCRIPTION_PATTERN = re.compile(r"^-\s+\*\*Purpose:\*\*\s+(.*\S)\s*$", re.IGNORECASE)
FRONTMATTER_FIELD = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*\S)\s*$")
WORD_TOKEN = re.compile(r"[A-Za-z]{3,}")

DEFAULT_INCLUDE_PATHS = (
    ".github/copilot-instructions.md",
    "src",
    "README.md",
)

DOMAIN_RULES = (
    ("src/0. Framework/", ["framework"]),
    ("src/1. Requirements/", ["requirements"]),
    ("src/2. Architecture/", ["architecture"]),
    ("src/3. Build Plan/", ["build-plan"]),
    ("src/4. Verification/", ["verification"]),
    ("src/5. Working/", ["working"]),
    ("src/5. Legacy Documentation/", ["legacy"]),
    ("src/KNOWLEDGE/", ["knowledge"]),
    (".github/", ["instructions"]),
)

OVERRIDE_STATUS = {
    # Add project-specific status overrides here, e.g.:
    # "src/3. Build Plan/old_plan.md": ("superseded", False),
}


@dataclass(frozen=True)
class DocumentMeta:
    relative_path: str
    lifecycle: str
    canonical: bool
    domains: list[str]
    authority_rank: int


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def datetime_to_iso(value: float) -> str:
    return datetime.fromtimestamp(value, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def classify_document(relative_path: str) -> DocumentMeta:
    if relative_path in OVERRIDE_STATUS:
        lifecycle, canonical = OVERRIDE_STATUS[relative_path]
        return DocumentMeta(relative_path, lifecycle, canonical, infer_domains(relative_path), authority_rank_for(lifecycle, canonical))

    if relative_path == ".github/copilot-instructions.md":
        lifecycle = "active"
        canonical = True
    elif relative_path.startswith(".github/instructions/"):
        lifecycle = "active"
        canonical = True
    elif relative_path.startswith("src/0. Framework/"):
        lifecycle = "active"
        canonical = True
    elif relative_path.startswith("src/1. Requirements/"):
        lifecycle = "active"
        canonical = True
    elif relative_path.startswith("src/2. Architecture/"):
        lifecycle = "active"
        canonical = True
    elif relative_path.startswith("src/3. Build Plan/"):
        lifecycle = "active"
        canonical = True
    elif relative_path.startswith("src/4. Verification/"):
        lifecycle = "active"
        canonical = True
    elif relative_path.startswith("src/5. Working/"):
        lifecycle = "working"
        canonical = False
    elif relative_path.startswith("src/5. Legacy Documentation/"):
        lifecycle = "legacy"
        canonical = False
    else:
        lifecycle = "supporting"
        canonical = False

    domains = infer_domains(relative_path)
    return DocumentMeta(relative_path, lifecycle, canonical, domains, authority_rank_for(lifecycle, canonical))


def infer_domains(relative_path: str) -> list[str]:
    for prefix, domains in DOMAIN_RULES:
        if relative_path.startswith(prefix):
            return list(domains)
    return ["supporting"]


def authority_rank_for(lifecycle: str, canonical: bool) -> int:
    if lifecycle == "active" and canonical:
        return 400
    if lifecycle == "active":
        return 300
    if lifecycle == "working":
        return 200
    if lifecycle == "legacy":
        return 100
    if lifecycle == "superseded":
        return 90
    return 50


def iter_markdown_files(root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for include_path in DEFAULT_INCLUDE_PATHS:
        target = root / include_path
        if target.is_file() and target.suffix.lower() == ".md":
            seen.add(target)
            yield target
            continue
        if target.is_dir():
            for file_path in sorted(target.rglob("*.md")):
                if "/bin/" in file_path.as_posix() or "/obj/" in file_path.as_posix():
                    continue
                if file_path not in seen:
                    seen.add(file_path)
                    yield file_path


def first_heading(lines: list[str]) -> str | None:
    for line in lines:
        match = HEADING_PATTERN.match(line)
        if match:
            return normalize_text(match.group(2))
    return None


def extract_status(lines: list[str]) -> str | None:
    for line in lines[:40]:
        match = STATUS_PATTERN.match(line)
        if match:
            return normalize_text(match.group(1))
    return None


def extract_description(lines: list[str]) -> str | None:
    for line in lines[:60]:
        match = DESCRIPTION_PATTERN.match(line)
        if match:
            return normalize_text(match.group(1))

    title_skipped = False
    paragraph_lines: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if title_skipped and paragraph_lines:
                break
            continue
        if line.startswith("#") and not title_skipped:
            title_skipped = True
            continue
        if line.startswith("-") or line.startswith("|") or line.startswith("```"):
            continue
        if line.startswith("##"):
            break
        paragraph_lines.append(line)
        if len(" ".join(paragraph_lines)) >= 220:
            break
    if paragraph_lines:
        return normalize_text(" ".join(paragraph_lines))
    return None


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse YAML-style frontmatter from the start of a markdown document.

    Returns a dict of key-value pairs. Returns empty dict if no frontmatter found.
    Only supports simple scalar values (no nested YAML). Stdlib-only.
    """
    if not text.startswith("---"):
        return {}
    lines = text.split("\n")
    if len(lines) < 3:
        return {}
    # Find closing ---
    end_index = None
    for i in range(1, len(lines)):
        stripped = lines[i].strip()
        if stripped == "---":
            end_index = i
            break
    if end_index is None or end_index < 2:
        return {}

    result: dict[str, str] = {}
    for line in lines[1:end_index]:
        match = FRONTMATTER_FIELD.match(line.strip())
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip().strip("\"'")
            result[key] = value
    return result


def extract_keywords(
    lines: list[str],
    headings: list[str],
    relative_path: str,
    anchors: set[str],
) -> list[str]:
    """Extract a bounded set of keywords from document content.

    Sources: headings, path segments, anchor name parts, high-frequency body terms.
    """
    keyword_counter: Counter[str] = Counter()

    # From headings — strong signal
    for heading in headings:
        for word in WORD_TOKEN.findall(heading):
            token = word.lower()
            if token not in KEYWORD_STOPWORDS and len(token) >= 3:
                keyword_counter[token] += 3

    # From path segments
    path_stem = relative_path.replace("/", " ").replace("_", " ").replace("-", " ")
    path_stem = re.sub(r"\b[vV]\s*\d+\b", "", path_stem)  # strip version suffixes
    path_stem = re.sub(r"\b\d+\b", "", path_stem)  # strip pure numbers
    path_stem = re.sub(r"\.md$", "", path_stem)
    for word in WORD_TOKEN.findall(path_stem):
        token = word.lower()
        if token not in KEYWORD_STOPWORDS and len(token) >= 3:
            keyword_counter[token] += 2

    # From anchor name parts (e.g., ARCH:BenchmarkFieldSemantics → benchmark, field, semantics)
    for anchor in anchors:
        parts = anchor.split(":", 1)
        if len(parts) == 2:
            # Split camelCase and dot-separated
            name = parts[1]
            name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
            name = name.replace(".", " ").replace("-", " ").replace("_", " ")
            for word in WORD_TOKEN.findall(name):
                token = word.lower()
                if token not in KEYWORD_STOPWORDS and len(token) >= 3:
                    keyword_counter[token] += 2

    # From body text — frequency signal (only significant terms)
    in_code_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped.startswith("#") or stripped.startswith("|") or stripped.startswith("- **"):
            continue  # already captured via headings/metadata
        for word in WORD_TOKEN.findall(stripped):
            token = word.lower()
            if token not in KEYWORD_STOPWORDS and len(token) >= 3:
                keyword_counter[token] += 1

    # Return top keywords by count, capped
    return [kw for kw, _ in keyword_counter.most_common(MAX_KEYWORDS_PER_DOC)]


KEYWORD_STOPWORDS = frozenset({
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "been",
    "being", "have", "has", "had", "does", "did", "will", "would", "could", "should",
    "may", "might", "shall", "can", "not", "but", "also", "into", "about", "over",
    "such", "each", "all", "any", "both", "few", "more", "most", "other", "some",
    "than", "too", "very", "just", "because", "before", "after", "during", "between",
    "through", "above", "below", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "which", "who", "whom", "what", "these",
    "those", "its", "own", "same", "only", "use", "used", "using", "see", "must",
    "need", "new", "per", "one", "two", "yes", "file", "line", "text", "note",
    "example", "section", "document", "table", "based", "ensure", "make", "like",
})

MAX_KEYWORDS_PER_DOC = 15


def build_document_entry(root: Path, file_path: Path) -> dict:
    relative_path = file_path.relative_to(root).as_posix()
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Parse frontmatter (if present)
    frontmatter = parse_frontmatter(text)

    # Classify with possible frontmatter overrides
    meta = classify_document(relative_path)
    fm_status = frontmatter.get("status")
    fm_canonical = frontmatter.get("canonical")
    effective_status = fm_status if fm_status else meta.lifecycle
    effective_canonical = meta.canonical
    if fm_canonical is not None:
        effective_canonical = fm_canonical.lower() in ("true", "yes", "1")
    effective_rank = authority_rank_for(effective_status, effective_canonical) if fm_status or fm_canonical else meta.authority_rank

    title = first_heading(lines) or file_path.stem.replace("_", " ")
    headings = [normalize_text(match.group(2)) for line in lines if (match := HEADING_PATTERN.match(line))]
    mentioned_anchors: set[str] = set()
    defined_anchors: set[str] = set()
    for line in lines:
        anchors_in_line = ANCHOR_PATTERN.findall(line)
        if not anchors_in_line:
            continue
        mentioned_anchors.update(anchors_in_line)

        lower_line = line.lower()
        heading_match = HEADING_PATTERN.match(line)
        if ("stable" in lower_line and "anchor" in lower_line) or heading_match:
            defined_anchors.update(anchors_in_line)

    anchors = sorted(mentioned_anchors)
    description = extract_description(lines)
    status_text = extract_status(lines)

    # Extract keywords
    keywords = extract_keywords(lines, headings, relative_path, mentioned_anchors)

    # Frontmatter declared date
    declared_last_updated = frontmatter.get("last_updated") or frontmatter.get("lastUpdated") or None

    return {
        "path": relative_path,
        "title": title,
        "description": description,
        "status": effective_status,
        "status_detail": status_text,
        "canonical": effective_canonical,
        "authority_rank": effective_rank,
        "domains": meta.domains,
        "keywords": keywords,
        "anchors": anchors,
        "defined_anchors": sorted(defined_anchors),
        "mentioned_anchors": anchors,
        "headings": headings,
        "declared_last_updated": declared_last_updated,
        "source_modified_utc": datetime_to_iso(file_path.stat().st_mtime),
    }


def build_relationships(documents: list[dict]) -> None:
    """Second pass: detect cross-document relationships via anchor references and path mentions."""
    # Build lookup: anchor → defining document path
    anchor_to_definer: dict[str, str] = {}
    for doc in documents:
        for anchor in doc.get("defined_anchors", []):
            anchor_to_definer[anchor] = doc["path"]

    # Build set of known paths for path-reference detection
    known_paths = {doc["path"] for doc in documents}

    for doc in documents:
        references: set[str] = set()
        referenced_by: set[str] = set()

        # Anchor-based: this doc mentions anchors defined elsewhere
        for anchor in doc.get("mentioned_anchors", []):
            definer_path = anchor_to_definer.get(anchor)
            if definer_path and definer_path != doc["path"]:
                references.add(definer_path)

        doc["relationships"] = {
            "references": sorted(references),
            "referenced_by": [],  # populated in second loop
        }

    # Reverse pass: populate referenced_by
    for doc in documents:
        for ref_path in doc["relationships"]["references"]:
            for target_doc in documents:
                if target_doc["path"] == ref_path:
                    if doc["path"] not in target_doc["relationships"]["referenced_by"]:
                        target_doc["relationships"]["referenced_by"].append(doc["path"])
                    break

    # Sort referenced_by for deterministic output
    for doc in documents:
        doc["relationships"]["referenced_by"] = sorted(doc["relationships"]["referenced_by"])


def build_index(root: Path) -> dict:
    documents = [build_document_entry(root, file_path) for file_path in iter_markdown_files(root)]
    documents.sort(key=lambda item: item["path"])
    build_relationships(documents)
    return {
        "generated_at_utc": utc_now_iso(),
        "repository_root": str(root),
        "document_count": len(documents),
        "documents": documents,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a markdown retrieval index for the repository.")
    parser.add_argument("--root", default=None, help="Repository root. Defaults to the parent repository of this script.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path. Defaults to src/9. Agent Tools/indexing/AGENT_INDEX.json under the repository root.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve() if args.root else repo_root_from_script()
    output_path = Path(args.output).resolve() if args.output else root / "src" / "9. Agent Tools" / "indexing" / "AGENT_INDEX.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    index = build_index(root)
    json_text = json.dumps(index, indent=2 if args.pretty or True else None, ensure_ascii=False)
    output_path.write_text(f"{json_text}\n", encoding="utf-8")

    print(f"Generated index with {index['document_count']} documents -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

