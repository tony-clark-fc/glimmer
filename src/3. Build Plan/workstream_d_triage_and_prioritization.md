# Glimmer — Workstream D: Triage and Prioritization

## Document Metadata

- **Document Title:** Glimmer — Workstream D: Triage and Prioritization
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Build Strategy and Scope, Testing Strategy, Workstream B Domain and Memory, Workstream C Connectors

---

## 1. Purpose

This document defines the implementation strategy for **Workstream D — Triage and Prioritization**.

Its purpose is to implement the first genuinely assistant-like operating workflows in Glimmer: taking ingested signals, understanding what they mean in project context, extracting likely actions and deadlines, and turning the resulting state into explainable prioritization and focus guidance.

This workstream is where Glimmer stops being only a memory-and-ingestion system and starts acting like a real project chief-of-staff.

**Stable plan anchor:** `PLAN:WorkstreamD.TriageAndPrioritization`

---

## 2. Workstream Objective

Workstream D exists to implement Glimmer’s assistant-core workflow layer, including:

- intake routing from normalized source records,
- contextual project classification,
- stakeholder-aware interpretation,
- extraction of actions, deadlines, decisions, and blockers,
- review-gated handling of ambiguity,
- project-summary refresh triggers,
- prioritization and focus generation,
- and planner-facing next-step support.

At the end of this workstream, Glimmer should be able to take real ingested signals and transform them into reviewable, explainable operational guidance.

**Stable plan anchor:** `PLAN:WorkstreamD.Objective`

---

## 3. Why This Workstream Comes After Connectors

The build strategy and phase model explicitly place assistant-core workflows after the runtime/memory foundation and the external-boundary intake layer. That sequencing is necessary because triage and prioritization depend on:

- structured project and stakeholder memory,
- accepted operational state,
- provenance-bearing source records,
- reviewable interpretation artifacts,
- and real intake from multiple connected accounts.

Without those layers, triage would devolve into prompt-only classification with weak memory, flattened provenance, and no trustworthy review boundary.

This workstream therefore builds on the substrate established by Workstream B and Workstream C and should not be treated as an isolated AI feature sprint.

**Stable plan anchor:** `PLAN:WorkstreamD.Rationale`

---

## 4. Related Requirements Anchors

This workstream directly supports the following requirements:

- `REQ:ContextualMessageClassification`
- `REQ:ActionDeadlineDecisionExtraction`
- `REQ:PrioritizationEngine`
- `REQ:WorkBreakdownSupport`
- `REQ:PreparedBriefings`
- `REQ:ProjectMemory`
- `REQ:StakeholderMemory`
- `REQ:Explainability`
- `REQ:HumanApprovalBoundaries`
- `REQ:SafeBehaviorDefaults`

These requirements define Glimmer’s core claim to usefulness: it must not just ingest messages, but understand them in project context, extract likely meaning, surface ambiguity honestly, and help the operator focus on what matters next.

**Stable plan anchor:** `PLAN:WorkstreamD.RequirementsAlignment`

---

## 5. Related Architecture Anchors

This workstream is primarily implementing the architecture described by:

- `ARCH:IntakeGraph`
- `ARCH:TriageGraph`
- `ARCH:TriageGraphReviewGate`
- `ARCH:PlannerGraph`
- `ARCH:PlannerGraphExplainability`
- `ARCH:PlannerGraphReviewGate`
- `ARCH:ProjectMemoryRefresh`
- `ARCH:TodayViewArchitecture`
- `ARCH:ReviewGateArchitecture`
- `ARCH:GraphVerificationStrategy`

These anchors define the core graph workflows, review-gate posture, explainability requirements, project-memory refresh model, and the user-facing priority surfaces that this workstream must make real.

**Stable plan anchor:** `PLAN:WorkstreamD.ArchitectureAlignment`

---

## 6. Workstream Scope

### 6.1 In scope

This workstream includes:

- Intake Graph routing behavior,
- Triage Graph implementation,
- Planner Graph implementation,
- classification and extraction logic,
- ambiguity/review interrupt behavior,
- project-memory refresh triggering,
- focus-pack generation,
- priority explanation generation,
- and application-service or orchestration-layer support needed to expose triage and prioritization results to the web UI.

**Stable plan anchor:** `PLAN:WorkstreamD.InScope`

### 6.2 Out of scope

This workstream does **not** include:

- final polished drafting workspace behavior,
- rich project-page UX implementation,
- final voice-session behavior,
- advanced Telegram companion polish,
- autonomous action execution,
- or outbound communication send flows.

This workstream creates the assistant-core decision layer. Later workstreams expose and polish it through drafting, UI, and voice surfaces.

