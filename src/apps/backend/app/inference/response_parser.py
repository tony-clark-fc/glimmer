"""Response parser — extracts and validates JSON from LLM output.

PLAN:WorkstreamI.PackageI2.PromptFramework
TEST:LLM.Prompts.ResponseParserExtractsValidJSON
TEST:LLM.Prompts.MalformedResponseHandledGracefully

Handles the real-world messiness of LLM JSON output:
- Strips markdown code fences (```json ... ```)
- Strips leading/trailing whitespace and text outside JSON
- Validates required fields
- Returns typed ParseResult with success/failure info

Design note: Gemma 4 31B frequently wraps JSON in markdown fences
even when told not to. The parser handles this transparently.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ParseResult:
    """Result of parsing an LLM response.

    TEST:LLM.Prompts.ResponseParserExtractsValidJSON
    """

    success: bool
    data: dict | None = None
    raw_content: str = ""
    error: str | None = None
    cleaned_content: str = ""


# ── Markdown fence patterns ──────────────────────────────────────────

# Match ```json\n...\n``` or ```\n...\n```
_FENCE_PATTERN = re.compile(
    r"```(?:json)?\s*\n(.*?)\n\s*```",
    re.DOTALL,
)

# Match a top-level JSON object or array in free text
_JSON_OBJECT_PATTERN = re.compile(
    r"(\{.*\})",
    re.DOTALL,
)


def strip_markdown_fences(content: str) -> str:
    """Strip markdown code fences from LLM output.

    Handles:
    - ```json\\n{...}\\n```
    - ```\\n{...}\\n```
    - Content with text before/after the fenced block
    """
    content = content.strip()

    # Try fenced block first
    match = _FENCE_PATTERN.search(content)
    if match:
        return match.group(1).strip()

    # Check for simple ``` wrapping without json tag
    if content.startswith("```") and content.endswith("```"):
        inner = content[3:]
        if inner.endswith("```"):
            inner = inner[:-3]
        # Skip optional language tag on first line
        lines = inner.split("\n", 1)
        if len(lines) > 1 and lines[0].strip() in ("json", ""):
            return lines[1].strip()
        return inner.strip()

    return content


def extract_json_from_text(content: str) -> str:
    """Extract a JSON object from text that may contain surrounding prose.

    Falls back to returning the content as-is if no JSON object is found.
    """
    content = strip_markdown_fences(content)

    # If it already looks like JSON, return as-is
    stripped = content.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        return stripped

    # Try to find a JSON object embedded in text
    match = _JSON_OBJECT_PATTERN.search(content)
    if match:
        return match.group(1)

    return content


def parse_llm_response(
    content: str,
    required_fields: list[str] | None = None,
) -> ParseResult:
    """Parse an LLM response into validated JSON.

    Args:
        content: Raw LLM output string.
        required_fields: Optional list of top-level keys that must be present.

    Returns:
        ParseResult with success=True and data if valid,
        or success=False with error message if invalid.

    TEST:LLM.Prompts.ResponseParserExtractsValidJSON
    TEST:LLM.Prompts.MalformedResponseHandledGracefully
    """
    if not content or not content.strip():
        return ParseResult(
            success=False,
            raw_content=content or "",
            error="Empty response from model",
        )

    cleaned = extract_json_from_text(content)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.warning(
            "Failed to parse LLM JSON: %s (cleaned: %s...)",
            exc,
            cleaned[:100],
        )
        return ParseResult(
            success=False,
            raw_content=content,
            cleaned_content=cleaned,
            error=f"Invalid JSON: {exc}",
        )

    if not isinstance(data, dict):
        return ParseResult(
            success=False,
            data=None,
            raw_content=content,
            cleaned_content=cleaned,
            error=f"Expected JSON object, got {type(data).__name__}",
        )

    # Validate required fields
    if required_fields:
        missing = [f for f in required_fields if f not in data]
        if missing:
            logger.warning(
                "LLM response missing required fields: %s", missing
            )
            return ParseResult(
                success=False,
                data=data,
                raw_content=content,
                cleaned_content=cleaned,
                error=f"Missing required fields: {missing}",
            )

    return ParseResult(
        success=True,
        data=data,
        raw_content=content,
        cleaned_content=cleaned,
    )

