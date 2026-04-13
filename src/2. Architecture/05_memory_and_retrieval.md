# Glimmer — Memory and Retrieval

## Document Metadata

- **Document Title:** Glimmer — Memory and Retrieval
- **Document Type:** Split Architecture Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `ARCHITECTURE.md`
- **Primary Companion Documents:** Requirements, Domain Model, LangGraph Orchestration, Connectors and Ingestion, UI and Voice

---

## 1. Purpose

This document defines the memory, summary, and retrieval architecture for **Glimmer**.

It explains how Glimmer stores structured operational memory, how synthesized summaries are created and refreshed, how semantic retrieval is used without becoming the system of record, and how traceability is preserved across raw signals, interpreted artifacts, accepted memory state, and user-facing outputs.

This document also defines the relationship between Glimmer’s product-memory layer and the repository-local documentation retrieval layer described by the Agentic Delivery Framework.

**Stable architecture anchor:** `ARCH:MemoryStorageStrategy`

---

## 2. Memory Architecture Intent

Glimmer must remember enough to act like a durable chief-of-staff, but it must not become an opaque memory bucket that silently mutates its own truth.

The memory architecture therefore has five core jobs:

1. store structured operational truth,
2. preserve source-linked evidence and provenance,
3. maintain synthesized summaries that speed understanding,
4. support bounded semantic retrieval where it adds value,
5. and keep memory refresh visible, reviewable, and auditable.

The architecture must make it possible to answer questions such as:

- what does Glimmer know about this project,
- where did that knowledge come from,
- what is accepted memory versus inferred interpretation,
- when was this summary last refreshed,
- and what evidence supports this recommendation.

**Stable architecture anchor:** `ARCH:MemoryArchitectureIntent`

---

## 3. Memory Principles

### 3.1 Structured records are primary

Structured relational records are the primary source of operational truth for Glimmer.

**Stable architecture anchor:** `ARCH:MemoryPrinciple.StructuredPrimary`
**Stable architecture anchor:** `ARCH:StructuredMemoryModel`

### 3.2 Summaries are first-class but derived

Project summaries, stakeholder summaries, and briefings are important domain artifacts, but they are derived from underlying state rather than replacing it.

**Stable architecture anchor:** `ARCH:MemoryPrinciple.DerivedSummaries`

### 3.3 Retrieval supports memory, it does not define truth

Semantic retrieval may help Glimmer find relevant context quickly, but retrieved text is not automatically accepted memory.

**Stable architecture anchor:** `ARCH:SemanticRecallBoundary`

### 3.4 Provenance must survive synthesis

Summaries and retrieval outputs must remain traceable back to their source records and source accounts/channels where relevant.

**Stable architecture anchor:** `ARCH:MemoryPrinciple.ProvenanceThroughSynthesis`

### 3.5 Refresh must be controlled

Memory refresh should happen through explicit triggers, thresholds, or workflow steps rather than through invisible uncontrolled rewriting.

**Stable architecture anchor:** `ARCH:ProjectMemoryRefresh`

### 3.6 Auditability is part of usefulness

A memory system that cannot explain when and why it changed is not trustworthy enough for Glimmer’s use case.

**Stable architecture anchor:** `ARCH:AuditAndTraceLayer`

---

## 4. Memory Layers

Glimmer’s memory architecture should be understood as four layered memory surfaces.

### 4.1 Source memory layer

This layer contains normalized source records such as:

- `Message`
- `MessageThread`
- `CalendarEvent`
- `ImportedSignal`

This is the persistent substrate from which higher-order understanding is built.

**Stable architecture anchor:** `ARCH:MemoryLayer.SourceRecords`

### 4.2 Interpretation layer

This layer contains reviewable interpreted artifacts such as:

- `MessageClassification`
- `ExtractedAction`
- `ExtractedDecision`
- `ExtractedDeadlineSignal`

This layer represents candidate understanding rather than accepted truth.

**Stable architecture anchor:** `ARCH:MemoryLayer.Interpretation`

### 4.3 Accepted operational memory layer

This layer contains accepted working truth such as:

- `Project`
- `ProjectWorkstream`
- `Milestone`
- `WorkItem`
- `DecisionRecord`
- `RiskRecord`
- `BlockerRecord`
- `WaitingOnRecord`
- `StakeholderProjectLink`

