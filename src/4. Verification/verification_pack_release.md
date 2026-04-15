# Glimmer — Verification Pack: Release

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Release
- **Document Type:** Canonical Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Test Catalog, Requirements, Architecture, Build Plan, Testing Strategy, Smoke Pack, Data Integrity Pack, Workstream Verification Packs

---

## 1. Purpose

This document defines the **release verification pack** for **Glimmer**.

Its purpose is to provide the representative cross-system proof set used to support:

- release readiness judgment,
- meaningful milestone or phase-exit confidence,
- and honest reporting of what has actually been proven.

Where workstream packs prove individual delivery slices and the data-integrity pack protects long-lived invariants, the release pack answers the practical question:

**Is Glimmer ready enough, across its most important layers, for the next serious usage or release step?**

**Stable verification anchor:** `TESTPACK:Release.ControlSurface`

---

## 2. Role of the Release Pack

The release pack is not intended to contain every test in the repository.

Its role is to compose a **high-value, representative proof set** drawn from across the major risk surfaces of the product:

- startup and baseline reachability,
- memory and provenance integrity,
- external-boundary normalization and safe intake,
- assistant-core workflow behavior,
- web workspace operator journeys,
- voice and companion boundedness where relevant,
- and cross-cutting safety boundaries such as review gates and no-auto-send discipline.

A passing release pack does not mean “nothing else matters.” It means the most important confidence checks have been executed and are in a healthy enough state to support a responsible release decision.

**Stable verification anchor:** `TESTPACK:Release.Role`

---

## 3. Relationship to the Control Surface

This verification pack is derived from and aligned to:

- the **Agentic Delivery Framework**, especially its authority model, verification model, evidence-of-completion posture, phase-exit thinking, and traceability expectations,
- the **Testing Strategy Companion**, especially automation-first proof, layered verification, Playwright/browser scope, explicit `ManualOnly` / `Deferred` handling, and release-confidence discipline,
- the **Glimmer Agentic Delivery Document Set**, which explicitly defines `verification-pack-release.md` as part of the canonical verification family,
- the **Glimmer Requirements**, especially product purpose, project memory, message ingestion, multi-account support, prioritization, draft-response workspace, voice interaction, Telegram mobile presence, explainability, privacy/least privilege, safe behavior defaults, and human approval boundaries,
- the latest **Architecture** state, especially the system boundary, structured memory, connector isolation, review-gate architecture, no-auto-send policy, UI surface map, voice layering strategy, and testing architecture,
- the **Build Plan**, **Build Strategy and Scope**, and **Governance and Process** documents, which define the phase model, workstream completion posture, evidence-backed delivery expectations, and the need for explicit release-confidence judgment,
- the **Glimmer Testing Strategy** and **Workstream G — Testing and Regression**, which define regression-pack architecture, evidence routines, cross-cutting verification, and release-oriented proof composition,
- and the current **Test Catalog**, which defines the stable `TEST:` vocabulary from which this release pack is composed.

**Stable verification anchor:** `TESTPACK:Release.ControlSurfaceAlignment`

---

## 4. Why This Pack Exists Separately

The smoke pack proves the floor is intact.
The workstream packs prove that specific delivery slices were implemented correctly.
The data-integrity pack protects the memory spine over time.

The release pack exists separately because release confidence is a **cross-system judgment**.

A release can be unsafe even when individual slices looked healthy in isolation, for example if:

- the system boots but the main operator journeys are broken,
- provenance is retained in storage but not surfaced meaningfully in review paths,
- assistant-core flows work but review/no-auto-send boundaries regress,
- or the workspace is usable while companion modes quietly create unsafe side-channel behavior.

This pack exists to catch that cross-system reality.

**Stable verification anchor:** `TESTPACK:Release.Rationale`

---

## 5. Release Verification Scope

### 5.1 In scope

This pack covers representative proof across the major release-relevant layers:

- smoke and startup baseline,
- memory/provenance integrity,
- connector intake and normalization,
- assistant-core workflow behavior,
- browser-visible operator workflows,
- voice/companion boundedness where in-scope for the current release,
- and global safety boundaries such as review-gate enforcement and no-auto-send discipline.

### 5.2 Out of scope

