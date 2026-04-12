# Glimmer — Verification Pack: Workstream D Triage and Prioritization

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Workstream D Triage and Prioritization
- **Document Type:** Canonical Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Test Catalog, Requirements, Architecture, Build Plan, Testing Strategy, Workstream D Triage and Prioritization, Workstream C Verification Pack

---

## 1. Purpose

This document defines the **Workstream D verification pack** for **Glimmer**.

Its purpose is to prove that the assistant-core workflow layer created by **Workstream D — Triage and Prioritization** is real, explainable, review-safe, and structurally trustworthy.

Where Workstream C proves that external signals can enter the system without losing meaning, this pack proves that those signals can be transformed into project classification, extracted actions, reviewable interpretations, priorities, and focus guidance without silent overreach.

**Stable verification anchor:** `TESTPACK:WorkstreamD.ControlSurface`

---

## 2. Role of the Workstream D Pack

This pack exists to verify the implementation outcomes expected from the Triage and Prioritization workstream, including:

- intake routing from normalized source records,
- contextual project classification,
- stakeholder-aware interpretation support,
- extraction of actions, deadlines, decisions, blockers, and waiting-on signals,
- structured review interrupts for ambiguity,
- planner and focus-pack behavior,
- project-memory refresh integration,
- and bounded application/API exposure of triage and priority outputs.

This pack is the first verification surface that proves Glimmer’s assistant core behaves like a governable operational partner rather than a passive data store or an unbounded chat engine.

**Stable verification anchor:** `TESTPACK:WorkstreamD.Role`

---

## 3. Relationship to the Control Surface

This verification pack is derived from and aligned to:

- the **Agentic Delivery Framework**, especially its authority model, work-package operating model, verification model, evidence-of-completion posture, and requirements-to-proof traceability, fileciteturn27file0
- the **Testing Strategy Companion**, especially automation-first proof, graph/state-machine testing, failure-path testing, browser/API layering, and evidence-backed completion, fileciteturn27file1
- the **Glimmer Agentic Delivery Document Set**, which explicitly defines `verification-pack-workstream-d.md` as part of the canonical verification family, fileciteturn27file2
- the **Glimmer Requirements**, especially contextual message classification, action/deadline/decision extraction, prioritization, work-breakdown support, explainability, project memory, and human approval boundaries, fileciteturn27file3
- the latest **Architecture** state, especially the intake, triage, planner, review-gate, project-memory refresh, UI-surface, and graph-verification anchors, including the current manually maintained architecture document, fileciteturn27file16turn27file5
- the **Build Plan**, **Build Strategy and Scope**, and **Workstream D — Triage and Prioritization**, which explicitly define Glimmer’s assistant-core workflows and why they come after memory and connectors, fileciteturn27file6turn27file7turn27file11
- the **Glimmer Testing Strategy** and **Workstream G — Testing and Regression**, which define graph verification, review-gate proof, explainability expectations, and regression-pack design, fileciteturn27file4turn27file14
- the **Governance and Process** document, which requires evidence-backed completion and surfaced drift for meaningful work, fileciteturn27file15
- and the current **Test Catalog**, which already defines the core triage, planning, drafting-boundary, and security `TEST:` anchors this pack should organize and extend. fileciteturn27file17

**Stable verification anchor:** `TESTPACK:WorkstreamD.ControlSurfaceAlignment`

---

## 4. Why This Pack Is Load-Bearing

The build strategy and architecture are explicit that Glimmer is meant to become a **reviewable, structured, advisory operating system for project coordination**, not a black-box assistant that guesses and commits silently. fileciteturn27file16

Workstream D is where that claim becomes real through:

- intake routing,
- project classification,
- stakeholder-aware interpretation,
- extracted candidate actions and deadlines,
- review interrupts for ambiguity,
- planner and focus-pack generation,
- project-memory refresh integration,
- and next-step/work-breakdown support. fileciteturn27file11

If this pack is weak, Glimmer may still appear smart while actually depending on:

- brittle routing,
- silent ambiguity handling,
- opaque prioritization,
- flattened candidate-vs-accepted state,
- or planner outputs that cannot be trusted or explained.

That is exactly what this pack is meant to prevent.