This is the layer that drives planning and portfolio coordination.

**Stable architecture anchor:** `ARCH:MemoryLayer.AcceptedOperationalState`

### 4.4 Synthesized memory layer

This layer contains derived but persisted synthesis artifacts such as:

- `ProjectSummary`
- stakeholder summaries
- `FocusPack`
- `BriefingArtifact`
- `ResearchSummaryArtifact` (from deep-research runs)
- channel-specific concise summaries

These artifacts speed decision-making and interaction but must remain linked to their underlying evidence.

**Stable architecture anchor:** `ARCH:MemoryLayer.SynthesizedArtifacts`

---

## 5. Primary Storage Strategy

### 5.1 Relational primary store

The primary persistence strategy for Glimmer should be a relational database that stores the authoritative structured domain state.

The current baseline is PostgreSQL.

This relational store should hold:

- operator records,
- projects,
- stakeholders,
- connected accounts,
- messages and events,
- interpreted artifacts,
- work items and decisions,
- drafts,
- summaries,
- research runs and findings,
- persona assets metadata,
- and audit/tracing records.

**Stable architecture anchor:** `ARCH:PrimaryRelationalMemoryStore`

### 5.2 Why relational first

A relational core is preferred because Glimmer’s workload depends heavily on:

- explicit relationships,
- state transitions,
- provenance joins,
- review states,
- and operator-visible reporting.

These concerns are poorly served if the product memory is treated primarily as loose vectorized text.

**Stable architecture anchor:** `ARCH:RelationalFirstRationale`

### 5.3 Artifact storage

Where large text blobs, transcripts, or richer serialized artifacts are needed, they may be stored in an associated artifact layer while remaining linked to the relational model.

Examples include:

- voice transcript segments,
- imported conversation payloads,
- large briefing exports,
- and generated evidence bundles.

**Stable architecture anchor:** `ARCH:ArtifactStorageBoundary`

---

## 6. Summary Strategy

### 6.1 Summary types

Glimmer should maintain several classes of persisted summary artifacts.

These include:

- project summary,
- stakeholder summary,
- thread summary,
- daily focus summary,
- weekly review summary,
- Telegram concise summary,
- and voice-session summary where relevant.

**Stable architecture anchor:** `ARCH:SummaryArtifactTypes`

### 6.2 Summary purpose

Summaries exist to reduce operator cognitive load and reduce repeated full-context reconstruction during orchestration.

They should help Glimmer:

- answer quickly,
- brief effectively,
- maintain continuity,
- and classify new inputs with awareness of recent state.

**Stable architecture anchor:** `ARCH:SummaryPurpose`

### 6.3 Summary persistence

Summaries should be stored as explicit records rather than regenerated invisibly on every use.

This supports:

- traceability,
- recency checking,
- refresh decisions,
- and better debugging of assistant behavior.

**Stable architecture anchor:** `ARCH:SummaryPersistence`

### 6.4 Summary scope metadata

Each summary record should retain metadata such as:

- summary type,
- generation timestamp,
- linked entity identifier,
- source record scope,
- refresh reason,
- and confidence or freshness indicator where relevant.

**Stable architecture anchor:** `ARCH:SummaryMetadataModel`

---

## 7. Summary Refresh Model

### 7.1 Refresh triggers

A summary refresh may be triggered by:

- significant new message or event intake,
- accepted action/decision changes,
- project-state mutation,
- explicit operator request,
- scheduled daily/weekly briefing generation,
- or channel-session context needing concise restatement.

**Stable architecture anchor:** `ARCH:SummaryRefreshTriggers`

### 7.2 Refresh threshold logic

Not every small change should trigger expensive full-summary regeneration.

The architecture should support a bounded refresh model that uses factors such as:

- amount of new source material,
- materiality of newly accepted state,
- age of the current summary,
- and interaction mode requirements.

**Stable architecture anchor:** `ARCH:SummaryRefreshThresholds`

### 7.3 Review posture for summary refresh

Summary refresh itself does not always require operator approval, but it must remain traceable and reversible enough that incorrect synthesis can be diagnosed and corrected.

**Stable architecture anchor:** `ARCH:SummaryRefreshGovernance`

---