This pack does **not** attempt to execute every possible regression scenario.

Deeper or broader scenario coverage remains in:

- the workstream packs,
- the data-integrity pack,
- and the ongoing regression estate.

The release pack should stay selective and high-signal rather than bloated.

**Stable verification anchor:** `TESTPACK:Release.Scope`

---

## 6. Source `TEST:` Anchors Included in This Pack

This pack composes representative high-value anchors from across the canonical Test Catalog and the previously defined verification packs.

### 6.1 Canonical release anchors already defined in the Test Catalog

#### `TEST:Release.Smoke.CoreSystemBoots`
- **Scenario name:** Core system smoke path passes for release confidence
- **Layers:** `integration`, `browser`
- **Role in this pack:** Baseline release sanity check.

#### `TEST:Release.DataIntegrity.MemoryAndProvenanceRemainConsistent`
- **Scenario name:** Data-integrity regression proves memory and provenance remain consistent
- **Layers:** `integration`
- **Role in this pack:** Protects the memory spine at release time.

#### `TEST:Release.Browser.CoreOperatorJourneysPass`
- **Scenario name:** Core operator browser journeys pass in release pack
- **Layers:** `browser`
- **Role in this pack:** Protects the practical day-to-day control-room experience.

#### `TEST:Release.Graph.CoreAssistantFlowsPass`
- **Scenario name:** Core graph-driven assistant flows pass in release pack
- **Layers:** `graph`, `integration`
- **Role in this pack:** Protects the assistant core as a coherent workflow layer.

### 6.2 Representative underlying anchors composed into the release pack

#### `TEST:Smoke.BackendStarts`
- **Scenario name:** Backend starts and exposes basic health/status behavior
- **Layers:** `integration`, `api`
- **Role in this pack:** Baseline release boot proof.

#### `TEST:Smoke.FrontendStarts`
- **Scenario name:** Frontend workspace shell starts and renders
- **Layers:** `integration`, `browser`
- **Role in this pack:** Baseline release workspace-shell proof.

#### `TEST:Smoke.DatabaseConnectivity`
- **Scenario name:** Primary relational store is reachable through the application
- **Layers:** `integration`
- **Role in this pack:** Baseline release persistence reachability proof.

#### `TEST:Domain.MultiAccount.ProvenancePersistence`
- **Scenario name:** Source provenance survives persistence round trips
- **Layers:** `integration`
- **Role in this pack:** Release-grade provenance guardrail.

#### `TEST:Domain.InterpretedVsAccepted.Separation`
- **Scenario name:** Interpreted artifacts remain distinct from accepted operational state
- **Layers:** `integration`
- **Role in this pack:** Release-grade candidate-vs-accepted guardrail.

#### `TEST:Domain.SummaryRefresh.Lineage`
- **Scenario name:** Summary refresh preserves lineage and metadata
- **Layers:** `integration`
- **Role in this pack:** Release-grade summary integrity guardrail.

#### `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount`
- **Scenario name:** Google mail normalization preserves thread and account meaning
- **Layers:** `integration`, `contract`
- **Role in this pack:** Representative mail normalization proof.

#### `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread`
- **Scenario name:** Microsoft mail normalization preserves mailbox and conversation context
- **Layers:** `integration`, `contract`
- **Role in this pack:** Representative multi-provider normalization proof.

#### `TEST:Connector.Normalization.PersistBeforeInterpretation`
- **Scenario name:** Normalized source records persist before assistant-core interpretation begins
- **Layers:** `integration`, `graph`
- **Role in this pack:** Protects source-truth before workflow reasoning.

#### `TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview`
- **Scenario name:** Ambiguous project classification creates structured review state
- **Layers:** `graph`, `integration`
- **Role in this pack:** Release-grade ambiguity-handling proof.

#### `TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview`
- **Scenario name:** Uncertain extracted action remains reviewable candidate state
- **Layers:** `graph`, `integration`
- **Role in this pack:** Release-grade extraction-safety proof.

#### `TEST:Planner.FocusPack.GeneratesExplainablePriorities`
- **Scenario name:** Focus pack generation produces explainable priorities
- **Layers:** `graph`, `integration`
- **Role in this pack:** Representative planner usefulness proof.

