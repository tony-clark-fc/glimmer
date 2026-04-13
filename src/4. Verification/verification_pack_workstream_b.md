# Glimmer — Verification Pack: Workstream B Domain and Memory

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Workstream B Domain and Memory
- **Document Type:** Canonical Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Test Catalog, Requirements, Architecture, Build Plan, Testing Strategy, Workstream B Domain and Memory, Workstream A Verification Pack

---

## 1. Purpose

This document defines the **Workstream B verification pack** for **Glimmer**.

Its purpose is to prove that the structured domain and memory substrate created by **Workstream B — Domain and Memory** is durable, reviewable, provenance-preserving, and safe for later connectors, orchestration flows, UI surfaces, and companion channels to build on.

Where Workstream A proves that Glimmer is buildable, this pack proves that Glimmer has started to become a real operational system of record.

**Stable verification anchor:** `TESTPACK:WorkstreamB.ControlSurface`

---

## 2. Role of the Workstream B Pack

This pack exists to verify the implementation outcomes expected from the Domain and Memory workstream, including:

- core portfolio entity correctness,
- stakeholder and identity modeling,
- connected-account and provenance-bearing source structures,
- reviewable interpretation artifacts,
- accepted operational execution artifacts,
- drafts and briefing artifact persistence,
- summary and refresh lineage,
- channel-session state,
- and auditability for meaningful state change.

This pack is one of the most load-bearing verification packs in the Glimmer project because later orchestration, connector, and UI work all depend on the truthfulness of the memory spine.

**Stable verification anchor:** `TESTPACK:WorkstreamB.Role`

---

## 3. Relationship to the Control Surface

This verification pack is derived from and aligned to:

- the **Agentic Delivery Framework**, especially its authority model, verification model, evidence-of-completion rules, requirements-to-verification traceability, and structured document hierarchy,
- the **Testing Strategy Companion**, especially automation-first proof, behavior-over-coverage, database/integration testing, and evidence-backed completion,
- the **Glimmer Agentic Delivery Document Set**, which explicitly defines `verification-pack-workstream-b.md` as part of the canonical verification family,
- the **Glimmer Requirements**, especially project memory, stakeholder memory, message ingestion, multi-account profile support, traceability and auditability, explainability, and state continuity,
- the **Glimmer Testing Strategy**, especially domain-memory verification, data-integrity expectations, provenance preservation, and reviewable state separation,
- the latest **Glimmer Architecture** state, including the canonical architecture index and the manually maintained current architecture document, especially the structured memory, domain model, state ownership, connected-account, audit, and project-memory refresh anchors,
- the **Build Plan**, **Build Strategy**, and **Workstream B — Domain and Memory**, which explicitly place the memory substrate ahead of deep connectors and assistant-core workflow sophistication,
- the **Governance and Process** document, which requires evidence-backed completion and surfaced drift for meaningful work,
- and the current **Test Catalog**, which already defines the canonical domain-and-memory `TEST:` anchors this pack should organize and extend.

**Stable verification anchor:** `TESTPACK:WorkstreamB.ControlSurfaceAlignment`

---

## 4. Why This Pack Is Load-Bearing

The Glimmer architecture is explicit that structured memory, provenance preservation, reviewable interpretation, and accepted operational state are foundational principles rather than implementation details.

Workstream B is where those principles become real in persistence and domain structure. It establishes:

- operator, project, workstream, and milestone entities,
- stakeholder and identity structures,
- connected accounts and provenance-bearing source records,
- interpreted candidate artifacts,
- accepted work/execution artifacts,
- drafts and briefing artifacts,
- channel-session state,
- summaries and memory refresh structures,
- and audit/trace linkage.

If this pack is weak, later workstreams may appear to function while actually depending on:

- flattened provenance,
- silent candidate-to-accepted state collapse,
- weak summary lineage,
- or ambiguous stakeholder identity handling.

That is exactly what this pack is meant to prevent.

**Stable verification anchor:** `TESTPACK:WorkstreamB.Rationale`

---

## 5. Workstream B Verification Scope

### 5.1 In scope

This pack covers proof for the following Domain and Memory concerns:

- persistence and retrieval of core project portfolio entities,
- stakeholder and stakeholder-identity relationship behavior,
- connected-account and provenance-bearing source persistence,
- separation between source records, interpreted artifacts, accepted operational state, and synthesized artifacts,
- review-state handling for interpreted artifacts,
- draft and briefing artifact persistence,
- summary refresh and lineage behavior,
- audit and trace behavior for meaningful state mutation,
- and channel-session state persistence where Workstream B defines it.

### 5.2 Out of scope

This pack does **not** attempt to prove:

