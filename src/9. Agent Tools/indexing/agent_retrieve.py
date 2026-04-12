#!/usr/bin/env python3
"""Resolve likely markdown documents and bounded snippets from AGENT_INDEX.json."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ANCHOR_PATTERN = re.compile(r"\b(?:REQ|ARCH|PLAN|TEST|ADR|OPS|DATA|SEC|API):[A-Za-z0-9._-]+")
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9._:-]+")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def default_index_path(root: Path) -> Path:
    return root / "src" / "9. Agent Tools" / "indexing" / "AGENT_INDEX.json"


def load_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Index file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(query: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(query) if len(token) >= 2]


@dataclass
class Candidate:
    document: dict[str, Any]
    score: int
    reasons: list[str]


def score_document(document: dict[str, Any], query: str, tokens: list[str]) -> Candidate:
    score = document.get("authority_rank", 0)
    reasons = [f"authority_rank={document.get('authority_rank', 0)}"]
    query_normalized = normalize(query)

    defined_anchors = [anchor.lower() for anchor in document.get("defined_anchors", [])]
    mentioned_anchors = [anchor.lower() for anchor in document.get("mentioned_anchors", document.get("anchors", []))]
    title = normalize(document.get("title", ""))
    path = normalize(document.get("path", ""))
    headings = [normalize(value) for value in document.get("headings", [])]
    description = normalize(document.get("description") or "")
    keywords = [normalize(value) for value in document.get("keywords", [])]

    if query_normalized in defined_anchors:
        score += 1400
        reasons.append("exact_defined_anchor_match")
    elif query_normalized in mentioned_anchors:
        score += 900
        reasons.append("exact_anchor_reference")

    if title == query_normalized:
        score += 200
        reasons.append("exact_title_match")

    if query_normalized and query_normalized in title:
        score += 90
        reasons.append("title_contains_query")

    if query_normalized and query_normalized in path:
        score += 60
        reasons.append("path_contains_query")

    for heading in headings:
        if query_normalized and query_normalized in heading:
            score += 75
            reasons.append("heading_contains_query")
            break

    # Keyword matching — ranked below anchors/title but above description
    keyword_hits = 0
    for kw in keywords:
        if kw == query_normalized:
            score += 30
            keyword_hits += 1
        elif query_normalized and query_normalized in kw:
            score += 12
            keyword_hits += 1
    if keyword_hits:
        reasons.append(f"keyword_hits={keyword_hits}")

    token_hits = 0
    for token in tokens:
        if token in defined_anchors:
            score += 160
            token_hits += 1
            continue
        if token in mentioned_anchors:
            score += 120
            token_hits += 1
            continue
        if token in title:
            score += 40
            token_hits += 1
        if token in path:
            score += 25
        if any(token in heading for heading in headings):
            score += 20
        if any(token == kw or token in kw for kw in keywords):
            score += 15
        if token and token in description:
            score += 10

    if token_hits:
        reasons.append(f"token_hits={token_hits}")

    if document.get("canonical"):
        score += 35
        reasons.append("canonical")

    if document.get("status") == "active":
        score += 30
        reasons.append("active")
    elif document.get("status") == "working":
        score += 10
        reasons.append("working")
    elif document.get("status") in {"legacy", "superseded"}:
        score -= 20
        reasons.append(document.get("status"))

    return Candidate(document=document, score=score, reasons=reasons)


def find_best_snippet(root: Path, document: dict[str, Any], query: str, context_lines: int = 4) -> dict[str, Any] | None:
    path = root / document["path"]
    if not path.exists():
        return None

    lines = path.read_text(encoding="utf-8").splitlines()
    query_normalized = normalize(query)
    exact_anchor = query_normalized if ANCHOR_PATTERN.fullmatch(query.strip()) else None
    tokens = tokenize(query)

    target_index: int | None = None
    reason = ""

    if exact_anchor:
        for idx, line in enumerate(lines):
            normalized_line = normalize(line)
            if exact_anchor in normalized_line and "stable" in normalized_line and "anchor" in normalized_line:
                target_index = idx
                reason = "defined_anchor"
                break
            if exact_anchor in normalized_line and line.lstrip().startswith("#"):
                target_index = idx
                reason = "anchor_heading"
                break
            if exact_anchor == normalized_line:
                target_index = idx
                reason = "anchor_line"
                break
            if exact_anchor in normalized_line:
                target_index = idx
                reason = "anchor_match"
                break

    if target_index is None:
        best_score = -1
        for idx, line in enumerate(lines):
            normalized_line = normalize(line)
            line_score = 0
            if query_normalized and query_normalized in normalized_line:
                line_score += 100
            line_score += sum(8 for token in tokens if token in normalized_line)
            if line_score > best_score:
                best_score = line_score
                target_index = idx
                reason = "query_match"

    if target_index is None:
        return None

    start = max(0, target_index - context_lines)
    end = min(len(lines), target_index + context_lines + 1)
    excerpt = "\n".join(f"{line_no + 1:>4} | {lines[line_no]}" for line_no in range(start, end))

    return {
        "path": document["path"],
        "line_start": start + 1,
        "line_end": end,
        "reason": reason,
        "excerpt": excerpt,
    }


def render_text_output(candidates: list[Candidate], snippet: dict[str, Any] | None, stale_warning: str | None) -> str:
    lines: list[str] = []
    if stale_warning:
        lines.append(f"WARNING: {stale_warning}")
        lines.append("")

    if not candidates:
        return "No matching documents found."

    lines.append("Top document matches:")
    for idx, candidate in enumerate(candidates, start=1):
        doc = candidate.document
        lines.append(
            f"{idx}. {doc['path']} | score={candidate.score} | status={doc.get('status')} | canonical={doc.get('canonical')}"
        )
        if doc.get("title"):
            lines.append(f"   title: {doc['title']}")
        if doc.get("anchors"):
            lines.append(f"   anchors: {', '.join(doc['anchors'][:6])}")
        if doc.get("defined_anchors"):
            lines.append(f"   defined anchors: {', '.join(doc['defined_anchors'][:6])}")
        if doc.get("keywords"):
            lines.append(f"   keywords: {', '.join(doc['keywords'][:8])}")
        lines.append(f"   reasons: {', '.join(candidate.reasons)}")

    if snippet:
        lines.append("")
        lines.append(f"Bounded snippet from {snippet['path']} ({snippet['line_start']}-{snippet['line_end']}, {snippet['reason']}):")
        lines.append(snippet["excerpt"])

    return "\n".join(lines)


def stale_warning_for(index_path: Path, index_data: dict[str, Any]) -> str | None:
    if not index_path.exists():
        return "index file is missing"

    index_mtime = index_path.stat().st_mtime
    root = Path(index_data["repository_root"])
    newer_docs: list[str] = []
    for document in index_data.get("documents", []):
        file_path = root / document["path"]
        if file_path.exists() and file_path.stat().st_mtime > index_mtime:
            newer_docs.append(document["path"])
            if len(newer_docs) >= 3:
                break
    if newer_docs:
        return f"index may be stale; newer files detected: {', '.join(newer_docs)}"
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve likely docs and bounded snippets from AGENT_INDEX.json.")
    parser.add_argument("query", help="Anchor or free-text query.")
    parser.add_argument("--index", default=None, help="Path to AGENT_INDEX.json.")
    parser.add_argument("--top", type=int, default=5, help="Number of ranked documents to show.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--no-snippet", action="store_true", help="Skip snippet extraction.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root_from_script()
    index_path = Path(args.index).resolve() if args.index else default_index_path(root)
    index_data = load_index(index_path)
    tokens = tokenize(args.query)

    candidates = [score_document(document, args.query, tokens) for document in index_data.get("documents", [])]
    candidates = [candidate for candidate in candidates if candidate.score > 0]
    candidates.sort(key=lambda item: (-item.score, item.document["path"]))
    top_candidates = candidates[: max(1, args.top)]

    snippet = None
    if top_candidates and not args.no_snippet:
        snippet = find_best_snippet(Path(index_data["repository_root"]), top_candidates[0].document, args.query)

    stale_warning = stale_warning_for(index_path, index_data)

    if args.json:
        payload = {
            "query": args.query,
            "stale_warning": stale_warning,
            "candidates": [
                {
                    "path": candidate.document["path"],
                    "title": candidate.document.get("title"),
                    "status": candidate.document.get("status"),
                    "canonical": candidate.document.get("canonical"),
                    "score": candidate.score,
                    "reasons": candidate.reasons,
                    "defined_anchors": candidate.document.get("defined_anchors", []),
                    "anchors": candidate.document.get("anchors", []),
                    "keywords": candidate.document.get("keywords", []),
                }
                for candidate in top_candidates
            ],
            "snippet": snippet,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_text_output(top_candidates, snippet, stale_warning))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