**Stable plan anchor:** `PLAN:WorkstreamD.OutOfScope`

---

## 7. Implementation Outcome Expected from This Workstream

By the end of Workstream D, Glimmer should be able to do the following in a structurally real way:

- accept normalized source artifacts at the intake boundary,
- classify messages and imported signals against likely projects,
- use stakeholder and provenance context during classification,
- extract likely actions, deadlines, decisions, and blockers,
- create review-needed states when ambiguity is significant,
- refresh project-level synthesized understanding based on new state,
- generate explainable priority outputs,
- produce focus-oriented artifacts such as daily focus packs,
- and provide the underlying data/services needed for Today and Triage experiences.

This is the threshold where Glimmer begins to behave like an operational assistant rather than just a structured store of imported data.

**Stable plan anchor:** `PLAN:WorkstreamD.ExpectedOutcome`

---

## 8. Assistant-Core Implementation Packages

## 8.1 Work Package D1 — Intake routing implementation

**Objective:** Implement the first operational version of the Intake Graph routing layer.

### In scope
- intake entrypoint from normalized source records
- routing logic by source type and interaction context
- graph-state initialization
- reference-based handoff into downstream graph flows
- persistence/use of workflow context and continuation metadata where required

### Expected outputs
- intake graph implementation or equivalent orchestration service
- initial graph-state structures for intake workflows
- tests for routing by source type and channel/session context

### Related anchors
- `ARCH:IntakeGraph`
- `ARCH:IntakeGraphRouting`
- `ARCH:GraphState.WorkflowContext`

### Definition of done
- normalized source records enter a real intake path that routes them to the correct downstream workflow without hard-coding business logic into connectors

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD1.IntakeRouting`

---

## 8.2 Work Package D2 — Project classification engine

**Objective:** Implement project-relevance classification over ingested messages and imported signals.

### In scope
- project matching logic using project summaries, stakeholder context, message content, thread context, and account provenance
- candidate project ranking
- ambiguity handling
- persistence of `MessageClassification`
- review-state creation when confidence is weak

### Expected outputs
- classification service/graph nodes
- persisted classification artifacts
- confidence and ambiguity scoring model
- tests for single-project, ambiguous, and no-strong-match scenarios

### Related anchors
- `ARCH:TriageGraph`
- `ARCH:MessageClassificationModel`
- `ARCH:GraphState.ConfidenceSignals`
- `ARCH:TriageGraphReviewGate`

### Definition of done
- Glimmer can create reviewable project classifications grounded in memory and provenance rather than just sender matching

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD2.ProjectClassificationEngine`

---

## 8.3 Work Package D3 — Stakeholder-aware interpretation support

**Objective:** Use stakeholder memory as a meaningful part of triage interpretation.

### In scope
- stakeholder identity resolution support for triage flows
- stakeholder-project linkage lookup during classification
- candidate stakeholder inference from source records
- ambiguity handling for uncertain identity linking

### Expected outputs
- stakeholder-resolution logic for triage
- persisted linkage from classification/extraction artifacts to stakeholders where appropriate
- tests for multi-identity and uncertain-identity scenarios

### Related anchors
- `ARCH:StakeholderModel`
- `ARCH:StakeholderIdentityModel`
- `ARCH:TriageGraph`
- `ARCH:ReviewRequiredCategories`

### Definition of done
- triage interpretation can use stakeholder context meaningfully without silently forcing low-confidence merges

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD3.StakeholderAwareInterpretation`

---

## 8.4 Work Package D4 — Action, deadline, decision, and blocker extraction

**Objective:** Implement extraction of likely operational meaning from ingested signals.

### In scope
- extraction of candidate actions
- extraction of deadline/time signals
- extraction of decision signals
- extraction of blocker/waiting-on signals where supported
- persistence of interpreted artifacts
- review-state creation when meaning is uncertain

### Expected outputs
- extraction service/graph nodes
- persisted `ExtractedAction`, `ExtractedDecision`, `ExtractedDeadlineSignal` and related artifacts
- tests for clear and ambiguous extraction cases

### Related anchors
- `ARCH:ExtractedActionModel`
- `ARCH:ExtractedDecisionModel`
- `ARCH:ExtractedDeadlineSignalModel`
- `ARCH:TriageGraphReviewGate`

### Definition of done
- incoming signals can yield persisted, reviewable candidate actions and related artifacts rather than disappearing into transient reasoning

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD4.ExtractionLayer`

---

## 8.5 Work Package D5 — Review interrupt and pending-decision model for triage

**Objective:** Make ambiguity and approval real in the orchestration path.

