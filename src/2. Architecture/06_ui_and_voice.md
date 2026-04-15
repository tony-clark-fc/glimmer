# Glimmer — UI and Voice

## Document Metadata

- **Document Title:** Glimmer — UI and Voice
- **Document Type:** Split Architecture Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `ARCHITECTURE.md`
- **Primary Companion Documents:** Requirements, System Overview, Domain Model, LangGraph Orchestration, Connectors and Ingestion

---

## 1. Purpose

This document defines the user-facing interaction architecture for **Glimmer**.

It covers:

- primary UI surfaces,
- interaction patterns,
- draft workspace behavior,
- portfolio and project views,
- triage presentation,
- visual persona rendering and selection,
- voice interaction architecture,
- and the Telegram companion user experience boundary.

This document does not define connector internals, OAuth/token handling, or persistence implementation details. Its role is to define how Glimmer is experienced by the operator and how the interaction surfaces align with the review-first, local-first, multi-account architecture.

**Stable architecture anchor:** `ARCH:UiSurfaceMap`

---

## 2. UI and Voice Design Intent

Glimmer’s interaction model must feel like a sharp, tactful, highly organized chief-of-staff rather than a generic chatbot.

The UI and voice layer should therefore optimize for:

- clarity over clutter,
- context over raw volume,
- preparation over passive reminders,
- reviewability over hidden automation,
- and continuity across web, voice, and Telegram.

The interface should make Glimmer feel proactive, composed, and trustworthy, while always keeping the operator in control of externally meaningful decisions.

**Stable architecture anchor:** `ARCH:UiVoiceIntent`

---

## 3. Interaction Principles

### 3.1 Workspace-first, not chat-only

The primary interaction model shall be a structured workspace with targeted conversational support, not an unbounded chat canvas pretending to be a project system.

**Stable architecture anchor:** `ARCH:UiPrinciple.WorkspaceFirst`

### 3.2 Reviewable outputs

Important outputs such as classifications, extracted actions, and drafts must be visible as reviewable artifacts, not buried inside transient conversation turns.

**Stable architecture anchor:** `ARCH:UiPrinciple.ReviewableOutputs`

### 3.3 Context before action

Where Glimmer asks the operator to act, the interface should surface enough relevant context to support fast, confident judgment.

**Stable architecture anchor:** `ARCH:UiPrinciple.ContextBeforeAction`
**Stable architecture anchor:** `ARCH:ContextBeforeAction`

### 3.4 Consistent persona, bounded theatrics

The visual and voice expression of Glimmer should reinforce clarity, tact, and engagement without becoming distracting, overly animated, or gimmicky.

**Stable architecture anchor:** `ARCH:UiPrinciple.BoundedPersona`

### 3.5 Multi-surface continuity

The operator should be able to move between web workspace, voice interaction, and Telegram companion flows without feeling that they are talking to different systems.

**Stable architecture anchor:** `ARCH:UiPrinciple.MultiSurfaceContinuity`

### 3.6 Mobile channels are a convenience layer, not the control center

Telegram should provide meaningful companion access, but the full control surface remains the main web application.

**Stable architecture anchor:** `ARCH:UiPrinciple.CompanionNotPrimary`

---

## 4. Primary UI Surface Map

The Glimmer web application should include five primary surfaces.

### 4.1 Today view

The Today view is the primary daily operating surface.

It should present:

- top priorities across projects,
- near-term obligations,
- waiting-on items,
- stale or blocked items,
- and suggested reply/action pressure.

The Today view is where Glimmer’s "what matters now" capability becomes most visible.

**Stable architecture anchor:** `ARCH:TodayViewArchitecture`

### 4.2 Portfolio view

The Portfolio view presents all active projects in comparative form.

It should allow the operator to see:

- project status,
- urgency ranking,
- progress signals,
- current blockers,
- and attention demand across the portfolio.

**Stable architecture anchor:** `ARCH:PortfolioViewArchitecture`

### 4.3 Project workspace view

The Project workspace is the detailed operating surface for one project.

It should present:

- project summary,
- workstreams,
- milestones,
- risks,
- decisions,
- stakeholders,
- recent messages,
- next actions,
- and related drafts or briefings.

**Stable architecture anchor:** `ARCH:ProjectWorkspaceArchitecture`

### 4.4 Triage view

The Triage view is the primary surface for newly ingested signals and review-needed interpretation.

It should present:

