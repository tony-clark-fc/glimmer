# Glimmer — Workstream B: Domain and Memory

## Document Metadata

- **Document Title:** Glimmer — Workstream B: Domain and Memory
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Build Strategy and Scope, Testing Strategy, Workstream A Foundation

---

## 1. Purpose

This document defines the implementation strategy for **Workstream B — Domain and Memory**.

Its purpose is to establish Glimmer’s structured operational state model, reviewable interpretation model, and synthesized memory model so that later connectors, orchestration flows, UI surfaces, and companion channels all work against a durable and explainable system of record.

This workstream is where Glimmer stops being just an implementation skeleton and starts becoming a real project chief-of-staff system.

**Stable plan anchor:** `PLAN:WorkstreamB.DomainAndMemory`

---

## 2. Workstream Objective

Workstream B exists to implement the structured domain and memory substrate for Glimmer, including:

- operator context,
- projects and workstreams,
- stakeholders and stakeholder identities,
- connected accounts and provenance-bearing source records,
- reviewable interpretation artifacts,
- accepted execution artifacts,
- drafts and briefing artifacts,
- persona asset records,
- channel session state,
- and summary/memory refresh structures.

At the end of this workstream, Glimmer should have a durable core state model that later workstreams can populate, query, refresh, review, and present safely.

**Stable plan anchor:** `PLAN:WorkstreamB.Objective`

---

## 3. Why This Workstream Comes Early

The build plan explicitly places **Domain and Memory** immediately after Foundation in the maturity order and phase model. The project is meant to mature from runtime skeleton to structured domain truth before deep connector and workflow sophistication.

That sequencing matters because Glimmer’s value depends on:

- structured project memory,
- reviewable interpretation,
- provenance-preserving source linkage,
- accepted operational state,
- and persisted summaries.

If connectors or orchestration are built before this substrate is real, the implementation will drift toward loose message handling, implicit memory, and hidden state mutation.

**Stable plan anchor:** `PLAN:WorkstreamB.Rationale`

---

## 4. Related Requirements Anchors

This workstream directly supports the following requirements:

- `REQ:ProjectMemory`
- `REQ:StakeholderMemory`
- `REQ:MessageIngestion`
- `REQ:MultiAccountProfileSupport`
- `REQ:ActionDeadlineDecisionExtraction`
- `REQ:DraftResponseWorkspace`
- `REQ:TraceabilityAndAuditability`
- `REQ:Explainability`
- `REQ:StateContinuity`

These requirements make it clear that Glimmer cannot rely on ephemeral conversational context. It needs structured, queryable, reviewable memory and accepted operational state.

**Stable plan anchor:** `PLAN:WorkstreamB.RequirementsAlignment`

---

## 5. Related Architecture Anchors

This workstream is primarily implementing the substrate described by:

- `ARCH:PortfolioDomainModel`
- `ARCH:ProjectStateModel`
- `ARCH:StakeholderModel`
- `ARCH:MessageModel`
- `ARCH:DraftModel`
- `ARCH:ConnectedAccountModel`
- `ARCH:ChannelSessionModel`
- `ARCH:MemoryStorageStrategy`
- `ARCH:ProjectMemoryRefresh`
- `ARCH:AuditAndTraceLayer`

These anchors define the conceptual model, memory layers, reviewable interpretation posture, and relational-first storage strategy that the implementation must follow.

**Stable plan anchor:** `PLAN:WorkstreamB.ArchitectureAlignment`

---

## 6. Workstream Scope

### 6.1 In scope

This workstream includes:

- core entity implementation for operator, project, stakeholder, account, source, execution, draft, persona, and channel state,
- relational schema and migrations for those entities,
- repository/data-access behavior for the domain,
- separation between source records, interpreted artifacts, accepted operational state, and synthesized artifacts,
- summary artifact persistence,
- memory refresh scaffolding,
- audit/trace linkage needed by core state mutation,
- and domain-level service abstractions needed by later orchestration work.

**Stable plan anchor:** `PLAN:WorkstreamB.InScope`

### 6.2 Out of scope

This workstream does **not** include:

- full Google/Microsoft connector implementation,
- full LangGraph business workflow implementation,
- polished UI behavior,
- rich Telegram message handling,
- or production voice interaction logic.

This workstream establishes the state model those later behaviors will depend on.

**Stable plan anchor:** `PLAN:WorkstreamB.OutOfScope`

---

