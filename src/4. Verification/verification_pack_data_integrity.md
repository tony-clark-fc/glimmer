# Glimmer — Verification Pack: Data Integrity

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Data Integrity
- **Document Type:** Canonical Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Test Catalog, Requirements, Architecture, Build Plan, Testing Strategy, Workstream B Verification Pack, Workstream G Testing and Regression

---

## 1. Purpose

This document defines the **data-integrity verification pack** for **Glimmer**.

Its purpose is to provide a cross-cutting regression surface that protects the truthfulness of Glimmer’s memory spine as the system evolves.

Where the workstream packs prove that specific slices were implemented correctly at the time they were built, this pack exists to answer a more durable question:

**Does the system still preserve the integrity of its structured memory, provenance, review boundaries, summaries, and traceability after ongoing change?**

**Stable verification anchor:** `TESTPACK:DataIntegrity.ControlSurface`

---

## 2. Role of the Data Integrity Pack

This pack exists to protect the most load-bearing invariants in Glimmer’s operational truth model, including:

- accepted-vs-interpreted separation,
- source provenance retention,
- connected-account and profile identity integrity,
- summary lineage and refresh discipline,
- auditability of meaningful state mutation,
- cross-channel origin traceability,
- and the prevention of silent flattening as connectors, graphs, UI, voice, and companion layers evolve.

This pack is intentionally cross-cutting. It is not owned by one feature surface alone.

**Stable verification anchor:** `TESTPACK:DataIntegrity.Role`

---

## 3. Relationship to the Control Surface

This verification pack is derived from and aligned to:

- the **Agentic Delivery Framework**, especially its authority model, verification model, evidence-of-completion posture, and traceability expectations,
- the **Testing Strategy Companion**, especially automation-first proof, integration/data testing, explicit `ManualOnly` / `Deferred` handling, and cross-cutting regression discipline,
- the **Glimmer Agentic Delivery Document Set**, which explicitly defines `verification-pack-data-integrity.md` as part of the canonical verification family,
- the **Glimmer Requirements**, especially project memory, stakeholder memory, message ingestion, multi-account profile support, explainability, traceability and auditability, human approval boundaries, and state continuity,
- the latest **Architecture** state, especially structured memory, account provenance, memory storage strategy, project-memory refresh, audit and trace, review-gate boundaries, and semantic-recall boundaries,
- the **Build Plan**, **Build Strategy and Scope**, and **Workstream G — Testing and Regression**, which explicitly define cross-cutting regression, verification packs, and data-integrity protection as first-class delivery concerns,
- the **Governance and Process** document, which requires evidence-backed completion and surfaced drift for meaningful work,
- and the current **Test Catalog**, which already defines many of the canonical domain, connector, security, and continuity scenarios this pack should compose into long-lived regression protection.

**Stable verification anchor:** `TESTPACK:DataIntegrity.ControlSurfaceAlignment`

---

## 4. Why This Pack Exists Separately

The workstream packs prove important behavior in context, but they are still organized by delivery sequence.

The data-integrity pack exists separately because some of Glimmer’s most dangerous failures are cross-cutting and may be introduced long after the original workstream appeared healthy.

Examples include:

- a connector change that quietly drops provenance fields,
- a planner change that accidentally promotes candidate state into accepted state,
- a summary change that rewrites memory without lineage,
- a UI/API change that blurs pending-vs-accepted distinctions,
- or a voice/Telegram change that creates channel artifacts with weak traceability.

This pack exists to catch that class of regression.

**Stable verification anchor:** `TESTPACK:DataIntegrity.Rationale`

---

## 5. Data Integrity Verification Scope

### 5.1 In scope

This pack covers proof for the following cross-cutting integrity concerns:

- explicit separation of source, interpreted, accepted, and synthesized layers,
- provenance retention across persistence and transformation,
- multi-account and profile identity durability,
- source-record explicitness across messages, threads, events, imported signals, and channel-session artifacts,
- summary refresh lineage and supersession behavior,
- audit-record creation for meaningful memory evolution,
- continuity artifacts with traceable origin,
- retrieval boundedness relative to structured truth,
- and integrity of review-state transitions as they affect durable memory.

### 5.2 Out of scope

This pack does **not** attempt to replace:

- smoke/startup proof,
- full connector-behavior proof,
- full assistant-core workflow proof,
- full browser-journey proof,
- or subjective UX/usability judgment.

Those remain in their respective packs.

**Stable verification anchor:** `TESTPACK:DataIntegrity.Scope`

---

## 6. Source `TEST:` Anchors Included in This Pack

