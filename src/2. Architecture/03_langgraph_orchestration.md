# Glimmer — LangGraph Orchestration

## Document Metadata

- **Document Title:** Glimmer — LangGraph Orchestration
- **Document Type:** Split Architecture Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `ARCHITECTURE.md`
- **Primary Companion Documents:** System Overview, Domain Model, Connectors and Ingestion, UI and Voice

---

## 1. Purpose

This document defines the orchestration architecture for **Glimmer** using **LangGraph**.

It describes how Glimmer’s major workflows are decomposed into graph-based execution models, how state moves through those graphs, where human review interrupts are required, and how the system maintains continuity across sessions, channels, and partially completed work.

This document is not intended to define connector-specific polling rules, UI layout specifics, or persistence implementation details. Its purpose is to define the canonical orchestration model that coordinates the domain, integrations, and user-facing surfaces.

**Stable architecture anchor:** `ARCH:LangGraphTopology`

---

## 2. Orchestration Role in the System

In Glimmer, LangGraph is the orchestration layer that coordinates:

- intake of incoming signals,
- contextual classification,
- project-memory refresh,
- prioritization,
- drafting,
- briefing generation,
- voice-session continuity,
- Telegram companion interactions,
- and human review / interrupt handling.

LangGraph is not the system of record. It is the **execution and coordination fabric** between source signals, domain entities, derived interpretations, and user-facing outputs.

This distinction matters because:

- durable truth belongs in the domain and persistence layer,
- bounded external access belongs in connectors,
- and operator-facing interaction belongs in the UI and channel layers.

LangGraph is responsible for deciding **what workflow happens next** and **what state transition or review action is needed**, not for becoming an unstructured memory bucket.

**Stable architecture anchor:** `ARCH:OrchestrationRole`

---

## 3. Orchestration Principles

### 3.1 Graphs by business workflow, not by technical layer

Graphs shall be decomposed around meaningful operational workflows rather than around arbitrary technical modules.

**Stable architecture anchor:** `ARCH:OrchestrationPrinciple.WorkflowDecomposition`

### 3.2 State must be durable and resumable

Where workflows span time, require review, or depend on asynchronous inputs, graph state shall be resumable rather than ephemeral.

**Stable architecture anchor:** `ARCH:OrchestrationPrinciple.ResumableState`

### 3.3 Review gates are explicit graph concepts

Human review is not a side effect. It is part of the orchestration design and must be represented explicitly through interrupts, pending-review states, and resumable continuation.

**Stable architecture anchor:** `ARCH:OrchestrationPrinciple.ExplicitReviewGates`

### 3.4 Graphs produce domain artifacts, not hidden reasoning only

The result of orchestration should be stored as visible and reviewable artifacts such as classifications, extracted actions, drafts, summaries, focus packs, and review requests.

**Stable architecture anchor:** `ARCH:OrchestrationPrinciple.VisibleArtifacts`

### 3.5 Channel-specific entrypoints, shared core flows

Web, voice, and Telegram interactions may begin differently, but they should reuse shared downstream planning, drafting, and memory-update logic wherever possible.

**Stable architecture anchor:** `ARCH:OrchestrationPrinciple.SharedCoreFlows`

### 3.6 Low-confidence outcomes must not silently self-commit

If classification, extraction, or next-step inference is ambiguous, the graph shall enter a reviewable state rather than silently hardening a weak interpretation into project memory.

**Stable architecture anchor:** `ARCH:OrchestrationPrinciple.LowConfidenceReview`

---

## 4. Graph Topology Overview

The Glimmer orchestration model is composed of a small set of primary graphs and supporting subflows.

### 4.1 Primary graphs

The primary graphs are:

1. **Intake Graph**
2. **Triage Graph**
3. **Planner Graph**
4. **Drafting Graph**
5. **Voice Session Graph**
6. **Telegram Companion Graph**
7. **Research Escalation Graph**

### 4.2 Supporting orchestration patterns