## 7. Implementation Outcome Expected from This Workstream

By the end of Workstream B, Glimmer should be able to do the following in a structurally real way, even if later workstreams improve the surrounding experience:

- store multiple projects and linked workstreams,
- store stakeholders and their identities across channels/accounts,
- store connected accounts and account profiles,
- persist normalized source artifacts with provenance,
- persist interpreted candidate artifacts without forcing them into accepted truth,
- persist accepted work items, decisions, risks, blockers, and waiting-on items,
- persist drafts and draft variants,
- persist summaries and briefing artifacts,
- and support later orchestration/state refresh through explicit repositories and services.

This is the threshold where Glimmer starts to have a durable memory spine rather than just a framework shell.

**Stable plan anchor:** `PLAN:WorkstreamB.ExpectedOutcome`

---

## 8. Domain Implementation Packages

## 8.1 Work Package B1 — Operator, project, and workstream core

**Objective:** Implement the foundational project portfolio entities.

### In scope
- `PrimaryOperator`
- `Project`
- `ProjectWorkstream`
- `Milestone`
- core relationships and persistence mappings
- base repository or service access patterns for these entities

### Expected outputs
- entity models
- migrations/schema updates
- repository/data-access layer for core portfolio records
- initial domain tests for lifecycle and relationship behavior

### Related anchors
- `ARCH:PrimaryOperatorModel`
- `ARCH:ProjectStateModel`
- `ARCH:ProjectWorkstreamModel`
- `ARCH:MilestoneModel`

### Definition of done
- the system can persist and retrieve operators, projects, workstreams, and milestones reliably
- relationships are explicit and test-proven

**Stable plan anchor:** `PLAN:WorkstreamB.PackageB1.ProjectPortfolioCore`

---

## 8.2 Work Package B2 — Stakeholder and relationship memory core

**Objective:** Implement stakeholder memory and project-specific stakeholder relationships.

### In scope
- `Stakeholder`
- `StakeholderIdentity`
- `StakeholderProjectLink`
- relationship importance and identity/channel distinctions
- review-safe identity linking patterns where confidence may later matter

### Expected outputs
- stakeholder entity set
- identity and relationship mappings
- queries/repositories for stakeholder resolution and project linkage
- tests for relationship behavior and identity separation

### Related anchors
- `ARCH:StakeholderModel`
- `ARCH:StakeholderIdentityModel`
- `ARCH:StakeholderProjectLinkModel`
- `ARCH:StakeholderIdentityMergeBoundary`

### Definition of done
- the system can represent one stakeholder across multiple identities/channels
- project-specific stakeholder relationships are stored explicitly

**Stable plan anchor:** `PLAN:WorkstreamB.PackageB2.StakeholderMemoryCore`

---

## 8.3 Work Package B3 — Connected accounts and provenance-bearing source core

**Objective:** Implement the multi-account source foundation that later connectors will populate.

### In scope
- `ConnectedAccount`
- `AccountProfile`
- provenance-bearing source link structures
- `Message`
- `MessageThread`
- `CalendarEvent`
- `ImportedSignal`
- source/account/profile linkage

### Expected outputs
- source-bearing entity model
- persistence mappings for source records and provenance fields
- basic repository/query support for source retrieval
- tests proving provenance preservation in persistence

### Related anchors
- `ARCH:ConnectedAccountModel`
- `ARCH:AccountProfileModel`
- `ARCH:AccountProvenanceConcept`
- `ARCH:MessageModel`
- `ARCH:MessageThreadModel`
- `ARCH:CalendarEventModel`
- `ARCH:ImportedSignalModel`

### Definition of done
- source records can be stored with explicit account/profile/provider provenance
- later connector work can write into these structures without redesigning them

**Stable plan anchor:** `PLAN:WorkstreamB.PackageB3.SourceAndProvenanceCore`

---

## 8.4 Work Package B4 — Reviewable interpretation artifacts

**Objective:** Implement the state layer for candidate understanding rather than accepted truth.

### In scope
- `MessageClassification`
- `ExtractedAction`
- `ExtractedDecision`
- `ExtractedDeadlineSignal`
- `ReviewState` handling model
- linkage back to source records and candidate project references

### Expected outputs
- interpretation entity set
- persistence and query support
- explicit review-state model
- tests proving separation from accepted operational state