- incoming messages and imported signals,
- proposed project classifications,
- extracted actions and deadlines,
- ambiguity/review flags,
- and quick actions to accept, amend, defer, or draft.

**Stable architecture anchor:** `ARCH:TriageViewArchitecture`

### 4.5 Draft workspace view

The Draft workspace is the review surface for outgoing draft responses.

It should present:

- linked source context,
- linked project and stakeholder context,
- one or more draft variants,
- tone posture,
- rationale,
- and copy-friendly output.

This surface must support fast revision and decision-making without encouraging silent sending.

**Stable architecture anchor:** `ARCH:DraftWorkspaceArchitecture`

### 4.6 Persona page

The Persona page is the primary conversational interface between the operator and Glimmer. It combines a real-time chat interface, a dynamic visual project mind-map, and a staged persistence model that protects the operational database from unreviewed mutation.

Unlike the other primary surfaces, which are structured data views, the Persona page is a conversational workspace where the operator explains, discusses, and iteratively builds project understanding with Glimmer's help.

**Stable architecture anchor:** `ARCH:UxSurface.PersonaPage`

---

## 5. Secondary UI Surfaces

### 5.1 Stakeholder context surface

A stakeholder-focused view should be available to show:

- who the stakeholder is,
- which projects they touch,
- recent interactions,
- open requests,
- and communication context that may influence drafting or prioritization.

**Stable architecture anchor:** `ARCH:StakeholderSurfaceArchitecture`

### 5.2 Briefing surface

A briefing-oriented presentation mode should support:

- meeting preparation,
- daily or weekly briefings,
- quick context summaries,
- and review of the most relevant recent changes.

**Stable architecture anchor:** `ARCH:BriefingSurfaceArchitecture`
**Stable architecture anchor:** `ARCH:PreparedBriefings`

### 5.3 Review queue surface

A generalized review queue may be used to collect:

- ambiguous classifications,
- extracted actions awaiting acceptance,
- memory updates needing approval,
- research results awaiting review,
- and other review-gated artifacts.

**Stable architecture anchor:** `ARCH:ReviewQueueArchitecture`

### 5.4 Research run surface

Research run visibility should be available to show:

- active and completed research runs,
- research summaries and findings,
- source references consulted,
- provenance linkage to triggering context (project, message, workflow),
- and review controls for accepting or discarding research results.

Research runs may appear as inline context within project or triage views, or as a dedicated lightweight surface. The architecture should not hide research activity from the operator.

**Stable architecture anchor:** `ARCH:ResearchRunSurface`

---

## 6. Today View Design

The Today view should not be a generic task list. It should behave like a chief-of-staff morning brief.

### 6.1 Core content

The Today view should include:

- top 3–5 recommended actions,
- a short explanation of why they matter,
- looming deadlines,
- calendar pressure,
- reply debt,
- waiting-on items,
- and any notable portfolio risk signal.

### 6.2 Presentation posture

The presentation should be concise and prioritization-forward.

The operator should be able to quickly answer:

- what matters now,
- what can wait,
- what needs a reply,
- and what is blocked on someone else.

**Stable architecture anchor:** `ARCH:TodayViewDesign`

---

## 7. Project Workspace Design

The Project workspace should function as the authoritative operational room for one project.

### 7.1 Core sections

Suggested sections include:

- summary
- workstreams
- milestones
- decisions
- risks and blockers
- stakeholders
- recent signals
- next actions
- linked drafts and briefings

### 7.2 Workspace posture

The workspace should prefer synthesis and relevance over raw historical dumping.

The operator should be able to orient quickly without reading through long chronological feeds.

**Stable architecture anchor:** `ARCH:ProjectWorkspaceDesign`

---

## 8. Triage View Design

The Triage view is where Glimmer’s message understanding becomes visible and contestable.

### 8.1 Core triage card contents

Each triage item should be capable of showing:

- source account/channel,
- sender and participants,
- message summary,
- proposed project match,
- confidence or ambiguity signal,
- extracted actions/deadlines/decisions,
- and recommended next handling step.

### 8.2 Triage actions

The operator should be able to:

- accept classification,
- reassign project,
- accept or amend extracted action,
- create a draft request,
- mark informational only,
- or defer review.

### 8.3 Multi-account visibility

Because Glimmer supports multiple connected accounts, the Triage view must preserve visible source provenance and support filtering by source account/profile.

**Stable architecture anchor:** `ARCH:TriageViewDesign`

