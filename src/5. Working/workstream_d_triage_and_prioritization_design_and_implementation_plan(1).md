# Glimmer — Workstream D Triage and Prioritization Design and Implementation Plan

## Document Metadata

- **Document Title:** Glimmer — Workstream D Triage and Prioritization Design and Implementation Plan
- **Document Type:** Working Implementation Plan
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** D — Triage and Prioritization
- **Primary Companion Documents:** Requirements, Architecture, Build Plan, Verification, Governance and Process, Global Copilot Instructions, Module Instructions, Workstream D Verification Pack

---

## 1. Purpose

This document is the active working implementation plan for **Workstream D — Triage and Prioritization**.

Its purpose is to translate the canonical Workstream D build-plan document into an execution-ready plan that a coding agent can use during real implementation sessions.

This file should remain practical and anchored. It is not the source of architecture truth. It is the working plan for how Glimmer’s assistant-core workflow layer should be implemented, verified, and advanced slice by slice.

**Stable working anchor:** `WORKD:Plan.ControlSurface`

---

## 2. Workstream Objective

The objective of Workstream D is to implement the assistant-core workflow layer that turns normalized source records and structured memory into reviewable operational guidance.

At the end of Workstream D, the repository should have real workflow support for:

- intake routing,
- contextual project classification,
- stakeholder-aware interpretation,
- extraction of candidate actions, deadlines, decisions, blockers, and waiting-on signals,
- structured review interrupts for ambiguity,
- planner and focus-pack generation,
- project-memory refresh integration,
- work-breakdown and next-step assistance,
- and application/API exposure of triage and priority outputs.

This workstream is where Glimmer starts behaving like a governable chief-of-staff rather than only storing information.

**Stable working anchor:** `WORKD:Plan.Objective`

---

## 3. Control Anchors in Scope

### 3.1 Requirements anchors

- `REQ:ContextualMessageClassification`
- `REQ:ActionDeadlineDecisionExtraction`
- `REQ:PrioritizationEngine`
- `REQ:WorkBreakdownSupport`
- `REQ:ProjectMemory`
- `REQ:PreparedBriefings`
- `REQ:Explainability`
- `REQ:HumanApprovalBoundaries`
- `REQ:SafeBehaviorDefaults`

### 3.2 Architecture anchors

- `ARCH:LangGraphTopology`
- `ARCH:IntakeGraph`
- `ARCH:TriageGraph`
- `ARCH:PlannerGraph`
- `ARCH:DraftingGraph`
- `ARCH:InterruptAndResumeModel`
- `ARCH:StructuredMemoryModel`
- `ARCH:ProjectMemoryRefresh`
- `ARCH:ReviewGateArchitecture`
- `ARCH:TodayViewArchitecture`
- `ARCH:ProjectWorkspaceArchitecture`
- `ARCH:VerificationLayerModel`
- `ARCH:GraphVerificationStrategy`

### 3.3 Build-plan anchors

- `PLAN:WorkstreamD.TriageAndPrioritization`
- `PLAN:WorkstreamD.Objective`
- `PLAN:WorkstreamD.InternalSequence`
- `PLAN:WorkstreamD.VerificationExpectations`
- `PLAN:WorkstreamD.DefinitionOfDone`

### 3.4 Verification anchors

