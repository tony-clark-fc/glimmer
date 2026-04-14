"""Unit tests — prompt framework: response parser, context builder, prompt templates.

PLAN:WorkstreamI.PackageI2.PromptFramework
TEST:LLM.Prompts.ContextBuilderAssemblesRelevantContext
TEST:LLM.Prompts.TokenBudgetRespected
TEST:LLM.Prompts.ResponseParserExtractsValidJSON
TEST:LLM.Prompts.MalformedResponseHandledGracefully

Covers:
- Response parser: fence stripping, JSON extraction, validation
- Context builder: token estimation, truncation, prompt assembly
- Prompt templates: user prompt generation for each task type
"""

from __future__ import annotations

import json
import uuid

import pytest

from app.inference.response_parser import (
    ParseResult,
    parse_llm_response,
    strip_markdown_fences,
    extract_json_from_text,
)
from app.inference.context_builder import (
    TokenBudget,
    estimate_tokens,
    truncate_to_token_budget,
    build_project_context,
    build_message_context,
    build_stakeholder_context,
    assemble_messages,
    estimate_prompt_tokens,
    DEFAULT_BUDGET,
    CHARS_PER_TOKEN,
)
from app.inference.prompts.classification import (
    SYSTEM_PROMPT as CLASSIFICATION_SYSTEM,
    build_user_prompt as build_classification_prompt,
)
from app.inference.prompts.extraction import (
    SYSTEM_PROMPT as EXTRACTION_SYSTEM,
    build_user_prompt as build_extraction_prompt,
)
from app.inference.prompts.prioritization import (
    SYSTEM_PROMPT as PRIORITIZATION_SYSTEM,
    build_user_prompt as build_prioritization_prompt,
)
from app.inference.prompts.drafting import (
    SYSTEM_PROMPT as DRAFTING_SYSTEM,
    build_user_prompt as build_drafting_prompt,
)
from app.inference.prompts.briefing import (
    SYSTEM_PROMPT as BRIEFING_SYSTEM,
    build_user_prompt as build_briefing_prompt,
)


# ═══════════════════════════════════════════════════════════════════════
# Response Parser Tests
# ═══════════════════════════════════════════════════════════════════════


class TestStripMarkdownFences:
    """TEST:LLM.Prompts.ResponseParserExtractsValidJSON — fence stripping."""

    def test_strips_json_fenced_block(self) -> None:
        content = '```json\n{"key": "value"}\n```'
        assert strip_markdown_fences(content) == '{"key": "value"}'

    def test_strips_plain_fenced_block(self) -> None:
        content = '```\n{"key": "value"}\n```'
        assert strip_markdown_fences(content) == '{"key": "value"}'

    def test_strips_fenced_block_with_surrounding_text(self) -> None:
        content = 'Here is the result:\n```json\n{"key": "value"}\n```\nDone.'
        assert strip_markdown_fences(content) == '{"key": "value"}'

    def test_returns_plain_json_unchanged(self) -> None:
        content = '{"key": "value"}'
        assert strip_markdown_fences(content) == '{"key": "value"}'

    def test_handles_multiline_json_in_fences(self) -> None:
        content = '```json\n{\n  "key": "value",\n  "num": 42\n}\n```'
        result = strip_markdown_fences(content)
        parsed = json.loads(result)
        assert parsed == {"key": "value", "num": 42}

    def test_handles_empty_string(self) -> None:
        assert strip_markdown_fences("") == ""

    def test_handles_whitespace_around_fences(self) -> None:
        content = '  ```json\n{"key": "value"}\n```  '
        assert strip_markdown_fences(content) == '{"key": "value"}'