---

## 9. Draft Workspace Design

### 9.1 Workspace purpose

The Draft workspace is where Glimmer’s communication support is made operational without giving the system direct sending authority.

### 9.2 Required visible context

The Draft workspace should visibly tie each draft to:

- the originating message or signal,
- the linked project,
- key stakeholder context,
- and the chosen tone posture.

### 9.3 Variants and editing

The workspace should support:

- multiple draft variants,
- operator editing,
- regeneration or reformulation,
- concise and fuller versions,
- firmer or warmer reformulations,
- and copy/mark-used actions.

### 9.4 Anti-pattern to avoid

The drafting workspace should not feel like an opaque "AI answer box." It should behave like a review surface for communication decisions.

**Stable architecture anchor:** `ARCH:DraftWorkspaceDesign`

---

## 9A. Persona Page Architecture

The Persona page is the most immersive Glimmer interaction surface. It brings together conversational AI, visual project mapping, and staged persistence into a single coherent workspace.

### 9A.1 Conversation model

The Persona page hosts a real-time conversational chat interface where the operator can:

- discuss priorities, explain new projects, give instructions, or request updates,
- paste in unstructured content (briefs, emails, meeting notes) for entity extraction,
- and iteratively refine Glimmer's understanding through natural dialogue.

Conversations on the Persona page are operator-initiated sessions. Each session has a lifecycle:

- **active** — the operator and Glimmer are interacting; the mind-map is being constructed,
- **paused** — the operator has navigated away without confirming; session state is preserved for resumption,
- **confirmed** — the operator has committed the working state to the database,
- **abandoned** — the session expired or was explicitly discarded without confirmation.

Persona-page conversations shall route through the same orchestration core used by all other Glimmer surfaces. The conversation model is a UX layer over the shared LangGraph orchestration, not a separate intelligence silo.

**Stable architecture anchor:** `ARCH:PersonaPage.ConversationModel`

### 9A.2 Mind-map visualization architecture

The Persona page shall render a dynamic, interactive mind-map visualization that grows as the conversation progresses.

#### Library choice

The mind-map shall be implemented using **React Flow** as the primary visualization library. React Flow provides:

- node and edge rendering with custom node types,
- built-in zoom, pan, and minimap controls,
- layout support via integration with layout algorithms (e.g., dagre, elkjs),
- a composable React component model consistent with the Next.js frontend baseline,
- and an active ecosystem with strong TypeScript support.

#### Visual semantics

The mind-map shall use semantically meaningful visual encoding:

- **distinct node types** for projects, stakeholders, milestones, risks, blockers, work items, decisions, and dependencies,
- **connection edges** showing relational links (e.g., stakeholder-to-project, risk-to-milestone),
- **visual state indicators** distinguishing working (unconfirmed) nodes from persisted nodes (e.g., dashed borders for working state, solid borders for confirmed),
- and **progressive disclosure** as new nodes are created during conversation (animated entry, radial fan-out from parent nodes).

#### Canvas behavior

The mind-map canvas shall support:

- zoom and pan for large or complex project maps,
- click-to-select for node detail inspection,
- hover-triggered contextual "Ask Glimmer" interaction on any node,
- optional operator-initiated node rearrangement,
- and a minimap for orientation within large maps.

**Stable architecture anchor:** `ARCH:PersonaPage.MindMapArchitecture`

### 9A.3 Staged persistence model

All entities extracted or created during a Persona page conversation shall follow a staged persistence model:

1. **Working state** — candidate nodes, edges, and extracted entities are held in client-side or lightweight session state. They are not written to the operational database.
2. **Operator review** — the operator can inspect, edit, remove, or request corrections for any working-state entity.
3. **Confirm & Save** — a single explicit operator action commits the entire accepted working state to the operational database as a coordinated batch.
4. **Discard / Abandon** — the operator may discard the working state entirely, or navigating away without confirming triggers a preservation-or-warning flow.

This staged model is architecturally load-bearing. It enforces the separation between interpreted candidate state and accepted operational memory that the domain model requires (`ARCH:StateOwnershipBoundaries`).

The working state shall be managed as follows:

- **Client-side primary store:** the working mind-map state (candidate nodes, edges, entity metadata) lives in React component state or a lightweight client store during the session.
- **Session backup:** if the operator pauses or navigates away, the working state may be serialized to a backend session store (keyed by persona-page session ID) to allow resumption.
- **Batch persistence on confirm:** on "Confirm & Save," the frontend sends the full accepted working state to a backend staged-persistence endpoint, which persists all accepted entities (projects, stakeholders, milestones, work items, risks, blockers, relationships) in a single coordinated database transaction.