## 8. Semantic Retrieval Strategy

### 8.1 Role of semantic retrieval

Semantic retrieval is used to help Glimmer locate relevant existing context quickly across projects, stakeholders, messages, and summaries.

It is a support capability, not the primary memory contract.

**Stable architecture anchor:** `ARCH:SummaryAndRetrievalStrategy`

### 8.2 Retrieval targets

Retrieval may operate over selected corpora such as:

- project summaries,
- stakeholder summaries,
- recent message summaries,
- briefing artifacts,
- accepted decision records,
- and other bounded synthesized artifacts.

It may also be used against selected raw or normalized text stores where that adds real value.

**Stable architecture anchor:** `ARCH:RetrievalTargetCorpora`

### 8.3 Retrieval boundaries

Retrieval should not be used as a shortcut to bypass structured joins or clear domain queries.

Use structured queries first when the answer is obviously about:

- linked project state,
- a specific stakeholder relationship,
- a known account source,
- or accepted task/decision records.

Use semantic retrieval when the system needs to find the most relevant supporting context across text-heavy artifacts.

**Stable architecture anchor:** `ARCH:StructuredQueryBeforeSemanticRecall`

### 8.4 Retrieval output posture

Retrieved content should be used as contextual support for graphs and UI surfaces, not silently hardened into accepted memory.

If retrieved context changes an important interpretation, that must flow through the normal reviewable artifact path.

**Stable architecture anchor:** `ARCH:RetrievalOutputPosture`

### 8.5 Retrieval storage baseline

The current baseline assumes pgvector or an equivalent semantic retrieval facility alongside the relational store.

**Stable architecture anchor:** `ARCH:VectorRetrievalBaseline`

---

## 9. Project Memory Refresh Model

### 9.1 Project memory as curated synthesis

Project memory is not just the sum of all linked records. It is the curated and refreshed working understanding of the project.

This includes:

- objective,
- current phase,
- active pressure points,
- major recent changes,
- leading next actions,
- major stakeholders,
- and known blockers or risks.

**Stable architecture anchor:** `ARCH:ProjectMemoryModel`

### 9.2 Refresh pipeline

A typical project memory refresh should:

1. gather relevant recent source artifacts,
2. gather newly accepted operational state,
3. gather recent interpreted artifacts if still relevant,
4. compare against the latest project summary,
5. generate an updated project summary,
6. persist the new summary with refresh metadata.

**Stable architecture anchor:** `ARCH:ProjectMemoryRefreshPipeline`

### 9.3 Review boundary

Routine project summary refresh does not necessarily require operator review, but if the system proposes meaningful structural changes — such as inferred new workstreams or major state reinterpretation — those should be surfaced through review-first mechanisms rather than silently rewritten into accepted memory.

**Stable architecture anchor:** `ARCH:ProjectMemoryRefreshReviewBoundary`

---

## 10. Stakeholder Memory Strategy

### 10.1 Stakeholder summary purpose

Stakeholder memory helps Glimmer support tactful communication and project-aware prioritization.

Stakeholder summaries should capture at least:

- who the person is,
- which projects they relate to,
- recent interaction themes,
- open asks or commitments,
- and useful communication cues.

**Stable architecture anchor:** `ARCH:StakeholderMemoryStrategy`

### 10.2 Identity merging caution

Because stakeholders may appear through multiple addresses and channels, the system must treat identity consolidation carefully.

Potential merges should remain reviewable where the confidence is not high.

**Stable architecture anchor:** `ARCH:StakeholderIdentityMergeBoundary`

---

## 11. Channel and Session Memory

### 11.1 Session continuity needs

Glimmer must preserve enough short-horizon session memory to maintain continuity across:

- web voice interactions,
- Telegram conversations,
- and other future companion channels.

**Stable architecture anchor:** `ARCH:SessionMemoryStrategy`

### 11.2 Channel session summaries

Long-running or repeated channel interactions should maintain concise session summaries so that Glimmer can recover recent context without replaying every raw turn.

This is especially valuable for:

- Telegram mobile follow-ups,
- resumed voice conversations,
- and channel handoff into the web workspace.

**Stable architecture anchor:** `ARCH:ChannelSessionSummaryStrategy`

### 11.3 Channel memory boundary