class TestExtractJsonFromText:
    """TEST:LLM.Prompts.ResponseParserExtractsValidJSON — embedded JSON extraction."""

    def test_extracts_from_plain_json(self) -> None:
        content = '{"key": "value"}'
        assert extract_json_from_text(content) == '{"key": "value"}'

    def test_extracts_from_fenced_json(self) -> None:
        content = '```json\n{"key": "value"}\n```'
        result = extract_json_from_text(content)
        assert json.loads(result) == {"key": "value"}

    def test_extracts_json_from_surrounding_prose(self) -> None:
        content = 'The classification is: {"project": "Alpha"} as determined.'
        result = extract_json_from_text(content)
        assert json.loads(result) == {"project": "Alpha"}

    def test_returns_content_if_no_json_found(self) -> None:
        content = "No JSON here at all"
        assert extract_json_from_text(content) == "No JSON here at all"


class TestParseLlmResponse:
    """TEST:LLM.Prompts.ResponseParserExtractsValidJSON
    TEST:LLM.Prompts.MalformedResponseHandledGracefully
    """

    def test_parses_clean_json(self) -> None:
        content = '{"project": "Alpha", "confidence": 0.9}'
        result = parse_llm_response(content)
        assert result.success is True
        assert result.data == {"project": "Alpha", "confidence": 0.9}
        assert result.error is None

    def test_parses_fenced_json(self) -> None:
        content = '```json\n{"project": "Beta", "confidence": 0.8}\n```'
        result = parse_llm_response(content)
        assert result.success is True
        assert result.data["project"] == "Beta"

    def test_validates_required_fields(self) -> None:
        content = '{"project": "Alpha"}'
        result = parse_llm_response(content, required_fields=["project", "confidence"])
        assert result.success is False
        assert "confidence" in result.error

    def test_passes_when_required_fields_present(self) -> None:
        content = '{"project": "Alpha", "confidence": 0.9}'
        result = parse_llm_response(content, required_fields=["project", "confidence"])
        assert result.success is True

    def test_handles_empty_response(self) -> None:
        result = parse_llm_response("")
        assert result.success is False
        assert "Empty" in result.error

    def test_handles_none_response(self) -> None:
        result = parse_llm_response(None)
        assert result.success is False
        assert "Empty" in result.error

    def test_handles_invalid_json(self) -> None:
        result = parse_llm_response("not json at all {broken")
        assert result.success is False
        assert "Invalid JSON" in result.error

    def test_handles_json_array_instead_of_object(self) -> None:
        result = parse_llm_response("[1, 2, 3]")
        assert result.success is False
        assert "Expected JSON object" in result.error

    def test_preserves_raw_content(self) -> None:
        raw = '```json\n{"key": "val"}\n```'
        result = parse_llm_response(raw)
        assert result.raw_content == raw

    def test_result_is_frozen(self) -> None:
        result = parse_llm_response('{"key": "val"}')
        with pytest.raises(AttributeError):
            result.success = False

    def test_handles_gemma_style_output(self) -> None:
        """Real-world test: Gemma 4 wraps JSON in fences with extra text."""
        content = (
            '```json\n'
            '{"project": "Beta Migration", "confidence": 1.0, '
            '"rationale": "The message mentions PostgreSQL 17 upgrade"}\n'
            '```'
        )
        result = parse_llm_response(
            content,
            required_fields=["project", "confidence", "rationale"],
        )
        assert result.success is True
        assert result.data["project"] == "Beta Migration"
        assert result.data["confidence"] == 1.0


# ═══════════════════════════════════════════════════════════════════════
# Token Estimation Tests
# ═══════════════════════════════════════════════════════════════════════


class TestTokenEstimation:
    """TEST:LLM.Prompts.TokenBudgetRespected — token estimation."""

    def test_estimate_empty_string(self) -> None:
        assert estimate_tokens("") == 0

    def test_estimate_short_string(self) -> None:
        # "hello" = 5 chars, 5/4 = 1.25, max(1, 1) = 1
        assert estimate_tokens("hello") >= 1

    def test_estimate_typical_sentence(self) -> None:
        text = "The quick brown fox jumps over the lazy dog."
        tokens = estimate_tokens(text)
        # ~44 chars / 4 = ~11 tokens
        assert 8 <= tokens <= 15

    def test_estimate_long_text_proportional(self) -> None:
        short = "word " * 10
        long = "word " * 100
        assert estimate_tokens(long) > estimate_tokens(short)

    def test_chars_per_token_constant(self) -> None:
        assert CHARS_PER_TOKEN == 4


