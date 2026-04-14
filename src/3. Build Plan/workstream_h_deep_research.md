# Glimmer — Workstream H: Deep Research, Expert Advice, and External Reasoning

## Document Metadata

- **Document Title:** Glimmer — Workstream H: Deep Research, Expert Advice, and External Reasoning
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Build Strategy and Scope, Testing Strategy, Workstream C Connectors, Workstream D Triage and Prioritization

---

## 1. Purpose

This document defines the implementation strategy for **Workstream H — Deep Research, Expert Advice, and External Reasoning**.

Its purpose is to implement Glimmer's bounded external reasoning capabilities: a Python-native, browser-mediated tool that allows Glimmer to escalate tasks to Gemini when the local model is insufficient, either through deep research (async, multi-step) or expert advice (synchronous chat consultation), and to return structured artifacts into the core workflow.

This workstream is where Glimmer gains the ability to reach beyond its local inference capability for harder research and reasoning tasks, while preserving the local-first, review-first, provenance-preserving operating model.

**Stable plan anchor:** `PLAN:WorkstreamH.DeepResearch`

---

## 2. Workstream Objective

Workstream H exists to implement:

- a Python-native port of the operator's existing C# / .NET browser-mediated Gemini agent,
- a clean adapter boundary between the Gemini tool and the rest of Glimmer,
- **deep research mode**: async, fire-and-forget interaction with Gemini Deep Research, producing Google Docs artifacts,
- **expert advice mode**: synchronous chat consultation with Gemini (Fast / Thinking / Pro), returning text responses,
- orchestration integration so research and expert advice can be invoked explicitly or through escalation policy,
- structured artifact persistence (ResearchRun, ExpertAdviceExchange, findings, source references, summaries),
- escalation routing that distinguishes between deep research and expert advice based on task characteristics,
- failure and degraded-mode handling when the browser or Gemini is unavailable,
- and reviewable, provenance-preserving ingestion of results into Glimmer's workflow.

At the end of this workstream, Glimmer should be able to:

- consult Gemini synchronously for expert advice on specific questions or decisions,
- perform bounded deep research for complex multi-step investigations,
- route escalations to the appropriate mode based on task characteristics,
- and return meaningful structured results into project memory, triage, planning, or drafting.

**Stable plan anchor:** `PLAN:WorkstreamH.Objective`

---

## 3. Why This Workstream Exists as a Dedicated Workstream

The deep-research capability could have been split across Workstream C (connector boundary) and Workstream D (orchestration escalation). However, it is given a dedicated workstream because:

1. The Python port of the existing C# research agent is a substantial body of work with its own implementation sequence.
2. The browser-mediated adapter is architecturally distinct from passive source connectors.
3. The escalation policy, research run lifecycle, and artifact model form a coherent capability boundary.
4. The security implications of browser debug-mode access warrant focused attention.
5. Verification requires a mix of automated, contract-level, and manual-only proof that benefits from dedicated treatment.

**Stable plan anchor:** `PLAN:WorkstreamH.Rationale`

---

## 4. Related Requirements Anchors

This workstream directly supports:

- `REQ:DeepResearchCapability`
- `REQ:ResearchEscalationPath`
- `REQ:ResearchOutputArtifacts`
- `REQ:ResearchRunProvenance`
- `REQ:BoundedBrowserMediatedResearch`
- `REQ:ExpertAdviceCapability`
- `REQ:ExpertAdviceProvenance`
- `REQ:EscalationRouting`
- `REQ:Explainability`
- `REQ:HumanApprovalBoundaries`
- `REQ:TraceabilityAndAuditability`
- `REQ:LocalFirstOperatingModel`
- `REQ:SafeBehaviorDefaults`

**Stable plan anchor:** `PLAN:WorkstreamH.RequirementsAlignment`

---

## 5. Related Architecture Anchors

This workstream implements the architecture described by:

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
- `ARCH:ExpertAdviceCapability`
- `ARCH:ExpertAdviceExchangeModel`
- `ARCH:ExpertAdviceSubflow`
- `ARCH:ExpertAdviceEscalationPolicy`
- `ARCH:GeminiChatAdapter`
- `ARCH:ExpertAdviceReviewBoundary`
- `ARCH:ReviewGateArchitecture`

**Stable plan anchor:** `PLAN:WorkstreamH.ArchitectureAlignment`

---

## 6. Workstream Scope

### 6.1 In scope

This workstream includes:

- Python port of the existing C# / .NET Gemini automation agent core,
- Playwright-based Chrome debug-mode browser attachment,
- Gemini interaction flow for both deep research and synchronous chat,
- research adapter service boundary and internal contract,
- research domain models (ResearchRun, ResearchFinding, ResearchSourceReference, ResearchSummaryArtifact),
- expert-advice domain model (ExpertAdviceExchange),
- research run persistence and provenance,
- expert-advice exchange persistence and provenance,
- orchestration integration (Research Escalation Graph and Expert Advice Subflow),
- escalation policy implementation with routing between deep research and expert advice,
- failure and degraded-mode handling,
- result normalization and re-entry into triage/planner/drafting workflows,
- and research/expert-advice visibility in the web workspace.

**Stable plan anchor:** `PLAN:WorkstreamH.InScope`

### 6.2 Out of scope

This workstream does **not** include:

- general autonomous web browsing or desktop automation,
- interaction with any web service other than Gemini (for MVP),
- autonomous action-taking based on research results,
- replacement of the local model for routine tasks,
- or expansion of browser automation to mail, calendar, or other sensitive surfaces.

**Stable plan anchor:** `PLAN:WorkstreamH.OutOfScope`

---

## 7. Implementation Outcome Expected

By the end of Workstream H, Glimmer should be able to:

- accept a deep-research request (from the operator or from orchestration escalation),
- attach to the operator's Chrome browser through the debug protocol,
- interact with Gemini to execute a bounded research task,
- capture and structure the response into research artifacts,
- persist the research run with full provenance,
- surface research results in the web workspace for review,
- route research outputs into downstream workflows (triage, planner, drafting),
- and handle browser/Gemini failures gracefully with visible degradation.

**Stable plan anchor:** `PLAN:WorkstreamH.ExpectedOutcome`

---

## 8. Implementation Packages

### 8.1 Work Package H1 — Research adapter boundary and browser bootstrap

**Objective:** Establish the Python research adapter boundary and Chrome debug-mode attachment.

#### In scope
- research adapter service interface / contract
- Chrome debug-mode attachment using Playwright
- browser availability detection and health check
- basic session lifecycle (connect, verify, disconnect)
- adapter abstraction that hides raw Playwright details from the rest of the codebase

#### Expected outputs
- research adapter boundary module
- browser bootstrap and attachment logic
- tests for adapter contract, connection, and failure handling (contract-level with mocks)

#### Related anchors
- `ARCH:GeminiBrowserMediatedAdapter`
- `ARCH:ResearchToolBoundary`
- `ARCH:BrowserResearchSecurityBoundary`

#### Definition of done
- the codebase has a clean, bounded research adapter entrypoint that can detect and attach to a Chrome debug session without leaking Playwright details

**Stable plan anchor:** `PLAN:WorkstreamH.PackageH1.AdapterBoundary`

---

### 8.2 Work Package H2 — Gemini interaction flow

**Objective:** Implement the Gemini interaction flow through the browser adapter.

#### In scope
- Gemini page navigation and session verification
- research query submission
- response capture and extraction
- retry and timeout handling
- whitelisted destination enforcement

#### Expected outputs
- Gemini interaction module within the adapter
- response capture and normalization logic
- tests for interaction flow (contract-level with mocks, manual validation for live browser)

#### Related anchors
- `ARCH:GeminiBrowserMediatedAdapter`
- `ARCH:ResearchAdapterSafetyBoundary`

#### Definition of done
- the adapter can submit a research query to Gemini through the operator's browser and capture a structured response

**Stable plan anchor:** `PLAN:WorkstreamH.PackageH2.GeminiInteraction`

---

### 8.3 Work Package H3 — Research domain models and persistence

**Objective:** Implement the research artifact domain models and persistence layer.

#### In scope
- `ResearchRun` model and repository
- `ResearchFinding` model and repository
- `ResearchSourceReference` model and repository
- `ResearchSummaryArtifact` model and repository
- research run status lifecycle (pending, in_progress, completed, failed, degraded)
- provenance fields and linkage to triggering context

#### Expected outputs
- research domain models (SQLAlchemy/Pydantic)
- migration support
- repository layer
- tests for persistence, provenance, and status transitions

#### Related anchors
- `ARCH:ResearchRunModel`
- `ARCH:ResearchFindingModel`
- `ARCH:ResearchSourceReferenceModel`
- `ARCH:ResearchSummaryArtifactModel`
- `ARCH:ResearchArtifactModel`

#### Definition of done
- research artifacts can be created, persisted, queried, and linked to projects and workflows with full provenance

**Stable plan anchor:** `PLAN:WorkstreamH.PackageH3.DomainAndPersistence`

---