**Stable architecture anchor:** `ARCH:PersonaPage.StagedPersistence`

### 9A.4 Paste-in ingestion pipeline

The Persona page shall support operator-initiated paste-in of unstructured content at any point during a conversation.

The paste-in pipeline follows these stages:

1. **Capture** — the operator pastes text into the chat interface or a dedicated paste area.
2. **Raw artifact preservation** — the pasted content is preserved as a `PasteInSourceArtifact` domain record with timestamp and session linkage, before any interpretation begins.
3. **Entity extraction** — Glimmer analyzes the pasted content through the orchestration core and extracts candidate entities (stakeholders, milestones, objectives, deadlines, risks, blockers, dependencies, work items).
4. **Working-state integration** — extracted entities appear as new candidate nodes on the mind-map in the temporary working state.
5. **Conversational explanation** — Glimmer explains what was extracted and why in the chat stream.
6. **Operator review** — the operator can accept, edit, or discard individual extracted entities within the working state.

Paste-in ingestion shall not bypass the staged persistence model. All extracted entities enter the working state and require explicit operator confirmation before database persistence.

**Stable architecture anchor:** `ARCH:PersonaPage.PasteInPipeline`

### 9A.5 Relationship to the orchestration core

Persona-page conversations are a UX surface layered onto the shared orchestration core, not a separate reasoning system.

- Chat messages from the operator enter the orchestration layer as conversational inputs with persona-page session context.
- Entity extraction (from conversation or paste-in) uses the same extraction services available to triage and other workflows.
- The orchestration core routes persona-page requests through the same LangGraph topology, with interrupt/resume support for review-gated outputs.
- Persona-page sessions are linked to the `ChannelSession` model as a web-channel session subtype.

This ensures that knowledge, context, and behavioral consistency are shared across all Glimmer surfaces rather than being siloed in the persona page.

**Stable architecture anchor:** `ARCH:PersonaPage.OrchestrationRelationship`

---

## 10. Visual Persona Architecture

### 10.1 Persona role in the UX

Glimmer’s persona images are part of the assistant experience layer and reinforce interaction mode, tone, and engagement.

They should not override functional clarity, but they should make Glimmer feel present and mode-aware.

**Stable architecture anchor:** `ARCH:VisualPersonaSelection`
**Stable architecture anchor:** `ARCH:VisualPersonaArchitecture`

### 10.2 Persona rendering surfaces

Persona rendering may appear in:

- Today view,
- briefing views,
- draft workspace,
- voice console,
- and other assistant-centric surfaces where a visible Glimmer presence adds clarity or tone support.

### 10.3 Persona selection logic

Persona selection should be driven by:

- approved `PersonaAsset` records,
- explicit `PersonaClassification` labels,
- interaction mode,
- tone or mood category,
- and fallback rules.

The system should never rely on ad hoc image generation for live persona display.

### 10.4 Fallback behavior

If no specific match exists, the UI shall fall back to a default approved Glimmer persona asset.

**Stable architecture anchor:** `ARCH:VisualPersonaRenderingRules`

---

## 11. Voice Interaction Architecture

### 11.1 Voice interaction role

Voice interaction should make Glimmer feel easier to use when the operator is moving, thinking aloud, or doing rapid planning.

It is not a separate product mode with separate business logic. It is a voice-shaped entrypoint into the same project-memory and orchestration system.

**Stable architecture anchor:** `ARCH:VoiceInteractionArchitecture`
**Stable architecture anchor:** `ARCH:VoiceLayeringStrategy`

### 11.2 Voice console surface

The web voice console should provide:

- current conversation transcript,
- recent assistant utterances,
- live speaking/listening state,
- extracted actions or project updates,
- and clear transition into the rest of the system when review is needed.

### 11.3 Voice-specific UX expectations

The voice experience should:

- feel conversational,
- support interruption and continuation,
- keep short-horizon context,
- and avoid making the operator repeat known context within a live session.

### 11.4 Voice-to-structure pathway

Voice interactions should be able to create or trigger:

- briefings,
- imported signals,
- extracted actions,
- planner refresh requests,
- and draft requests.

These should appear in the same reviewable system surfaces used by non-voice workflows.