class TestTruncateToTokenBudget:
    """TEST:LLM.Prompts.TokenBudgetRespected — truncation."""

    def test_no_truncation_when_within_budget(self) -> None:
        text = "Short text"
        assert truncate_to_token_budget(text, 100) == text

    def test_truncation_when_over_budget(self) -> None:
        text = "word " * 200  # ~1000 chars, ~250 tokens
        result = truncate_to_token_budget(text, 50)
        assert len(result) < len(text)
        assert result.endswith("...")

    def test_truncation_at_word_boundary(self) -> None:
        text = "alpha bravo charlie delta echo foxtrot golf hotel"
        result = truncate_to_token_budget(text, 5)  # ~20 chars
        # Should end at a word boundary, not mid-word
        assert result.endswith("...")
        # The truncated part (without ...) should not end mid-word
        core = result[:-3]
        assert core == "" or core[-1] == " " or core[-1].isalpha()


class TestTokenBudget:
    """TEST:LLM.Prompts.TokenBudgetRespected — budget allocation."""

    def test_default_budget_totals(self) -> None:
        budget = TokenBudget()
        assert budget.total_window == 52000
        assert budget.system_prompt == 500
        assert budget.response_space == 2000

    def test_available_for_content(self) -> None:
        budget = TokenBudget()
        # total - system - response
        assert budget.available_for_content == 52000 - 500 - 2000

    def test_remaining_after(self) -> None:
        budget = TokenBudget()
        available = budget.available_for_content
        assert budget.remaining_after(1000) == available - 1000

    def test_remaining_never_negative(self) -> None:
        budget = TokenBudget()
        assert budget.remaining_after(999999) == 0


# ═══════════════════════════════════════════════════════════════════════
# Context Builder Tests
# ═══════════════════════════════════════════════════════════════════════


class TestBuildProjectContext:
    """TEST:LLM.Prompts.ContextBuilderAssemblesRelevantContext — projects."""

    def test_builds_from_dicts(self) -> None:
        projects = [
            {"id": "1", "name": "Alpha", "objective": "Launch product", "short_summary": "Q3 launch"},
            {"id": "2", "name": "Beta", "objective": "Migrate DB", "short_summary": "PostgreSQL 17"},
        ]
        result = build_project_context(projects)
        assert len(result) == 2
        assert result[0]["name"] == "Alpha"
        assert result[1]["name"] == "Beta"

    def test_truncates_when_over_budget(self) -> None:
        projects = [
            {"id": str(i), "name": f"Project {i}", "objective": "obj", "short_summary": "x " * 500}
            for i in range(20)
        ]
        result = build_project_context(projects, max_tokens=100)
        # Should have fewer projects than input
        assert len(result) < 20

    def test_handles_empty_list(self) -> None:
        assert build_project_context([]) == []

    def test_handles_orm_like_objects(self) -> None:
        class FakeProject:
            id = uuid.uuid4()
            name = "Gamma"
            objective = "Research"
            short_summary = "APAC expansion"
            status = "active"

        result = build_project_context([FakeProject()])
        assert len(result) == 1
        assert result[0]["name"] == "Gamma"


class TestBuildMessageContext:
    """TEST:LLM.Prompts.ContextBuilderAssemblesRelevantContext — messages."""

    def test_builds_complete_context(self) -> None:
        result = build_message_context(
            sender="alice@example.com",
            subject="Update on migration",
            body="The migration is on track.",
        )
        assert result["sender"] == "alice@example.com"
        assert result["subject"] == "Update on migration"
        assert result["body"] == "The migration is on track."

    def test_truncates_long_body(self) -> None:
        long_body = "word " * 5000  # ~25000 chars, ~6250 tokens
        result = build_message_context(
            sender="test@test.com",
            subject="Test",
            body=long_body,
            max_tokens=100,
        )
        assert len(result["body"]) < len(long_body)

    def test_handles_none_values(self) -> None:
        result = build_message_context(sender=None, subject=None, body=None)
        assert result["sender"] is None
        assert result["subject"] is None
        assert result["body"] is None