#### `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable`
- **Scenario name:** Project-memory refresh trigger is explicit and traceable
- **Layers:** `integration`, `graph`
- **Role in this pack:** Protects memory evolution at release time.

#### `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly`
- **Scenario name:** Today view presents priorities, pressure, and rationale clearly
- **Layers:** `browser`
- **Role in this pack:** Representative daily-operator proof.

#### `TEST:UI.TriageView.ShowsProvenanceAndReviewControls`
- **Scenario name:** Triage view shows provenance, ambiguity, and review controls
- **Layers:** `browser`
- **Role in this pack:** Representative reviewability/provenance proof.

#### `TEST:UI.DraftWorkspace.ShowsContextAndVariants`
- **Scenario name:** Draft workspace shows linked context and draft variants clearly
- **Layers:** `browser`
- **Role in this pack:** Representative drafting-surface proof.

#### `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious`
- **Scenario name:** Review queue makes pending vs accepted state obvious
- **Layers:** `browser`
- **Role in this pack:** Representative approval-surface clarity proof.

#### `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- **Scenario name:** Draft workflow does not create outbound send behavior
- **Layers:** `graph`, `api`, `integration`
- **Role in this pack:** Release-grade no-auto-send protection.

#### `TEST:Security.NoAutoSend.GlobalBoundaryPreserved`
- **Scenario name:** No-auto-send boundary is preserved across all channels
- **Layers:** `integration`, `graph`, `api`
- **Role in this pack:** Cross-surface safety proof.

#### `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`
- **Scenario name:** Externally meaningful actions require structured approval
- **Layers:** `graph`, `api`, `browser`
- **Role in this pack:** Cross-system approval-discipline proof.

### 6.3 Optional release-scope anchors when voice/companion is in scope for the release

#### `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded`
- **Scenario name:** Telegram interaction hands off to workspace when richer review is required
- **Layers:** `graph`, `browser`, `contract`
- **Role in this pack:** Include when Telegram companion behavior is part of the release scope.

#### `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions`
- **Scenario name:** Voice-derived meaningful actions still require review where appropriate
- **Layers:** `graph`, `integration`
- **Role in this pack:** Include when voice behavior is part of the release scope.

#### `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved`
- **Scenario name:** Voice and Telegram both route into the same shared core review and planning model
- **Layers:** `graph`, `integration`
- **Role in this pack:** Include when cross-channel parity is a release claim.

**Stable verification anchor:** `TESTPACK:Release.IncludedTests`

### 6.4 LLM integration release-scope anchors (when LLM layer is in scope)

#### `TEST:LLM.Orchestration.TriagePipelineUsesLLMWhenAvailable`
- **Scenario name:** Triage pipeline uses LLM classification/extraction when provider is available
- **Layers:** `integration`, `graph`
- **Role in this pack:** Proves the LLM integration is wired end-to-end, not dead code.

#### `TEST:LLM.Safety.NoAutoSendNotWeakened`
- **Scenario name:** No-auto-send boundary is preserved through the LLM integration layer
- **Layers:** `integration`, `graph`
- **Role in this pack:** Cross-cutting safety proof that LLM drafting doesn't weaken send boundary.

#### `TEST:LLM.Safety.ReviewGatesNotWeakened`
- **Scenario name:** Review gates are preserved through the LLM integration layer
- **Layers:** `integration`, `graph`
- **Role in this pack:** Proves LLM confidence → review gate behavior remains intact.

---

## 7. Release Pack Entry Table