- live provider ingestion behavior,
- connector normalization semantics,
- triage/planner graph quality,
- browser-visible UX behavior,
- Telegram companion usefulness,
- or voice-session runtime interaction quality.

Those belong to later workstream packs and cross-cutting packs.

**Stable verification anchor:** `TESTPACK:WorkstreamB.Scope`

---

## 6. Source `TEST:` Anchors Included in This Pack

The Workstream B pack is built primarily from the domain-and-memory scenario group in the canonical Test Catalog and adds a small number of memory-specific scenarios needed to cover the full Workstream B shape.

### 6.1 Canonical domain-and-memory anchors already defined in the Test Catalog

#### `TEST:Domain.ProjectLifecycle.BasicPersistence`
- **Scenario name:** Project records persist and reload correctly
- **Layers:** `integration`
- **Role in this pack:** Baseline proof that project state is durable and queryable.

#### `TEST:Domain.StakeholderIdentity.MultiIdentityLinking`
- **Scenario name:** One stakeholder can hold multiple identities without losing distinction
- **Layers:** `integration`
- **Role in this pack:** Proves identity plurality without forced merge.

#### `TEST:Domain.MultiAccount.ProvenancePersistence`
- **Scenario name:** Source provenance survives persistence round trips
- **Layers:** `integration`
- **Role in this pack:** Proves account/profile/provider provenance is durable.

#### `TEST:Domain.InterpretedVsAccepted.Separation`
- **Scenario name:** Interpreted artifacts remain distinct from accepted operational state
- **Layers:** `integration`
- **Role in this pack:** Proves candidate understanding does not silently become accepted truth.

#### `TEST:Domain.SummaryRefresh.Lineage`
- **Scenario name:** Summary refresh preserves lineage and metadata
- **Layers:** `integration`
- **Role in this pack:** Proves summary artifacts remain explicit, traceable, and refresh-aware.

#### `TEST:Domain.Audit.MeaningfulStateMutation`
- **Scenario name:** Meaningful state mutations generate durable audit records
- **Layers:** `integration`
- **Role in this pack:** Proves the memory spine is traceable rather than opaque.

### 6.2 Additional Workstream B-specific anchors introduced by this pack

#### `TEST:Domain.ProjectPortfolio.WorkstreamsAndMilestonesPersist`
- **Scenario name:** Project workstreams and milestones persist with explicit relationship semantics
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:ProjectPortfolioManagement`, `ARCH:ProjectStateModel`, `ARCH:ProjectWorkstreamModel`, `ARCH:MilestoneModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove the portfolio structure above the task level is durable and relationship-safe.

#### `TEST:Domain.SourceRecords.MessagesThreadsEventsPersistSeparately`
- **Scenario name:** Messages, threads, events, and imported signals persist as distinct source-bearing records
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:MessageIngestion`, `ARCH:MessageModel`, `ARCH:MessageThreadModel`, `ARCH:CalendarEventModel`, `ARCH:ImportedSignalModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove the source layer is explicitly modeled rather than flattened.

#### `TEST:Domain.Interpretation.ReviewStateLifecyclePersists`
- **Scenario name:** Interpretation review-state lifecycle persists correctly
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:InterpretationReviewState`, `ARCH:StateOwnershipBoundaries`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove candidate artifacts can move through review-safe states without ambiguity.

#### `TEST:Domain.Execution.AcceptedArtifactsPersistSeparately`
- **Scenario name:** Accepted work items, decisions, blockers, risks, and waiting-on records persist separately from interpreted candidates
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:ProjectMemory`, `REQ:Explainability`, `ARCH:WorkItemModel`, `ARCH:DecisionRecordModel`, `ARCH:RiskRecordModel`, `ARCH:BlockerRecordModel`, `ARCH:WaitingOnRecordModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove accepted operational state is a real durable layer.

#### `TEST:Domain.Drafting.DraftsAndVariantsPersistWithIntent`
- **Scenario name:** Drafts and draft variants persist as linked drafting artifacts
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:DraftResponseWorkspace`, `ARCH:DraftModel`, `ARCH:DraftVariantModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove drafting artifacts are part of the memory model rather than transient text blobs.

#### `TEST:Domain.Briefings.FocusAndBriefingArtifactsPersist`
- **Scenario name:** Focus packs and briefing artifacts persist as explicit generated outputs
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:PreparedBriefings`, `REQ:PrioritizationEngine`, `ARCH:BriefingArtifactModel`, `ARCH:FocusPackModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove the system stores generated briefing artifacts explicitly.

#### `TEST:Domain.Persona.AssetsAndClassificationPersist`
- **Scenario name:** Persona assets and persona classifications persist as managed UX records
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:VisualPersonaSupport`, `REQ:VisualPersonaAssetManagement`, `ARCH:PersonaAssetModel`, `ARCH:PersonaClassificationModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove persona assets are managed records rather than ad hoc UI files only.

#### `TEST:Domain.ChannelSessions.TelegramAndVoiceStatePersist`
- **Scenario name:** Channel session state persists for companion and voice continuity
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:StateContinuity`, `ARCH:ChannelSessionModel`, `ARCH:TelegramConversationStateModel`, `ARCH:VoiceSessionStateModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamF.Voice`
- **Intent:** Prove channel continuity has a durable state layer to build on.