### 8.4 Work Package H4 — Research Escalation Graph and orchestration integration

**Objective:** Implement the orchestration graph that coordinates research escalation, invocation, and result re-entry.

#### In scope
- Research Escalation Graph implementation
- escalation policy logic (explicit request, task-type routing, threshold-based)
- research run invocation from graph
- result capture and artifact persistence from graph
- continuation signal back to originating workflow
- review-gate integration for research results
- failure and timeout handling in graph state

#### Expected outputs
- research escalation graph
- escalation policy module
- graph tests for happy path, failure path, and review-gate behavior

#### Related anchors
- `ARCH:ResearchEscalationGraph`
- `ARCH:ResearchEscalationPolicy`
- `ARCH:ResearchRunLifecycle`
- `ARCH:ResearchVerificationStrategy`

#### Definition of done
- the orchestration layer can invoke deep research, persist results, and route them back into downstream workflows with review-gate compliance

**Stable plan anchor:** `PLAN:WorkstreamH.PackageH4.OrchestrationIntegration`

---

### 8.5 Work Package H5 — Research visibility in the web workspace

**Objective:** Surface research runs and results in the web workspace.

#### In scope
- research run status visibility (in progress, completed, failed)
- research summary and findings display
- provenance visibility (what triggered the run, what sources were consulted)
- review controls for accepting/rejecting research results
- linkage from project/triage/draft views to associated research runs

#### Expected outputs
- research-related UI components
- browser tests for research visibility and review flows

#### Related anchors
- `ARCH:DeepResearchCapability`
- `ARCH:ResearchArtifactModel`
- `REQ:ResearchOutputArtifacts`

#### Definition of done
- the operator can see active and completed research runs, review findings, and accept or discard research results from within the workspace

**Stable plan anchor:** `PLAN:WorkstreamH.PackageH5.WorkspaceVisibility`

---

### 8.6 Work Package H6 — Failure, degraded-mode, and safety hardening

**Objective:** Harden failure handling and safety boundaries for the research capability.

#### In scope
- comprehensive failure handling (browser unavailable, debug port unreachable, Gemini timeout, interaction failure)
- graceful degradation to local-model-only behavior
- safety enforcement (whitelisted destinations, no-external-action boundary, no-credential-storage)
- audit trail completeness
- operator notification of research failures

#### Expected outputs
- hardened adapter failure handling
- safety boundary enforcement tests
- degraded-mode integration tests

#### Related anchors
- `ARCH:BrowserResearchSecurityBoundary`
- `ARCH:ResearchAdapterSafetyBoundary`
- `REQ:BoundedBrowserMediatedResearch`
- `REQ:SafeBehaviorDefaults`

#### Definition of done
- the research capability handles all expected failure modes visibly and does not silently fail, overreach, or bypass safety boundaries

**Stable plan anchor:** `PLAN:WorkstreamH.PackageH6.SafetyAndFailure`

---

### 8.7 Work Package H7 — Expert advice adapter and domain model

**Objective:** Implement the synchronous Gemini chat flow in the adapter and the ExpertAdviceExchange domain model.

#### In scope
- synchronous chat interaction flow within the Gemini adapter (mode selection, prompt entry, response capture)
- `ExpertAdviceExchange` Pydantic and SQLAlchemy models
- migration support for expert_advice_exchanges table
- repository layer for ExpertAdviceExchange
- adapter contract extension: `execute_chat(request) -> ChatResult`
- operation-lock serialization with deep research (one Gemini op at a time)

#### Expected outputs
- chat interaction module within the adapter
- ExpertAdviceExchange domain model and persistence
- tests for chat flow (contract-level with mocks), exchange persistence, and provenance

#### Related anchors
- `ARCH:GeminiChatAdapter`
- `ARCH:ExpertAdviceExchangeModel`
- `ARCH:ExpertAdviceCapability`
- `REQ:ExpertAdviceCapability`
- `REQ:ExpertAdviceProvenance`

#### Definition of done
- the adapter can send a prompt to Gemini in a selected mode and return the response text
- ExpertAdviceExchange records are persisted with full provenance

**Stable plan anchor:** `PLAN:WorkstreamH.PackageH7.ExpertAdviceAdapter`

---

### 8.8 Work Package H8 — Expert advice orchestration and routing

**Objective:** Implement the Expert Advice Subflow and escalation routing that distinguishes between deep research and expert advice.

#### In scope
- Expert Advice Subflow in the orchestration layer
- escalation routing policy (expert advice vs. deep research based on task characteristics)
- review-gate integration for expert-advice responses
- API endpoint for ad-hoc expert-advice requests
- UI surface for viewing expert-advice history and invoking consultations