Channel-session memory should remain bounded and purpose-specific. It should not become a second uncontrolled general memory system outside the structured domain.

**Stable architecture anchor:** `ARCH:ChannelMemoryBoundary`

---

## 12. Audit and Trace Layer

### 12.1 Purpose

The audit and trace layer exists so Glimmer can explain how operational memory evolved and how important assistant outputs were produced.

**Stable architecture anchor:** `ARCH:AuditTracePurpose`

### 12.2 What should be traceable

At minimum, the system should preserve traceability for:

- source intake,
- account provenance,
- message classification creation,
- extracted action creation,
- summary refresh events,
- draft generation,
- persona selection event generation where helpful,
- operator overrides,
- and important accepted-memory mutations.

**Stable architecture anchor:** `ARCH:AuditTraceCoverage`

### 12.3 Audit posture

The audit layer is for operational trust, explainability, and diagnosis.

It is not intended to become invasive surveillance of every keystroke or conversational nuance.

**Stable architecture anchor:** `ARCH:AuditTracePosture`

---

## 13. Relationship to Repository-Local Documentation Retrieval

The Agentic Delivery Framework defines a repository-local documentation retrieval layer under `9. Agent Tools/` to help coding agents resolve anchors and relevant bounded snippets efficiently.

Glimmer’s product-memory retrieval architecture is separate from that documentation-retrieval layer.

The distinction is:

- **Product memory retrieval** supports Glimmer’s runtime behavior as a project chief-of-staff system.
- **Documentation retrieval** supports humans and coding agents working on the repository and its control documents.

These two retrieval systems may share implementation ideas, but they are not the same authority layer and should not be conflated.

**Stable architecture anchor:** `ARCH:RuntimeVsRepositoryRetrievalBoundary`

### 13.1 Shared design lessons

Even though they are separate, both retrieval systems should follow similar guardrails:

- prefer structured authority before broad semantic search,
- preserve source identity,
- avoid silent staleness,
- and keep retrieved context bounded and explainable.

**Stable architecture anchor:** `ARCH:RetrievalGuardrailParity`

---

## 14. Memory Failure Modes and Recovery

### 14.1 Failure classes

Relevant memory-layer failure classes include:

- stale summaries,
- retrieval returning weak or irrelevant support,
- summary drift from accepted state,
- provenance loss,
- accidental hardening of candidate interpretation into accepted truth,
- and session-memory confusion across channels.

### 14.2 Recovery posture

Where memory inconsistency is detected, the system should favor:

- preserving underlying source records,
- regenerating summaries,
- surfacing review,
- and avoiding silent destructive correction.

**Stable architecture anchor:** `ARCH:MemoryFailureRecovery`

---

## 15. Relationship to Verification

Because Glimmer’s behavior depends so heavily on stored and refreshed memory, the verification strategy must explicitly test:

- structured persistence correctness,
- provenance preservation,
- summary refresh behavior,
- retrieval relevance boundaries,
- audit trail creation,
- and state-boundary discipline between interpreted and accepted memory.

This aligns with the framework’s principle that testing and verification are first-class parts of design rather than cleanup work after implementation.

**Stable architecture anchor:** `ARCH:MemoryVerificationImplications`

---

## 16. Relationship to the Rest of the Architecture Set

This document defines Glimmer’s memory and retrieval behavior, but it does not define:

- graph step design,
- connector API specifics,
- UI rendering details,
- or token/security enforcement details.

Those concerns are handled in:

- `03_langgraph_orchestration.md`
- `04_connectors_and_ingestion.md`
- `06_ui_and_voice.md`
- `07_security_and_permissions.md`
- `08_testing_strategy.md` (housed under `4. Verification/`)

**Stable architecture anchor:** `ARCH:MemoryDocumentBoundary`

---

## 17. Final Note

Glimmer’s memory architecture must make the assistant feel informed and continuous without becoming opaque, brittle, or self-deceptive.

That means:

- structured records remain the foundation,
- summaries remain explicit and refreshable,
- retrieval remains bounded and explainable,
- and all important memory evolution remains traceable.

If later implementation drifts toward “just vectorize everything” or “just let the model remember it,” this document should be treated as the corrective reference.

**Stable architecture anchor:** `ARCH:MemoryConclusion`