These graphs are supported by shared orchestration patterns for:

- state loading and hydration,
- review interrupts,
- summary refresh,
- provenance preservation,
- focus-pack generation,
- research escalation routing,
- and memory update handoff.

The architecture should prefer a **small number of coherent graphs** over one giant monolithic graph or an excessive number of micro-graphs.

**Stable architecture anchor:** `ARCH:GraphTopologyOverview`

---

## 5. Shared Graph State Concepts

Each graph may have its own local working state, but the orchestration architecture shall rely on a common set of state concepts.

### 5.1 Workflow context

Workflow context should include:

- workflow type,
- initiating channel,
- initiating user/operator context,
- linked project identifiers where known,
- linked source artifact identifiers,
- and current step / pending status.

**Stable architecture anchor:** `ARCH:GraphState.WorkflowContext`

### 5.2 Domain references

Graphs should pass references to domain records rather than repeatedly duplicating full business state.

Examples include:

- project identifiers,
- message identifiers,
- connected account identifiers,
- stakeholder identifiers,
- draft identifiers,
- and channel session identifiers.

**Stable architecture anchor:** `ARCH:GraphState.DomainReferences`

### 5.3 Review state

Where a graph pauses for human involvement, the pending review state should preserve:

- what decision is required,
- which candidate outcomes were produced,
- what context the operator should see,
- and what continuation path will resume after approval or amendment.

**Stable architecture anchor:** `ARCH:GraphState.ReviewState`

### 5.4 Continuation metadata

Graphs should preserve enough continuation metadata to support safe resumption after:

- time delay,
- session restart,
- channel switch,
- or operator review.

**Stable architecture anchor:** `ARCH:GraphState.ContinuationMetadata`

### 5.5 Confidence and ambiguity signals

Where the system generates interpretation, the graph state should retain confidence and ambiguity signals so that downstream review and UI presentation can remain honest.

**Stable architecture anchor:** `ARCH:GraphState.ConfidenceSignals`

---

## 6. Intake Graph

The Intake Graph is responsible for converting incoming signals into normalized, domain-linked, reviewable starting artifacts.

### 6.1 Responsibilities

The Intake Graph shall:

- accept incoming signal payloads from connectors or companion channels,
- normalize them into internal source records,
- preserve source provenance,
- identify the likely source type and workflow path,
- persist the raw/normalized input record,
- and route the result into the next graph stage.

**Stable architecture anchor:** `ARCH:IntakeGraph`

### 6.2 Typical inputs

Inputs may include:

- imported Gmail message,
- imported Microsoft 365 message,
- imported calendar event,
- manually imported chat text,
- Telegram message from the operator,
- or voice transcript segment.

### 6.3 Typical outputs

Outputs may include:

- `Message`
- `CalendarEvent`
- `ImportedSignal`
- source provenance record linkage
- next-step routing instruction

### 6.4 Routing outcomes

The Intake Graph shall typically route into one of the following:

- Triage Graph for classification and extraction,
- Planner Graph for direct memory refresh or focus generation,
- Drafting Graph when the operator explicitly requests a response draft,
- Voice Session Graph when the signal belongs to an active voice conversation,
- Telegram Companion Graph when the signal belongs to a channel session.

**Stable architecture anchor:** `ARCH:IntakeGraphRouting`

---

## 7. Triage Graph

The Triage Graph is responsible for interpreting incoming messages and signals in project context.

### 7.1 Responsibilities

The Triage Graph shall:

- load relevant project memory,
- load stakeholder context,
- evaluate account provenance,
- classify project relevance,
- extract likely actions, decisions, deadlines, and blockers,
- determine whether review is required,
- and persist interpretation artifacts.

**Stable architecture anchor:** `ARCH:TriageGraph`

### 7.2 Inputs

Typical inputs include:

- normalized `Message`
- normalized `ImportedSignal`
- linked `MessageThread` context where available
- linked `ConnectedAccount` / `AccountProfile`
- relevant recent project summaries
- stakeholder matches