**Stable verification anchor:** `TESTPACK:WorkstreamD.Rationale`

---

## 5. Workstream D Verification Scope

### 5.1 In scope

This pack covers proof for the following Triage and Prioritization concerns:

- source-record intake routing,
- project classification using memory and provenance,
- stakeholder-aware interpretation support,
- extraction of candidate actions, deadlines, decisions, blockers, and waiting-on signals,
- review-state creation and interrupt/resume behavior,
- planner graph behavior and rationale-bearing priorities,
- focus-pack generation,
- project-memory refresh integration,
- work-breakdown and next-step suggestion behavior,
- and application/API exposure of triage and priority outputs.

### 5.2 Out of scope

This pack does **not** attempt to prove:

- deep connector/provider normalization correctness,
- rich browser-visible UX quality,
- final draft-workspace interaction quality,
- Telegram companion usefulness beyond bounded routing parity,
- or full voice-session conversational quality.

Those belong to adjacent and later packs.

**Stable verification anchor:** `TESTPACK:WorkstreamD.Scope`

---

## 6. Source `TEST:` Anchors Included in This Pack

The Workstream D pack is built primarily from the triage-and-interpretation, planning-and-prioritization, drafting-boundary, and security scenario groups in the canonical Test Catalog, with a small number of workstream-specific extensions where needed. fileciteturn27file17

### 6.1 Canonical triage and interpretation anchors already defined in the Test Catalog

#### `TEST:Triage.Intake.SourceRoutesCorrectly`
- **Scenario name:** Normalized source records route into the correct intake path
- **Layers:** `graph`
- **Role in this pack:** Proves intake routing is source-aware and bounded. fileciteturn27file17

#### `TEST:Triage.ProjectClassification.SingleStrongMatch`
- **Scenario name:** Strong project match is classified correctly
- **Layers:** `graph`, `integration`
- **Role in this pack:** Proves memory- and provenance-aware classification can find a clear project match. fileciteturn27file17

#### `TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview`
- **Scenario name:** Ambiguous project classification creates structured review state
- **Layers:** `graph`, `integration`
- **Role in this pack:** Proves ambiguity does not silently harden into accepted truth. fileciteturn27file17

#### `TEST:Triage.StakeholderInterpretation.UncertainIdentityRequiresReview`
- **Scenario name:** Uncertain stakeholder interpretation does not silently merge identities
- **Layers:** `graph`, `integration`
- **Role in this pack:** Proves stakeholder uncertainty is review-safe. fileciteturn27file17

#### `TEST:Triage.ActionExtraction.ClearRequestBecomesCandidateAction`
- **Scenario name:** Clear follow-up request becomes persisted candidate action
- **Layers:** `graph`, `integration`
- **Role in this pack:** Proves clear operational meaning becomes reviewable structured output. fileciteturn27file17

#### `TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview`
- **Scenario name:** Uncertain extracted action remains reviewable candidate state
- **Layers:** `graph`, `integration`
- **Role in this pack:** Proves uncertain extraction does not become accepted work automatically. fileciteturn27file17

### 6.2 Canonical planning and prioritization anchors already defined in the Test Catalog

#### `TEST:Planner.FocusPack.GeneratesExplainablePriorities`
- **Scenario name:** Focus pack generation produces explainable priorities
- **Layers:** `graph`, `integration`
- **Role in this pack:** Proves planner output is not opaque urgency theater. fileciteturn27file17

#### `TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure`
- **Scenario name:** Work-breakdown assistance proposes next steps without silent structural mutation
- **Layers:** `graph`, `integration`
- **Role in this pack:** Proves planning help remains advisory and review-safe. fileciteturn27file17

#### `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable`
- **Scenario name:** Project-memory refresh trigger is explicit and traceable
- **Layers:** `integration`, `graph`
- **Role in this pack:** Proves memory evolution caused by triage/planner activity remains visible. fileciteturn27file17

### 6.3 Canonical drafting-boundary and security anchors already defined in the Test Catalog

#### `TEST:Drafting.DraftGeneration.CreatesReviewableDraft`
- **Scenario name:** Draft generation creates a reviewable draft artifact
- **Layers:** `graph`, `integration`, `api`
- **Role in this pack:** Proves assistant-core workflows can hand off into drafting as durable reviewable output. fileciteturn27file17

