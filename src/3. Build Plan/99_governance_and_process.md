# Glimmer — Governance and Process

## Document Metadata

- **Document Title:** Glimmer — Governance and Process
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Testing Strategy, Workstreams A–H

---

## 1. Purpose

This document defines the governance, control, and delivery process model for **Glimmer**.

Its purpose is to explain how the project is managed once the control documents, workstreams, and verification model are in place. This includes:

- phase-exit logic,
- human intervention points,
- design-change handling,
- working-document expectations,
- completion rules,
- and the operating relationship between the human lead and the coding agent.

This document is not the source of product requirements or architecture truth. It is the process document that governs how those truths are carried through implementation safely.

**Stable plan anchor:** `PLAN:GovernanceAndProcess`

---

## 2. Governance Intent

Glimmer is being delivered under an agentic delivery model, which means implementation velocity can become very high once the repo, instructions, and workstreams are in place.

That is useful, but it also creates risk:

- drift from architecture,
- false progress,
- unreviewed design shortcuts,
- incomplete verification,
- and ambiguity about what the agent may decide versus what requires human approval.

The governance model exists to keep the project:

- architecturally aligned,
- reviewable,
- evidence-backed,
- and practical for sustained AI-assisted implementation.

**Stable plan anchor:** `PLAN:GovernanceIntent`

---

## 3. Governance Principles

### 3.1 Control documents outrank implementation convenience

Requirements, architecture, build plan, and verification documents are the primary control surface. Implementation should follow them rather than quietly rewriting them through code.

**Stable plan anchor:** `PLAN:GovernancePrinciple.ControlDocsFirst`

### 3.2 Working documents track implementation truth, not design truth

Workstream plan/progress files are authoritative for current execution state, but they do not replace requirements or architecture.

**Stable plan anchor:** `PLAN:GovernancePrinciple.WorkingDocsScope`

### 3.3 Human approval remains load-bearing

The coding agent can implement extensively, but it cannot silently approve scope change, architecture change, connector-scope expansion, security weakening, or release confidence.

**Stable plan anchor:** `PLAN:GovernancePrinciple.HumanApprovalLoadBearing`

### 3.4 Verification evidence is required for meaningful completion

A work package, workstream, or phase is not considered complete purely because code exists. Executed proof and recorded evidence are required.

**Stable plan anchor:** `PLAN:GovernancePrinciple.EvidenceRequired`

### 3.5 Drift must be surfaced, not hidden

When the code, documents, or implementation path diverge materially, that divergence must be surfaced explicitly rather than worked around quietly.

**Stable plan anchor:** `PLAN:GovernancePrinciple.SurfaceDrift`

---

## 4. Authority Model Across the Project

The Glimmer project follows the authority model defined in the framework and reflected in the project document set.

### 4.1 Authoritative control surfaces

The authoritative control surfaces are:

1. **Requirements** — what must be true
2. **Architecture** — how the system is shaped
3. **Build Plan** — how the work is sequenced
4. **Verification** — how completion is proven

**Stable plan anchor:** `PLAN:AuthorityModel.ControlSurfaces`

### 4.2 Operational support surfaces

Operational support surfaces include:

- `.github/copilot-instructions.md`
- module-scoped instructions
- `8. Agent Skills/`
- `9. Agent Tools/`
- generated retrieval maps
- validation helpers

These are important, but they are not the design source of truth.

**Stable plan anchor:** `PLAN:AuthorityModel.OperationalSupport`

### 4.3 Working documents

Working documents are authoritative for:

- current implementation state,
- blockers,
- evidence status,
- and session handoff.

They are not authoritative for changing requirements or architecture.

**Stable plan anchor:** `PLAN:AuthorityModel.WorkingDocs`

---

## 5. Human–Agent Responsibility Model

### 5.1 Human responsibilities

The human lead is responsible for:

- product intent,
- requirements truth,
- architecture truth,
- scope changes,
- connector and security boundary decisions,
- release judgment,
- and approval of deferred/manual verification where meaningful.

**Stable plan anchor:** `PLAN:ResponsibilityModel.Human`

### 5.2 Agent responsibilities

The coding agent is responsible for:

- implementing work packages,
- maintaining working documents,
- following instructions and anchors,
- writing and running tests,
- updating verification status,
- surfacing blockers,
- and making bounded implementation progress without waiting unnecessarily.

**Stable plan anchor:** `PLAN:ResponsibilityModel.Agent`