### Related anchors
- `ARCH:MessageClassificationModel`
- `ARCH:ExtractedActionModel`
- `ARCH:ExtractedDecisionModel`
- `ARCH:ExtractedDeadlineSignalModel`
- `ARCH:InterpretationReviewState`

### Definition of done
- interpreted artifacts can be stored, retrieved, and reviewed without being mistaken for accepted truth

**Stable plan anchor:** `PLAN:WorkstreamB.PackageB4.InterpretationLayer`

---

## 8.5 Work Package B5 — Accepted execution artifact layer

**Objective:** Implement Glimmer’s accepted operational work state.

### In scope
- `WorkItem`
- `DecisionRecord`
- `RiskRecord`
- `BlockerRecord`
- `WaitingOnRecord`
- project linkage and provenance-aware origin metadata

### Expected outputs
- accepted execution entity set
- repository/query support
- tests for state, linkage, and accepted-vs-candidate separation

### Related anchors
- `ARCH:WorkItemModel`
- `ARCH:DecisionRecordModel`
- `ARCH:RiskRecordModel`
- `ARCH:BlockerRecordModel`
- `ARCH:WaitingOnRecordModel`

### Definition of done
- accepted operational state exists as a durable layer separate from interpretation artifacts

**Stable plan anchor:** `PLAN:WorkstreamB.PackageB5.AcceptedExecutionState`

---

## 8.6 Work Package B6 — Drafting, briefing, and focus artifacts

**Objective:** Implement the persisted user-facing output artifacts Glimmer will generate.

### In scope
- `Draft`
- `DraftVariant`
- `BriefingArtifact`
- `FocusPack`
- project/source/stakeholder linkage
- initial versioning/status support for drafts

### Expected outputs
- drafting and briefing entity set
- persistence mappings and repositories
- tests for artifact creation and relationship integrity

### Related anchors
- `ARCH:DraftModel`
- `ARCH:DraftVariantModel`
- `ARCH:BriefingArtifactModel`
- `ARCH:FocusPackModel`

### Definition of done
- user-facing generated artifacts can be persisted and linked cleanly to their source/project context

**Stable plan anchor:** `PLAN:WorkstreamB.PackageB6.DraftingAndBriefingArtifacts`

---

## 8.7 Work Package B7 — Persona and channel session state

**Objective:** Implement the asset/state model for persona rendering and companion/voice continuity.

### In scope
- `PersonaAsset`
- `PersonaClassification`
- `PersonaSelectionEvent`
- `ChannelSession`
- `TelegramConversationState`
- `VoiceSessionState`

### Expected outputs
- persona asset metadata model
- channel/session entity set
- persistence support for session continuity and persona selection traceability
- tests for core session linkage and state persistence

### Related anchors
- `ARCH:PersonaAssetModel`
- `ARCH:PersonaClassificationModel`
- `ARCH:PersonaSelectionEventModel`
- `ARCH:ChannelSessionModel`
- `ARCH:TelegramConversationStateModel`
- `ARCH:VoiceSessionStateModel`

### Definition of done
- persona assets and channel sessions can be persisted and recovered as domain-linked state

**Stable plan anchor:** `PLAN:WorkstreamB.PackageB7.PersonaAndChannelState`

---

## 8.8 Work Package B8 — Summary and memory refresh scaffolding

**Objective:** Implement the first durable summary and refresh substrate.

### In scope
- `ProjectSummary`
- summary metadata model
- refresh metadata fields
- summary persistence behavior
- initial refresh service abstractions or domain services
- summary-scope linkage to source and accepted state

### Expected outputs
- summary persistence model
- refresh/service scaffolding
- initial refresh-trigger rules as code-safe infrastructure
- tests for summary persistence and refresh traceability

### Related anchors
- `ARCH:ProjectSummaryModel`
- `ARCH:SummaryArtifactTypes`
- `ARCH:SummaryMetadataModel`
- `ARCH:SummaryRefreshTriggers`
- `ARCH:ProjectMemoryRefreshPipeline`

### Definition of done
- summaries are first-class persisted artifacts and the codebase has a real place for refresh logic to live

**Stable plan anchor:** `PLAN:WorkstreamB.PackageB8.SummaryAndRefreshScaffolding`

---

## 8.9 Work Package B9 — Audit and trace substrate for memory evolution

**Objective:** Implement the domain-linked audit/trace substrate required by memory-heavy behavior.

