# Glimmer — Workstream B Domain and Memory Design and Implementation Plan

## Document Metadata

- **Document Title:** Glimmer — Workstream B Domain and Memory Design and Implementation Plan
- **Document Type:** Working Implementation Plan
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** B — Domain and Memory
- **Primary Companion Documents:** Requirements, Architecture, Build Plan, Verification, Governance and Process, Global Copilot Instructions, Module Instructions, Workstream B Verification Pack

---

## 1. Purpose

This document is the active working implementation plan for **Workstream B — Domain and Memory**.

Its purpose is to translate the canonical Workstream B build-plan document into an execution-ready plan that a coding agent can use during real implementation sessions.

This file should remain practical and anchored. It is not the source of architecture truth. It is the working plan for how the Glimmer memory spine should be implemented, verified, and advanced slice by slice.

**Stable working anchor:** `WORKB:Plan.ControlSurface`

---

## 2. Workstream Objective

The objective of Workstream B is to establish Glimmer’s structured operational memory model so that later connectors, assistant-core workflows, workspace surfaces, and companion modes all have durable, traceable state to build on.

At the end of Workstream B, the repository should have a real, queryable, persistence-backed model for:

- projects,
- workstreams,
- milestones,
- stakeholders and stakeholder identities,
- connected accounts and profiles,
- source-bearing records,
- interpreted candidate artifacts,
- accepted operational artifacts,
- drafts and briefing artifacts,
- summaries and refresh lineage,
- channel-session continuity state,
- and audit/trace records.

This workstream is where Glimmer stops being just an application shell and starts becoming a structured system of record.

**Stable working anchor:** `WORKB:Plan.Objective`

---

## 3. Control Anchors in Scope

### 3.1 Requirements anchors

- `REQ:ProjectMemory`
- `REQ:StakeholderMemory`
- `REQ:MessageIngestion`
- `REQ:MultiAccountProfileSupport`
- `REQ:DraftResponseWorkspace`
- `REQ:PreparedBriefings`
- `REQ:VisualPersonaSupport`
- `REQ:VisualPersonaAssetManagement`
- `REQ:TraceabilityAndAuditability`
- `REQ:Explainability`
- `REQ:StateContinuity`
- `REQ:HumanApprovalBoundaries`

### 3.2 Architecture anchors

- `ARCH:StructuredMemoryModel`
- `ARCH:PortfolioDomainModel`
- `ARCH:ProjectStateModel`
- `ARCH:StakeholderModel`
- `ARCH:MessageModel`
- `ARCH:DraftModel`
- `ARCH:PersonaAssetModel`
- `ARCH:ConnectedAccountModel`
- `ARCH:ChannelSessionModel`
- `ARCH:MemoryStorageStrategy`
- `ARCH:ProjectMemoryRefresh`
- `ARCH:AuditAndTraceLayer`
- `ARCH:ReviewGateArchitecture`
- `ARCH:AccountProvenanceModel`

### 3.3 Build-plan anchors

- `PLAN:WorkstreamB.DomainAndMemory`
- `PLAN:WorkstreamB.Objective`
- `PLAN:WorkstreamB.InternalSequence`
- `PLAN:WorkstreamB.VerificationExpectations`
- `PLAN:WorkstreamB.DefinitionOfDone`

### 3.4 Verification anchors

- `TEST:Domain.ProjectLifecycle.BasicPersistence`
- `TEST:Domain.ProjectPortfolio.WorkstreamsAndMilestonesPersist`
- `TEST:Domain.StakeholderIdentity.MultiIdentityLinking`
- `TEST:Domain.MultiAccount.ProvenancePersistence`
- `TEST:Domain.SourceRecords.MessagesThreadsEventsPersistSeparately`
- `TEST:Domain.InterpretedVsAccepted.Separation`
- `TEST:Domain.Interpretation.ReviewStateLifecyclePersists`
- `TEST:Domain.Execution.AcceptedArtifactsPersistSeparately`
- `TEST:Domain.Drafting.DraftsAndVariantsPersistWithIntent`
- `TEST:Domain.Briefings.FocusAndBriefingArtifactsPersist`
- `TEST:Domain.Persona.AssetsAndClassificationPersist`
- `TEST:Domain.ChannelSessions.TelegramAndVoiceStatePersist`
- `TEST:Domain.SummaryRefresh.Lineage`
- `TEST:Domain.Audit.MeaningfulStateMutation`

