# Glimmer — Domain Model

## Document Metadata

- **Document Title:** Glimmer — Domain Model
- **Document Type:** Split Architecture Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `ARCHITECTURE.md`
- **Primary Companion Documents:** Requirements, System Overview, LangGraph Orchestration, Memory and Retrieval

---

## 1. Purpose

This document defines the core domain model for **Glimmer**.

It describes the principal entities, relationships, ownership boundaries, and state-bearing records that the system uses to coordinate multiple projects, multiple connected accounts, multiple interaction surfaces, and a persistent assistant memory model.

The purpose of this document is not to define table schemas or API payload contracts in final implementation detail. Its role is to define the canonical conceptual model that downstream orchestration, connector, UI, persistence, and verification design must follow.

**Stable architecture anchor:** `ARCH:PortfolioDomainModel`

---

## 2. Domain Modeling Principles

The domain model for Glimmer shall follow these principles.

### 2.1 Structured operational memory

The system must store operationally meaningful state in structured entities rather than relying on unbounded chat transcripts or opaque memory blobs.

**Stable architecture anchor:** `ARCH:DomainPrinciple.StructuredOperationalMemory`

### 2.2 Provenance preservation

The domain model must preserve where information came from, including source account, source channel, source thread, and source message identity.

**Stable architecture anchor:** `ARCH:DomainPrinciple.ProvenancePreservation`

### 2.3 Single-operator, multi-context design

The primary user model is one operator with multiple projects, stakeholders, connected accounts, and interaction channels.

**Stable architecture anchor:** `ARCH:DomainPrinciple.SingleOperatorMultiContext`

### 2.4 Reviewable interpretation

Extracted actions, classifications, summaries, and draft outputs must remain reviewable domain artifacts rather than invisible transient model thoughts.

**Stable architecture anchor:** `ARCH:DomainPrinciple.ReviewableInterpretation`

### 2.5 Separation of raw signal and interpreted state

The system shall distinguish between:

- raw imported signals,
- normalized internal records,
- interpreted outputs,
- and user-approved memory state.

This reduces drift and improves auditability.

**Stable architecture anchor:** `ARCH:DomainPrinciple.SignalVsInterpretation`

---

## 3. Core Domain Entity Groups

At the highest level, the Glimmer domain is composed of eight major entity groups:

1. **Operator context**
2. **Project portfolio**
3. **Stakeholder and relationship memory**
4. **Connected account and source provenance**
5. **Messages, events, and imported signals**
6. **Tasks, decisions, risks, and execution artifacts**
7. **Drafts, briefings, and assistant-facing outputs**
8. **Persona and channel interaction state**

**Stable architecture anchor:** `ARCH:DomainEntityGroups`

---

## 4. Operator Context Model

### 4.1 PrimaryOperator

The `PrimaryOperator` entity represents the person using Glimmer.

This entity exists to anchor:

- project ownership,
- connected account ownership,
- channel identity,
- personalization settings,
- and prioritization context.

Typical conceptual properties include:

- operator identifier
- display name
- preferred timezone
- preferred working hours
- preferred language or tone settings
- channel preferences
- summary preferences
- escalation or interruption preferences

The domain should not assume a multi-user collaborative model in MVP, but it should maintain a clear operator entity so the system is not built on anonymous local state.

**Stable architecture anchor:** `ARCH:PrimaryOperatorModel`

---

## 5. Project Portfolio Model

### 5.1 Project

`Project` is the central organizing entity in Glimmer.

A project represents a coherent body of work requiring memory, prioritization, stakeholder tracking, and communication support.

Typical conceptual properties include:

- project identifier
- name
- short summary
- objective
- status
- phase
- priority band
- confidence or health signal
- created/updated timestamps
- archive state

A project should be able to link to:

- milestones
- workstreams
- work items
- decisions
- risks
- blockers
- stakeholders
- recent messages
- related drafts
- focus summaries