**Stable verification anchor:** `TESTPACK:WorkstreamB.IncludedTests`

---

## 7. Workstream B Pack Entry Table

| TEST Anchor | Scenario | Layer | Automation Status | Pack Priority | Notes |
|---|---|---|---|---|---|
| `TEST:Domain.ProjectLifecycle.BasicPersistence` | Project records persist and reload correctly | `integration` | Planned | Critical | Canonical domain baseline |
| `TEST:Domain.ProjectPortfolio.WorkstreamsAndMilestonesPersist` | Project workstreams and milestones persist with explicit relationship semantics | `integration` | Planned | High | Extends project model coverage |
| `TEST:Domain.StakeholderIdentity.MultiIdentityLinking` | One stakeholder can hold multiple identities without losing distinction | `integration` | Planned | Critical | Protects stakeholder memory semantics |
| `TEST:Domain.MultiAccount.ProvenancePersistence` | Source provenance survives persistence round trips | `integration` | Planned | Critical | Load-bearing for connectors and later UI |
| `TEST:Domain.SourceRecords.MessagesThreadsEventsPersistSeparately` | Messages, threads, events, and imported signals persist as distinct source-bearing records | `integration` | Planned | High | Protects source-layer explicitness |
| `TEST:Domain.InterpretedVsAccepted.Separation` | Interpreted artifacts remain distinct from accepted operational state | `integration` | Planned | Critical | One of the most important memory protections |
| `TEST:Domain.Interpretation.ReviewStateLifecyclePersists` | Interpretation review-state lifecycle persists correctly | `integration` | Planned | High | Protects review-safe candidate state |
| `TEST:Domain.Execution.AcceptedArtifactsPersistSeparately` | Accepted work items, decisions, blockers, risks, and waiting-on records persist separately from interpreted candidates | `integration` | Planned | Critical | Protects operational truth layer |
| `TEST:Domain.Drafting.DraftsAndVariantsPersistWithIntent` | Drafts and draft variants persist as linked drafting artifacts | `integration` | Planned | High | Supports later drafting UI and reviewability |
| `TEST:Domain.Briefings.FocusAndBriefingArtifactsPersist` | Focus packs and briefing artifacts persist as explicit generated outputs | `integration` | Planned | High | Supports planner and Today view later |
| `TEST:Domain.Persona.AssetsAndClassificationPersist` | Persona assets and persona classifications persist as managed UX records | `integration` | Planned | Medium | Supports bounded persona rendering later |
| `TEST:Domain.ChannelSessions.TelegramAndVoiceStatePersist` | Channel session state persists for companion and voice continuity | `integration` | Planned | Medium | Supports later continuity layers |
| `TEST:Domain.SummaryRefresh.Lineage` | Summary refresh preserves lineage and metadata | `integration` | Planned | Critical | Protects synthesized memory correctness |
| `TEST:Domain.Audit.MeaningfulStateMutation` | Meaningful state mutations generate durable audit records | `integration` | Planned | Critical | Protects explainability and traceability |

**Stable verification anchor:** `TESTPACK:WorkstreamB.EntryTable`

---

## 8. Expected Automation Shape

### 8.1 Integration-heavy proof by default

Most Workstream B proof should be implemented as integration tests because this workstream is fundamentally about:

- persistence,
- relationships,
- state boundaries,
- lineage,
- and audit behavior.

Unit tests may exist for deterministic helpers, but they are not the primary proof vehicle here.

### 8.2 Relationship and persistence proof

This proof should verify that:

- core entities persist and reload correctly,
- required relationships behave correctly,
- distinct state layers remain distinct,
- and provenance-bearing foreign-key or equivalent linkage survives round trips.

### 8.3 Review-state and accepted-state proof

This proof should verify that:

- interpreted artifacts can exist without automatic promotion,
- review states are durable,
- accepted state is persisted separately,
- and queries do not flatten candidate and accepted layers together accidentally.

### 8.4 Summary and audit proof

This proof should verify that:

- summary refresh metadata is captured,
- lineage is explicit,
- and meaningful mutations generate durable trace records.