### 5.3 Shared responsibility areas

The human and agent jointly participate in:

- refining work package decomposition,
- clarifying ambiguous behavior,
- deciding where new anchors are needed,
- and determining whether design drift requires document updates.

**Stable plan anchor:** `PLAN:ResponsibilityModel.Shared`

---

## 6. Working-Document Operating Rules

### 6.1 Required working-document pair per workstream

Each major workstream should eventually have:

- `WorkstreamX_*_DESIGN_AND_IMPLEMENTATION_PLAN.md`
- `WorkstreamX_*_DESIGN_AND_IMPLEMENTATION_PROGRESS.md`

**Stable plan anchor:** `PLAN:WorkingDocs.RequiredPair`

### 6.2 Plan file role

The plan file should describe:

- current implementation approach,
- active scope,
- linked anchors,
- expected tests,
- file-level change areas,
- and human dependencies.

**Stable plan anchor:** `PLAN:WorkingDocs.PlanRole`

### 6.3 Progress file role

The progress file should record:

- what has been implemented,
- what remains,
- what verification has passed or failed,
- current blockers,
- assumptions made,
- and what the next session should pick up.

**Stable plan anchor:** `PLAN:WorkingDocs.ProgressRole`

### 6.4 Update expectation

Working documents should be updated during meaningful implementation progress, not left stale until the end of a workstream.

**Stable plan anchor:** `PLAN:WorkingDocs.UpdateCadence`

---

## 7. Phase Exit Model

The build plan defines five phases for Glimmer. This document defines how the project should judge exit readiness for each.

### 7.1 Phase 0 exit — Control surface readiness

Phase 0 should be considered complete when:

- requirements exist and are coherent,
- architecture index and split docs exist,
- build-plan index and workstream set exist,
- testing strategy exists,
- and the control surface is stable enough to guide implementation.

**Stable plan anchor:** `PLAN:PhaseExit.Phase0`

### 7.2 Phase 1 exit — Runtime and memory foundation readiness

Phase 1 should be considered complete when:

- the implementation skeleton is real,
- persistence baseline exists,
- the core domain/memory model exists,
- and foundational verification has been executed.

**Stable plan anchor:** `PLAN:PhaseExit.Phase1`

### 7.3 Phase 2 exit — External boundary readiness

Phase 2 should be considered complete when:

- connected-account handling is real,
- normalization/provenance are real,
- supported connectors are implemented against their boundaries,
- and connector proof exists.

**Stable plan anchor:** `PLAN:PhaseExit.Phase2`

### 7.4 Phase 3 exit — Assistant-core readiness

Phase 3 should be considered complete when:

- intake, triage, planner, and project-memory refresh flows are real,
- focus and priority outputs exist,
- the main reviewable web surfaces exist,
- and the relevant graph/browser/API proof has executed successfully.

**Stable plan anchor:** `PLAN:PhaseExit.Phase3`

### 7.5 Phase 4 exit — Companion and voice readiness

Phase 4 should be considered complete when:

- Telegram companion behavior is real and bounded,
- voice mode is real and review-safe,
- handoff/continuity behavior exists,
- and the remaining manual/deferred verification is explicitly understood.

**Stable plan anchor:** `PLAN:PhaseExit.Phase4`

---

## 8. Human Intervention Points

Some activities require explicit human action and should be treated as expected governance points, not interruptions.

### 8.1 Typical intervention categories

Expected human intervention categories include:

- external OAuth app registration and consent configuration,
- secret provisioning,
- Telegram bot provisioning,
- production voice infrastructure decisions,
- approval of meaningful architecture changes,
- acceptance of `ManualOnly` / `Deferred` verification,
- and release readiness judgment.

**Stable plan anchor:** `PLAN:HumanInterventionCategories`

### 8.2 How the agent should surface intervention needs

When human help is required, the agent should present:

- what is needed,
- why it is needed,
- what work was completed before hitting the dependency,
- and what remains blocked.

**Stable plan anchor:** `PLAN:HumanInterventionRequestFormat`

### 8.3 Avoiding premature blocking

The coding agent should complete all code-safe work before surfacing a blocker that depends on human action.

**Stable plan anchor:** `PLAN:HumanInterventionNoPrematureBlock`

---

## 9. Design Change and Drift Handling

### 9.1 Minor implementation refinements

Minor refinements that do not materially change requirements, architecture, or safety posture may be handled within working documents and implementation notes.