class TestBuildStakeholderContext:
    """TEST:LLM.Prompts.ContextBuilderAssemblesRelevantContext — stakeholders."""

    def test_builds_from_dicts(self) -> None:
        stakeholders = [
            {"display_name": "Alice Smith"},
            {"display_name": "Bob Jones"},
        ]
        result = build_stakeholder_context(stakeholders)
        assert result == ["Alice Smith", "Bob Jones"]

    def test_truncates_when_over_budget(self) -> None:
        stakeholders = [{"display_name": f"Name{'X' * 100} {i}"} for i in range(50)]
        result = build_stakeholder_context(stakeholders, max_tokens=50)
        assert len(result) < 50

    def test_handles_empty_list(self) -> None:
        assert build_stakeholder_context([]) == []


class TestAssembleMessages:
    """TEST:LLM.Prompts.ContextBuilderAssemblesRelevantContext — message assembly."""

    def test_produces_correct_format(self) -> None:
        messages = assemble_messages("You are Glimmer.", "Classify this message.")
        assert len(messages) == 2
        assert messages[0] == {"role": "system", "content": "You are Glimmer."}
        assert messages[1] == {"role": "user", "content": "Classify this message."}

    def test_estimate_prompt_tokens(self) -> None:
        tokens = estimate_prompt_tokens("System prompt text", "User prompt text")
        assert tokens > 0


# ═══════════════════════════════════════════════════════════════════════
# Prompt Template Tests
# ═══════════════════════════════════════════════════════════════════════


class TestClassificationPrompt:
    """TEST:LLM.Classification.ProducesValidClassificationResult — prompt shape."""

    def test_system_prompt_is_non_empty(self) -> None:
        assert len(CLASSIFICATION_SYSTEM) > 100

    def test_system_prompt_requests_json(self) -> None:
        assert "JSON" in CLASSIFICATION_SYSTEM
        assert "project_name" in CLASSIFICATION_SYSTEM
        assert "confidence" in CLASSIFICATION_SYSTEM

    def test_build_user_prompt_with_projects(self) -> None:
        prompt = build_classification_prompt(
            projects=[
                {"id": "1", "name": "Alpha", "objective": "Launch"},
                {"id": "2", "name": "Beta", "objective": "Migrate"},
            ],
            sender="alice@corp.com",
            subject="Migration update",
            body="PostgreSQL 17 upgrade is on track.",
        )
        assert "Alpha" in prompt
        assert "Beta" in prompt
        assert "alice@corp.com" in prompt
        assert "PostgreSQL 17" in prompt

    def test_build_user_prompt_empty_projects(self) -> None:
        prompt = build_classification_prompt(
            projects=[],
            sender="test@test.com",
            subject="Hello",
            body="Test message",
        )
        assert "(none)" in prompt

    def test_build_user_prompt_with_account(self) -> None:
        prompt = build_classification_prompt(
            projects=[],
            sender="test@test.com",
            subject="Hello",
            body="Test",
            source_account="work-gmail",
        )
        assert "work-gmail" in prompt


class TestExtractionPrompt:
    """TEST:LLM.Extraction.ProducesValidStructuredActions — prompt shape."""

    def test_system_prompt_is_non_empty(self) -> None:
        assert len(EXTRACTION_SYSTEM) > 100

    def test_system_prompt_defines_all_types(self) -> None:
        assert "ACTIONS" in EXTRACTION_SYSTEM
        assert "DECISIONS" in EXTRACTION_SYSTEM
        assert "DEADLINES" in EXTRACTION_SYSTEM

    def test_system_prompt_anti_hallucination(self) -> None:
        assert "hallucinate" in EXTRACTION_SYSTEM.lower()

    def test_build_user_prompt_with_context(self) -> None:
        prompt = build_extraction_prompt(
            sender="bob@example.com",
            subject="Decision on Q3 timeline",
            body="We've decided to push the launch to August 15th.",
            project_name="Alpha Launch",
            project_objective="Q3 product launch",
        )
        assert "Alpha Launch" in prompt
        assert "August 15th" in prompt

    def test_build_user_prompt_empty_body(self) -> None:
        prompt = build_extraction_prompt(
            sender="test@test.com",
            subject="Empty",
            body=None,
        )
        assert "(empty)" in prompt