| TEST Anchor | Scenario | Layer | Automation Status | Pack Priority | Notes |
|---|---|---|---|---|---|
| `TEST:Release.Smoke.CoreSystemBoots` | Core system smoke path passes for release confidence | `integration`, `browser` | ✅ Passing | Critical | 5 smoke tests + 33 Playwright |
| `TEST:Release.DataIntegrity.MemoryAndProvenanceRemainConsistent` | Data-integrity regression proves memory and provenance remain consistent | `integration` | ✅ Passing | Critical | 10 data_integrity tests pass |
| `TEST:Release.Graph.CoreAssistantFlowsPass` | Core graph-driven assistant flows pass in release pack | `graph`, `integration` | ✅ Passing | Critical | Triage, planner, voice, research graphs tested |
| `TEST:Release.Browser.CoreOperatorJourneysPass` | Core operator browser journeys pass in release pack | `browser` | ✅ Passing | Critical | 33 Playwright tests pass |
| `TEST:Smoke.BackendStarts` | Backend starts and exposes basic health/status behavior | `integration`, `api` | ✅ Passing | Critical | test_smoke.py |
| `TEST:Smoke.FrontendStarts` | Frontend workspace shell starts and renders | `integration`, `browser` | ✅ Passing | Critical | workspace-navigation.spec.ts |
| `TEST:Smoke.DatabaseConnectivity` | Primary relational store is reachable through the application | `integration` | ✅ Passing | Critical | test_smoke.py |
| `TEST:Domain.MultiAccount.ProvenancePersistence` | Source provenance survives persistence round trips | `integration` | ✅ Passing | Critical | test_domain_source.py |
| `TEST:Domain.InterpretedVsAccepted.Separation` | Interpreted artifacts remain distinct from accepted operational state | `integration` | ✅ Passing | Critical | test_data_integrity_pack.py |
| `TEST:Domain.SummaryRefresh.Lineage` | Summary refresh preserves lineage and metadata | `integration` | ✅ Passing | High | test_domain_summary.py |
| `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount` | Google mail normalization preserves thread and account meaning | `integration`, `contract` | ✅ Passing | High | test_connector_gmail.py (15 tests) |
| `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread` | Microsoft mail normalization preserves mailbox and conversation context | `integration`, `contract` | ✅ Passing | High | test_connector_msmail.py |
| `TEST:Connector.Normalization.PersistBeforeInterpretation` | Normalized source records persist before assistant-core interpretation begins | `integration`, `graph` | ✅ Passing | Critical | test_triage_intake.py |
| `TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview` | Ambiguous project classification creates structured review state | `graph`, `integration` | ✅ Passing | Critical | test_triage_classification.py |
| `TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview` | Uncertain extracted action remains reviewable candidate state | `graph`, `integration` | ✅ Passing | Critical | test_triage_extraction.py |
| `TEST:Planner.FocusPack.GeneratesExplainablePriorities` | Focus pack generation produces explainable priorities | `graph`, `integration` | ✅ Passing | High | test_planner_focus.py (11 tests) |
| `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable` | Project-memory refresh trigger is explicit and traceable | `integration`, `graph` | ✅ Passing | High | test_planner_refresh.py |
| `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly` | Today view presents priorities, pressure, and rationale clearly | `browser` | ✅ Passing | High | workspace-surfaces.spec.ts |
| `TEST:UI.TriageView.ShowsProvenanceAndReviewControls` | Triage view shows provenance, ambiguity, and review controls | `browser` | ✅ Passing | High | workspace-surfaces.spec.ts |
| `TEST:UI.DraftWorkspace.ShowsContextAndVariants` | Draft workspace shows linked context and draft variants clearly | `browser` | ✅ Passing | High | workspace-surfaces.spec.ts |
| `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious` | Review queue makes pending vs accepted state obvious | `browser` | ✅ Passing | High | persona-and-safety.spec.ts |
| `TEST:Drafting.NoAutoSend.BoundaryPreserved` | Draft workflow does not create outbound send behavior | `graph`, `api`, `integration` | ✅ Passing | Critical | test_projects_drafts.py + Playwright |
| `TEST:Security.NoAutoSend.GlobalBoundaryPreserved` | No-auto-send boundary is preserved across all channels | `integration`, `graph`, `api` | ✅ Passing | Critical | test_cross_surface_handoff.py |
| `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` | Externally meaningful actions require structured approval | `graph`, `api`, `browser` | ✅ Passing | Critical | test_cross_surface_handoff.py + Playwright |
| `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded` | Telegram interaction hands off to workspace when richer review is required | `graph`, `browser`, `contract` | ✅ Passing | Conditional | test_cross_surface_handoff.py |
| `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions` | Voice-derived meaningful actions still require review where appropriate | `graph`, `integration` | ✅ Passing | Conditional | test_voice_routing.py |
| `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved` | Voice and Telegram both route into the same shared core review and planning model | `graph`, `integration` | ✅ Passing | Conditional | test_cross_surface_handoff.py |
| `TEST:LLM.Orchestration.TriagePipelineUsesLLMWhenAvailable` | Triage pipeline uses LLM when provider is available | `integration`, `graph` | ✅ Passing | High | test_llm_orchestration.py + test_llm_wiring.py |
| `TEST:LLM.Safety.NoAutoSendNotWeakened` | No-auto-send preserved through LLM layer | `integration`, `graph` | ✅ Passing | Critical | test_llm_orchestration.py + test_llm_wiring.py |
| `TEST:LLM.Safety.ReviewGatesNotWeakened` | Review gates preserved through LLM layer | `integration`, `graph` | ✅ Passing | Critical | test_llm_orchestration.py + test_llm_wiring.py |
| `TEST:Triage.Pipeline.EndToEndClassificationAndExtraction` | Intake pipeline classifies and extracts from real source records | `integration`, `service` | ✅ Passing | High | test_triage_pipeline.py |
| `TEST:Triage.Pipeline.APIEndpointReturnsCorrectShape` | Manual triage API returns correct response shape | `api`, `integration` | ✅ Passing | Medium | test_triage_pipeline.py |
| `TEST:Connector.IntakeDispatch.ReferencesInvokeIntakeGraph` | Connector references invoke intake graph for triage | `integration`, `graph` | ✅ Passing | High | test_connector_dispatch.py |
| `TEST:Connector.IntakeDispatch.FullPipelineConnectorToTriage` | Full connector→persist→graph→triage chain works | `integration`, `service` | ✅ Passing | Critical | test_connector_dispatch.py |
| `TEST:Connector.IntakeDispatch.GracefulDegradationOnError` | Dispatch handles graph errors gracefully | `integration` | ✅ Passing | High | test_connector_dispatch.py |