This pack composes the most important integrity-oriented scenarios from across the canonical Test Catalog and adds a small number of dedicated integrity anchors where needed.

### 6.1 Canonical domain/memory anchors already defined in the Test Catalog

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
- **Role in this pack:** Proves summary artifacts remain explicit and traceable.

#### `TEST:Domain.Audit.MeaningfulStateMutation`
- **Scenario name:** Meaningful state mutations generate durable audit records
- **Layers:** `integration`
- **Role in this pack:** Proves memory evolution remains auditable.

### 6.2 Canonical connector/provenance anchors already defined in the Test Catalog

#### `TEST:Connector.Normalization.PersistBeforeInterpretation`
- **Scenario name:** Normalized source records persist before assistant-core interpretation begins
- **Layers:** `integration`, `graph`
- **Role in this pack:** Protects the source-truth layer from being skipped.

#### `TEST:Connector.IntakeHandoff.BoundedReferenceFlow`
- **Scenario name:** Connector-to-intake handoff uses bounded references instead of provider payload sprawl
- **Layers:** `integration`, `graph`
- **Role in this pack:** Protects bounded state transition into the core.

### 6.3 Canonical assistant-core anchors already defined in the Test Catalog

#### `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable`
- **Scenario name:** Project-memory refresh trigger is explicit and traceable
- **Layers:** `integration`, `graph`
- **Role in this pack:** Protects memory refresh from becoming invisible drift.

#### `TEST:Triage.ReviewInterrupt.ResumeContinuesSafely`
- **Scenario name:** Review interrupt and resume behavior continues the triage flow safely
- **Layers:** `graph`, `integration`, `api`
- **Role in this pack:** Protects review-state lifecycle as part of durable state evolution.

### 6.4 Canonical voice/companion anchors already defined in the Test Catalog

#### `TEST:ChannelSession.SummariesPersistWithTraceableOrigin`
- **Scenario name:** Voice and companion session summaries persist with traceable origin
- **Layers:** `integration`
- **Role in this pack:** Protects cross-channel continuity artifacts from becoming opaque.

### 6.5 Canonical security anchors already defined in the Test Catalog

#### `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`
- **Scenario name:** Externally meaningful actions require structured approval
- **Layers:** `graph`, `api`, `browser`
- **Role in this pack:** Protects the integrity of approval-state semantics as they intersect with memory and review records.

### 6.6 Additional data-integrity-specific anchors introduced by this pack

#### `TEST:Integrity.SourceLayer.MessagesThreadsEventsSignalsRemainDistinct`
- **Scenario name:** Source-layer messages, threads, events, and imported signals remain explicitly distinct across the model
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:MessageIngestion`, `ARCH:StructuredMemoryModel`, `ARCH:MemoryStorageStrategy`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove source-bearing records do not collapse into one generic content bucket.

#### `TEST:Integrity.AcceptedState.PromotionRetainsOriginTrace`
- **Scenario name:** Promotion from interpreted state to accepted state retains traceable origin linkage
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:Explainability`, `REQ:TraceabilityAndAuditability`, `ARCH:AuditAndTraceLayer`, `ARCH:StructuredMemoryModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove accepted state can still be traced back to its source and candidate history.

#### `TEST:Integrity.Summaries.SupersessionDoesNotEraseHistory`
- **Scenario name:** Summary supersession does not erase prior lineage or hide refresh history
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:ProjectMemory`, `ARCH:ProjectMemoryRefresh`, `ARCH:AuditAndTraceLayer`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove summary replacement remains historically traceable.

#### `TEST:Integrity.Retrieval.StructuredTruthOutranksSemanticRecall`
- **Scenario name:** Retrieval behavior does not silently replace structured truth with semantic recall output
- **Primary layers:** `integration`, `manual_only`
- **Primary drivers:** `REQ:Explainability`, `ARCH:SemanticRecallBoundary`, `ARCH:StructuredMemoryModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamG.TestingAndRegression`
- **Intent:** Prove retrieval remains bounded support rather than an ungoverned memory replacement.

#### `TEST:Integrity.ChannelArtifacts.OriginAndSessionLinkageRemainDurable`
- **Scenario name:** Channel-origin artifacts retain durable origin and session linkage across persistence and summary creation
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:StateContinuity`, `REQ:ProjectMemory`, `ARCH:ChannelSessionModel`, `ARCH:AuditAndTraceLayer`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamF.Voice`
- **Intent:** Prove channel continuity does not create untraceable side-memory.

