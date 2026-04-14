# Glimmer — Workstream H Deep Research, Expert Advice, and External Reasoning Design and Implementation Plan

## Document Metadata

- **Document Title:** Glimmer — Workstream H Deep Research, Expert Advice, and External Reasoning Design and Implementation Plan
- **Document Type:** Working Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** H — Deep Research, Expert Advice, and External Reasoning
- **Primary Companion Documents:** Workstream H Build Plan, Requirements, Architecture, Verification Pack

---

## 1. Purpose

This document records the active implementation plan for **Workstream H — Deep Research, Expert Advice, and External Reasoning**.

It captures the intended implementation approach, target file areas, linked anchors, expected tests, and human dependencies for the Python port of the operator's existing C# research agent and its integration into Glimmer.

---

## 2. Active Scope

### 2.1 What this workstream implements

- Python-native browser-mediated Gemini adapter (ported from existing C# / .NET agent)
- Chrome debug-mode attachment using Playwright
- Gemini deep-research interaction flow (navigation, query submission, Deep Research mode, response capture, Google Docs export)
- Gemini synchronous chat interaction flow (navigation, mode selection, prompt entry, response capture)
- Research domain models (ResearchRun, ResearchFinding, ResearchSourceReference, ResearchSummaryArtifact)
- Expert advice domain model (ExpertAdviceExchange)
- Research run persistence and provenance
- Expert advice exchange persistence and provenance
- Research Escalation Graph (orchestration integration)
- Expert Advice Subflow (orchestration integration)
- Escalation policy with routing between deep research and expert advice
- Failure and degraded-mode handling
- Research and expert advice visibility in the web workspace
- Safety boundary enforcement

### 2.2 What this workstream does not implement

- General web browsing or desktop automation
- Interaction with services other than Gemini (MVP)
- Autonomous action-taking based on research results
- Replacement of local model for routine tasks

---

## 3. Linked Control Anchors

### 3.1 Requirements
- `REQ:DeepResearchCapability`
- `REQ:ResearchEscalationPath`
- `REQ:ResearchOutputArtifacts`
- `REQ:ResearchRunProvenance`
- `REQ:BoundedBrowserMediatedResearch`
- `REQ:ExpertAdviceCapability`
- `REQ:ExpertAdviceProvenance`
- `REQ:EscalationRouting`

### 3.2 Architecture
- `ARCH:DeepResearchCapability`
- `ARCH:ResearchToolBoundary`
- `ARCH:GeminiBrowserMediatedAdapter`
- `ARCH:GeminiChatAdapter`
- `ARCH:ResearchEscalationGraph`
- `ARCH:ResearchEscalationPolicy`
- `ARCH:ResearchRunLifecycle`
- `ARCH:ResearchRunModel`
- `ARCH:ResearchFindingModel`
- `ARCH:ResearchSourceReferenceModel`
- `ARCH:ResearchSummaryArtifactModel`
- `ARCH:ResearchArtifactModel`
- `ARCH:ResearchAdapterSafetyBoundary`
- `ARCH:BrowserResearchSecurityBoundary`
- `ARCH:ResearchVerificationStrategy`
- `ARCH:ExpertAdviceCapability`
- `ARCH:ExpertAdviceExchangeModel`
- `ARCH:ExpertAdviceSubflow`
- `ARCH:ExpertAdviceEscalationPolicy`
- `ARCH:ExpertAdviceReviewBoundary`

### 3.3 Build plan
- `PLAN:WorkstreamH.DeepResearch`
- `PLAN:WorkstreamH.PackageH1.AdapterBoundary`
- `PLAN:WorkstreamH.PackageH2.GeminiInteraction`
- `PLAN:WorkstreamH.PackageH3.DomainAndPersistence`
- `PLAN:WorkstreamH.PackageH4.OrchestrationIntegration`
- `PLAN:WorkstreamH.PackageH5.WorkspaceVisibility`
- `PLAN:WorkstreamH.PackageH6.SafetyAndFailure`
- `PLAN:WorkstreamH.PackageH7.ExpertAdviceAdapter`
- `PLAN:WorkstreamH.PackageH8.ExpertAdviceOrchestration`

### 3.4 Verification
- `TEST:Research.Escalation.RoutesWhenTaskRequiresDeepResearch`
- `TEST:Research.Invocation.StartsBoundedResearchRun`
- `TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult`
- `TEST:Research.Provenance.RunAndSourceTrailPersisted`
- `TEST:Research.Failure.BrowserUnavailableHandledSafely`
- `TEST:Research.Failure.GeminiInteractionFailureVisible`
- `TEST:Research.Security.NoUnboundedActionTaking`
- `TEST:Research.Output.ResultsReenterWorkflowSafely`
- `TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse`
- `TEST:ExpertAdvice.Provenance.ExchangeRecordPersisted`
- `TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected`
- `TEST:ExpertAdvice.Failure.GeminiUnavailableHandledSafely`
- `TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice`
- `TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate`

---

## 4. Expected File Areas

### 4.1 Backend — Gemini adapter
- `apps/backend/app/research/` — adapter core, browser bootstrap, Gemini interaction
- `apps/backend/app/research/adapter.py` — unified adapter service interface
- `apps/backend/app/research/browser.py` — Chrome debug-mode attachment
- `apps/backend/app/research/gemini_research.py` — deep research interaction flow
- `apps/backend/app/research/gemini_chat.py` — synchronous chat interaction flow
- `apps/backend/app/research/contracts.py` — request/response contracts
- `apps/backend/app/research/config.py` — adapter configuration (timeouts, rate limits, modes)

### 4.2 Backend — domain models
- `apps/backend/app/models/research.py` — ResearchRun, ResearchFinding, ResearchSourceReference, ResearchSummaryArtifact, ExpertAdviceExchange

### 4.3 Backend — orchestration
- `apps/backend/app/graphs/research.py` — Research Escalation Graph
- `apps/backend/app/graphs/expert_advice.py` — Expert Advice Subflow
- `apps/backend/app/graphs/state.py` — research/expert-advice graph state extensions

### 4.4 Frontend — research and expert advice visibility
- `apps/web/src/app/research/` or integrated into existing project/triage views

### 4.5 Tests
- `tests/test_research_adapter.py`
- `tests/test_research_models.py`
- `tests/test_research_graph.py`
- `tests/test_research_safety.py`
- `tests/test_expert_advice.py`
- `tests/test_expert_advice_models.py`

---

## 5. Implementation Sequence

1. **H1** — Research adapter boundary and browser bootstrap
2. **H3** — Domain models and persistence (parallel with H1)
3. **H7** — Expert advice adapter and ExpertAdviceExchange model (parallel with H1/H3)
4. **H2** — Deep research Gemini interaction flow (depends on H1)
5. **H4** — Research orchestration integration (depends on H1–H3)
6. **H8** — Expert advice orchestration and routing (depends on H7 + H4)
7. **H5** — Workspace visibility (depends on H3–H4, H7)
8. **H6** — Safety hardening (depends on H1–H4, H7)

---

## 6. Human Dependencies

- ~~**C# research agent source code:** Must be provided by the operator before H1/H2 implementation can begin.~~ ✅ **Resolved** — source code provided at `src/5. Working/ResearchAgentLegacyCode/`
- **Chrome debug-mode setup:** Required for live validation of H1/H2/H7. Not needed for contract-level testing.
- **Gemini access confirmation:** Required for end-to-end validation of H2/H7.
- **Whitelisted destination policy:** May need operator confirmation if destinations beyond Gemini are considered.

---

## 7. Python Port Design Approach

### 7.1 Guiding principles

The Python port must:

- be idiomatic to the Glimmer Python backend (FastAPI, Pydantic, async where appropriate),
- expose a stable service interface that hides browser automation details,
- be testable without a live browser through contract-level abstractions,
- follow Glimmer's existing connector/adapter patterns from Workstream C,
- and preserve the conceptual module boundaries of the original C# agent.

### 7.2 C# source code analysis — conceptual modules identified

The C# source code has been analyzed. The following conceptual modules have been identified for porting:

| C# Module | Python Target | Description |
|---|---|---|
| `ChromeBrowserProvider` | `app/research/browser.py` | Singleton Chrome CDP attachment, auto-launch, port detection, reconnection |
| `GeminiAutomationService` (research path) | `app/research/gemini_research.py` | Deep Research flow: navigate, enter prompt, activate Deep Research, wait, export, rename |
| `GeminiAutomationService` (chat path) | `app/research/gemini_chat.py` | Synchronous chat: navigate, new chat, mode selection, prompt, response capture |
| `ResearchJobTracker` | `app/research/job_tracker.py` | In-memory job queue and rate limiting (may be replaced with DB-backed tracking) |
| `ResearchJobWorker` | `app/research/worker.py` | Background sequential job processor |
| `Models/*` | `app/research/contracts.py` + `app/models/research.py` | DTOs and domain models |

### 7.3 Key design decisions from C# analysis

1. **Single operation lock** — both chat and research share a semaphore ensuring one Gemini op at a time. Preserved in Python as `asyncio.Lock`.
2. **Multi-strategy selectors** — every UI interaction has 3-4 fallback CSS/JS strategies. Preserved in Python with ordered strategy lists.
3. **Human pacing** — randomized delays between interactions. Preserved to avoid bot detection.
4. **Chat mode selection** — supports Fast, Thinking, Pro via mode picker dropdown. Default: Pro for expert advice.
5. **Response capture** — primary: clipboard read; fallback: clipboard intercept; fallback: DOM extraction. All three strategies preserved.
6. **Research delivery** — via Google Docs export + rename. Glimmer may additionally capture text summary locally.

### 7.4 Python target architecture

The Python port should expose an interface such as:

```python
class GeminiAdapter:
    async def check_browser_available(self) -> bool: ...
    async def execute_research(self, request: ResearchRequest) -> ResearchResult: ...
    async def execute_chat(self, request: ChatRequest) -> ChatResult: ...
    @property
    def is_busy(self) -> bool: ...
```

The rest of Glimmer should depend on this contract, not on Playwright internals.

---

## 8. Assumptions

1. The existing C# research agent is functional and its design intent can be preserved in Python.
2. Chrome debug mode is a stable and supported attachment mechanism for Playwright.
3. Gemini's web interface is stable enough for bounded automation during the MVP period.
4. The operator's browser session provides authenticated access to Gemini without additional credential management.
5. The research capability is used for intermittent deep tasks, not continuous high-frequency operation.

---

## 9. Risks

1. **Gemini UI instability** — if Gemini's web interface changes frequently, the adapter may require maintenance.
2. **Browser debug mode reliability** — Chrome debug mode attachment may have edge cases on different OS versions.
3. **Scope creep** — research capability could be pressured to expand beyond Gemini into general web automation.
4. **Testing gap** — live browser/Gemini validation cannot be fully automated, creating a manual-only verification layer.

---

## 10. Next Step

C# source code has been provided and analyzed. Implementation begins with:

1. H1 — adapter boundary and Chrome debug-mode browser bootstrap
2. H3 — domain models (ResearchRun, ExpertAdviceExchange, findings, source references, summaries)
3. H7 — expert advice synchronous chat flow in the adapter