**Stable architecture anchor:** `ARCH:ProjectStateModel`

### 5.2 ProjectWorkstream

A `ProjectWorkstream` represents a meaningful subdivision of a project.

This is the domain concept that supports planning structure above the task level.

Typical conceptual properties include:

- workstream identifier
- parent project identifier
- title
- summary
- status
- ordering / sequence hint
- owner hint
- dependency notes

**Stable architecture anchor:** `ARCH:ProjectWorkstreamModel`

### 5.3 Milestone

A `Milestone` represents a project-level checkpoint or meaningful outcome marker.

Typical conceptual properties include:

- milestone identifier
- parent project identifier
- title
- description
- target date
- status
- completion timestamp
- importance weighting

**Stable architecture anchor:** `ARCH:MilestoneModel`

### 5.4 ProjectSummary

A `ProjectSummary` is a derived domain artifact representing the current synthesized understanding of a project.

It should be treated as a first-class stored artifact rather than something regenerated invisibly every time.

Typical conceptual properties include:

- summary identifier
- project identifier
- summary text
- generated_at timestamp
- source scope metadata
- version marker
- confidence indicator

**Stable architecture anchor:** `ARCH:ProjectSummaryModel`

---

## 6. Stakeholder and Relationship Model

### 6.1 Stakeholder

A `Stakeholder` represents a person or meaningful external/internal actor related to one or more projects.

Typical conceptual properties include:

- stakeholder identifier
- display name
- organization
- role/title
- notes
- relationship importance
- communication style hints
- activity recency

A stakeholder may link to:

- multiple projects
- multiple email identities
- multiple account-specific aliases
- open requests
- recent interactions
- drafts involving them

**Stable architecture anchor:** `ARCH:StakeholderModel`

### 6.2 StakeholderIdentity

A `StakeholderIdentity` captures one concrete addressable identity for a stakeholder.

Examples include:

- email address
- alternate email address
- Telegram username or handle
- Slack identity in future phases

This separation matters because one stakeholder may appear through multiple addresses or channels.

Typical conceptual properties include:

- identity identifier
- stakeholder identifier
- channel type
- identity value
- tenant / workspace context where relevant
- verification or confidence state

**Stable architecture anchor:** `ARCH:StakeholderIdentityModel`

### 6.3 StakeholderProjectLink

A `StakeholderProjectLink` represents the relationship between a stakeholder and a project.

This allows the same stakeholder to have different roles, salience, tone expectations, or open asks in different projects.

Typical conceptual properties include:

- link identifier
- stakeholder identifier
- project identifier
- relationship type
- relative importance within project
- open commitments
- notes

**Stable architecture anchor:** `ARCH:StakeholderProjectLinkModel`

---

## 7. Connected Account and Source Provenance Model

### 7.1 ConnectedAccount

A `ConnectedAccount` represents one connected external communication or calendar account belonging to the primary operator.

This entity is central to Glimmer’s multi-account design.

Typical conceptual properties include:

- connected account identifier
- operator identifier
- provider type (`google`, `google_workspace`, `microsoft_365`, etc.)
- account display label
- mailbox or account address
- tenant/workspace context where relevant
- account purpose label (optional)
- status
- authorization metadata
- sync metadata

The system must preserve `ConnectedAccount` linkage for all imported messages and events.

**Stable architecture anchor:** `ARCH:ConnectedAccountModel`

### 7.2 AccountProfile

An `AccountProfile` represents a more specific logical profile under a connected account where needed.

Examples include:

- mail profile
- calendar profile
- sub-calendar
- inbox or folder context

This concept exists so Glimmer can distinguish between account-level identity and profile-level operating context.

**Stable architecture anchor:** `ARCH:AccountProfileModel`

### 7.3 AccountProvenance

`AccountProvenance` is not necessarily a standalone user-facing entity, but it is a required conceptual model.

Every imported item must be able to preserve provenance such as:

- connected account source
- account profile source
- provider type
- remote item identifier
- thread identifier
- folder/label context where relevant
- import timestamp

**Stable architecture anchor:** `ARCH:AccountProvenanceConcept`

---

## 8. Message, Event, and Signal Model

### 8.1 Message

A `Message` is the normalized internal representation of an imported communication unit.

This may originate from:

- Gmail
- Microsoft 365 mail
- manual imported chat content
- future supported channels

Typical conceptual properties include:

- message identifier
- source type
- connected account identifier
- account profile identifier where applicable
- external message identifier
- external thread identifier
- subject/title
- normalized body text
- sent/received timestamp
- sender identity
- recipient identities
- import metadata
- attachment summary metadata where relevant

A `Message` should not be treated as the same thing as a conversation thread.

**Stable architecture anchor:** `ARCH:MessageModel`

### 8.2 MessageThread

A `MessageThread` represents a grouped communication thread where threading semantics exist.

Typical conceptual properties include:

- thread identifier
- source type
- connected account identifier
- external thread identifier
- derived subject or label
- participant set
- last activity timestamp

Threads matter because project classification often depends on thread context, not just one message.

**Stable architecture anchor:** `ARCH:MessageThreadModel`

### 8.3 CalendarEvent

A `CalendarEvent` is the normalized internal representation of an imported calendar item.

Typical conceptual properties include:

- event identifier
- connected account identifier
- external event identifier
- title
- description summary
- start time
- end time
- participants
- location or meeting link
- source calendar identity
- import timestamp

Calendar events are used both as planning inputs and as briefing triggers.

**Stable architecture anchor:** `ARCH:CalendarEventModel`

### 8.4 ImportedSignal

An `ImportedSignal` is a broader abstraction for raw or semi-structured imported input that may not fit neatly into a standard message or event.

Examples include:

- manual paste of a WhatsApp conversation
- imported text note from Telegram interaction
- future voice transcript import unit

This entity group helps preserve raw inputs before interpretation.

**Stable architecture anchor:** `ARCH:ImportedSignalModel`

---

## 9. Interpretation and Triage Model

### 9.1 MessageClassification

A `MessageClassification` represents Glimmer’s structured interpretation of a message or signal.

Typical conceptual properties include:

- classification identifier
- source record identifier
- candidate project identifiers
- selected project identifier
- confidence signal
- ambiguity flag
- classification rationale summary
- extracted stakeholder identifiers
- created timestamp
- review status

The classification should be stored as a domain artifact, not merely held transiently during LLM execution.

**Stable architecture anchor:** `ARCH:MessageClassificationModel`

### 9.2 ExtractedAction

An `ExtractedAction` represents a candidate follow-up or requested action detected from a message, event, or spoken update.

Typical conceptual properties include:

- action identifier
- source record identifier
- linked project identifier
- proposed owner
- action text
- due-date signal
- urgency signal
- review status

**Stable architecture anchor:** `ARCH:ExtractedActionModel`

### 9.3 ExtractedDecision

An `ExtractedDecision` represents a decision inferred or captured from a communication or briefing artifact.

**Stable architecture anchor:** `ARCH:ExtractedDecisionModel`

### 9.4 ExtractedDeadlineSignal

An `ExtractedDeadlineSignal` represents a time-bound obligation or inferred deadline reference.

This is separated conceptually because a time signal may exist before it is accepted as a concrete work item due date.

**Stable architecture anchor:** `ARCH:ExtractedDeadlineSignalModel`

### 9.5 ReviewState

A `ReviewState` concept applies to classification outputs, extracted actions, and other interpreted records.

Typical values may include:

- pending_review
- accepted
- amended
- rejected
- superseded

The exact implementation can vary, but the domain model must preserve the concept of reviewable interpretation.

**Stable architecture anchor:** `ARCH:InterpretationReviewState`

---

## 10. Execution Artifact Model

### 10.1 WorkItem

A `WorkItem` is the canonical actionable execution record in Glimmer.