**Stable verification anchor:** `TESTPACK:Release.EntryTable`

---

## 8. Expected Automation Shape

### 8.1 Mixed representative proof by design

The release pack should deliberately mix:

- integration proof,
- graph/workflow proof,
- API proof,
- browser proof,
- and explicit manual/deferred items where genuinely necessary.

It is meant to reflect the real cross-system confidence picture, not one isolated layer.

### 8.2 Prefer proven representative journeys over exhaustive volume

The release pack should select the most meaningful confidence checks rather than trying to replay every regression scenario.

The deeper packs remain the place for fuller coverage.

### 8.3 Explicit conditional scope for voice/companion

Voice and Telegram checks should be included in the release pack only when those capabilities are part of the actual release claim or milestone under judgment.

This keeps the pack honest and avoids pretending every release has the same scope.

### 8.4 Minimal `manual_only` use

This pack should remain primarily automated.

`ManualOnly` or `Deferred` items should be used only where the release claim genuinely depends on environment-bound validation that has not yet been automated.

**Stable verification anchor:** `TESTPACK:Release.AutomationShape`

---

## 9. Environment Assumptions

The release pack assumes the relevant lower-level packs have already been established and that the system is being evaluated in a release-like environment posture.

### 9.1 Required assumptions

Expected baseline assumptions include:

- backend runtime and persistence substrate working,
- representative test data or seeded state available,
- executable graph/API/browser harnesses,
- and explicit identification of whether voice/companion capabilities are in release scope.

### 9.2 Scope honesty matters

This pack should be run against the actual claimed release scope.

Do not present a release as voice-ready or companion-ready if those checks were not included and evaluated.

### 9.3 Live-provider posture

Core release confidence should not depend on uncontrolled production-provider environments unless the release claim itself explicitly requires that. Where such checks matter, they must be named clearly as scoped `ManualOnly` or supplemental validation.

**Stable verification anchor:** `TESTPACK:Release.EnvironmentAssumptions`

---

## 10. Execution Guidance

### 10.1 When to run this pack

This pack should normally be run:

- before a named release or serious milestone,
- before claiming phase-exit readiness,
- after major cross-cutting changes that could affect confidence across multiple workstreams,
- and whenever a human decision-maker needs a concise but honest cross-system confidence picture.