#### `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- **Scenario name:** Draft workflow does not create outbound send behavior
- **Layers:** `graph`, `api`, `integration`
- **Role in this pack:** Proves no-auto-send discipline is preserved in the assistant core. fileciteturn27file17

#### `TEST:Security.NoAutoSend.GlobalBoundaryPreserved`
- **Scenario name:** No-auto-send boundary is preserved across all channels
- **Layers:** `integration`, `graph`, `api`
- **Role in this pack:** Proves the core workflow layer does not create hidden externalization paths. fileciteturn27file17

#### `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`
- **Scenario name:** Externally meaningful actions require structured approval
- **Layers:** `graph`, `api`, `browser`
- **Role in this pack:** Proves review gates are real and not merely advisory prose. fileciteturn27file17

### 6.4 Additional Workstream D-specific anchors introduced by this pack

#### `TEST:Triage.Extraction.DecisionAndDeadlineSignalsPersist`
- **Scenario name:** Decision and deadline signals persist as reviewable interpreted artifacts
- **Primary layers:** `graph`, `integration`
- **Primary drivers:** `REQ:ActionDeadlineDecisionExtraction`, `ARCH:ExtractedDecisionModel`, `ARCH:ExtractedDeadlineSignalModel`, `ARCH:InterpretationReviewState`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove decision and time signals are explicit artifacts rather than transient reasoning only.

#### `TEST:Triage.ReviewInterrupt.ResumeContinuesSafely`
- **Scenario name:** Review interrupt and resume behavior continues the triage flow safely
- **Primary layers:** `graph`, `integration`, `api`
- **Primary drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:InterruptAndResumeModel`, `ARCH:ReviewGateArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove human review is a real resumable orchestration concept rather than a dead-end pause.

#### `TEST:Planner.PriorityRationale.VisibleInApplicationSurface`
- **Scenario name:** Priority rationale is exposed through the application surface
- **Primary layers:** `api`, `integration`
- **Primary drivers:** `REQ:Explainability`, `ARCH:PlannerGraph`, `ARCH:TodayViewArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove the planner can explain itself beyond hidden internal scoring.

#### `TEST:Planner.FocusPack.PersistsTopActionsAndPressureSignals`
- **Scenario name:** Focus pack persists top actions, waiting-on items, and pressure signals coherently
- **Primary layers:** `graph`, `integration`
- **Primary drivers:** `REQ:PrioritizationEngine`, `ARCH:FocusPackModel`, `ARCH:TodayViewArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove focus-pack content is durable, structured, and suitable for later UI consumption.