It may originate from:

- user-created task
- extracted action accepted into project memory
- planning-generated next step
- imported reminder or follow-up

Typical conceptual properties include:

- work item identifier
- parent project identifier
- optional parent workstream identifier
- title
- description
- type
- status
- due date
- owner hint
- source provenance
- priority indicators
- dependency references

**Stable architecture anchor:** `ARCH:WorkItemModel`

### 10.2 DecisionRecord

A `DecisionRecord` is the accepted, canonical project memory record of a decision.

This is distinct from `ExtractedDecision`, which is an interpreted candidate.

**Stable architecture anchor:** `ARCH:DecisionRecordModel`

### 10.3 RiskRecord

A `RiskRecord` represents a recognized project risk.

Typical conceptual properties include:

- risk identifier
- parent project identifier
- summary
- severity signal
- likelihood signal
- mitigation notes
- status

**Stable architecture anchor:** `ARCH:RiskRecordModel`

### 10.4 BlockerRecord

A `BlockerRecord` represents an active impediment to project execution.

**Stable architecture anchor:** `ARCH:BlockerRecordModel`

### 10.5 WaitingOnRecord

A `WaitingOnRecord` represents something pending from another person, team, or external dependency.

This is important because Glimmer explicitly helps the operator understand what is blocked by others versus what requires direct action.

**Stable architecture anchor:** `ARCH:WaitingOnRecordModel`

---

## 11. Drafting and Briefing Model

### 11.1 Draft

A `Draft` is a proposed outgoing response or message prepared by Glimmer for operator review.

Typical conceptual properties include:

- draft identifier
- linked source message or signal
- linked project identifier
- linked stakeholder set
- channel type
- tone mode
- body content
- rationale summary
- version number
- status
- created timestamp

The domain model must support multiple drafts or revisions per source where appropriate.

**Stable architecture anchor:** `ARCH:DraftModel`

### 11.2 DraftVariant

A `DraftVariant` is an alternate wording/version linked to a common drafting intent.

Examples include:

- concise
- fuller
- firmer
- warmer
- executive

This should not require entirely separate unrelated draft records when the domain intent is clearly one drafting episode with multiple renderings.

**Stable architecture anchor:** `ARCH:DraftVariantModel`

### 11.3 BriefingArtifact

A `BriefingArtifact` is a generated briefing output used to prepare the operator.

Examples include:

- daily focus pack
- meeting prep brief
- weekly review brief
- concise Telegram status summary

**Stable architecture anchor:** `ARCH:BriefingArtifactModel`

### 11.4 FocusPack

A `FocusPack` is a specialized briefing artifact that summarizes what matters now.

Typical conceptual properties include:

- focus pack identifier
- operator identifier
- generated_at timestamp
- top actions
- high-risk items
- waiting-on items
- reply debt summary
- calendar pressure summary

**Stable architecture anchor:** `ARCH:FocusPackModel`

---

## 12. Persona and Experience Model

### 12.1 PersonaAsset

A `PersonaAsset` represents one approved Glimmer image or visual persona asset.

Typical conceptual properties include:

- persona asset identifier
- label/name
- asset path or storage reference
- asset type
- active flag
- default flag
- notes

**Stable architecture anchor:** `ARCH:PersonaAssetModel`

### 12.2 PersonaClassification

A `PersonaClassification` represents the labeling of a persona asset for UX selection.

Typical concepts include:

- mood label
- interaction mode label
- tone label
- priority/focus suitability
- drafting suitability
- morale/support suitability

This may be implemented as tags or a normalized taxonomy, but the domain must support explicit labeling.

**Stable architecture anchor:** `ARCH:PersonaClassificationModel`

### 12.3 PersonaSelectionEvent

A `PersonaSelectionEvent` represents the runtime selection of a persona asset for a given interaction context.

This is not purely cosmetic; it supports auditability, UX consistency, and later analysis of persona mapping logic.