**Stable working anchor:** `WORKB:Plan.ControlAnchors`

---

## 4. Execution Principles for This Workstream

### 4.1 Explicit memory layers first

Keep the memory model visibly separated into:

- source records,
- interpreted candidate artifacts,
- accepted operational state,
- and synthesized/summary artifacts.

Do not collapse these layers for convenience.

### 4.2 Relational truth before retrieval convenience

The primary goal is explicit, queryable structured state in PostgreSQL. Retrieval and semantic helpers may come later, but they must not replace the real memory model.

### 4.3 Provenance is part of the model, not metadata garnish

Connected account identity, provider/source identity, profile context, and origin linkage must be treated as load-bearing parts of the schema and persistence design.

### 4.4 Review-state semantics must be durable

Interpreted artifacts should not become accepted truth implicitly. Review-state and promotion pathways need to be modeled clearly.

### 4.5 Auditability is required, not optional polish

Meaningful state mutation, refresh, and promotion paths must create traceable records or at least land inside structures designed for traceability.

### 4.6 Build one coherent entity slice at a time

Prefer bounded vertical memory slices rather than trying to define the entire domain in one huge pass.

**Stable working anchor:** `WORKB:Plan.ExecutionPrinciples`

---

## 5. Memory Shape Target for Workstream B

By the end of this workstream, the implementation should materially support the following memory categories or directly equivalent concrete shapes:

- portfolio entities
- stakeholder and identity entities
- connected accounts and account profiles
- source-layer records
- interpretation-layer records
- accepted operational records
- drafting and briefing artifacts
- persona asset and classification records
- channel-session continuity records
- summaries, lineage, and audit records

The exact code-level structure may evolve, but these conceptual layers must remain explicit and queryable.

**Stable working anchor:** `WORKB:Plan.MemoryShapeTarget`

---

## 6. Work Packages to Execute

## 6.1 WB1 — Core portfolio entities

### Objective
Implement the durable base entities for projects, workstreams, milestones, and related project state.

### Expected touch points
- domain models
- persistence mappings
- repository/query surfaces
- migrations

### Verification expectation
- `TEST:Domain.ProjectLifecycle.BasicPersistence`
- `TEST:Domain.ProjectPortfolio.WorkstreamsAndMilestonesPersist`

### Notes
This is the structural backbone for everything else. Keep lifecycle semantics explicit.

**Stable working anchor:** `WORKB:Plan.PackageWB1`

---

## 6.2 WB2 — Stakeholder and identity model

### Objective
Implement stakeholders and their multiple identities without forced flattening.

### Expected touch points
- stakeholder model
- stakeholder identity model
- relationships to projects and source records
- repository/query surfaces
- migrations

### Verification expectation
- `TEST:Domain.StakeholderIdentity.MultiIdentityLinking`

### Notes
The model should make it possible to avoid premature identity merging.

**Stable working anchor:** `WORKB:Plan.PackageWB2`

---

## 6.3 WB3 — Connected accounts, profiles, and provenance-bearing source layer

### Objective
Implement connected-account and account-profile entities plus the explicit source-layer records needed later by connectors.

### Expected touch points
- connected account model
- account profile model
- message/thread/event/imported-signal entities
- provenance fields and linkages
- migrations

### Verification expectation
- `TEST:Domain.MultiAccount.ProvenancePersistence`
- `TEST:Domain.SourceRecords.MessagesThreadsEventsPersistSeparately`

### Notes
Even before live connectors, the target source-layer model should be explicit and durable.

**Stable working anchor:** `WORKB:Plan.PackageWB3`

---

## 6.4 WB4 — Interpretation-layer artifacts and review-state model

### Objective
Implement reviewable candidate artifacts for classification, action/deadline/decision extraction, and related interpretation outcomes.

### Expected touch points
- interpreted artifact entities
- review-state fields/model
- origin linkages to source layer
- migrations