#### `TEST:ApplicationSurface.TriageAndPriorityEndpointsSupportReviewActions`
- **Scenario name:** Triage and priority application surfaces support retrieval and review actions correctly
- **Primary layers:** `api`, `integration`
- **Primary drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:TriageViewArchitecture`, `ARCH:ReviewQueueArchitecture`, `ARCH:VerificationLayerModel`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove backend application/API boundaries expose the assistant-core outputs in a controllable way.

**Stable verification anchor:** `TESTPACK:WorkstreamD.IncludedTests`

---

## 7. Workstream D Pack Entry Table

| TEST Anchor | Scenario | Layer | Automation Status | Pack Priority | Notes |
|---|---|---|---|---|---|
| `TEST:Triage.Intake.SourceRoutesCorrectly` | Normalized source records route into the correct intake path | `graph` | Planned | Critical | Intake baseline |
| `TEST:Triage.ProjectClassification.SingleStrongMatch` | Strong project match is classified correctly | `graph`, `integration` | Planned | Critical | Core classification proof |
| `TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview` | Ambiguous project classification creates structured review state | `graph`, `integration` | Planned | Critical | Core review-gate proof |
| `TEST:Triage.StakeholderInterpretation.UncertainIdentityRequiresReview` | Uncertain stakeholder interpretation does not silently merge identities | `graph`, `integration` | Planned | High | Protects stakeholder safety |
| `TEST:Triage.ActionExtraction.ClearRequestBecomesCandidateAction` | Clear follow-up request becomes persisted candidate action | `graph`, `integration` | Planned | Critical | Candidate-action baseline |
| `TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview` | Uncertain extracted action remains reviewable candidate state | `graph`, `integration` | Planned | Critical | Ambiguity safety |
| `TEST:Triage.Extraction.DecisionAndDeadlineSignalsPersist` | Decision and deadline signals persist as reviewable interpreted artifacts | `graph`, `integration` | Planned | High | Extends extraction coverage |
| `TEST:Triage.ReviewInterrupt.ResumeContinuesSafely` | Review interrupt and resume behavior continues the triage flow safely | `graph`, `integration`, `api` | Planned | Critical | Protects HITL orchestration |
| `TEST:Planner.FocusPack.GeneratesExplainablePriorities` | Focus pack generation produces explainable priorities | `graph`, `integration` | Planned | Critical | Planner baseline |
| `TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure` | Work-breakdown assistance proposes next steps without silent structural mutation | `graph`, `integration` | Planned | High | Advisory planning safety |
| `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable` | Project-memory refresh trigger is explicit and traceable | `integration`, `graph` | Planned | Critical | Memory evolution traceability |
| `TEST:Planner.PriorityRationale.VisibleInApplicationSurface` | Priority rationale is exposed through the application surface | `api`, `integration` | Planned | High | Explainability visibility |
| `TEST:Planner.FocusPack.PersistsTopActionsAndPressureSignals` | Focus pack persists top actions, waiting-on items, and pressure signals coherently | `graph`, `integration` | Planned | High | Today-view readiness |
| `TEST:Drafting.DraftGeneration.CreatesReviewableDraft` | Draft generation creates a reviewable draft artifact | `graph`, `integration`, `api` | Planned | High | Assistant-to-drafting handoff |
| `TEST:Drafting.NoAutoSend.BoundaryPreserved` | Draft workflow does not create outbound send behavior | `graph`, `api`, `integration` | Planned | Critical | Safety boundary |
| `TEST:Security.NoAutoSend.GlobalBoundaryPreserved` | No-auto-send boundary is preserved across all channels | `integration`, `graph`, `api` | Planned | Critical | Cross-cutting safety proof |
| `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` | Externally meaningful actions require structured approval | `graph`, `api`, `browser` | Planned | Critical | Review-gate enforcement |
| `TEST:ApplicationSurface.TriageAndPriorityEndpointsSupportReviewActions` | Triage and priority application surfaces support retrieval and review actions correctly | `api`, `integration` | Planned | High | Makes outputs controllable |

**Stable verification anchor:** `TESTPACK:WorkstreamD.EntryTable`

---

## 8. Expected Automation Shape

### 8.1 Graph and integration proof by default

Most Workstream D proof should be implemented through graph/workflow and integration testing because this workstream is fundamentally about:

- orchestration,
- classification and extraction behavior,
- review interrupts,
- planner outputs,
- and memory-refresh side effects.

### 8.2 API proof where outputs become operator-facing control surfaces

Where triage and priority outputs are exposed for review or control, API/application-surface proof should verify:

- retrieval behavior,
- review-action behavior,
- validation,
- and stable contract shape.

### 8.3 Limited browser dependence here

This pack may include small browser-visible proof where review-gate or approval flows are inseparable from the application surface, but it should not attempt to replace the fuller UI/browser coverage of Workstream E.

### 8.4 Failure and ambiguity proof matters

This proof should verify that:

- ambiguity creates review-needed state,
- interrupts can be resumed safely,
- planner outputs remain explainable,
- and no-auto-send boundaries are preserved even when the workflow is otherwise successful.

### 8.5 Minimal `manual_only` use

This pack should be heavily automated. `ManualOnly` use should be rare because the assistant core is exactly the sort of behavior that needs durable automated proof rather than informal confidence.

**Stable verification anchor:** `TESTPACK:WorkstreamD.AutomationShape`

---

## 9. Environment Assumptions

The Workstream D pack assumes the foundation, memory, and connector substrate are already in place.

### 9.1 Required assumptions

Expected baseline assumptions include:

- backend runtime and persistence substrate already working,
- controlled database/integration-test environment,
- stable source-record fixtures or controlled normalized-source setup,
- and executable graph/application test harnesses.

### 9.2 No dependence on live provider environments for core proof

This pack should not require live Google, Microsoft, Telegram, or voice production environments for its core proof.

The assistant-core behavior should be provable against controlled normalized inputs and test harnesses.

### 9.3 Earlier proof should already exist

This pack assumes Workstream B and Workstream C verification have already made the memory and intake layers trustworthy enough that assistant-core failures can be interpreted as workflow/logic problems rather than substrate chaos. fileciteturn27file9turn27file10

**Stable verification anchor:** `TESTPACK:WorkstreamD.EnvironmentAssumptions`

---

## 10. Execution Guidance

### 10.1 When to run this pack

This pack should normally be run:

- after meaningful graph/orchestration changes,
- after classification or extraction changes,
- after planner or focus-pack changes,
- after review-interrupt/resume changes,
- after triage/priority API-surface changes,
- before declaring Workstream D substantially complete,
- and before trusting richer UI, drafting, or companion behavior built on assistant-core outputs.

### 10.2 Failure handling

If this pack fails:

- later UI, drafting, and companion confidence should be treated cautiously,
- the failure should usually be resolved before broader usability claims are made,
- and progress reporting should explicitly state whether the problem affects routing, ambiguity handling, review safety, priority explainability, memory refresh, or no-auto-send boundaries.

### 10.3 Relationship to later packs

This Workstream D pack proves the assistant-core behavior in the workstream context.

Later UI, voice, browser, and release packs should build on it rather than rediscovering these failures indirectly.

**Stable verification anchor:** `TESTPACK:WorkstreamD.ExecutionGuidance`

---

## 11. Evidence Expectations

When the Workstream D pack is executed, evidence reporting should capture at minimum:

- execution date/time,
- environment posture used,
- which included `TEST:` anchors were executed,
- pass/fail outcome,
- any `Deferred` entries and why,
- and a brief statement of whether the assistant-core workflow layer is considered stable enough for richer UI and companion extension.

This should be summarized in the relevant Workstream D progress file and referenced in broader phase-exit or regression summaries where appropriate. fileciteturn27file15turn27file1

**Stable verification anchor:** `TESTPACK:WorkstreamD.EvidenceExpectations`

---

## 12. Operational Ready Definition for This Pack

The Workstream D verification pack should be considered operationally established when:

1. all included `TEST:` anchors are defined and mapped,
2. intake routing proof exists,
3. classification and extraction proof exists,
4. ambiguity/review-interrupt proof exists,
5. planner and focus-pack proof exists,
6. project-memory refresh traceability proof exists,
7. triage/priority API-surface proof exists,
8. no-auto-send and review-gate proof exists,
9. and the pack can be run repeatably against controlled normalized-source inputs and workflow test harnesses.

At that point, Workstream D has a meaningful verification surface that later UX and companion work can trust.

**Stable verification anchor:** `TESTPACK:WorkstreamD.DefinitionOfOperationalReady`

---

## 13. Relationship to Later Packs

This pack establishes the proof surface for the assistant-core workflow layer only.

Later packs should build on it as follows:

- **Workstream E** should prove browser-visible use of triage, review, draft, and priority artifacts produced here,
- **Workstream F** should prove voice and companion interactions route through the same review-safe core,
- **Data Integrity** should later absorb the most important candidate-vs-accepted and memory-refresh protections here into long-lived regression proof,
- and **Release** should compose representative assistant-core proof into cross-workstream confidence.

This progression is consistent with the Glimmer build plan, workstream map, and Workstream G verification-estate design. fileciteturn27file12turn27file13turn27file14

**Stable verification anchor:** `TESTPACK:WorkstreamD.RelationshipToLaterPacks`

---

## 14. Final Note

If Workstream D is implemented but not properly verified, Glimmer may still feel clever while quietly depending on unsafe ambiguity handling, weak planning logic, or invisible review failures.

That is the danger this pack is meant to prevent.

Its job is to prove that Glimmer’s assistant core is:

- routed correctly,
- review-safe,
- explainable,
- bounded,
- and operationally trustworthy enough for the rest of the product to surface confidently.

**Stable verification anchor:** `TESTPACK:WorkstreamD.Conclusion`