### 10.2 Failure handling

If this pack fails:

- release confidence should be treated cautiously,
- the decision should not be hidden behind passing lower-level tests,
- and reporting should explicitly state which release-relevant layer is unstable: startup, integrity, connectors, assistant core, workspace, or companion scope.

### 10.3 Relationship to lower-level packs

A failing release pack should usually trigger inspection of the relevant lower-level pack rather than ad hoc debugging with no traceability.

**Stable verification anchor:** `TESTPACK:Release.ExecutionGuidance`

---

## 11. Evidence Expectations

When the release pack is executed, evidence reporting should capture at minimum:

- execution date/time,
- the release or milestone being evaluated,
- the environment posture used,
- which included `TEST:` anchors were executed,
- pass/fail outcome,
- any `ManualOnly` checks performed,
- any `Deferred` entries and why,
- any conditional-scope exclusions such as voice or Telegram not being in scope,
- and a concise release-confidence judgment with explicit caveats.

This should be summarized in the relevant release-status or progress surface and should be easy for a human lead to understand without reconstructing the test estate from scratch.

**Stable verification anchor:** `TESTPACK:Release.EvidenceExpectations`

---

## 12. Operational Ready Definition for This Pack

The release verification pack should be considered operationally established when:

1. all included `TEST:` anchors are defined and mapped,
2. the pack selects a representative set of smoke, integrity, connector, assistant-core, workspace, and safety scenarios,
3. the inclusion/exclusion of companion/voice scenarios is explicit,
4. the pack can be run repeatably against a release-like environment posture,
5. evidence reporting produces a clear release-confidence summary,
6. and the pack is concise enough to remain practical while still being meaningful.

At that point, Glimmer has a real release-confidence surface rather than a vague sense that "most things seem okay."

**Stable verification anchor:** `TESTPACK:Release.DefinitionOfOperationalReady`

---

## 13. Relationship to the Broader Verification Estate

This pack is the top-level representative confidence surface.

It depends on:

- the smoke pack,
- the workstream packs,
- the data-integrity pack,
- and the broader ongoing regression estate.

It should not replace them.

Instead, it should let a human decision-maker ask one focused question — "are we ready enough for this release claim?" — and get an honest, evidence-backed answer.

**Stable verification anchor:** `TESTPACK:Release.RelationshipToEstate`

---

## 14. Final Note

A good release pack is not the biggest pack.

It is the most honest pack.

Its job is to make sure Glimmer does not ship on vibes, optimism, or a mountain of unprioritized test results.

It should force clarity about whether the system is truly ready at the level that matters for the release being claimed.

**Stable verification anchor:** `TESTPACK:Release.Conclusion`

---

## 15. Execution Evidence

### 15.1 Latest execution — 2026-04-14 (refreshed — connector→intake dispatch wiring)

- **Execution date:** 2026-04-14
- **Milestone evaluated:** Phase 3A+ completion — all 9 workstreams verified, full connector→intake→triage chain wired
- **Environment:** macOS development, PostgreSQL test/dev DBs, Next.js dev server for Playwright

#### Backend release pack
- **Command:** `python -m pytest tests/ -m release -q`
- **Result:** 335 passed, 470 deselected, 0 failures

#### Full backend suite
- **Command:** `python -m pytest tests/ --tb=short -q`
- **Result:** 805 passed, 0 failures

#### Per-workstream breakdown
| Workstream | Tests |
|---|---|
| smoke | 5 |
| workstream_a | 7 |
| workstream_b | 88 |
| workstream_c | 111 |
| workstream_d | 90 |
| workstream_e | 58 |
| workstream_f | 136 |
| workstream_h | 124 |
| workstream_i | 230 |
| data_integrity | 58 |
| **release** | **335** |

#### Playwright browser suite
- **Command:** `npx playwright test --reporter=list`
- **Result:** 33 passed, 0 failures

