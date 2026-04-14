# Glimmer — Workstream I: LLM Integration Layer

## Document Metadata

- **Document Title:** Glimmer — Workstream I: LLM Integration Layer
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Build Strategy and Scope, Workstream D Triage and Prioritization, Workstream F Voice

---

## 1. Purpose

This document defines the implementation strategy for **Workstream I — LLM Integration Layer**.

Its purpose is to replace the deterministic keyword/scoring logic currently used for triage, classification, extraction, prioritization, and drafting with real local LLM inference, while preserving all existing review-gate, provenance, and safety boundaries.

This is where Glimmer gains genuine intelligence — the ability to read a message and understand what it means in project context, not just match keywords.

**Stable plan anchor:** `PLAN:WorkstreamI.LLMIntegration`

---

## 2. Workstream Objective

Workstream I exists to:

- establish a clean inference abstraction layer behind which model providers can be swapped,
- integrate the local Gemma 4 31B model (via LM Studio's OpenAI-compatible API) as the primary reasoning backend,
- replace deterministic classification with LLM-powered project classification,
- replace keyword extraction with LLM-powered action/deadline/decision extraction,
- enhance prioritization with LLM-generated rationale and contextual ranking,
- enable LLM-powered draft generation with tone and stakeholder awareness,
- enhance briefing generation with natural language synthesis,
- and prepare the inference abstraction for future E4B voice model integration via mlx-lm.

At the end of this workstream, Glimmer should produce materially better triage, extraction, prioritization, and drafting output — grounded in real language understanding rather than string matching.

**Stable plan anchor:** `PLAN:WorkstreamI.Objective`

---

## 3. Technology Baseline

### 3.1 Primary inference provider

- **LM Studio** running locally at `http://127.0.0.1:1234`
- **Model:** Gemma 4 31B (google/gemma-4-31b)
- **Context window:** 52,000 tokens
- **Throughput:** ~20 tokens/second on Apple M5 Max 128GB
- **API:** OpenAI-compatible (`/v1/chat/completions`, `/v1/models`)

### 3.2 Client library

- **`openai` Python SDK** (or `httpx` direct) against the local endpoint
- No cloud dependency — all inference is local-first

### 3.3 Future voice provider (out of scope for this workstream)

- **mlx-lm** Python library for in-process Gemma 4 E4B inference
- Will be integrated during Workstream F voice hardening
- The inference abstraction built here must accommodate this future provider

**Stable plan anchor:** `PLAN:WorkstreamI.TechnologyBaseline`

---

## 4. Architecture Alignment

### 4.1 Architecture anchors this workstream serves

- `ARCH:LocalInferenceBaseline` — local model inference for reasoning tasks
- `ARCH:TargetHardwareProfile` — M5 Max 128GB unified memory
- `ARCH:TriageGraph` — LLM-powered classification and extraction
- `ARCH:PlannerGraph` — LLM-enhanced prioritization and rationale
- `ARCH:DraftingGraph` — LLM-powered draft generation
- `ARCH:PlannerGraphExplainability` — LLM-generated explanations
- `ARCH:Quality.Explainability` — visible rationale for operator trust
- `ARCH:OrchestrationPrinciple.LowConfidenceReview` — LLM confidence → review gates
- `ARCH:VoiceInfrastructureDirection` — inference abstraction supports future multi-model

### 4.2 What this workstream must NOT change

- Review-gate enforcement — LLM outputs are still interpreted candidates, not accepted truth
- No-auto-send boundary — LLM-generated drafts still require operator review
- Provenance preservation — LLM does not flatten source identity
- Accepted vs. interpreted separation — LLM outputs do not silently harden into memory
- Stakeholder identity safety — LLM does not silently merge ambiguous identities

**Stable plan anchor:** `PLAN:WorkstreamI.ArchitectureAlignment`

---

## 5. What Exists Today (Deterministic Baseline)

The current implementation uses keyword/heuristic logic that the code explicitly marks as placeholder for LLM augmentation:

| Function | File | Current approach | LLM replacement |
|---|---|---|---|
| `classify_project()` | `graphs/triage.py` | Keyword match against project names/summaries, score 0–1 | LLM reads message + project context, produces classification with rationale |
| `resolve_stakeholders()` | `graphs/triage.py` | Exact email match against StakeholderIdentity table | Stays deterministic (identity lookup), but LLM can enhance with name inference |
| `extract_and_persist()` | `graphs/triage.py` | Caller provides pre-structured extraction dicts | LLM reads message text and extracts actions/decisions/deadlines |
| `_score_work_item()` | `graphs/planner.py` | Rule-based scoring (status, due date, urgency flag) | LLM-enhanced ranking with contextual rationale |
| `suggest_next_steps()` | `graphs/planner.py` | Rule-based: check blockers, overdue items, pending actions | LLM synthesizes project state into natural-language next-step advice |
| `generate_focus_pack()` | `graphs/planner.py` | Aggregates scored items, persists top-5 | LLM generates narrative summary and priority rationale |
| `create_draft()` | `graphs/drafting.py` | Caller provides body_content directly | LLM generates draft text from message context + stakeholder + tone |
| `generate_spoken_briefing()` | `services/briefing.py` | Template-based string formatting | LLM generates natural spoken briefing from focus pack data |

**Stable plan anchor:** `PLAN:WorkstreamI.DeterministicBaseline`

---

## 6. What Must Stay Deterministic

Not everything should be replaced by LLM inference. The following remain rule-based:

- **Stakeholder identity resolution** — exact email/identity matching is deterministic and correct; LLM may enhance with fuzzy name matching but the core lookup stays
- **Review-gate thresholds** — the decision to trigger review is based on confidence scores, not LLM judgment about whether review is needed
- **No-auto-send enforcement** — hard-coded safety boundary, never LLM-decided
- **Provenance attachment** — source account/thread/provider metadata is structural, not inferred
- **Audit logging** — deterministic record of what happened
- **Database persistence** — structured writes, not LLM-generated SQL

**Stable plan anchor:** `PLAN:WorkstreamI.DeterministicBoundary`

---

## 7. Implementation Packages

### 7.1 Work Package I1 — Inference abstraction layer

**Objective:** Build the foundational inference provider abstraction and OpenAI-compatible client.

#### In scope
- `app/inference/` module with clean provider protocol
- `InferenceProvider` base protocol: `chat_completion(messages, temperature, max_tokens, response_format) → InferenceResult`
- `OpenAICompatibleProvider` implementation targeting LM Studio at configurable endpoint
- Health check: verify model is loaded and responding
- Configuration via `pydantic-settings` (endpoint URL, model name, timeouts, default temperature)
- Graceful degradation: if LM Studio is unavailable, return a structured error (not crash)
- Add `openai` package dependency

#### Expected outputs
- `app/inference/__init__.py`
- `app/inference/base.py` — protocol/types
- `app/inference/openai_compat.py` — LM Studio provider
- `app/inference/config.py` — pydantic-settings configuration
- Unit tests for provider behavior, health check, error handling
- Integration test against running LM Studio (live test, like WS-H)

#### Related anchors
- `ARCH:LocalInferenceBaseline`
- `ARCH:TargetHardwareProfile`

#### Definition of done
- Glimmer can send a chat completion to the local model and receive a structured response
- Health check reports model availability
- Graceful fallback when LM Studio is not running

**Stable plan anchor:** `PLAN:WorkstreamI.PackageI1.InferenceAbstraction`

---

### 7.2 Work Package I2 — Prompt engineering framework

**Objective:** Build the prompt construction layer that turns domain context into well-structured LLM prompts.

#### In scope
- System prompt templates for each task type (classification, extraction, prioritization, drafting, briefing)
- Context assembly: gather relevant project summaries, stakeholder info, message content, thread history into bounded prompt context
- Token budget management: estimate context size, truncate intelligently to stay within 52K window
- Response parsing: extract structured output (JSON) from LLM responses with validation
- Prompt versioning: templates stored as named, versionable artifacts (not inline strings)

#### Expected outputs
- `app/inference/prompts/` directory with task-specific prompt templates
- `app/inference/context_builder.py` — assembles domain context for prompts
- `app/inference/response_parser.py` — validates and parses LLM JSON responses
- Unit tests for context assembly, token estimation, response parsing

#### Related anchors
- `ARCH:Quality.Explainability`
- `ARCH:GraphState.ConfidenceSignals`

#### Definition of done
- Prompt templates exist for all major task types
- Context builder can assemble bounded, relevant context from domain records
- Response parser can extract structured data from LLM JSON responses with error handling

**Stable plan anchor:** `PLAN:WorkstreamI.PackageI2.PromptFramework`

---

### 7.3 Work Package I3 — LLM-powered project classification

**Objective:** Replace keyword-based `classify_project()` with LLM-powered classification.

#### In scope
- New `llm_classify_project()` function that:
  - Assembles message content + active project summaries + stakeholder context into a prompt
  - Asks the LLM to identify the best-matching project with confidence and rationale
  - Parses the structured response into the existing `ClassificationResult` type
  - Preserves the same review-gate behavior (low confidence → needs_review)
- Fallback: if LLM is unavailable, fall back to existing deterministic classification
- Existing `classify_project()` preserved as the deterministic fallback

#### Expected outputs
- `app/inference/tasks/classification.py`
- Tests proving LLM classification produces valid ClassificationResult
- Tests proving fallback to deterministic when LLM unavailable
- Tests proving review-gate thresholds still enforced on LLM output
- Live integration test against running LM Studio

#### Related anchors
- `ARCH:TriageGraph`
- `ARCH:MessageClassificationModel`
- `ARCH:TriageGraphReviewGate`

#### Definition of done
- Project classification uses the LLM when available and produces materially better results than keyword matching
- Review gates are preserved
- Deterministic fallback works when LLM is unavailable

**Stable plan anchor:** `PLAN:WorkstreamI.PackageI3.LLMClassification`

---

### 7.4 Work Package I4 — LLM-powered extraction

**Objective:** Replace caller-provided extraction dicts with LLM-powered action/deadline/decision extraction.

#### In scope
- New `llm_extract()` function that:
  - Reads message text in project context
  - Extracts candidate actions, decisions, deadlines, and blockers
  - Returns structured output compatible with `extract_and_persist()`
  - Includes confidence per extraction
- Fallback: if LLM unavailable, caller can still provide manual extraction dicts
- Extraction prompt designed to minimize hallucination (extract only what's stated or strongly implied)

#### Expected outputs
- `app/inference/tasks/extraction.py`
- Tests for extraction quality, structure validation, confidence scoring
- Tests for hallucination resistance (no extraction from empty/irrelevant messages)
- Live integration test

#### Related anchors
- `ARCH:ExtractedActionModel`
- `ARCH:ExtractedDecisionModel`
- `ARCH:ExtractedDeadlineSignalModel`
- `ARCH:TriageGraphReviewGate`

#### Definition of done
- The LLM can read a message and produce structured extraction candidates that flow through the existing persistence and review-gate machinery

**Stable plan anchor:** `PLAN:WorkstreamI.PackageI4.LLMExtraction`

---

### 7.5 Work Package I5 — LLM-enhanced prioritization and rationale

**Objective:** Enhance focus-pack generation with LLM-generated priority rationale and contextual ranking.

#### In scope
- LLM-enhanced `generate_focus_pack()` that:
  - Takes the existing scored/ranked items
  - Asks the LLM to synthesize a natural-language priority narrative
  - Produces a "what matters most and why" summary
  - Optionally re-ranks items based on contextual understanding
- LLM-enhanced `suggest_next_steps()` with richer project-aware advice
- Deterministic scoring preserved as baseline; LLM adds narrative layer

#### Expected outputs
- `app/inference/tasks/prioritization.py`
- Tests for narrative generation, ranking stability, explainability
- Live integration test

#### Related anchors
- `ARCH:PlannerGraphExplainability`
- `ARCH:FocusPackModel`
- `ARCH:Quality.Explainability`

#### Definition of done
- Focus packs include natural-language priority rationale generated by the LLM
- Next-step suggestions are contextually richer than rule-based output

**Stable plan anchor:** `PLAN:WorkstreamI.PackageI5.LLMPrioritization`

---

### 7.6 Work Package I6 — LLM-powered draft generation

**Objective:** Enable the drafting service to generate reply drafts from context rather than requiring pre-written body content.

#### In scope
- New `llm_generate_draft()` function that:
  - Takes source message, project context, stakeholder context, and tone mode
  - Generates one or more draft variants
  - Returns structured output compatible with `create_draft()`
- Tone mode support: professional, concise, warm, direct, cautious
- Stakeholder-aware: adapts wording based on relationship and context
- No-auto-send boundary preserved: drafts are always review-required

#### Expected outputs
- `app/inference/tasks/drafting.py`
- Tests for draft generation, tone variation, stakeholder awareness
- Tests proving no-auto-send boundary is intact
- Live integration test

#### Related anchors
- `ARCH:DraftingGraph`
- `ARCH:DraftingGraphNoAutoSend`
- `ARCH:Quality.TactfulDrafting`
- `ARCH:Capability.DraftingSupport`

#### Definition of done
- Glimmer can generate contextual, stakeholder-aware reply drafts from message context
- All drafts remain review-required

**Stable plan anchor:** `PLAN:WorkstreamI.PackageI6.LLMDrafting`

---

### 7.7 Work Package I7 — LLM-enhanced briefing generation

**Objective:** Replace template-based briefing formatting with LLM-generated natural language briefings.

#### In scope
- LLM-enhanced `generate_spoken_briefing()` that produces fluid, spoken-friendly summaries
- LLM-enhanced daily/project briefings
- Bounded output length preserved (MAX_BRIEFING_LENGTH)
- Factual grounding: briefing must be based on focus-pack data, not hallucinated

#### Expected outputs
- `app/inference/tasks/briefing.py`
- Tests for output quality, length bounds, factual grounding
- Live integration test

#### Related anchors
- `ARCH:VoiceInteractionArchitecture`
- `ARCH:BriefingSurfaceArchitecture`
- `REQ:PreparedBriefings`

#### Definition of done
- Spoken briefings sound natural and conversational rather than template-formatted
- Content is grounded in real focus-pack data

**Stable plan anchor:** `PLAN:WorkstreamI.PackageI7.LLMBriefings`

---

### 7.8 Work Package I8 — Orchestration wiring and fallback strategy

**Objective:** Wire the LLM-powered functions into the existing graph/service flows with clean fallback behavior.

#### In scope
- Update triage graph flow to call LLM classification → LLM extraction → existing persistence
- Update planner flow to call LLM prioritization enhancement
- Update drafting flow to optionally use LLM draft generation
- Update briefing service to use LLM briefing generation
- Fallback chain: LLM → deterministic → explicit error (never silent failure)
- Configuration: enable/disable LLM per task type via settings
- Latency logging: track LLM call duration for operational awareness

#### Expected outputs
- Updated graph/service wiring
- Configuration for per-task LLM enable/disable
- Fallback behavior tests
- End-to-end integration tests (message in → LLM triage → persisted artifacts)

#### Related anchors
- `ARCH:OrchestrationRole`
- `ARCH:OrchestrationFailureRecovery`
- `ARCH:GraphVerificationStrategy`

#### Definition of done
- The full triage → classify → extract → prioritize → draft pipeline uses LLM when available
- Clean fallback to deterministic when LLM is unavailable
- All existing tests still pass

**Stable plan anchor:** `PLAN:WorkstreamI.PackageI8.OrchestrationWiring`

---

### 7.9 Work Package I9 — Live validation and prompt tuning

**Objective:** Validate the full LLM-integrated pipeline against realistic data and tune prompts for quality.

#### In scope
- Live integration tests against running LM Studio (like WS-H live browser tests)
- Test with realistic multi-project, multi-stakeholder scenarios
- Prompt tuning based on observed output quality
- Latency profiling: measure end-to-end triage time with LLM
- Document prompt versions and quality observations

#### Expected outputs
- `tests/live/test_live_llm_*.py` — live LLM integration tests
- Prompt tuning notes in working documents
- Latency profile data

#### Related anchors
- `ARCH:LocalInferenceBaseline`
- `ARCH:TargetHardwareProfile`

#### Definition of done
- The LLM-integrated pipeline produces demonstrably better results than deterministic baseline
- End-to-end latency is acceptable for interactive use (<30s for triage, <60s for drafting)
- Prompts are tuned and documented

**Stable plan anchor:** `PLAN:WorkstreamI.PackageI9.LiveValidation`

---

## 8. Sequencing Inside the Workstream

The recommended internal order is:

1. **I1** — Inference abstraction layer (foundation — everything depends on this)
2. **I2** — Prompt engineering framework (prompt templates and response parsing)
3. **I3** — LLM-powered project classification (first real LLM task, validates the full stack)
4. **I4** — LLM-powered extraction (builds on I3's patterns)
5. **I5** — LLM-enhanced prioritization and rationale
6. **I6** — LLM-powered draft generation
7. **I7** — LLM-enhanced briefing generation
8. **I8** — Orchestration wiring and fallback strategy (connects everything)
9. **I9** — Live validation and prompt tuning (end-to-end proof)

I1–I3 is the critical path. Once classification works end-to-end through the LLM, the remaining packages follow the same pattern.

**Stable plan anchor:** `PLAN:WorkstreamI.InternalSequence`

---

## 9. Human Dependencies

This workstream requires:

- **LM Studio running** with Gemma 4 31B loaded — already confirmed operational at 20 tok/s
- **Prompt quality review** — operator should review classification/extraction/drafting output quality during I9
- **Tone calibration** — operator input on Glimmer's drafting voice and briefing style

The coding agent can implement the full structural pipeline (I1–I8) before prompt quality review becomes blocking.

**Stable plan anchor:** `PLAN:WorkstreamI.HumanDependencies`

---

## 10. Risk and Considerations

### 10.1 Latency budget

At 20 tok/s, a 200-token classification response takes ~10 seconds. A 500-token draft takes ~25 seconds. This is acceptable for async triage but may feel slow for interactive use. Consider:
- Streaming responses for draft generation
- Caching repeated context assembly
- Using shorter prompts where full context isn't needed

### 10.2 Non-deterministic testing

LLM outputs are non-deterministic. Tests must validate structural correctness (valid JSON, correct fields, confidence in range) rather than exact text. Use `temperature=0` for test reproducibility where possible.

### 10.3 Hallucination risk

The extraction and drafting tasks must be designed to minimize hallucination:
- Extraction prompts should say "extract only what is stated or strongly implied"
- Draft generation should be grounded in provided context
- Briefings must reference only data from the focus pack

### 10.4 Memory usage

Gemma 4 31B at Q8 requires ~33GB. LM Studio manages this separately from Glimmer's Python process. On M5 Max 128GB, this leaves ~95GB for everything else — no contention concern.

### 10.5 Model unavailability

LM Studio may not always be running. The fallback strategy is:
1. Try LLM provider
2. Fall back to deterministic baseline
3. Log the fallback clearly
4. Never silently degrade without visibility

**Stable plan anchor:** `PLAN:WorkstreamI.RiskConsiderations`

---

## 11. Verification Expectations

### 11.1 Verification layers

- **Unit tests** for inference abstraction, prompt construction, response parsing
- **Integration tests** for provider health check, LLM call/response cycle
- **Task tests** for classification, extraction, prioritization, drafting, briefing output structure
- **Fallback tests** proving deterministic baseline activates when LLM unavailable
- **Safety tests** proving review gates, no-auto-send, and provenance survive LLM integration
- **Live tests** against running LM Studio (manual_only marker, like WS-H)

### 11.2 Key proof targets

- LLM classification produces valid ClassificationResult with confidence and rationale
- LLM extraction produces valid structured actions/decisions/deadlines
- LLM drafts are review-required and stakeholder-aware
- Fallback to deterministic works cleanly
- All 575+ existing tests continue to pass
- Review-gate enforcement is not weakened by LLM integration

**Stable plan anchor:** `PLAN:WorkstreamI.VerificationExpectations`

---

## 12. Relationship to Future Work

### 12.1 Voice model integration (Workstream F hardening)

The inference abstraction built in I1 will later support a second provider: `mlx-lm` for in-process Gemma 4 E4B voice model inference. The abstraction must be designed to accommodate:
- Multiple concurrent providers (LM Studio for reasoning, mlx-lm for voice)
- Provider selection by task type
- Different response formats (text vs. audio tensors)

### 12.2 Semantic retrieval / embeddings

The inference abstraction may later support embedding generation for pgvector-based semantic retrieval. This is out of scope for this workstream but the provider protocol should not preclude it.

### 12.3 Model upgrades

The OpenAI-compatible API abstraction means model upgrades (Gemma 5, different quant, etc.) require only changing the LM Studio configuration — no Glimmer code changes.

**Stable plan anchor:** `PLAN:WorkstreamI.FutureRelationships`

---

## 13. Definition of Done

Workstream I should be considered complete when all of the following are true:

1. A clean inference abstraction layer exists behind a provider protocol
2. The OpenAI-compatible provider connects to LM Studio and handles health/error/fallback
3. Project classification uses LLM inference and produces better results than keyword matching
4. Action/deadline/decision extraction uses LLM inference
5. Prioritization includes LLM-generated natural-language rationale
6. Draft generation uses LLM with tone and stakeholder awareness
7. Briefing generation uses LLM for natural spoken output
8. All LLM tasks fall back cleanly to deterministic baseline when the model is unavailable
9. All existing tests continue to pass
10. Review-gate, no-auto-send, and provenance boundaries remain intact
11. Live validation demonstrates measurably better output quality
12. The inference abstraction is designed to accommodate future voice model integration

**Stable plan anchor:** `PLAN:WorkstreamI.DefinitionOfDone`

---

## 14. Final Note

Workstream I is where Glimmer gains real intelligence.

The deterministic baseline built in Workstream D was the right starting point — it proved the workflow shape, review gates, persistence, and safety boundaries without depending on model availability. But keyword matching is not understanding.

This workstream replaces the placeholder logic with genuine language comprehension while preserving every safety guarantee that makes Glimmer trustworthy. The result should be an assistant that can actually read a message, understand its project relevance, extract what matters, explain its reasoning, and draft a thoughtful reply — all running locally on the operator's own hardware.

**Stable plan anchor:** `PLAN:WorkstreamI.Conclusion`