**Stable architecture anchor:** `ARCH:PersonaSelectionEventModel`

---

## 13. Channel Interaction Model

### 13.1 ChannelSession

A `ChannelSession` represents an ongoing interaction context between the operator and Glimmer over a specific companion or interaction channel.

Examples include:

- Telegram conversation session
- web voice session
- future Slack direct session

Typical conceptual properties include:

- channel session identifier
- operator identifier
- channel type
- channel identity
- session state
- last interaction timestamp
- linked conversation summary

**Stable architecture anchor:** `ARCH:ChannelSessionModel`

### 13.2 TelegramConversationState

A `TelegramConversationState` is a Telegram-specific specialization or conceptual extension of `ChannelSession`.

It exists because the Telegram companion may require channel-local state such as:

- pending clarification
- current topic
- last referenced project
- temporary reply mode

Whether implemented as a separate table/entity or as typed channel-session metadata, the domain must preserve this concept.

**Stable architecture anchor:** `ARCH:TelegramConversationStateModel`

### 13.3 VoiceSessionState

A `VoiceSessionState` represents an active or recent voice interaction state.

This supports:

- transcript continuity
- summary continuity
- action extraction lineage
- and session recovery where required

**Stable architecture anchor:** `ARCH:VoiceSessionStateModel`

---

## 14. Relationship Summary

The most important domain relationships are:

- one `PrimaryOperator` to many `Projects`
- one `PrimaryOperator` to many `ConnectedAccounts`
- one `Project` to many `Workstreams`, `Milestones`, `WorkItems`, `DecisionRecords`, `RiskRecords`, and `BlockerRecords`
- many `Stakeholders` to many `Projects` through `StakeholderProjectLink`
- one `ConnectedAccount` to many `Messages`, `CalendarEvents`, and `MessageThreads`
- one `MessageThread` to many `Messages`
- one `Message` to zero or many `MessageClassification`, `ExtractedAction`, and `Draft` records
- one `Project` to many `BriefingArtifacts`
- one `Draft` to many `DraftVariants`
- many `PersonaAsset` records to many interaction contexts through persona selection logic
- one `PrimaryOperator` to many `ChannelSession` records

**Stable architecture anchor:** `ARCH:DomainRelationshipSummary`

---

## 15. State Ownership and Mutation Boundaries

The domain model should distinguish between the following mutation categories:

1. **Imported source state**
   - external messages, events, raw imported signals

2. **Interpreted candidate state**
   - classifications, extracted actions, candidate decisions, summaries

3. **Accepted operational memory state**
   - project records, work items, stakeholder links, accepted decision records

4. **User-facing generated output state**
   - drafts, focus packs, briefings, persona selection events

This distinction helps protect the operator from silent mutation and supports review-first behavior.

**Stable architecture anchor:** `ARCH:StateOwnershipBoundaries`

---

## 16. Domain Boundaries for the Next Documents

This domain model intentionally stops short of:

- graph node design,
- connector polling/subscription strategies,
- storage engine specifics,
- token/OAuth semantics,
- and detailed UI rendering behavior.

Those concerns are delegated to:

- `03-langgraph-orchestration.md`
- `04-connectors-and-ingestion.md`
- `05-memory-and-retrieval.md`
- `06-ui-and-voice.md`
- `07-security-and-permissions.md`

**Stable architecture anchor:** `ARCH:DomainModelDocumentBoundary`

---

## 17. Final Note

The Glimmer domain model is designed to preserve the meaning of work, communication, and operator context without collapsing everything into generic chat memory.

Its purpose is to make the assistant durable, reviewable, explainable, and useful across multiple projects, multiple accounts, and multiple interaction modes.

If later implementation decisions threaten to flatten provenance, blur interpretation with accepted state, or erase the distinction between structured memory and transient model output, this document should be treated as the corrective reference.

**Stable architecture anchor:** `ARCH:DomainModelConclusion`