**Stable architecture anchor:** `ARCH:VoiceToStructuredOutputPath`

### 11.5 Voice infrastructure direction

The voice pipeline has two structurally different implementation paths, and Glimmer's target hardware profile supports both.

#### Pipeline architecture (ASR → reasoning model → TTS)

In this approach, voice recognition and voice generation are handled by separate specialized components:

1. **Recognition (operator → Glimmer):** A dedicated ASR model (e.g., Whisper or equivalent) transcribes the operator's speech into text.
2. **Reasoning:** The transcribed text enters the same orchestration and reasoning layer used by text-based interactions (using a high-capability model such as Gemma 4 31B or 26B A4B).
3. **Generation (Glimmer → operator):** A dedicated TTS engine converts the model's text response into spoken output.

This approach maximizes reasoning quality and allows the strongest available model to handle all substantive work. The voice layer is purely an I/O bridge.

#### Native audio architecture (speech-to-speech)

In this approach, a model with a native audio encoder processes the operator's speech waveform directly, without a separate ASR step:

1. **Recognition:** The model receives raw audio and can interpret not only words but also tone, prosody, emotion, and urgency.
2. **Reasoning and generation:** The model produces a response that may include direct audio output.

This approach trades peak reasoning depth for richer input signal. A native-audio model (such as Gemma 4 E4B) can detect whether the operator sounds frustrated, rushed, or relaxed — context that a text transcript strips away.

#### Glimmer's expected voice architecture

The target approach is a **hybrid multi-model voice architecture**:

- **Voice session I/O** uses a native-audio-capable model (E4B class) running locally for low-latency, prosody-aware conversational interaction.
- **Heavy reasoning tasks** triggered during a voice session (triage decisions, draft generation, prioritization analysis) are routed to the larger local model (31B or 26B class) through the same orchestration core used by text interactions.
- **TTS for the output side** may use either the native audio model's output, a dedicated local TTS engine, or Apple system speech — depending on quality and persona-fit assessment during Workstream F implementation.

This hybrid approach means that voice sessions benefit from emotional and tonal awareness at the interaction boundary while preserving full reasoning depth for substantive work. It also means the voice layer remains a **mode layered on the shared core**, not a separate intelligence silo.

The specific model versions, quantization levels, and pipeline routing will be confirmed during Workstream F implementation, but the multi-model local inference direction is the approved starting point.

**Stable architecture anchor:** `ARCH:VoiceInfrastructureDirection`
**Stable architecture anchor:** `ARCH:VoicePipelineArchitecture`

---

## 12. Telegram Companion UX

### 12.1 Telegram UX role

Telegram is the MVP mobile companion channel for Glimmer.

Its purpose is to let the operator remain in contact with Glimmer when away from the main workspace, without pretending that Telegram is the full application.

**Stable architecture anchor:** `ARCH:TelegramCompanionUx`
**Stable architecture anchor:** `ARCH:TelegramCompanionChannel`

### 12.2 Appropriate Telegram interactions

Telegram should support:

- asking what matters most now,
- asking for a project summary,
- capturing a note or action,
- requesting a concise briefing,
- and continuing a lightweight conversational interaction.

### 12.3 Inappropriate Telegram use

Telegram should not be the main surface for:

- deep triage review,
- complex project restructuring,
- rich draft comparison,
- or opaque approval of significant memory mutations.

Where richer review is needed, Telegram should hand the operator back to the web workspace.

### 12.4 Telegram response style

Telegram responses should be more concise than the web workspace, but still consistent with Glimmer’s voice and review posture.

**Stable architecture anchor:** `ARCH:TelegramCompanionInteractionStyle`

---

## 13. Multi-Account UX Considerations

### 13.1 Provenance visibility

Where messages, events, or triage items are shown, the UI must make source provenance visible enough for the operator to understand which account or profile an item came from.

**Stable architecture anchor:** `ARCH:MultiAccountUxProvenance`

### 13.2 Filtering and grouping

The UI should support account-aware filtering and grouping where it materially helps the operator interpret workload and triage.

### 13.3 Avoiding source flattening

The UI must not flatten multiple connected accounts into a single undifferentiated inbox if that would remove meaning needed for decision-making.

**Stable architecture anchor:** `ARCH:MultiAccountUxBoundaries`

---

## 14. Review and Approval UX

### 14.1 Review-first interaction model

The UX should make it clear when Glimmer is:

- suggesting,
- interpreting,
- asking for confirmation,
- or waiting on a human decision.

**Stable architecture anchor:** `ARCH:ReviewGateUx`

### 14.2 Reviewable artifact presentation

Reviewable artifacts should be presented with:

- the proposed result,
- enough context to judge it,
- any confidence/ambiguity signal where relevant,
- and clear actions such as accept, amend, reject, or defer.

### 14.3 Avoiding accidental commitment

The UX should not make it easy to accidentally mistake a generated suggestion for an already accepted fact.

**Stable architecture anchor:** `ARCH:ReviewArtifactPresentation`

---

## 14A. Contextual "Ask Glimmer" Interaction Architecture

### 14A.1 Cross-surface interaction affordance

Every significant data element across all workspace pages shall provide a lightweight mechanism for the operator to invoke Glimmer's intelligence directly on that element.

This includes, but is not limited to:

- project cards,
- action items,
- draft variants,
- classifications,
- risks, blockers, and waiting-on records,
- stakeholder entries,
- and briefing artifacts.

The affordance shall appear as a hover-triggered or click-triggered icon (e.g., sparkle ✦) that opens a compact popover or panel anchored to the element. The popover shall include:

- a Glimmer avatar for persona presence,
- a single-line text input allowing the operator to ask a question or give an instruction related to the specific element,
- and contextual routing of the request to the appropriate orchestration flow with the element's data as input context.

### 14A.2 Routing and orchestration

Contextual "Ask Glimmer" requests shall be routed through the same orchestration core used by all other Glimmer interaction surfaces. The element type and context shall be passed as input metadata so that the orchestration layer can provide relevant, context-aware responses.

### 14A.3 Review-gate compliance

Responses from the contextual interaction shall follow the same review-gate and approval rules as any other Glimmer output. If the operator's request implies an externally meaningful action (e.g., "draft a follow-up to this person"), the result must enter the standard review flow rather than being applied immediately.

### 14A.4 Consistency

The "Ask Glimmer" interaction pattern shall be visually and behaviorally consistent across all workspace pages. It is a shared UX component, not a per-page reimplementation.

**Stable architecture anchor:** `ARCH:ContextualAskGlimmerInteraction`

---

## 15. Cross-Surface Continuity

### 15.1 Shared session continuity

The interaction architecture should preserve continuity across:

- web workspace sessions,
- voice conversations,
- and Telegram companion interactions.

This continuity does not require perfect conversational memory everywhere. It does require that Glimmer can maintain enough context that the operator does not feel they are constantly restarting.

**Stable architecture anchor:** `ARCH:CrossSurfaceContinuity`

### 15.2 Channel handoff behavior

When a flow must move from one channel to another, the system should preserve:

- relevant context,
- pending review state,
- and a clear sense of what the operator needs to do next.

Examples include:

- Telegram to web for draft review,
- voice to triage view for extracted action confirmation,
- briefing to project workspace for deeper planning.

**Stable architecture anchor:** `ARCH:ChannelHandoffUx`

---

## 16. Accessibility and Clarity Expectations

The UI should favor:

- readable hierarchy,
- strong contrast and legibility,
- concise summaries,
- and low-friction navigation between major surfaces.

The assistant persona layer should not reduce accessibility, obscure content, or complicate essential workflows.

**Stable architecture anchor:** `ARCH:UiAccessibilityAndClarity`

---

## 17. Relationship to the Rest of the Architecture Set

This document defines Glimmer’s interaction architecture, but it does not define:

- connector-specific behavior,
- persistence strategy,
- detailed security controls,
- or test-pack structure.

Those concerns are handled in:

- `04_connectors_and_ingestion.md`
- `05_memory_and_retrieval.md`
- `07_security_and_permissions.md`
- `08_testing_strategy.md` (housed under `4. Verification/`)

**Stable architecture anchor:** `ARCH:UiVoiceDocumentBoundary`

---

## 18. Final Note

Glimmer’s user experience should make the system feel like a capable, tactful, high-context chief-of-staff rather than a raw AI console.

That means the surfaces must do three things well:

- show the operator what matters,
- preserve enough context for confident judgment,
- and keep Glimmer’s persona present without overwhelming the work.

If later implementation drifts toward generic chat-first UX, hidden side effects, or Telegram becoming a poor substitute for the real workspace, this document should be treated as the corrective reference.

**Stable architecture anchor:** `ARCH:UiVoiceConclusion`