### In scope
- audit records for meaningful state mutations
- provenance-aware trace linkage for interpreted and accepted artifacts
- operator override attribution hooks where applicable
- minimal query/reporting support for audit inspection

### Expected outputs
- audit entity/model set or equivalent persistence design
- persistence mappings
- tests for audit creation on key state transitions

### Related anchors
- `ARCH:AuditAndTraceLayer`
- `ARCH:AuditTraceCoverage`
- `ARCH:OperatorOverrideAttribution`

### Definition of done
- meaningful state changes can be traced back through persisted evidence rather than only through logs

**Stable plan anchor:** `PLAN:WorkstreamB.PackageB9.AuditAndTraceSubstrate`

---

## 9. Sequencing Inside the Workstream

The recommended internal order for Workstream B is:

1. B1 — Operator, project, and workstream core
2. B2 — Stakeholder and relationship memory core
3. B3 — Connected accounts and provenance-bearing source core
4. B4 — Reviewable interpretation artifacts
5. B5 — Accepted execution artifact layer
6. B6 — Drafting, briefing, and focus artifacts
7. B7 — Persona and channel session state
8. B8 — Summary and memory refresh scaffolding
9. B9 — Audit and trace substrate

This order follows the architecture’s memory layering logic: source and accepted-state foundations first, then derived/user-facing artifacts, then refresh and traceability.

**Stable plan anchor:** `PLAN:WorkstreamB.InternalSequence`

---

## 10. Human Dependencies

This workstream should be largely agent-executable once Workstream A is in place.

Expected human involvement is mostly around:

- confirming any unresolved naming or schema semantics,
- approving meaningful deviations from the conceptual domain model,
- and reviewing any proposed simplifications where implementation convenience conflicts with the architecture.

This is consistent with the framework’s human–agent responsibility model: the agent can implement, but the human remains accountable for design truth.

**Stable plan anchor:** `PLAN:WorkstreamB.HumanDependencies`

---

## 11. Verification Expectations

Workstream B is complete only when the structured memory spine is not just modeled, but proven.

### Verification layers expected
- unit verification for domain rules and state handling
- integration verification for persistence and relationship behavior
- data-integrity verification for provenance and separation of state layers
- API-level proof where repository/service behavior is surfaced

### Minimum proof expectations
- projects, stakeholders, connected accounts, source records, and accepted artifacts persist correctly
- interpreted artifacts remain distinct from accepted operational memory
- summary artifacts persist with metadata and refresh lineage
- audit records are created for meaningful state evolution
- multi-account provenance fields survive persistence round-trips

This aligns directly to the Glimmer testing strategy’s domain/memory, connector/provenance, and data integrity proof expectations.

**Stable plan anchor:** `PLAN:WorkstreamB.VerificationExpectations`

---

## 12. Suggested Future Working Documents for This Workstream

This workstream should eventually be paired with:

- `WorkstreamB_DomainAndMemory_DESIGN_AND_IMPLEMENTATION_PLAN.md`
- `WorkstreamB_DomainAndMemory_DESIGN_AND_IMPLEMENTATION_PROGRESS.md`

Those files will become the active implementation memory for the workstream once coding starts, following the framework’s working-document convention.

**Stable plan anchor:** `PLAN:WorkstreamB.WorkingDocumentPair`

---

## 13. Definition of Done

Workstream B should be considered complete when all of the following are true:

1. the core Glimmer domain entities are implemented and persisted,
2. multi-account and provenance-bearing source structures are real,
3. interpreted artifacts and accepted operational state are explicitly separated,
4. drafts, briefings, focus packs, persona assets, and channel sessions are modeled and persisted,
5. summary artifacts and refresh scaffolding exist,
6. audit/trace substrate exists for meaningful state evolution,
7. the relevant migrations and repositories are in place,
8. and the required automated verification evidence has been executed and recorded.

If these are not true, Glimmer still lacks the durable memory spine required for real assistant behavior.

**Stable plan anchor:** `PLAN:WorkstreamB.DefinitionOfDone`

---

## 14. Final Note

Workstream B is the point where Glimmer earns the right to claim that it has memory rather than just context.

If this workstream is done well, later connectors, graphs, and UI layers can remain bounded, explainable, and reviewable.
If it is done badly, everything later will drift toward implicit state, prompt-only memory, and brittle behavior.

This workstream should therefore be treated as one of the most structurally important in the whole delivery plan.

**Stable plan anchor:** `PLAN:WorkstreamB.Conclusion`