### 7.3 Outputs

Typical outputs include:

- `MessageClassification`
- `ExtractedAction`
- `ExtractedDecision`
- `ExtractedDeadlineSignal`
- triage queue entry
- review request when ambiguity is high

### 7.4 Decision points

The Triage Graph should explicitly decide:

- is this project-relevant,
- which project is the best current match,
- is the classification ambiguous,
- does this create or update a task-worthy action,
- does this imply urgency or deadline pressure,
- and does it warrant a draft suggestion.

### 7.5 Review gate behavior

The graph shall interrupt when:

- classification confidence is low,
- multiple projects are plausible,
- stakeholder matching is uncertain in a materially important way,
- or extracted action meaning is too ambiguous to commit safely.

**Stable architecture anchor:** `ARCH:TriageGraphReviewGate`

---

## 8. Planner Graph

The Planner Graph is responsible for converting project memory and interpreted signal state into actionable prioritization and planning outputs.

### 8.1 Responsibilities

The Planner Graph shall:

- refresh project-level synthesized understanding,
- update or propose next actions,
- infer work breakdown opportunities,
- rank work by relevance and urgency,
- generate daily/weekly operating views,
- and produce focus-oriented outputs for the operator.

**Stable architecture anchor:** `ARCH:PlannerGraph`

### 8.2 Inputs

Typical inputs include:

- current project records,
- recent `MessageClassification` artifacts,
- extracted actions and deadline signals,
- calendar pressure,
- waiting-on state,
- and the operator’s current context or explicit request.

### 8.3 Outputs

Typical outputs include:

- refreshed `ProjectSummary`
- proposed `WorkItem` additions or updates
- `FocusPack`
- daily brief
- weekly review artifact
- priority rationale summaries

### 8.4 Priority reasoning posture

The Planner Graph must produce outputs that are:

- explainable,
- adjustable by review,
- and visibly grounded in project state, deadlines, risks, dependencies, and operator ownership.

The graph should not become a black-box ranker whose outputs cannot be explained or challenged.

**Stable architecture anchor:** `ARCH:PlannerGraphExplainability`

### 8.5 Planner review gates

The Planner Graph may require review when:

- it proposes substantial restructuring of work breakdown,
- it reclassifies a project’s apparent urgency significantly,
- or it suggests memory changes that should not silently harden into accepted project state.

**Stable architecture anchor:** `ARCH:PlannerGraphReviewGate`

---

## 9. Drafting Graph

The Drafting Graph is responsible for generating reviewable response drafts in Glimmer’s dedicated drafting workspace.

### 9.1 Responsibilities

The Drafting Graph shall:

- load source message context,
- load project and stakeholder context,
- infer reply intent,
- select an appropriate tone posture,
- generate one or more draft variants,
- persist them as reviewable domain artifacts,
- and route them to the operator-facing draft workspace.

**Stable architecture anchor:** `ARCH:DraftingGraph`

### 9.2 Inputs

Typical inputs include:

- source `Message` or `ImportedSignal`
- linked `Project`
- linked `Stakeholder` records
- recent thread/project summary context
- requested tone or mode if explicitly provided

### 9.3 Outputs

Typical outputs include:

- `Draft`
- one or more `DraftVariant`
- rationale summary
- review-required state

### 9.4 Constraints

The Drafting Graph must not send or commit external communication.

Its role ends with:

- persisted draft creation,
- reviewable presentation,
- and optional operator-approved copy/export workflows handled elsewhere.

**Stable architecture anchor:** `ARCH:DraftingGraphNoAutoSend`

### 9.5 Drafting review gates

The Drafting Graph is inherently review-first. All draft outputs should be treated as needing operator review before use.

**Stable architecture anchor:** `ARCH:DraftingGraphReviewGate`

---

## 10. Voice Session Graph

The Voice Session Graph is responsible for maintaining continuity and meaning across real-time or near-real-time spoken interaction.

### 10.1 Responsibilities