#### Release confidence judgment
- **Smoke:** ✅ All 5 smoke tests pass — backend boots, DB connected, frontend renders
- **Memory/Provenance:** ✅ Data integrity and provenance tests pass across 58 scenarios
- **Connectors:** ✅ Google/Microsoft normalization, multi-account provenance preserved, connector→intake dispatch wired and proven (111 tests)
- **Triage/Planner:** ✅ Classification, extraction, focus packs, project memory refresh, intake pipeline all tested (90 tests)
- **Workspace UI:** ✅ 33 Playwright tests — Today, Portfolio, Triage, Drafts, Research, Review all reachable with correct content
- **Safety:** ✅ No-auto-send boundary preserved across all surfaces, review gates enforced, whitelisted destinations locked
- **Research:** ✅ Adapter, lifecycle, escalation, review endpoints all tested (124 tests)
- **Voice/Companion:** ✅ Handoff, routing, safety parity all tested at contract level (136 tests)
- **LLM Integration:** ✅ Inference abstraction, prompt framework, classification, extraction, prioritization, drafting, briefing — all with fallback chains and safety invariants (230 tests)
- **LLM Wiring:** ✅ Graph/service layer wired to use LLM when available, per-task toggles, deterministic fallback on all paths (20 wiring tests)
- **Intake Pipeline:** ✅ Messages routed through triage_handoff now actually get classified and extracted (17 pipeline tests)
- **Draft Creation:** ✅ `POST /drafts` endpoint wired to `create_draft_enhanced()`, no-auto-send enforced, LLM context fields accepted (14 API tests)
- **Connector→Intake Dispatch:** ✅ `persist_and_dispatch()` closes the final gap — connector persistence feeds into intake graph → triage pipeline (18 dispatch tests)

#### Caveats
- **ManualOnly:** Chrome debug-mode + live Gemini validation not yet executed (requires operator machine setup)
- **ManualOnly:** End-to-end deep research run and expert advice exchange with live Gemini not yet validated
- **ManualOnly:** Live LLM inference validation against running LM Studio (9 live tests exist but require LM Studio running)
- **Voice/Companion:** Tested at contract/graph level, not live with real Telegram bot or audio model

#### Confidence level
**High** — all automated proof targets pass across all 9 workstreams. The system is architecturally complete through Phase 3A+ with strong verification coverage (805 backend + 33 Playwright = 838 total tests). The full connector → persist → intake graph → triage pipeline chain is now wired and proven end-to-end. No dead-code wiring gaps remain in the production pipeline. Remaining gaps are ManualOnly live-environment validations.

**Stable verification anchor:** `TESTPACK:Release.ExecutionEvidence`

### 15.2 Previous execution — 2026-04-14 (draft creation endpoint)

- **Execution date:** 2026-04-14
- **Milestone evaluated:** Phase 3A+ — all 9 workstreams verified including LLM wiring, intake pipeline, and draft creation API

#### Backend release pack
- **Result:** 317 passed, 470 deselected, 0 failures

#### Full backend suite
- **Result:** 787 passed, 0 failures

#### Confidence level
**High** — all automated proof targets passed at that time. Connector→intake chain was the final gap.

### 15.3 Previous execution — 2026-04-14 (pre-draft creation)

- **Execution date:** 2026-04-14
- **Milestone evaluated:** Phase 3A+ — all 9 workstreams verified including LLM integration wiring and intake pipeline

#### Backend release pack
- **Result:** 303 passed, 470 deselected, 0 failures

#### Full backend suite
- **Result:** 773 passed, 0 failures

#### Confidence level
**High** — all automated proof targets passed at that time.

### 15.4 Previous execution — 2026-04-14 (pre-Workstream I wiring)

- **Execution date:** 2026-04-14
- **Milestone evaluated:** Phase 3A completion — all 8 workstreams verified
- **Environment:** macOS development, SQLite test DB, Next.js dev server for Playwright

#### Backend release pack
- **Command:** `python -m pytest tests/ -m release -q`
- **Result:** 246 passed, 329 deselected, 0 failures
- **Duration:** 1.82s

#### Full backend suite
- **Command:** `python -m pytest tests/ --tb=short -q`
- **Result:** 575 passed, 0 warnings, 0 failures
- **Duration:** 4.61s

#### Playwright browser suite
- **Command:** `npx playwright test --reporter=list`
- **Result:** 33 passed, 0 failures
- **Duration:** 6.3s

#### Confidence level
**High** — all automated proof targets passed across all 8 workstreams at that time.