### 8.5 Limited `manual_only` use

This pack should be overwhelmingly automated.

`ManualOnly` classification should be rare here because domain-memory truth is exactly the kind of thing that should be proven through automation rather than informal inspection.

**Stable verification anchor:** `TESTPACK:WorkstreamB.AutomationShape`

---

## 9. Environment Assumptions

The Workstream B pack assumes the foundation substrate established by Workstream A is already in place.

### 9.1 Required assumptions

Expected baseline assumptions include:

- backend runtime dependencies installed,
- reachable PostgreSQL instance or controlled integration-test equivalent,
- migration and schema baseline already established,
- and a repeatable way to isolate or reset integration-test state.

### 9.2 No dependency on live connectors
n
This pack must not depend on live:

- Google connectivity,
- Microsoft Graph connectivity,
- Telegram bot connectivity,
- or voice infrastructure.

It tests the memory substrate those later layers will populate.

### 9.3 Foundation proof should already exist

This pack assumes the Workstream A substrate is sufficiently stable that domain-memory failures can be interpreted as actual memory/model issues rather than app-boot chaos.

**Stable verification anchor:** `TESTPACK:WorkstreamB.EnvironmentAssumptions`

---

## 10. Execution Guidance

### 10.1 When to run this pack

This pack should normally be run:

- after major domain-model or schema changes,
- after repository/query changes,
- after summary or audit behavior changes,
- before declaring Workstream B substantially complete,
- and before trusting later connector or assistant-core implementation built on the memory substrate.

### 10.2 Failure handling

If this pack fails:

- later connector, triage, planner, and UI confidence should be treated cautiously,
- the failure should usually be resolved before deep assistant-core work proceeds,
- and progress reporting should explicitly state whether the problem affects provenance, review safety, accepted state, summary lineage, or auditability.

### 10.3 Relationship to the data-integrity pack

This Workstream B pack proves the domain and memory substrate within the workstream context.

The later **data-integrity** pack should harden those protections into a broader cross-cutting regression surface for ongoing delivery and release confidence.

**Stable verification anchor:** `TESTPACK:WorkstreamB.ExecutionGuidance`

---

## 11. Evidence Expectations

When the Workstream B pack is executed, evidence reporting should capture at minimum:

- execution date/time,
- environment posture used,
- which included `TEST:` anchors were executed,
- pass/fail outcome,
- any explicitly `Deferred` entries and why,
- and a brief statement of whether the domain/memory spine is considered stable enough for connector and assistant-core extension.

This should be summarized in the relevant Workstream B progress file and referenced in broader phase-exit or regression summaries where appropriate.

**Stable verification anchor:** `TESTPACK:WorkstreamB.EvidenceExpectations`

---

## 12. Operational Ready Definition for This Pack

The Workstream B verification pack should be considered operationally established when:

1. all included `TEST:` anchors are defined and mapped,
2. core project/stakeholder/account/source entities are covered by executable integration proof,
3. interpreted-vs-accepted state separation is covered by executable proof,
4. summary refresh lineage is covered by executable proof,
5. audit-record behavior is covered by executable proof,
6. the pack can be run repeatably against a controlled persistence environment,
7. and evidence reporting makes the stability of the memory spine explicit.

At that point, Workstream B has a meaningful verification surface that later workstreams can trust.

**Stable verification anchor:** `TESTPACK:WorkstreamB.DefinitionOfOperationalReady`

---

## 13. Relationship to Later Packs

This pack establishes the proof surface for the domain/memory substrate only.

Later packs should build on it as follows:

- **Workstream C** should prove real connector normalization and provenance-preserving intake into the structures protected here,
- **Workstream D** should prove triage, extraction, planner, and review-interrupt behavior on top of this state model,
- **Workstream E** should prove browser-visible interaction with the artifacts stored here,
- **Workstream F** should prove voice and companion continuity using the session and summary structures established here,
- **Data Integrity** should convert the most important protections here into broader long-term regression proof,
- and **Release** should compose representative memory-spine proof into cross-workstream confidence.

This progression is consistent with the Glimmer build plan, workstream map, and Workstream G verification-estate design.

**Stable verification anchor:** `TESTPACK:WorkstreamB.RelationshipToLaterPacks`

---

## 14. Final Note

If Workstream B is implemented but not properly verified, Glimmer may still look intelligent while quietly depending on weak memory truth.

That is the danger this pack is meant to prevent.

Its job is to prove that Glimmer’s memory spine is:

- structured,
- provenance-preserving,
- review-safe,
- traceable,
- and durable enough for the rest of the product to build on.

**Stable verification anchor:** `TESTPACK:WorkstreamB.Conclusion`