The Voice Session Graph shall:

- track voice-session context,
- receive transcript segments,
- maintain short-horizon conversational continuity,
- interpret spoken updates,
- convert spoken intent into structured downstream actions,
- and route work into planning, drafting, or memory update flows as needed.

**Stable architecture anchor:** `ARCH:VoiceSessionGraph`

### 10.2 Inputs

Typical inputs include:

- transcript segments,
- active `VoiceSessionState`,
- recent operator prompts,
- referenced project or focus context,
- channel/session metadata.

### 10.3 Outputs

Typical outputs include:

- spoken response content,
- `ImportedSignal` or structured update artifacts,
- extracted actions,
- planner requests,
- draft requests,
- session-summary artifacts.

### 10.4 Continuity model

Voice interaction should not require the operator to re-establish context repeatedly during one session.

The Voice Session Graph should therefore preserve:

- recent topic,
- referenced projects,
- unresolved prompts,
- and recent assistant response context.

**Stable architecture anchor:** `ARCH:VoiceSessionContinuity`

### 10.5 Review boundaries

Voice may capture intent quickly, but significant downstream actions must still respect the same review boundaries as other modes.

**Stable architecture anchor:** `ARCH:VoiceSessionReviewBoundary`

---

## 11. Telegram Companion Graph

The Telegram Companion Graph is responsible for handling Glimmer’s Telegram-based mobile interaction mode.

### 11.1 Responsibilities

The Telegram Companion Graph shall:

- manage Telegram session continuity,
- interpret operator messages in mobile context,
- support quick status and priority queries,
- capture notes and follow-ups,
- and route requests into shared planning, drafting, or briefing flows.

**Stable architecture anchor:** `ARCH:TelegramCompanionGraph`

### 11.2 Inputs

Typical inputs include:

- Telegram text message from the operator,
- current `ChannelSession`
- `TelegramConversationState`
- recent relevant focus/project summaries

### 11.3 Outputs

Typical outputs include:

- concise Telegram reply content,
- note/import signal record,
- planner request,
- briefing request,
- or pending clarification state.

### 11.4 Scope discipline

The Telegram graph should be optimized for:

- short conversational turns,
- constrained interaction,
- status retrieval,
- capture of updates,
- and lightweight assistant continuity.

It should not be treated as a full replacement for the web workspace.

**Stable architecture anchor:** `ARCH:TelegramCompanionScope`

### 11.5 Telegram review boundaries

Where Telegram interaction leads to draft creation, project-memory mutation, or ambiguous interpretation, the graph must either:

- route into a reviewable pending state,
- or instruct the operator to continue in the web workspace where richer review is possible.

**Stable architecture anchor:** `ARCH:TelegramCompanionReviewBoundary`

---

## 11A. Research Escalation Graph

### 11A.1 Purpose

The Research Escalation Graph manages the lifecycle of deep-research tasks that exceed the local model's practical capability.

This graph coordinates:

- research escalation decisions,
- research run invocation through the browser-mediated adapter,
- structured result capture and normalization,
- research artifact persistence,
- failure and degraded-mode handling,
- and re-entry of research results into the appropriate downstream workflow (triage, planner, drafting).

**Stable architecture anchor:** `ARCH:ResearchEscalationGraph`

### 11A.2 Inputs

Typical inputs include:

- research task description or query,
- triggering context (linked project, message, workflow, or operator request),
- escalation policy metadata (why this task was routed to research),
- and relevant project/stakeholder context for query enrichment.

### 11A.3 Outputs

Typical outputs include:

- `ResearchRun` record with completion status,
- `ResearchFinding` records,
- `ResearchSourceReference` records,
- `ResearchSummaryArtifact` with review state,
- and continuation signal back to the originating workflow (triage, planner, or drafting graph).

### 11A.4 Research escalation policy

The graph should implement a bounded escalation policy that determines when a task should be routed to external reasoning and which mode to use. The policy distinguishes two escalation paths:

1. **Expert advice (synchronous chat)** — for bounded questions, decisions, or reasoning tasks that can be answered in a single prompt-response exchange. This is the lightweight, fast path.
2. **Deep research (async Deep Research)** — for complex, multi-step research tasks requiring extended investigation and structured output. This is the heavyweight, long-running path.

Escalation triggers may include:

- explicit operator request (with mode selection),
- task complexity exceeding a configurable threshold,
- task type that inherently benefits from multi-source research,
- or orchestration-level determination that local model output is insufficient.

The escalation policy must be configurable and explainable. The system should not silently escalate every task to browser-mediated research.

**Stable architecture anchor:** `ARCH:ResearchEscalationPolicy`
**Stable architecture anchor:** `ARCH:ExpertAdviceEscalationPolicy`

### 11A.5 Research run lifecycle

The research run lifecycle within this graph follows:

1. **Initiation** — validate escalation context, prepare research query, check browser availability.
2. **Execution** — invoke the browser-mediated adapter, interact with Gemini, capture responses.
3. **Normalization** — structure raw results into findings, source references, and summary artifacts.
4. **Persistence** — store the research run, findings, and summary artifacts with full provenance.
5. **Re-entry** — return structured results to the originating workflow for integration into triage, planning, or drafting.
6. **Failure handling** — if browser attachment fails, Gemini is unavailable, or the run times out, record a visible failure state and allow graceful degradation.

**Stable architecture anchor:** `ARCH:ResearchRunLifecycle`

### 11A.6 Review and safety boundaries

Research results enter Glimmer as **interpreted candidate artifacts**, not accepted operational memory. They must pass through the same review model as other interpreted outputs before being hardened into project memory.

The research graph must not:

- silently commit research findings into accepted project state,
- send external messages based on research results,
- or allow the browser-mediated adapter to take unbounded action.

**Stable architecture anchor:** `ARCH:ResearchVerificationStrategy`

---

## 11B. Expert Advice Subflow

### 11B.1 Purpose

The Expert Advice Subflow manages synchronous consultations with Gemini for tasks that benefit from a more powerful model but do not require full deep research.

This subflow coordinates:

- expert-advice invocation through the browser-mediated adapter,
- mode selection (Fast, Thinking, or Pro),
- response capture and provenance recording,
- persistence of the `ExpertAdviceExchange` record,
- and return of the response to the originating workflow as an interpreted candidate.

**Stable architecture anchor:** `ARCH:ExpertAdviceSubflow`

### 11B.2 Lifecycle

1. **Invocation** — validate escalation context, prepare the prompt, check browser availability.
2. **Mode selection** — select Gemini mode (default: Pro, with operator override or policy-driven selection).
3. **Execution** — invoke the browser-mediated adapter's synchronous chat method.
4. **Recording** — persist the `ExpertAdviceExchange` record with full provenance.
5. **Re-entry** — return the response text to the originating workflow as interpreted advisory content.
6. **Failure handling** — if browser or Gemini is unavailable, record a visible failure and fall back to local model output.

### 11B.3 Review and safety boundaries

Expert-advice responses enter Glimmer as **interpreted candidates**. They follow the same review-gate discipline as research findings.

The expert-advice subflow must not:

- silently commit advisory content into accepted project state,
- send external messages based on the response,
- or bypass the adapter's single-operation lock.

**Stable architecture anchor:** `ARCH:ExpertAdviceReviewBoundary`

In addition to the primary graphs, Glimmer should implement a set of reusable orchestration subflows.

### 12.1 Context hydration subflow

Loads the minimum relevant project, stakeholder, provenance, and session context required for a workflow.

**Stable architecture anchor:** `ARCH:Subflow.ContextHydration`

### 12.2 Summary refresh subflow

Regenerates or updates synthesized summaries when underlying state has changed enough to justify refresh.

**Stable architecture anchor:** `ARCH:Subflow.SummaryRefresh`

### 12.3 Review request creation subflow