- `TEST:Triage.Intake.SourceRoutesCorrectly`
- `TEST:Triage.ProjectClassification.SingleStrongMatch`
- `TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview`
- `TEST:Triage.StakeholderInterpretation.UncertainIdentityRequiresReview`
- `TEST:Triage.ActionExtraction.ClearRequestBecomesCandidateAction`
- `TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview`
- `TEST:Triage.Extraction.DecisionAndDeadlineSignalsPersist`
- `TEST:Triage.ReviewInterrupt.ResumeContinuesSafely`
- `TEST:Planner.FocusPack.GeneratesExplainablePriorities`
- `TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure`
- `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable`
- `TEST:Planner.PriorityRationale.VisibleInApplicationSurface`
- `TEST:Planner.FocusPack.PersistsTopActionsAndPressureSignals`
- `TEST:Drafting.DraftGeneration.CreatesReviewableDraft`
- `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- `TEST:Security.NoAutoSend.GlobalBoundaryPreserved`
- `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`
- `TEST:ApplicationSurface.TriageAndPriorityEndpointsSupportReviewActions`

**Stable working anchor:** `WORKD:Plan.ControlAnchors`

---

## 4. Execution Principles for This Workstream

### 4.1 Workflow state must be explicit and review-safe

The assistant core must produce explicit reviewable artifacts and explicit review-needed states. It must not hide consequential interpretation inside transient graph state.

### 4.2 Strong signals and ambiguous signals must diverge cleanly

Clear classification or extraction may flow toward candidate artifacts directly. Ambiguous outcomes must create structured review interrupts rather than confident-looking guesses.

### 4.3 Planner output must be explainable

Focus and prioritization outputs should carry rationale signals that can be surfaced later in the application layer. Avoid opaque priority scoring that cannot be defended.

### 4.4 Graphs coordinate; they do not become memory stores

LangGraph workflows should route, coordinate, interrupt, and resume. Durable truth belongs in the memory model created in Workstream B.

### 4.5 No-auto-send is non-negotiable

Even when routing from triage to drafting, the assistant core must remain advisory and review-bound. There should be no hidden outbound side effects.

### 4.6 One coherent workflow slice at a time

Prefer bounded workflow slices such as intake+classification or planner+focus-pack rather than attempting to light up the whole assistant core at once.

**Stable working anchor:** `WORKD:Plan.ExecutionPrinciples`

---

## 5. Assistant-Core Shape Target for Workstream D

By the end of this workstream, the implementation should materially support the following assistant-core categories or directly equivalent concrete shapes:

- intake routing from normalized source records
- project classification workflow
- interpretation workflow for actions/deadlines/decisions/blockers/waiting-on
- review interrupt and resume handling
- planner/focus-pack workflow
- project-memory refresh trigger integration
- drafting handoff as reviewable artifact creation
- triage and priority application/API surfaces

These layers must remain bounded, review-safe, and testable.

**Stable working anchor:** `WORKD:Plan.AssistantCoreShapeTarget`

---

## 6. Work Packages to Execute

## 6.1 WD1 — Intake graph baseline

### Objective
Implement the initial intake graph and routing surface that accepts normalized source references and routes them into the correct triage path.

### Expected touch points
- intake graph nodes
- workflow state contracts
- intake entrypoints/adapters
- graph tests

### Verification expectation
- `TEST:Triage.Intake.SourceRoutesCorrectly`

### Notes
Keep state bounded and reference-based rather than payload-heavy.

**Stable working anchor:** `WORKD:Plan.PackageWD1`

---

## 6.2 WD2 — Project classification flow

### Objective
Implement contextual project classification using memory and provenance signals, including clear-match handling and ambiguous review-needed handling.

### Expected touch points
- triage graph nodes
- classification services/helpers
- interpreted artifact creation
- review-state creation
- graph/integration tests

### Verification expectation
- `TEST:Triage.ProjectClassification.SingleStrongMatch`
- `TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview`

### Notes
A correct “needs review” outcome is better than a confident wrong match.

**Stable working anchor:** `WORKD:Plan.PackageWD2`

---

## 6.3 WD3 — Stakeholder-aware interpretation flow

### Objective
Implement interpretation support that can account for stakeholder context while preserving safe handling of uncertain identity resolution.

### Expected touch points
- triage graph nodes
- stakeholder-resolution helpers
- interpreted artifact creation
- graph/integration tests

### Verification expectation
- `TEST:Triage.StakeholderInterpretation.UncertainIdentityRequiresReview`

### Notes
Do not allow uncertain stakeholder identity to collapse silently.

**Stable working anchor:** `WORKD:Plan.PackageWD3`

---

## 6.4 WD4 — Candidate extraction flow

### Objective
Implement extraction of candidate actions, deadlines, decisions, blockers, and waiting-on signals as reviewable interpreted artifacts.

### Expected touch points
- extraction services/helpers
- interpreted artifact entities/use
- graph nodes
- integration tests

### Verification expectation
- `TEST:Triage.ActionExtraction.ClearRequestBecomesCandidateAction`
- `TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview`
- `TEST:Triage.Extraction.DecisionAndDeadlineSignalsPersist`

### Notes
This layer should create artifacts, not hidden reasoning.

**Stable working anchor:** `WORKD:Plan.PackageWD4`

---

## 6.5 WD5 — Review interrupt and resume model

### Objective
Implement the durable interrupt/resume behavior that allows ambiguous or externally meaningful workflow states to stop for human input and then continue safely.

### Expected touch points
- graph interrupt/resume logic
- review-state transitions
- API/application hooks where needed
- graph/API tests

### Verification expectation
- `TEST:Triage.ReviewInterrupt.ResumeContinuesSafely`
- `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`

### Notes
This is one of the most important control mechanisms in the whole system.

**Stable working anchor:** `WORKD:Plan.PackageWD5`

---

## 6.6 WD6 — Planner and focus-pack flow

### Objective
Implement planner behavior that turns interpreted/accepted context into explainable priorities and durable focus-pack artifacts.

### Expected touch points
- planner graph nodes
- priority/rationale helpers
- focus-pack persistence
- graph/integration tests

### Verification expectation
- `TEST:Planner.FocusPack.GeneratesExplainablePriorities`
- `TEST:Planner.FocusPack.PersistsTopActionsAndPressureSignals`
- `TEST:Planner.PriorityRationale.VisibleInApplicationSurface`

### Notes
Avoid opaque urgency theater. Rationale matters.

**Stable working anchor:** `WORKD:Plan.PackageWD6`

---

## 6.7 WD7 — Work-breakdown and next-step assistance

### Objective
Implement bounded planner assistance that suggests next steps without silently restructuring the project model or accepted work state.

### Expected touch points
- planner helpers
- interpreted advisory artifacts or bounded output structures
- graph/integration tests

### Verification expectation
- `TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure`

### Notes
This must remain advisory.

**Stable working anchor:** `WORKD:Plan.PackageWD7`

---

## 6.8 WD8 — Project-memory refresh trigger integration

### Objective
Implement the explicit trigger path from triage/planner activity into project-memory refresh behavior with traceability preserved.

### Expected touch points
- refresh trigger services
- graph integration points
- audit/lineage support surfaces
- graph/integration tests

### Verification expectation
- `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable`

### Notes
Refresh must remain visible and traceable, not magical.

**Stable working anchor:** `WORKD:Plan.PackageWD8`

---

## 6.9 WD9 — Drafting handoff from assistant core

### Objective
Implement the bounded handoff from assistant-core workflows into reviewable draft artifact creation.

### Expected touch points
- drafting handoff nodes/adapters
- draft creation services
- graph/API/integration tests

### Verification expectation
- `TEST:Drafting.DraftGeneration.CreatesReviewableDraft`
- `TEST:Drafting.NoAutoSend.BoundaryPreserved`

### Notes
Draft creation is allowed. Autonomous sending is not.

**Stable working anchor:** `WORKD:Plan.PackageWD9`

---

## 6.10 WD10 — Triage and priority application/API surfaces

### Objective
Implement the application/API surfaces needed to expose triage, review, and priority outputs to the workspace and later companion layers.

### Expected touch points
- FastAPI routes / application services
- response models/contracts
- review action endpoints
- API/integration tests

### Verification expectation
- `TEST:ApplicationSurface.TriageAndPriorityEndpointsSupportReviewActions`
- `TEST:Security.NoAutoSend.GlobalBoundaryPreserved`

### Notes
These surfaces should expose control, not hide it.

**Stable working anchor:** `WORKD:Plan.PackageWD10`

---

## 7. Recommended Execution Order

The recommended execution order inside this working plan is:

1. WD1 — Intake graph baseline
2. WD2 — Project classification flow
3. WD3 — Stakeholder-aware interpretation flow
4. WD4 — Candidate extraction flow
5. WD5 — Review interrupt and resume model
6. WD6 — Planner and focus-pack flow
7. WD7 — Work-breakdown and next-step assistance
8. WD8 — Project-memory refresh trigger integration
9. WD9 — Drafting handoff from assistant core
10. WD10 — Triage and priority application/API surfaces

This sequence keeps the assistant core bounded and lets more complex downstream behavior build on already-proven workflow primitives.

**Stable working anchor:** `WORKD:Plan.ExecutionOrder`

---

## 8. Expected Files and Layers Likely to Change

The initial Workstream D implementation is likely to touch files or file groups such as:

- LangGraph workflow modules
- triage/planner/drafting service helpers
- application/API service files
- interpreted and accepted artifact interaction code
- refresh trigger and audit integration surfaces
- graph/API/integration test fixtures
- Workstream D working documents

This list should be refined as implementation begins.

**Stable working anchor:** `WORKD:Plan.LikelyTouchPoints`

---

## 9. Verification Plan for Workstream D

### 9.1 Minimum required proof

At minimum, Workstream D implementation should produce executable proof for:

- intake routing
- clear-match classification
- ambiguous review-needed classification
- uncertain stakeholder handling
- candidate extraction
- decision/deadline signal persistence
- review interrupt/resume behavior
- focus-pack generation and rationale
- project-memory refresh traceability
- advisory work-breakdown behavior
- drafting handoff without auto-send
- triage/priority API-surface correctness
- cross-cutting review-gate and no-auto-send safety

### 9.2 Primary verification surfaces

The main verification references for this workstream are:

- `verification-pack-workstream-d.md`
- `verification-pack-data-integrity.md`
- `verification-pack-release.md` for representative release-level checks later

### 9.3 Evidence expectation

Meaningful implementation slices in this workstream should update the Workstream D progress file with:

- what was implemented
- what proof was executed
- what passed
- what failed
- what remains blocked or deferred

**Stable working anchor:** `WORKD:Plan.VerificationPlan`

---

## 10. Human Dependencies and Likely Decisions

This workstream is mostly agent-executable, but a few human decisions may still be needed.

Likely human-dependent areas include:

- confirming especially sensitive review-gate thresholds or ambiguity posture if tradeoffs emerge
- deciding how much rationale detail should be exposed initially in API/application surfaces
- and reviewing any attempt to widen planner influence over accepted state or structure

The coding agent should complete all safe workflow and proof work before surfacing human dependencies as blockers.

**Stable working anchor:** `WORKD:Plan.HumanDependencies`

---

## 11. Known Risks in This Workstream

### 11.1 Risk — Ambiguity gets hidden behind confidence

If unclear cases are styled as clear enough, the assistant core will become unsafe very quickly.

### 11.2 Risk — Graph state becomes shadow memory

If workflow state carries too much truth instead of persisting real artifacts, traceability and restart behavior will degrade.

### 11.3 Risk — Planner outputs become opaque

If priorities and next steps cannot be explained, operator trust will erode.

### 11.4 Risk — Review interrupt becomes a dead end

If pause/resume is not truly modeled, human review will behave like a workflow break rather than part of the system.

### 11.5 Risk — Drafting handoff blurs into action execution

If the drafting boundary is weak, no-auto-send posture will be undermined.

### 11.6 Risk — API surfaces expose outputs without control semantics

If triage/priority data is retrievable but not reviewable, the workspace will inherit a weak control surface.

**Stable working anchor:** `WORKD:Plan.Risks`

---

## 12. Immediate Next Session Recommendations

When actual coding for Workstream D begins, the first sensible execution slice is:

1. implement the intake graph baseline,
2. add strong-match and ambiguous project-classification behavior,
3. persist candidate classification artifacts,
4. add the first review-needed interrupt path,
5. and execute the first triage workflow proof.

That slice creates the first real assistant-core workflow while preserving the central review-safe posture.

**Stable working anchor:** `WORKD:Plan.ImmediateNextSlice`

---

## 13. Definition of Ready for Workstream D Completion

Workstream D should only be considered ready for completion when all of the following are materially true:

- intake routing is real
- classification is real
- candidate extraction is real
- review interrupt/resume is real
- planner/focus-pack generation is real
- memory refresh trigger integration is real
- advisory work-breakdown is real
- drafting handoff is real and bounded
- triage/priority API surfaces are real
- no-auto-send and review-gate safeguards are real
- and the corresponding workflow proof paths have been executed and recorded

If these are not true, Workstream D is not done, even if some assistant behavior appears to work.

**Stable working anchor:** `WORKD:Plan.DefinitionOfReadyForCompletion`

---

## 14. Final Note

This workstream is where Glimmer either becomes a trustworthy operational partner or drifts into fuzzy AI theater.

That is the standard here.

The goal is not to make the system sound clever. The goal is to make the core workflow:

- review-safe,
- explainable,
- bounded,
- and reliable enough that the workspace and companion layers can surface it with confidence.

**Stable working anchor:** `WORKD:Plan.Conclusion`

