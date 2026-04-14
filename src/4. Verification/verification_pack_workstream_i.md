# Glimmer — Verification Pack: Workstream I (LLM Integration Layer)

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Workstream I
- **Document Type:** Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** I — LLM Integration Layer
- **Primary Companion Documents:** Test Catalog, Workstream I Build Plan, Testing Strategy

---

## 1. Purpose

This verification pack defines the expected proof targets for **Workstream I — LLM Integration Layer**.

It groups the relevant `TEST:` anchors and defines the evidence expectations for proving that LLM-powered triage, classification, extraction, prioritization, drafting, and briefing are implemented correctly with clean fallback, safety boundary preservation, and measurable quality improvement over the deterministic baseline.

---

## 2. Scenarios in This Pack

### 2.1 Inference abstraction and provider

| Anchor | Layer | Status |
|---|---|---|
| `TEST:LLM.Provider.OpenAICompatibleConnectsToLMStudio` | integration, live | Not started |
| `TEST:LLM.Provider.HealthCheckReportsModelAvailability` | unit, integration | Not started |
| `TEST:LLM.Provider.GracefulDegradationWhenUnavailable` | unit | Not started |
| `TEST:LLM.Provider.TimeoutHandledCleanly` | unit | Not started |
| `TEST:LLM.Provider.ChatCompletionReturnsStructuredResult` | integration, live | Not started |

### 2.2 Prompt framework and response parsing

| Anchor | Layer | Status |
|---|---|---|
| `TEST:LLM.Prompts.ContextBuilderAssemblesRelevantContext` | unit | Not started |
| `TEST:LLM.Prompts.TokenBudgetRespected` | unit | Not started |
| `TEST:LLM.Prompts.ResponseParserExtractsValidJSON` | unit | Not started |
| `TEST:LLM.Prompts.MalformedResponseHandledGracefully` | unit | Not started |

### 2.3 LLM-powered classification

| Anchor | Layer | Status |
|---|---|---|
| `TEST:LLM.Classification.ProducesValidClassificationResult` | unit, live | Not started |
| `TEST:LLM.Classification.ConfidenceAndRationalePresent` | unit, live | Not started |
| `TEST:LLM.Classification.LowConfidenceTriggersReviewGate` | unit | Not started |
| `TEST:LLM.Classification.FallsBackToDeterministicWhenUnavailable` | unit | Not started |
| `TEST:LLM.Classification.BetterThanKeywordBaseline` | live | Not started |

### 2.4 LLM-powered extraction

| Anchor | Layer | Status |
|---|---|---|
| `TEST:LLM.Extraction.ProducesValidStructuredActions` | unit, live | Not started |
| `TEST:LLM.Extraction.ConfidencePerExtractionPresent` | unit | Not started |
| `TEST:LLM.Extraction.NoHallucinationFromEmptyContent` | unit, live | Not started |
| `TEST:LLM.Extraction.FallsBackWhenUnavailable` | unit | Not started |
| `TEST:LLM.Extraction.OutputCompatibleWithPersistenceLayer` | unit | Not started |

### 2.5 LLM-enhanced prioritization

| Anchor | Layer | Status |
|---|---|---|
| `TEST:LLM.Prioritization.ProducesNarrativeRationale` | unit, live | Not started |
| `TEST:LLM.Prioritization.NextStepSuggestionsAreContextual` | live | Not started |
| `TEST:LLM.Prioritization.FallsBackToDeterministicScoring` | unit | Not started |

### 2.6 LLM-powered drafting

| Anchor | Layer | Status |
|---|---|---|
| `TEST:LLM.Drafting.GeneratesContextualDraft` | unit, live | Not started |
| `TEST:LLM.Drafting.ToneModeRespected` | live | Not started |
| `TEST:LLM.Drafting.StakeholderAwarenessPresent` | live | Not started |
| `TEST:LLM.Drafting.NoAutoSendBoundaryPreserved` | unit | Not started |
| `TEST:LLM.Drafting.FallsBackWhenUnavailable` | unit | Not started |

### 2.7 LLM-enhanced briefings

| Anchor | Layer | Status |
|---|---|---|
| `TEST:LLM.Briefing.ProducesNaturalSpokenOutput` | live | Not started |
| `TEST:LLM.Briefing.GroundedInFocusPackData` | unit, live | Not started |
| `TEST:LLM.Briefing.LengthBoundRespected` | unit | Not started |
| `TEST:LLM.Briefing.FallsBackWhenUnavailable` | unit | Not started |

### 2.8 Orchestration wiring and safety

| Anchor | Layer | Status |
|---|---|---|
| `TEST:LLM.Orchestration.TriagePipelineUsesLLMWhenAvailable` | integration | Not started |
| `TEST:LLM.Orchestration.FallbackChainWorksCleanly` | integration | Not started |
| `TEST:LLM.Orchestration.ExistingTestsSurviveIntegration` | regression | Not started |
| `TEST:LLM.Safety.ReviewGatesNotWeakened` | unit, integration | Not started |
| `TEST:LLM.Safety.ProvenanceNotFlattened` | unit | Not started |
| `TEST:LLM.Safety.NoAutoSendNotWeakened` | unit | Not started |

---

## 3. Evidence Requirements

### 3.1 Automated proof (required)

- Unit tests for provider protocol, health check, fallback, response parsing
- Unit tests for each task type producing valid output structures
- Unit tests proving safety boundaries survive LLM integration
- Integration tests for fallback chain behavior
- All 575+ existing tests still pass after integration

### 3.2 Live proof (manual_only)

- Provider connectivity against running LM Studio
- Classification quality against realistic messages
- Extraction quality against realistic messages
- Draft generation with tone and stakeholder context
- Briefing natural language quality
- End-to-end latency profiling

### 3.3 Quality comparison (manual_only)

- Side-by-side comparison of LLM vs. deterministic classification on sample messages
- Documented in progress file with specific examples

---

## 4. Relationship to Existing Verification

This pack extends the existing verification structure. It does NOT replace:

- Workstream D verification (triage/prioritization safety — those tests must continue passing)
- Workstream E verification (drafting safety — no-auto-send must survive)
- Data integrity pack (memory boundaries must survive)
- Smoke pack (startup and health must survive)

All existing verification packs must remain green after Workstream I.

---

## 5. Definition of Done for Verification

Workstream I verification is complete when:

1. All unit-level TEST anchors in this pack have passing automated tests
2. All safety-boundary tests are passing
3. All 575+ existing tests still pass
4. Live tests demonstrate quality improvement over deterministic baseline
5. Latency is documented and within acceptable bounds
6. Prompt versions are documented in working files