#### Expected outputs
- expert advice subflow/graph node
- escalation routing policy module
- API endpoint for expert advice
- UI components for expert-advice visibility
- tests for routing, subflow lifecycle, and review-gate behavior

#### Related anchors
- `ARCH:ExpertAdviceSubflow`
- `ARCH:ExpertAdviceEscalationPolicy`
- `ARCH:ExpertAdviceReviewBoundary`
- `REQ:EscalationRouting`

#### Definition of done
- the orchestration layer can invoke expert advice and route the response back into downstream workflows
- the escalation policy correctly distinguishes between deep research and expert advice
- expert-advice exchanges are visible and reviewable in the workspace

**Stable plan anchor:** `PLAN:WorkstreamH.PackageH8.ExpertAdviceOrchestration`

---

## 9. Internal Sequencing

The recommended implementation sequence is:

1. **H1 → H2** — Adapter boundary and deep-research Gemini interaction flow
2. **H3** — Domain models and persistence for research artifacts (can proceed in parallel with H1/H2)
3. **H7** — Expert advice adapter and ExpertAdviceExchange model (shares browser bootstrap with H1, can proceed in parallel)
4. **H4** — Deep-research orchestration integration (depends on H1–H3)
5. **H8** — Expert advice orchestration and escalation routing (depends on H7 + H4)
6. **H5** — Workspace visibility for research and expert advice (depends on H3–H4, H7)
7. **H6** — Safety hardening (depends on H1–H4, H7, can proceed partially in parallel)

**Stable plan anchor:** `PLAN:WorkstreamH.InternalSequence`

---

## 10. Dependencies

### 10.1 Internal dependencies

- Workstream A foundation (runtime, persistence baseline) — already complete
- Workstream B domain model (base entity patterns, repository patterns) — already complete
- Workstream C connectors (adapter patterns, contract patterns) — already complete
- Workstream D triage and orchestration (graph patterns, escalation routing) — partially complete

### 10.2 External dependencies

- **Existing C# / .NET research agent codebase** — ✅ provided by the operator (`src/5. Working/ResearchAgentLegacyCode/`)
- **Chrome running in debug mode** — required for live validation (not for unit/contract-level testing)
- **Active Gemini access** in the operator's browser — required for end-to-end validation

### 10.3 Human dependencies

- ~~Operator must provide the C# research agent source code~~ ✅ Resolved
- Operator must confirm Chrome debug-mode setup for live validation
- Operator may need to confirm whitelisted destination policy

**Stable plan anchor:** `PLAN:WorkstreamH.Dependencies`

---

## 11. Verification Expectations

### 11.1 Verification layers

| Layer | Coverage |
|---|---|
| Unit | Escalation policy logic, result normalization, domain model rules |
| Integration | Research run persistence, provenance linkage, artifact lifecycle |
| Graph | Research Escalation Graph routing, failure handling, review-gate behavior |
| Contract | Adapter boundary (mock browser), Gemini interaction contract |
| Browser | Research visibility in workspace, review controls |
| ManualOnly | Live Chrome debug-mode attachment, live Gemini interaction, end-to-end research run |

### 11.2 Key verification anchors

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

**Stable plan anchor:** `PLAN:WorkstreamH.VerificationExpectations`

---

## 12. Definition of Done

This workstream is done when:

1. the Python Gemini adapter can attach to Chrome and interact with Gemini for both deep research and synchronous chat,
2. research runs produce structured, persisted, provenance-preserving artifacts,
3. expert-advice exchanges produce persisted, provenance-preserving consultation records,
4. the orchestration layer can invoke research or expert advice through explicit or policy-based escalation,
5. escalation routing correctly distinguishes between deep research and expert advice,
6. results re-enter triage, planner, or drafting workflows as reviewable candidates,
7. the web workspace surfaces research runs, expert-advice exchanges, and findings for operator review,
8. failure and degraded-mode handling is visibly tested,
9. safety boundaries are enforced and verified,
10. and verification evidence is recorded in the workstream progress file.

**Stable plan anchor:** `PLAN:WorkstreamH.DefinitionOfDone`

---

## 13. Final Note

This workstream gives Glimmer a meaningful capability that most local-first assistants lack: the ability to escalate to deeper external research when needed, while preserving the bounded, reviewable, provenance-preserving operating model.

The key discipline is that this capability must remain a **bounded tool**, not an unbounded autonomous web agent.

**Stable plan anchor:** `PLAN:WorkstreamH.Conclusion`