Creates a normalized pending-review artifact with rationale, candidate outputs, and continuation metadata.

**Stable architecture anchor:** `ARCH:Subflow.ReviewRequestCreation`

### 12.4 Focus-pack generation subflow

Generates a current focus-oriented artifact from project and prioritization state.

**Stable architecture anchor:** `ARCH:Subflow.FocusPackGeneration`

### 12.5 Persona selection subflow

Selects a labeled Glimmer persona asset suitable for the current interaction context.

This is a UX support subflow and should remain bounded to approved assets and transparent selection logic.

**Stable architecture anchor:** `ARCH:Subflow.PersonaSelection`

---

## 13. Interrupt and Resume Model

A core architectural reason for using LangGraph is support for durable interruption and resumption.

### 13.1 Interrupt-worthy conditions

The orchestration layer should support explicit interrupt states for cases such as:

- classification ambiguity,
- review of extracted actions,
- draft approval,
- unresolved clarification need,
- channel-to-web handoff,
- and operator confirmation for non-trivial memory mutation.

**Stable architecture anchor:** `ARCH:InterruptAndResumeModel`

### 13.2 Required persisted interrupt context

When a graph interrupts, the system should persist at minimum:

- workflow identifier,
- graph type,
- pending decision type,
- source artifact references,
- candidate outputs,
- rationale summary,
- and the continuation path to resume.

**Stable architecture anchor:** `ARCH:InterruptPersistenceContract`

### 13.3 Resume behavior

When resumed, the graph should:

- rehydrate necessary state,
- validate that upstream artifacts remain current enough,
- apply the operator’s decision,
- and continue from the correct downstream node rather than replaying the entire flow blindly.

**Stable architecture anchor:** `ARCH:ResumeBehavior`

---

## 14. Orchestration and Domain Boundaries

The orchestration layer must preserve the boundary between:

- source records,
- interpreted candidate records,
- accepted memory state,
- and user-facing generated artifacts.

Graphs may generate proposals, but proposals should not automatically become accepted operational memory without passing the relevant rules and review gates.

This is especially important for:

- extracted actions,
- project classification,
- stakeholder identity matching,
- work breakdown refinement,
- and Telegram/voice-captured updates.

**Stable architecture anchor:** `ARCH:OrchestrationDomainBoundary`

---

## 15. Failure and Recovery Posture

The orchestration architecture should be designed to fail visibly and recover safely.

### 15.1 Failure classes

Relevant orchestration failure classes include:

- connector payload issues,
- incomplete source context,
- low-confidence interpretation,
- persistence failure,
- session-state mismatch,
- and external channel delivery failure.

### 15.2 Failure posture

Where possible, the graph should:

- preserve the source artifact,
- preserve partial interpretive artifacts if still diagnostically useful,
- record enough state for retry or manual follow-up,
- and avoid silently dropping meaningful work.

**Stable architecture anchor:** `ARCH:OrchestrationFailureRecovery`

---

## 16. Relationship to Verification

The orchestration model will require strong verification across:

- graph routing,
- interrupt/resume correctness,
- review-gate behavior,
- domain artifact production,
- provenance preservation,
- and channel-specific continuity.

The testing strategy and verification model should therefore explicitly include:

- graph happy paths,
- graph ambiguity/review paths,
- channel handoff paths,
- and persistence of resumable state.

**Stable architecture anchor:** `ARCH:GraphVerificationStrategy`

---

## 17. Final Note

The LangGraph orchestration layer is the execution spine of Glimmer.

Its job is not to be clever in the abstract. Its job is to:

- move work through the right bounded workflows,
- preserve context and provenance,
- surface ambiguity honestly,
- respect review boundaries,
- and make Glimmer feel consistent and dependable across projects, accounts, and channels.

If later implementation drifts toward one giant opaque agent loop, or collapses reviewable workflows into hidden prompts with no durable state, this document should be treated as the corrective architecture reference.

**Stable architecture anchor:** `ARCH:LangGraphConclusion`

