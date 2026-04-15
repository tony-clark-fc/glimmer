"""LLM-powered entity extraction from paste-in content.

PLAN:WorkstreamE.PackageE15.PersonaPagePasteIn
ARCH:PersonaPage.PasteInPipeline
TEST:PersonaPage.PasteIn.ExtractedEntitiesAppearAsCandidateNodes

Extracts structured entities (projects, stakeholders, milestones, risks,
blockers, work items, decisions, dependencies) from operator-pasted content.

All extracted items are INTERPRETED CANDIDATES — they enter pending state
in the working mind-map and require explicit operator review.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.inference.base import InferenceError, InferenceResult
from app.inference.context_builder import assemble_messages
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.prompts.paste_in_extraction import SYSTEM_PROMPT, build_user_prompt
from app.inference.response_parser import parse_llm_response

logger = logging.getLogger(__name__)

VALID_ENTITY_TYPES = frozenset({
    "project", "stakeholder", "milestone", "risk",
    "blocker", "work_item", "decision", "dependency",
})


@dataclass
class ExtractedEntity:
    """A single entity extracted from pasted content."""

    entity_type: str
    label: str
    subtitle: str | None = None
    confidence: float = 0.5


@dataclass
class LLMPasteInExtractionResult:
    """Result of LLM-powered paste-in entity extraction.

    All entities are interpreted candidates — they enter pending state.
    """

    entities: list[ExtractedEntity] = field(default_factory=list)
    explanation: str = ""
    used_llm: bool = False
    inference_latency_ms: float = 0.0
    raw_llm_response: str | None = None

    @property
    def total_entities(self) -> int:
        return len(self.entities)

    @property
    def is_empty(self) -> bool:
        return self.total_entities == 0


async def extract_entities_from_paste_in_llm(
    provider: OpenAICompatibleProvider,
    *,
    raw_content: str,
    content_type_hint: str = "freeform",
    project_summaries: list[dict] | None = None,
) -> LLMPasteInExtractionResult:
    """Extract entities from pasted content using the LLM.

    Args:
        provider: The inference provider.
        raw_content: The raw pasted text.
        content_type_hint: What kind of content this is.
        project_summaries: Active project context for grounding.

    Returns:
        LLMPasteInExtractionResult with extracted entities and explanation.

    Raises:
        InferenceError: If the provider fails.
    """
    user_prompt = build_user_prompt(
        raw_content=raw_content,
        content_type_hint=content_type_hint,
        project_summaries=project_summaries,
    )

    messages = assemble_messages(SYSTEM_PROMPT, user_prompt)

    result: InferenceResult = await provider.chat_completion(
        messages=messages,
        temperature=0.2,
        max_tokens=2000,
    )

    parsed = parse_llm_response(
        result.content,
        required_fields=["entities", "explanation"],
    )

    if not parsed.success:
        logger.warning(
            "LLM paste-in extraction parse failed: %s (raw: %s)",
            parsed.error,
            result.content[:200],
        )
        raise InferenceError(
            f"Failed to parse paste-in extraction response: {parsed.error}",
            provider="llm_paste_in_extraction",
            detail=result.content[:500],
        )

    data = parsed.data
    assert data is not None

    entities = _normalize_entities(data.get("entities", []))
    explanation = str(data.get("explanation", "")).strip()

    if not explanation:
        explanation = (
            f"I found {len(entities)} entities in the pasted content."
            if entities
            else "I couldn't find any structured entities in the pasted content."
        )

    return LLMPasteInExtractionResult(
        entities=entities,
        explanation=explanation,
        used_llm=True,
        inference_latency_ms=result.latency_ms,
        raw_llm_response=result.content,
    )


def _normalize_entities(raw_entities: list) -> list[ExtractedEntity]:
    """Normalize and validate extracted entities."""
    normalized: list[ExtractedEntity] = []
    seen_labels: set[str] = set()

    for item in raw_entities:
        if not isinstance(item, dict):
            continue

        entity_type = str(item.get("entity_type", "")).strip().lower()
        if entity_type not in VALID_ENTITY_TYPES:
            continue

        label = str(item.get("label", "")).strip()
        if not label or len(label) > 200:
            continue

        # Deduplicate
        label_key = f"{entity_type}:{label.lower()}"
        if label_key in seen_labels:
            continue
        seen_labels.add(label_key)

        subtitle = item.get("subtitle")
        if subtitle:
            subtitle = str(subtitle).strip()[:200]

        confidence = _clamp_confidence(item.get("confidence", 0.5))

        normalized.append(ExtractedEntity(
            entity_type=entity_type,
            label=label,
            subtitle=subtitle or None,
            confidence=confidence,
        ))

    return normalized


def _clamp_confidence(value) -> float:
    """Clamp a confidence value to [0.0, 1.0]."""
    try:
        v = float(value)
        return max(0.0, min(1.0, v))
    except (TypeError, ValueError):
        return 0.5