class TestPrioritizationPrompt:
    """TEST:LLM.Prioritization.ProducesNarrativeRationale — prompt shape."""

    def test_system_prompt_is_non_empty(self) -> None:
        assert len(PRIORITIZATION_SYSTEM) > 100

    def test_system_prompt_requests_narrative(self) -> None:
        assert "narrative" in PRIORITIZATION_SYSTEM

    def test_build_user_prompt_with_items(self) -> None:
        prompt = build_prioritization_prompt(
            priority_items=[
                {
                    "item_id": "1",
                    "item_type": "work_item",
                    "title": "Fix login bug",
                    "priority_score": 0.85,
                    "rationale": "High urgency, blocking release",
                },
            ],
            active_projects=[{"name": "Alpha", "objective": "Launch"}],
            reply_debt_summary="3 emails awaiting reply",
        )
        assert "Fix login bug" in prompt
        assert "0.85" in prompt
        assert "3 emails" in prompt


class TestDraftingPrompt:
    """TEST:LLM.Drafting.GeneratesContextualDraft — prompt shape."""

    def test_system_prompt_is_non_empty(self) -> None:
        assert len(DRAFTING_SYSTEM) > 100

    def test_system_prompt_mentions_tone_modes(self) -> None:
        assert "concise" in DRAFTING_SYSTEM
        assert "professional" in DRAFTING_SYSTEM
        assert "warm" in DRAFTING_SYSTEM
        assert "formal" in DRAFTING_SYSTEM

    def test_system_prompt_enforces_review(self) -> None:
        assert "REVIEW" in DRAFTING_SYSTEM

    def test_build_user_prompt_reply(self) -> None:
        prompt = build_drafting_prompt(
            intent="reply",
            channel_type="email",
            tone_mode="professional",
            project_name="Alpha Launch",
            stakeholder_names=["Alice Smith"],
            original_message_summary="Alice asked about the Q3 timeline.",
            key_points=["Confirm August 15 date", "Request resource allocation"],
        )
        assert "reply" in prompt
        assert "professional" in prompt
        assert "Alice Smith" in prompt
        assert "August 15" in prompt

    def test_build_user_prompt_with_variants(self) -> None:
        prompt = build_drafting_prompt(
            intent="update",
            variant_count=2,
        )
        assert "2 alternative" in prompt


class TestBriefingPrompt:
    """TEST:LLM.Briefing.ProducesNaturalSpokenOutput — prompt shape."""

    def test_system_prompt_is_non_empty(self) -> None:
        assert len(BRIEFING_SYSTEM) > 100

    def test_system_prompt_enforces_length(self) -> None:
        assert "600" in BRIEFING_SYSTEM

    def test_system_prompt_is_spoken_oriented(self) -> None:
        assert "spoken" in BRIEFING_SYSTEM.lower()

    def test_build_user_prompt_with_data(self) -> None:
        prompt = build_briefing_prompt(
            top_actions=[
                {"title": "Review contract", "rationale": "Due tomorrow"},
            ],
            high_risk_items=[
                {"summary": "Server capacity at 90%"},
            ],
            waiting_on_items=[
                {"waiting_on": "Alice", "description": "Budget approval"},
            ],
            reply_debt_summary="2 emails pending",
            project_names=["Alpha", "Beta"],
        )
        assert "Review contract" in prompt
        assert "Server capacity" in prompt
        assert "Alice" in prompt

    def test_build_user_prompt_empty_data(self) -> None:
        prompt = build_briefing_prompt()
        assert "No focus-pack data" in prompt