### In scope
- review-request creation for low-confidence classification/extraction cases
- pending-review persistence
- continuation metadata for resume flows
- explicit operator-decision pathways (accept / amend / reject / defer)

### Expected outputs
- normalized review-request creation path
- interrupt/resume support for triage flows
- tests for review gating and safe continuation

### Related anchors
- `ARCH:OrchestrationPrinciple.ExplicitReviewGates`
- `ARCH:Subflow.ReviewRequestCreation`
- `ARCH:InterruptAndResumeModel`
- `ARCH:ReviewGateEnforcement`

### Definition of done
- low-confidence triage outcomes no longer silently harden into memory; they pause in a structured, resumable review state

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD5.TriageReviewInterrupts`

---

## 8.6 Work Package D6 — Planner graph core

**Objective:** Implement the first operational version of Glimmer’s planning and prioritization workflow.

### In scope
- planner graph/state implementation
- use of accepted operational state and interpreted artifacts as planner input
- generation of priority candidates and ranked focus outputs
- rationale capture for prioritization decisions

### Expected outputs
- planner graph implementation or equivalent orchestration service
- persisted planner outputs and/or derived artifacts
- tests for priority ranking behavior and rationale visibility

### Related anchors
- `ARCH:PlannerGraph`
- `ARCH:PlannerGraphExplainability`
- `ARCH:GraphState.DomainReferences`

### Definition of done
- Glimmer can produce explainable priority outputs grounded in current project state rather than generic urgency heuristics alone

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD6.PlannerGraphCore`

---

## 8.7 Work Package D7 — Focus-pack and daily-priority artifact generation

**Objective:** Implement persisted focus-oriented outputs for day-to-day operator use.

### In scope
- generation of `FocusPack`
- daily-priority artifact creation
- inclusion of top actions, waiting-on items, reply pressure, and calendar pressure where available
- summary/rationale generation for focus outputs

### Expected outputs
- focus-pack generation logic
- persisted `FocusPack` artifacts
- tests for artifact integrity and ranking composition

### Related anchors
- `ARCH:FocusPackModel`
- `ARCH:Subflow.FocusPackGeneration`
- `ARCH:TodayViewDesign`

### Definition of done
- Glimmer can create persisted focus artifacts that provide a meaningful “what matters now” view for the operator

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD7.FocusPackGeneration`

---

## 8.8 Work Package D8 — Project memory refresh integration

**Objective:** Connect triage and planning outcomes into project-summary refresh behavior.

### In scope
- refresh trigger logic from accepted/interpreted state changes
- summary refresh service invocation from workflow paths
- project-summary update persistence with refresh metadata
- handling of meaningful structural changes through review-first pathways where needed

### Expected outputs
- memory-refresh integration path
- project-summary update behavior linked to triage/planner flows
- tests for refresh triggers, thresholds, and persistence lineage

### Related anchors
- `ARCH:ProjectMemoryRefresh`
- `ARCH:ProjectMemoryRefreshPipeline`
- `ARCH:SummaryRefreshTriggers`
- `ARCH:SummaryRefreshThresholds`

### Definition of done
- project memory actually evolves when meaningful new signal state arrives, and that evolution remains traceable

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD8.ProjectMemoryRefreshIntegration`

---

## 8.9 Work Package D9 — Work breakdown and next-step suggestion support

**Objective:** Implement the first advisory work-breakdown assistance behavior.

### In scope
- inference of likely next steps from current project state and new signals
- proposal of workstream/task refinements where appropriate
- advisory generation only, not silent structural mutation
- review-first handling for substantial restructuring suggestions

### Expected outputs
- next-step suggestion logic
- proposal artifacts or planner outputs for work-breakdown support
- tests for safe advisory posture and review gating on larger changes

### Related anchors
- `ARCH:Capability.PlanningAndPrioritization`
- `ARCH:PlannerGraphReviewGate`
- `ARCH:ProjectWorkspaceDesign`

