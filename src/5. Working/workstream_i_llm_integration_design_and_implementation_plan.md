# Workstream I — LLM Integration Layer: Design and Implementation Plan

## Scope

Replace deterministic keyword/scoring logic with real LLM inference (Gemma 4 31B via LM Studio) for triage, classification, extraction, prioritization, drafting, and briefings. Build a clean inference abstraction that supports future voice model integration via mlx-lm.

## Infrastructure

| Component | Detail |
|---|---|
| **Inference provider** | LM Studio at `http://127.0.0.1:1234` |
| **Primary model** | `google/gemma-4-31b` (reasoning, triage, drafting) |
| **Embedding model** | `text-embedding-nomic-embed-text-v1.5` (available for future semantic retrieval) |
| **Context window** | 52,000 tokens |
| **Throughput** | ~20 tok/s on M5 Max 128GB |
| **API** | OpenAI-compatible `/v1/chat/completions`, `/v1/models` |
| **Client** | `openai` Python SDK (v1+) |

*Note: LM Studio also has `openai/gpt-oss-20b` loaded, which could serve as a fast alternative if needed.*

## Active Anchors

- `PLAN:WorkstreamI.LLMIntegration`
- `ARCH:LocalInferenceBaseline`
- `ARCH:TargetHardwareProfile`
- `ARCH:TriageGraph`
- `ARCH:PlannerGraphExplainability`
- `ARCH:DraftingGraph`
- `ARCH:Quality.Explainability`

## Work Package Sequence

| Package | Title | Status | Depends on |
|---|---|---|---|
| **I1** | Inference abstraction layer | ✅ Complete | — |
| **I2** | Prompt engineering framework | ✅ Complete | I1 |
| **I3** | LLM-powered project classification | ✅ Complete | I1, I2 |
| **I4** | LLM-powered extraction | ✅ Complete | I1, I2 |
| **I5** | LLM-enhanced prioritization & rationale | ✅ Complete | I1, I2 |
| **I6** | LLM-powered draft generation | ✅ Complete | I1, I2 |
| **I7** | LLM-enhanced briefing generation | ✅ Complete | I1, I2 |
| **I8** | Orchestration wiring & fallback strategy | ✅ Complete | I3–I7 |
| **I9** | Health/status API & live validation | ✅ Complete | I8 |

## File-Level Change Areas

### New files (inference module)
- `app/inference/__init__.py`
- `app/inference/base.py` — provider protocol, result types
- `app/inference/openai_compat.py` — LM Studio / OpenAI-compatible provider
- `app/inference/config.py` — pydantic-settings for endpoint, model, timeouts
- `app/inference/context_builder.py` — domain context → prompt context assembly
- `app/inference/response_parser.py` — LLM JSON response → validated structure
- `app/inference/prompts/` — task-specific prompt templates
- `app/inference/tasks/classification.py`
- `app/inference/tasks/extraction.py`
- `app/inference/tasks/prioritization.py`
- `app/inference/tasks/drafting.py`
- `app/inference/tasks/briefing.py`

### Modified files (orchestration wiring)
- `app/graphs/triage.py` — call LLM classification/extraction with fallback
- `app/graphs/planner.py` — call LLM prioritization enhancement with fallback
- `app/graphs/drafting.py` — call LLM draft generation with fallback
- `app/services/briefing.py` — call LLM briefing generation with fallback

### New test files
- `tests/workstream_i/` — unit and integration tests for inference module
- `tests/live/test_live_llm_connection.py` — provider health, basic completion
- `tests/live/test_live_llm_classification.py` — real classification against model
- `tests/live/test_live_llm_extraction.py` — real extraction against model
- `tests/live/test_live_llm_drafting.py` — real draft generation against model

### Modified config
- `pyproject.toml` — add `openai` dependency

## Design Decisions

### 1. Provider protocol shape

```python
class InferenceProvider(Protocol):
    async def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2000,
        response_format: dict | None = None,
    ) -> InferenceResult: ...

    async def health_check(self) -> ProviderHealth: ...
```

### 2. Fallback chain

```
LLM available? → Use LLM classification/extraction/etc.
LLM unavailable? → Use deterministic baseline (existing code)
Both fail? → Return explicit error, never silent degradation
```

### 3. Prompt template strategy

Templates stored as Python string constants (not external files) within `app/inference/prompts/`. Each template has:
- System prompt defining Glimmer's role and output format
- User prompt assembled from domain context
- Expected JSON response schema documented in the template

### 4. Token budget management

At 52K context, budget allocation per task:
- System prompt: ~500 tokens
- Project context: ~2,000 tokens (summaries of active projects)
- Message content: ~2,000 tokens (the message being triaged)
- Stakeholder context: ~500 tokens
- Response space: ~2,000 tokens
- Safety margin: ~45,000 tokens remaining

No aggressive truncation needed for typical messages.

## Safety Invariants

These must be verified in every work package:

1. LLM outputs are **interpreted candidates**, not accepted truth
2. Review gates fire on low-confidence LLM output just as they do for deterministic
3. No-auto-send boundary is not weakened
4. Provenance is not flattened by LLM processing
5. Deterministic fallback activates cleanly when LLM is unavailable
6. All 575+ existing tests continue to pass after each package

## Human Dependencies

- LM Studio must be running for live tests (operator responsibility)
- Prompt quality review after I9 (operator judgment on output quality)
- Tone calibration for drafting (operator preference)

