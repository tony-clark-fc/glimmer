# Glimmer — Verification Pack: Workstream H (Deep Research and Expert Advice)

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Workstream H
- **Document Type:** Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** H — Deep Research, Expert Advice, and External Reasoning
- **Primary Companion Documents:** Test Catalog, Workstream H Build Plan, Testing Strategy

---

## 1. Purpose

This verification pack defines the expected proof targets for **Workstream H — Deep Research, Expert Advice, and External Reasoning**.

It groups the relevant `TEST:` anchors and defines the evidence expectations for proving that both the deep-research and expert-advice capabilities are implemented correctly, safely, and reviewably.

---

## 2. Scenarios in This Pack

### 2.1 Escalation, invocation, and routing

| Anchor | Layer | Status |
|---|---|---|
| `TEST:Research.Escalation.RoutesWhenTaskRequiresDeepResearch` | graph, unit | Not executed |
| `TEST:Research.Invocation.StartsBoundedResearchRun` | integration, graph | Not executed |
| `TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse` | contract, integration | Not executed |
| `TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice` | unit, graph | Not executed |

### 2.2 Adapter and interaction

| Anchor | Layer | Status |
|---|---|---|
| `TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult` | contract, manual_only | Not executed |
| `TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected` | contract, unit | Not executed |

### 2.3 Provenance and persistence

| Anchor | Layer | Status |
|---|---|---|
| `TEST:Research.Provenance.RunAndSourceTrailPersisted` | integration | Not executed |
| `TEST:ExpertAdvice.Provenance.ExchangeRecordPersisted` | integration | Not executed |

### 2.4 Failure and degraded mode

| Anchor | Layer | Status |
|---|---|---|
| `TEST:Research.Failure.BrowserUnavailableHandledSafely` | contract, integration | Not executed |
| `TEST:Research.Failure.GeminiInteractionFailureVisible` | contract, integration | Not executed |
| `TEST:ExpertAdvice.Failure.GeminiUnavailableHandledSafely` | contract, integration | Not executed |

### 2.5 Safety and security

| Anchor | Layer | Status |
|---|---|---|
| `TEST:Research.Security.NoUnboundedActionTaking` | unit, contract | Not executed |

### 2.6 Output and workflow re-entry

| Anchor | Layer | Status |
|---|---|---|
| `TEST:Research.Output.ResultsReenterWorkflowSafely` | graph, integration | Not executed |
| `TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate` | graph, integration | Not executed |

---

## 3. Evidence Expectations

### 3.1 Automated proof

The following should be provable through automated tests:

- escalation policy routing logic including expert-advice vs. deep-research distinction (unit)
- research run persistence and provenance (integration)
- expert-advice exchange persistence and provenance (integration)
- graph routing, failure handling, and review-gate behavior (graph)
- adapter contract compliance with mock/fake browser — both research and chat paths (contract)
- mode selection for expert advice (unit, contract)
- safety boundary enforcement (unit, contract)

### 3.2 Manual-only proof

The following require live environment validation:

- Chrome debug-mode attachment on the operator's machine
- live Gemini interaction and response capture (both deep research and chat)
- end-to-end research run from invocation through result display
- end-to-end expert-advice exchange from prompt to response display

These should be classified as `ManualOnly` with explicit evidence notes in the progress file.

### 3.3 Evidence recording

Evidence should be recorded in the Workstream H progress file under the verification log section. Automated test results should reference test file paths and pass/fail counts. Manual validation should include date, environment notes, and outcome description.

---

## 4. Pack Execution Guidance

This pack should be executed:

- incrementally as each work package (H1–H8) is implemented,
- with automated proof executed first,
- and manual/live proof executed when the operator's browser environment is available.

---

## 5. Relationship to Other Packs

- The **smoke pack** does not need deep-research or expert-advice proof initially.
- The **release pack** should eventually include research capability happy path, expert-advice happy path, and degraded-mode evidence.
- The **data integrity pack** should eventually include research artifact and expert-advice exchange provenance consistency checks.

---

## 6. Final Note

The deep-research and expert-advice capabilities involve a unique mix of automated and environment-dependent verification. The verification model must be honest about what can be proven automatically and what requires live operator-environment validation.