### Verification expectation
- `TEST:Domain.InterpretedVsAccepted.Separation`
- `TEST:Domain.Interpretation.ReviewStateLifecyclePersists`

### Notes
This layer is one of the most important architecture protections in the whole project.

**Stable working anchor:** `WORKB:Plan.PackageWB4`

---

## 6.5 WB5 — Accepted operational artifact layer

### Objective
Implement the durable accepted-state layer for work items, decisions, risks, blockers, waiting-on records, and similar operational truths.

### Expected touch points
- accepted artifact entities
- promotion linkage from interpreted layer
- repository/query surfaces
- migrations

### Verification expectation
- `TEST:Domain.Execution.AcceptedArtifactsPersistSeparately`

### Notes
Do not collapse this into interpretation-layer records for query convenience.

**Stable working anchor:** `WORKB:Plan.PackageWB5`

---

## 6.6 WB6 — Drafting, briefing, and focus artifacts

### Objective
Implement persistent models for drafts, draft variants, focus packs, and briefing artifacts.

### Expected touch points
- draft and variant models
- briefing/focus artifact models
- origin/project linkage
- migrations

### Verification expectation
- `TEST:Domain.Drafting.DraftsAndVariantsPersistWithIntent`
- `TEST:Domain.Briefings.FocusAndBriefingArtifactsPersist`

### Notes
These artifacts should be first-class records, not ad hoc blobs attached to UI state.

**Stable working anchor:** `WORKB:Plan.PackageWB6`

---

## 6.7 WB7 — Persona assets and classification records

### Objective
Implement the managed records needed to support bounded persona rendering and asset selection later.

### Expected touch points
- persona asset model
- persona classification / context mapping model
- migrations

### Verification expectation
- `TEST:Domain.Persona.AssetsAndClassificationPersist`

### Notes
This is about managed UX assets, not just static images in a folder.

**Stable working anchor:** `WORKB:Plan.PackageWB7`

---

## 6.8 WB8 — Channel-session continuity records

### Objective
Implement the durable state records needed to support Telegram and voice continuity later.

### Expected touch points
- channel session model
- Telegram conversation state model
- voice session state model
- linkage to summaries/origin where needed
- migrations

### Verification expectation
- `TEST:Domain.ChannelSessions.TelegramAndVoiceStatePersist`

### Notes
This should support continuity without becoming a hidden shadow-memory system.

**Stable working anchor:** `WORKB:Plan.PackageWB8`

---

## 6.9 WB9 — Summary, refresh, and lineage model

### Objective
Implement summary artifacts, refresh metadata, supersession behavior, and lineage structures.

### Expected touch points
- summary models
- refresh metadata
- supersession linkage
- repository/query surfaces
- migrations

### Verification expectation
- `TEST:Domain.SummaryRefresh.Lineage`

### Notes
Summaries should be explicit derived artifacts, not magic rewrites of history.

**Stable working anchor:** `WORKB:Plan.PackageWB9`

---

## 6.10 WB10 — Audit and trace layer

### Objective
Implement or materially establish durable audit/trace records for meaningful memory evolution.

### Expected touch points
- audit record model
- state-change trace linkage
- repository/query surfaces
- migrations

### Verification expectation
- `TEST:Domain.Audit.MeaningfulStateMutation`

### Notes
Auditability must be visible in the model, not left to generic logs alone.

**Stable working anchor:** `WORKB:Plan.PackageWB10`

---

## 7. Recommended Execution Order

The recommended execution order inside this working plan is:

1. WB1 — Core portfolio entities
2. WB2 — Stakeholder and identity model
3. WB3 — Connected accounts, profiles, and provenance-bearing source layer
4. WB4 — Interpretation-layer artifacts and review-state model
5. WB5 — Accepted operational artifact layer
6. WB6 — Drafting, briefing, and focus artifacts
7. WB7 — Persona assets and classification records
8. WB8 — Channel-session continuity records
9. WB9 — Summary, refresh, and lineage model
10. WB10 — Audit and trace layer

This sequence keeps the memory model layered and avoids designing derived artifacts before the lower layers exist.

**Stable working anchor:** `WORKB:Plan.ExecutionOrder`