#### `TEST:Integrity.ReviewStates.PendingAcceptedRejectedDeferredRemainDistinct`
- **Scenario name:** Pending, accepted, rejected, and deferred review outcomes remain explicitly distinct in durable state
- **Primary layers:** `integration`, `api`
- **Primary drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:ReviewGateArchitecture`, `ARCH:StructuredMemoryModel`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`, `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove review-state semantics remain durable and queryable instead of collapsing after UI interaction.

**Stable verification anchor:** `TESTPACK:DataIntegrity.IncludedTests`

---

## 7. Data Integrity Pack Entry Table

| TEST Anchor | Scenario | Layer | Automation Status | Pack Priority | Notes |
|---|---|---|---|---|---|
| `TEST:Domain.MultiAccount.ProvenancePersistence` | Source provenance survives persistence round trips | `integration` | Planned | Critical | Provenance baseline |
| `TEST:Domain.InterpretedVsAccepted.Separation` | Interpreted artifacts remain distinct from accepted operational state | `integration` | Planned | Critical | Core memory-boundary protection |
| `TEST:Domain.SummaryRefresh.Lineage` | Summary refresh preserves lineage and metadata | `integration` | Planned | Critical | Summary integrity baseline |
| `TEST:Domain.Audit.MeaningfulStateMutation` | Meaningful state mutations generate durable audit records | `integration` | Planned | Critical | Audit baseline |
| `TEST:Connector.Normalization.PersistBeforeInterpretation` | Normalized source records persist before assistant-core interpretation begins | `integration`, `graph` | Planned | Critical | Source-before-interpretation guardrail |
| `TEST:Connector.IntakeHandoff.BoundedReferenceFlow` | Connector-to-intake handoff uses bounded references instead of provider payload sprawl | `integration`, `graph` | Planned | High | Prevents hidden state sprawl |
| `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable` | Project-memory refresh trigger is explicit and traceable | `integration`, `graph` | Planned | Critical | Refresh traceability |
| `TEST:Triage.ReviewInterrupt.ResumeContinuesSafely` | Review interrupt and resume behavior continues the triage flow safely | `graph`, `integration`, `api` | Planned | High | Review-state lifecycle integrity |
| `TEST:ChannelSession.SummariesPersistWithTraceableOrigin` | Voice and companion session summaries persist with traceable origin | `integration` | Planned | High | Cross-channel traceability |
| `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` | Externally meaningful actions require structured approval | `graph`, `api`, `browser` | Planned | High | Approval integrity |
| `TEST:Integrity.SourceLayer.MessagesThreadsEventsSignalsRemainDistinct` | Source-layer messages, threads, events, and imported signals remain explicitly distinct across the model | `integration` | Planned | High | Source-layer explicitness |
| `TEST:Integrity.AcceptedState.PromotionRetainsOriginTrace` | Promotion from interpreted state to accepted state retains traceable origin linkage | `integration` | Planned | Critical | Candidate-to-accepted traceability |
| `TEST:Integrity.Summaries.SupersessionDoesNotEraseHistory` | Summary supersession does not erase prior lineage or hide refresh history | `integration` | Planned | High | Historical integrity |
| `TEST:Integrity.Retrieval.StructuredTruthOutranksSemanticRecall` | Retrieval behavior does not silently replace structured truth with semantic recall output | `integration`, `manual_only` | Planned | Medium | Retrieval-boundary guardrail |
| `TEST:Integrity.ChannelArtifacts.OriginAndSessionLinkageRemainDurable` | Channel-origin artifacts retain durable origin and session linkage across persistence and summary creation | `integration` | Planned | High | Companion/voice memory integrity |
| `TEST:Integrity.ReviewStates.PendingAcceptedRejectedDeferredRemainDistinct` | Pending, accepted, rejected, and deferred review outcomes remain explicitly distinct in durable state | `integration`, `api` | Planned | High | Review-state durability |

**Stable verification anchor:** `TESTPACK:DataIntegrity.EntryTable`

---

## 8. Expected Automation Shape

### 8.1 Integration proof by default

Most of this pack should be implemented through integration testing because the pack is fundamentally about:

- persistence boundaries,
- relationship integrity,
- state separation,
- lineage,
- and auditability.

### 8.2 Graph/API proof where integrity depends on workflow transition

Where durable integrity depends on transition behavior rather than static schema alone, graph and API tests should verify:

- review interrupt/resume semantics,
- accepted-state promotion semantics,
- refresh trigger visibility,
- and durable review-state distinctions.

### 8.3 Minimal `manual_only` use

This pack should be overwhelmingly automated.

A small `ManualOnly` slice may still be appropriate for bounded review of retrieval-boundary behavior where human inspection adds value, but the primary integrity guarantees should not depend on informal review.

### 8.4 No shallow coverage theater

This pack should favor a smaller number of strong invariant tests over a large number of weak superficial checks.

**Stable verification anchor:** `TESTPACK:DataIntegrity.AutomationShape`

---

## 9. Environment Assumptions

The data-integrity pack assumes the foundation, memory, connector, assistant-core, and companion/session substrate are already in place.

### 9.1 Required assumptions

Expected baseline assumptions include:

- backend runtime and persistence substrate already working,
- controlled database/integration-test environment,
- repeatable fixture or seeded-state setup that exercises candidate, accepted, summary, connector-origin, and channel-origin artifacts,
- and executable graph/API harnesses for transition-sensitive integrity checks.

### 9.2 No live production dependency for core integrity proof

This pack should not require live Google, Microsoft, Telegram, or production voice environments for its core proof.

Integrity should be provable against controlled persisted state and deterministic workflow/test harnesses.

### 9.3 Earlier workstream proof should already exist

This pack assumes the workstream packs have already established basic correctness within their slices, so this cross-cutting pack can focus on long-lived integrity rather than basic feature bring-up.

**Stable verification anchor:** `TESTPACK:DataIntegrity.EnvironmentAssumptions`

---

## 10. Execution Guidance

### 10.1 When to run this pack

This pack should normally be run:

- after schema or repository changes,
- after connector normalization or provenance changes,
- after changes to candidate/accepted promotion logic,
- after summary refresh or audit logic changes,
- after review-state lifecycle changes,
- before release-confidence is claimed for serious system changes,
- and at recurring regression checkpoints once Glimmer is under active development.

### 10.2 Failure handling

If this pack fails:

- confidence in multiple workstreams should be treated cautiously,
- the failure should usually be resolved before release or phase-exit confidence is claimed,
- and progress reporting should explicitly state whether the problem affects provenance, state separation, lineage, auditability, review-state durability, or retrieval boundedness.

### 10.3 Relationship to other packs

This pack does not replace the workstream packs.

Instead, it hardens the most important integrity rules from across them into a longer-lived regression surface.

**Stable verification anchor:** `TESTPACK:DataIntegrity.ExecutionGuidance`

---

## 11. Evidence Expectations

When the data-integrity pack is executed, evidence reporting should capture at minimum:

- execution date/time,
- environment posture used,
- which included `TEST:` anchors were executed,
- pass/fail outcome,
- any `ManualOnly` checks performed,
- any `Deferred` entries and why,
- and a brief statement of whether Glimmer’s memory spine is still considered trustworthy across ongoing system change.

This should be summarized in the relevant verification/progress surfaces and referenced in broader regression and release-confidence reporting where appropriate.

**Stable verification anchor:** `TESTPACK:DataIntegrity.EvidenceExpectations`

---

## 12. Operational Ready Definition for This Pack

The data-integrity verification pack should be considered operationally established when:

1. all included `TEST:` anchors are defined and mapped,
2. provenance-retention proof exists,
3. candidate-vs-accepted separation proof exists,
4. summary lineage and supersession proof exists,
5. auditability proof exists,
6. cross-channel origin/session linkage proof exists,
7. review-state durability proof exists,
8. retrieval-boundedness proof exists,
9. and the pack can be run repeatably against controlled persisted state and workflow harnesses.

At that point, Glimmer has a meaningful long-lived integrity regression surface rather than only one-time workstream confidence.

**Stable verification anchor:** `TESTPACK:DataIntegrity.DefinitionOfOperationalReady`

---

## 13. Relationship to Later Packs

This pack is one of the major cross-cutting verification surfaces that should remain important over the life of the project.

From here:

- the **release** pack should compose representative integrity scenarios from this pack together with smoke, assistant-core, workspace, connector, and companion proof,
- and ongoing regression should treat the highest-priority integrity scenarios here as non-negotiable confidence checks.

This progression is consistent with the Glimmer build plan, workstream map, and Workstream G verification-estate design.

**Stable verification anchor:** `TESTPACK:DataIntegrity.RelationshipToLaterPacks`

---

## 14. Final Note

If this pack is weak, Glimmer may still appear functional while quietly rotting underneath.

That is the danger it exists to catch.

Its job is to prove that Glimmer’s memory and provenance model remains:

- explicit,
- traceable,
- review-safe,
- historically coherent,
- and strong enough to keep supporting the rest of the system as change accumulates.

**Stable verification anchor:** `TESTPACK:DataIntegrity.Conclusion`