**Stable plan anchor:** `PLAN:ChangeControl.MinorRefinement`

### 9.2 Material design changes

A material design change includes things such as:

- changing the primary technology baseline,
- weakening local-first or review-first posture,
- broadening connector scope,
- changing no-auto-send boundaries,
- introducing multi-user scope,
- or redefining core domain semantics.

Material design changes require explicit human review and the relevant control-document updates.

**Stable plan anchor:** `PLAN:ChangeControl.MaterialChange`

### 9.3 Drift handling rule

If implementation drifts from the current control documents, one of two things must happen:

1. the implementation is corrected to match the documents, or
2. the documents are intentionally updated through human-approved change.

Quiet divergence is not acceptable.

**Stable plan anchor:** `PLAN:ChangeControl.DriftRule`

---

## 10. Completion and Status Model

### 10.1 Status vocabulary

The project should use a small, explicit status vocabulary for work packages and workstreams.

Suggested statuses:

- `Designed`
- `InProgress`
- `Implemented`
- `Verified`
- `Blocked`
- `HumanReviewRequired`
- `Deferred`

**Stable plan anchor:** `PLAN:StatusVocabulary`

### 10.2 Completion rule

A work item should not be marked complete unless:

- the implementation is present,
- the linked verification has been executed or explicitly classified,
- and the progress file reflects the current truth.

**Stable plan anchor:** `PLAN:CompletionRule`

### 10.3 False-green prevention

The governance model should resist these false-green conditions:

- code written but not executed,
- tests written but not run,
- browser flows assumed but not automated,
- review boundaries implied but not proven,
- or “mostly works” being recorded as complete without explicit caveats.

**Stable plan anchor:** `PLAN:FalseGreenPrevention`

---

## 11. Verification Governance

### 11.1 Verification pack ownership

Each feature workstream owns its own proof obligations, but Workstream G owns the cross-cutting regression estate and the verification control surface.

**Stable plan anchor:** `PLAN:VerificationGovernance.Ownership`

### 11.2 Release-confidence posture

Release confidence should be judged from:

- relevant workstream pack status,
- smoke pack status,
- release pack status,
- unresolved deferred/manual items,
- and human judgment on the seriousness of any remaining gaps.

**Stable plan anchor:** `PLAN:VerificationGovernance.ReleaseConfidence`

### 11.3 Evidence reporting expectation

Verification evidence should be recorded in a way that allows the human lead to answer:

- what passed,
- what failed,
- what is deferred,
- and what that means for confidence.

**Stable plan anchor:** `PLAN:VerificationGovernance.EvidenceReporting`

---

## 12. Retrieval, Skills, and Operational Support Governance

### 12.1 Retrieval layer rule

If the repo contains a local retrieval/index layer under `9. Agent Tools/`, the agent should use it to narrow context before broadly reading large document sets.

**Stable plan anchor:** `PLAN:OperationalSupport.RetrievalRule`

### 12.2 Skills and instructions rule

Agent skills and module-scoped instructions should be treated as operational behavior controls. They should be kept aligned to the canonical requirements, architecture, build plan, and verification documents.

**Stable plan anchor:** `PLAN:OperationalSupport.InstructionAlignment`

### 12.3 Validation and freshness rule

Generated indexes, validation outputs, and related helper artifacts should not become silent stale authorities. Their freshness must be checked or regenerated as part of responsible agent use.

**Stable plan anchor:** `PLAN:OperationalSupport.FreshnessRule`

---

## 13. Suggested Next Governance Artifacts

After this document, the next governance/control artifacts that should be created are:

- `.github/copilot-instructions.md`
- module-scoped instruction files under `.github/instructions/`
- `8. Agent Skills/README.md`
- `9. Agent Tools/README.md`
- `4. Verification/TEST_CATALOG.md`
- the verification packs defined in the document set

This order preserves the intended transition from planning into instruction and proof surfaces.

**Stable plan anchor:** `PLAN:GovernanceNextArtifacts`

---

## 14. Final Note

Glimmer’s governance model should not feel bureaucratic. It should feel stabilizing.

The point is not to create paperwork. The point is to make AI-assisted delivery safe enough to move quickly without fooling ourselves.

If the project keeps:

- clear control documents,
- explicit human approval points,
- current working documents,
- honest verification evidence,
- and surfaced drift,

then the coding agent can move fast without the project losing its shape.

**Stable plan anchor:** `PLAN:GovernanceConclusion`