---

## 8. Expected Files and Layers Likely to Change

The initial Workstream B implementation is likely to touch files or file groups such as:

- domain models/entities
- ORM mappings / persistence models
- migrations
- repository/query services
- summary-refresh support services
- audit/trace support surfaces
- test fixtures and integration harnesses
- Workstream B working documents

This list should be refined as implementation begins.

**Stable working anchor:** `WORKB:Plan.LikelyTouchPoints`

---

## 9. Verification Plan for Workstream B

### 9.1 Minimum required proof

At minimum, Workstream B implementation should produce executable proof for:

- project persistence
- stakeholder identity plurality
- provenance persistence
- source-layer explicitness
- interpreted-vs-accepted separation
- review-state lifecycle persistence
- accepted-state persistence
- draft/briefing/focus artifact persistence
- channel-session persistence
- summary lineage
- audit mutation recording

### 9.2 Primary verification surfaces

The main verification references for this workstream are:

- `verification-pack-workstream-b.md`
- `verification-pack-data-integrity.md`

### 9.3 Evidence expectation

Meaningful implementation slices in this workstream should update the Workstream B progress file with:

- what was implemented
- what proof was executed
- what passed
- what failed
- what remains blocked or deferred

**Stable working anchor:** `WORKB:Plan.VerificationPlan`

---

## 10. Human Dependencies and Likely Decisions

This workstream is mostly agent-executable, but a few human decisions may still be needed.

Likely human-dependent areas include:

- confirmation of any especially contentious entity naming or lifecycle semantics
- confirmation of how broad the first accepted-artifact set should be if time pressure forces prioritization
- and review of any schema tradeoff that materially affects provenance, review-state semantics, or summary lineage

The coding agent should complete all safe model and persistence work before surfacing human dependencies as blockers.

**Stable working anchor:** `WORKB:Plan.HumanDependencies`

---

## 11. Known Risks in This Workstream

### 11.1 Risk — Collapsing candidate and accepted state

This is the most dangerous shortcut in the workstream and must be resisted.

### 11.2 Risk — Weak provenance modeling

If connected-account and source-origin semantics are underspecified here, Workstream C inherits a broken foundation.

### 11.3 Risk — Summary model becomes magical

If summaries are not modeled with lineage and supersession, later memory refresh work becomes opaque.

### 11.4 Risk — Over-designing every future artifact up front

There is a risk of spending too long modeling rarely used artifacts before proving the core memory layers.

### 11.5 Risk — Auditability left to logs only

If audit and trace are not designed into the model, later explainability becomes much harder.

**Stable working anchor:** `WORKB:Plan.Risks`

---

## 12. Immediate Next Session Recommendations

When actual coding for Workstream B begins, the first sensible execution slice is:

1. define the project/workstream/milestone entities,
2. create the first migration for the core portfolio layer,
3. add repository/query support for basic project persistence,
4. execute the first domain persistence proof,
5. then expand into stakeholder identity and provenance-bearing source records.

That creates a real memory backbone quickly without prematurely mixing in interpretation or UI concerns.

**Stable working anchor:** `WORKB:Plan.ImmediateNextSlice`

---

## 13. Definition of Ready for Workstream B Completion

Workstream B should only be considered ready for completion when all of the following are materially true:

- portfolio entities are real
- stakeholder and identity entities are real
- connected accounts and source-layer records are real
- interpreted artifacts and review states are real
- accepted operational artifacts are real
- drafts/briefings/focus artifacts are real
- summaries and lineage are real
- audit and trace are real
- channel-session continuity records are real
- and the corresponding persistence/integrity proof paths have been executed and recorded

If these are not true, Workstream B is not done, even if many tables or models exist.

**Stable working anchor:** `WORKB:Plan.DefinitionOfReadyForCompletion`

---

## 14. Final Note

This workstream is where Glimmer earns the right to call itself a structured chief-of-staff system instead of just an interface sitting on prompts.

That is the standard.

The goal is not to model everything imaginable. The goal is to build a memory spine strong enough that connectors, orchestration, UI, and companion modes can all trust it.

**Stable working anchor:** `WORKB:Plan.Conclusion`