### Definition of done
- Glimmer can suggest reasonable next execution slices without silently rewriting project structure

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD9.WorkBreakdownSupport`

---

## 8.10 Work Package D10 — Service/API boundary for triage and priority surfaces

**Objective:** Expose the triage and prioritization outputs cleanly to the application/UI layer.

### In scope
- API or application-service endpoints for triage items
- retrieval of review-needed items
- retrieval of focus packs and priority views
- actions to accept/amend/reject/defer triage outputs where appropriate

### Expected outputs
- FastAPI routes or application-service surfaces
- DTO/contract definitions for triage and priority views
- tests for route behavior, validation, and review-action flow

### Related anchors
- `ARCH:VerificationLayer.Api`
- `ARCH:TriageViewArchitecture`
- `ARCH:TodayViewArchitecture`
- `ARCH:ReviewQueueArchitecture`

### Definition of done
- the UI layer has a clean, testable boundary through which triage and prioritization outputs can be consumed and acted on

**Stable plan anchor:** `PLAN:WorkstreamD.PackageD10.TriageAndPriorityApplicationSurface`

---

## 9. Sequencing Inside the Workstream

The recommended internal order for Workstream D is:

1. D1 — Intake routing implementation
2. D2 — Project classification engine
3. D3 — Stakeholder-aware interpretation support
4. D4 — Action, deadline, decision, and blocker extraction
5. D5 — Review interrupt and pending-decision model for triage
6. D6 — Planner graph core
7. D8 — Project memory refresh integration
8. D7 — Focus-pack and daily-priority artifact generation
9. D9 — Work breakdown and next-step suggestion support
10. D10 — Service/API boundary for triage and priority surfaces

This order keeps the work aligned to the graph model: first intake, then interpretation, then review safety, then planning, then memory refresh, then user-facing application access.

**Stable plan anchor:** `PLAN:WorkstreamD.InternalSequence`

---

## 10. Human Dependencies

This workstream is mostly agent-executable once Workstreams A–C are in place.

Expected human involvement is primarily around:

- approval of any materially new classification or prioritization heuristics where business judgment is strong,
- review of any proposed simplifications that weaken explainability or reviewability,
- and confirmation of ambiguous product-behavior tradeoffs such as how assertive Glimmer should be in planner suggestions.

The coding agent should still be able to implement the full structural workflow and verification shape before such inputs become blocking.

**Stable plan anchor:** `PLAN:WorkstreamD.HumanDependencies`

---

## 11. Verification Expectations

Workstream D is complete only when the assistant-core workflow behavior is proven, not merely implemented.

### Verification layers expected
- graph workflow verification
- unit verification for ranking/extraction helpers and rule logic
- integration verification for persistence of interpreted and derived artifacts
- API verification for triage/review/focus surfaces
- browser-visible verification support for later Today/Triage UI flows

### Minimum proof expectations
- intake routes to the correct downstream graph path
- project classification is persisted with confidence and ambiguity state
- extracted actions/deadlines/decisions are reviewable and do not silently become accepted truth
- low-confidence cases create structured review states
- planner outputs produce explainable priorities
- focus packs are persisted and queryable
- project-summary refresh is triggered and traceable when meaningful new state arrives
- no workflow bypasses review gates or no-auto-send boundaries

This aligns directly to Glimmer’s testing strategy, which treats graph routing, review-gate enforcement, domain-memory boundaries, and explainable planning as load-bearing proof targets.

**Stable plan anchor:** `PLAN:WorkstreamD.VerificationExpectations`

---

## 12. Suggested Future Working Documents for This Workstream

This workstream should eventually be paired with:

- `WorkstreamD_TriageAndPrioritization_DESIGN_AND_IMPLEMENTATION_PLAN.md`
- `WorkstreamD_TriageAndPrioritization_DESIGN_AND_IMPLEMENTATION_PROGRESS.md`

Those files will hold the active implementation state, session handoff, verification evidence, and human-decision tracking once coding begins.

**Stable plan anchor:** `PLAN:WorkstreamD.WorkingDocumentPair`

---

## 13. Definition of Done

Workstream D should be considered complete when all of the following are true:

1. intake routing is implemented against normalized source artifacts,
2. project classification is real, persisted, and provenance-aware,
3. action/deadline/decision extraction is real and reviewable,
4. ambiguity creates structured review interrupts rather than silent mutation,
5. planner behavior produces explainable priority outputs,
6. focus packs and related daily-priority artifacts are generated and persisted,
7. project-memory refresh is integrated and traceable,
8. application/API surfaces exist for triage and priority consumption,
9. review-first and no-auto-send boundaries remain intact,
10. and the required automated verification evidence has been executed and recorded.

If these are not true, Glimmer still lacks the core assistant decision layer that turns ingested signals into meaningful operational guidance.

**Stable plan anchor:** `PLAN:WorkstreamD.DefinitionOfDone`

---

## 14. Final Note

Workstream D is where Glimmer starts to justify its existence.

If this workstream is done well, the operator will stop seeing Glimmer as a structured inbox and start seeing it as a real operational partner.
If it is done badly, the system will either become a fuzzy suggestion machine or a brittle rule engine with no honest way to surface ambiguity.

The right outcome is neither of those.
The right outcome is a reviewable, provenance-aware, explainable assistant core that can be trusted to interpret work without pretending to replace judgment.

**Stable plan anchor:** `PLAN:WorkstreamD.Conclusion`

