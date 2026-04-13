# Glimmer — Workstream H Deep Research Design and Implementation Plan

## Document Metadata

- **Document Title:** Glimmer — Workstream H Deep Research Design and Implementation Plan
- **Document Type:** Working Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** H — Deep Research and External Reasoning
- **Primary Companion Documents:** Workstream H Build Plan, Requirements, Architecture, Verification Pack

---

## 1. Purpose

This document records the active implementation plan for **Workstream H — Deep Research and External Reasoning**.

It captures the intended implementation approach, target file areas, linked anchors, expected tests, and human dependencies for the Python port of the operator's existing C# research agent and its integration into Glimmer.

---

## 2. Active Scope

### 2.1 What this workstream implements

- Python-native browser-mediated research adapter (ported from existing C# / .NET research agent)
- Chrome debug-mode attachment using Playwright
- Gemini interaction flow (navigation, query submission, response capture)
- Research domain models (ResearchRun, ResearchFinding, ResearchSourceReference, ResearchSummaryArtifact)
- Research run persistence and provenance
- Research Escalation Graph (orchestration integration)
- Escalation policy (explicit, policy-based, threshold-based)
- Failure and degraded-mode handling
- Research visibility in the web workspace
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

### 3.2 Architecture
- `ARCH:DeepResearchCapability`
- `ARCH:ResearchToolBoundary`
- `ARCH:GeminiBrowserMediatedAdapter`
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

### 3.3 Build plan
- `PLAN:WorkstreamH.DeepResearch`
- `PLAN:WorkstreamH.PackageH1.AdapterBoundary`
- `PLAN:WorkstreamH.PackageH2.GeminiInteraction`
- `PLAN:WorkstreamH.PackageH3.DomainAndPersistence`
- `PLAN:WorkstreamH.PackageH4.OrchestrationIntegration`
- `PLAN:WorkstreamH.PackageH5.WorkspaceVisibility`
- `PLAN:WorkstreamH.PackageH6.SafetyAndFailure`

### 3.4 Verification
- `TEST:Research.Escalation.RoutesWhenTaskRequiresDeepResearch`
- `TEST:Research.Invocation.StartsBoundedResearchRun`
- `TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult`
- `TEST:Research.Provenance.RunAndSourceTrailPersisted`
- `TEST:Research.Failure.BrowserUnavailableHandledSafely`
- `TEST:Research.Failure.GeminiInteractionFailureVisible`
- `TEST:Research.Security.NoUnboundedActionTaking`
- `TEST:Research.Output.ResultsReenterWorkflowSafely`

---

## 4. Expected File Areas

### 4.1 Backend — research adapter
- `apps/backend/app/research/` — research adapter, Gemini interaction, browser bootstrap
- `apps/backend/app/research/adapter.py` — adapter service interface
- `apps/backend/app/research/browser.py` — Chrome debug-mode attachment
- `apps/backend/app/research/gemini.py` — Gemini interaction flow
- `apps/backend/app/research/contracts.py` — request/response contracts

### 4.2 Backend — research domain models
- `apps/backend/app/models/research.py` — ResearchRun, ResearchFinding, ResearchSourceReference, ResearchSummaryArtifact

### 4.3 Backend — orchestration
- `apps/backend/app/graphs/research.py` — Research Escalation Graph
- `apps/backend/app/graphs/state.py` — research-related graph state extensions

### 4.4 Frontend — research visibility
- `apps/web/src/app/research/` or integrated into existing project/triage views

### 4.5 Tests
- `tests/test_research_adapter.py`
- `tests/test_research_models.py`
- `tests/test_research_graph.py`
- `tests/test_research_safety.py`

---

## 5. Implementation Sequence

1. **H1** — Research adapter boundary and browser bootstrap
2. **H2** — Gemini interaction flow
3. **H3** — Domain models and persistence (can proceed in parallel with H1/H2)
4. **H4** — Orchestration integration
5. **H5** — Workspace visibility
6. **H6** — Safety hardening

---

## 6. Human Dependencies

- **C# research agent source code:** Must be provided by the operator before H1/H2 implementation can begin. The agent needs to analyze the existing code to design the Python port correctly.
- **Chrome debug-mode setup:** Required for live validation of H1/H2. Not needed for contract-level testing.
- **Gemini access confirmation:** Required for end-to-end validation of H2.
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

### 7.2 Expected conceptual modules to identify from the C# source

When the C# codebase is provided, the agent should identify:

- browser bootstrap / Chrome debug attachment logic
- Playwright session management
- Gemini navigation and interaction flow
- prompt/task packaging
- response capture and normalization
- retry and failure handling
- logging and evidence capture
- orchestration-facing invocation interface

### 7.3 Python target architecture

The Python port should expose an interface such as:

```python
class ResearchAdapter:
    async def check_browser_available(self) -> bool: ...
    async def start_research_run(self, request: ResearchRequest) -> ResearchRun: ...
    async def execute_research(self, run: ResearchRun) -> ResearchResult: ...
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

Await the operator's provision of the existing C# / .NET research agent codebase. Once provided:

1. Analyze the C# code structure and identify conceptual modules.
2. Produce a detailed Python port mapping.
3. Begin H1 (adapter boundary) and H3 (domain models) in parallel.

