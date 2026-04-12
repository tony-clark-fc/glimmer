# Glimmer — Workstream F: Voice

## Document Metadata

- **Document Title:** Glimmer — Workstream F: Voice
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Build Strategy and Scope, Testing Strategy, Workstream D Triage and Prioritization, Workstream E Drafting UI

---

## 1. Purpose

This document defines the implementation strategy for **Workstream F — Voice**.

Its purpose is to implement Glimmer’s voice interaction layer as a bounded, reviewable, continuity-preserving extension of the core system rather than as a separate assistant product.

This workstream is where Glimmer becomes conversationally usable for briefings, updates, note capture, and planning while remaining anchored to the same project memory, orchestration, and approval model as the rest of the product.

**Stable plan anchor:** `PLAN:WorkstreamF.Voice`

---

## 2. Workstream Objective

Workstream F exists to implement Glimmer’s voice session capability, including:

- voice session initiation and lifecycle handling,
- transcript ingestion,
- session continuity,
- spoken briefing and update flows,
- conversion of spoken content into structured internal artifacts,
- routing from voice into planner, triage, and drafting flows where appropriate,
- and voice-aware UI support through the main web workspace.

At the end of this workstream, Glimmer should support useful spoken interaction without weakening the product’s local-first, review-first, structured-memory operating model.

**Stable plan anchor:** `PLAN:WorkstreamF.Objective`

---

## 3. Why This Workstream Comes After the Core Web Workspace

The strategy and architecture are explicit that voice is important, but it must be layered onto a strong non-voice core rather than treated as the primary product shape. The build sequencing therefore places voice after:

- runtime and memory foundation,
- external-boundary ingestion,
- triage and prioritization,
- and the main web control surface.

That sequencing matters because voice needs somewhere reliable to put its outputs.

A voice interface without:

- structured memory,
- reviewable triage artifacts,
- a real draft workspace,
- project and stakeholder context,
- and a canonical web review surface,

would quickly collapse into ephemeral conversation with weak auditability.

This workstream therefore extends the core. It does not replace it.

**Stable plan anchor:** `PLAN:WorkstreamF.Rationale`

---

## 4. Related Requirements Anchors

This workstream directly supports the following requirements:

- `REQ:VoiceInteraction`
- `REQ:PreparedBriefings`
- `REQ:ActionDeadlineDecisionExtraction`
- `REQ:ProjectMemory`
- `REQ:WorkBreakdownSupport`
- `REQ:HumanApprovalBoundaries`
- `REQ:StateContinuity`
- `REQ:Explainability`

These requirements make voice more than an audio wrapper. Voice must preserve continuity, support real briefings and updates, and convert spoken content into structured, reviewable outputs.

**Stable plan anchor:** `PLAN:WorkstreamF.RequirementsAlignment`

---

## 5. Related Architecture Anchors

This workstream is primarily implementing the architecture described by:

- `ARCH:VoiceLayeringStrategy`
- `ARCH:VoiceInteractionArchitecture`
- `ARCH:VoiceSessionGraph`
- `ARCH:VoiceSessionContinuity`
- `ARCH:VoiceToStructuredOutputPath`
- `ARCH:CrossSurfaceContinuity`
- `ARCH:ChannelHandoffUx`
- `ARCH:ReviewGateArchitecture`
- `ARCH:GraphVerificationStrategy`

These anchors define voice as a mode layered on the same orchestration and memory core, require session continuity, and establish that significant downstream actions still respect the same review and approval boundaries as other interaction modes.

**Stable plan anchor:** `PLAN:WorkstreamF.ArchitectureAlignment`

---

## 6. Workstream Scope

### 6.1 In scope

This workstream includes:

- voice-session lifecycle handling,
- transcript or utterance ingestion,
- short-horizon conversational continuity,
- spoken briefing generation,
- spoken capture of project updates and actions,
- routing from voice into internal triage/planner/drafting flows,
- voice-session summary artifacts,
- and web-workspace voice-console support.

**Stable plan anchor:** `PLAN:WorkstreamF.InScope`

### 6.2 Out of scope

This workstream does **not** include:

- broad unmanaged desktop control by voice,
- autonomous external action-taking via voice,
- voice as a substitute for the web review surface,
- or speculative multimodal theatrics that do not materially support project coordination.

This workstream focuses on useful, bounded spoken interaction within Glimmer’s existing product model.

**Stable plan anchor:** `PLAN:WorkstreamF.OutOfScope`

---

## 7. Implementation Outcome Expected from This Workstream

By the end of Workstream F, Glimmer should be able to do the following in a structurally real way:

- support a live or near-live voice session through the main application,
- ingest transcript segments or utterances into voice-session state,
- maintain short-horizon spoken context during a session,
- provide spoken briefings and interactive planning responses,
- convert spoken updates into structured internal artifacts such as imported signals or candidate actions,
- route voice-derived work into triage, planner, or drafting flows,
- preserve voice-session summaries and continuity across handoffs where appropriate,
- and redirect the operator into the web workspace when richer review is required.

At that point, Glimmer’s voice capability becomes a real companion operating mode rather than a disconnected demo surface.

**Stable plan anchor:** `PLAN:WorkstreamF.ExpectedOutcome`

---

## 8. Voice Implementation Packages

## 8.1 Work Package F1 — Voice infrastructure boundary and session bootstrap

**Objective:** Establish the integration boundary and lifecycle shape for voice sessions.

### In scope
- voice-layer adapter boundary
- session start/stop/init semantics
- voice-session identity and operator binding
- initial connection to the application/orchestration layer
- bounded integration with LiveKit Agents or equivalent voice infrastructure

### Expected outputs
- voice boundary abstraction
- session bootstrap flow
- tests for session initialization and operator/session binding where feasible

### Related anchors
- `ARCH:VoiceLayeringStrategy`
- `ARCH:VoiceInteractionArchitecture`
- `ARCH:SecurityBoundaryMap`

### Definition of done
- the codebase has a clear, bounded entrypoint for voice sessions that does not entangle raw voice infrastructure with the whole application

**Stable plan anchor:** `PLAN:WorkstreamF.PackageF1.VoiceBoundaryAndBootstrap`

---

## 8.2 Work Package F2 — Voice session state and continuity core

**Objective:** Make voice sessions durable enough to preserve short-horizon context.

### In scope
- `VoiceSessionState` operational use
- session context loading and update behavior
- recent-topic and unresolved-prompt continuity
- continuity across one active voice interaction session

### Expected outputs
- session-state handling logic
- persistence/update support for voice-session continuity
- tests for session continuity and state recovery behavior

### Related anchors
- `ARCH:VoiceSessionStateModel`
- `ARCH:VoiceSessionContinuity`
- `ARCH:GraphState.ContinuationMetadata`

### Definition of done
- voice interaction no longer behaves like isolated one-shot utterances; it has real short-horizon continuity

**Stable plan anchor:** `PLAN:WorkstreamF.PackageF2.VoiceSessionContinuityCore`

---

## 8.3 Work Package F3 — Transcript ingestion and normalization

**Objective:** Convert spoken interaction into normalized internal source material.

### In scope
- transcript/utterance receipt
- normalization into `ImportedSignal` or equivalent voice-derived artifacts
- source typing for voice-origin content
- provenance and timestamp preservation for voice-derived records

### Expected outputs
- transcript ingestion path
- normalization logic for voice-origin source artifacts
- tests for transcript-to-source-record conversion

### Related anchors
- `ARCH:VoiceSessionGraph`
- `ARCH:ImportedSignalModel`
- `ARCH:NormalizationOutputBoundary`

### Definition of done
- spoken content can be turned into structured internal input rather than remaining trapped in ephemeral voice-session state

**Stable plan anchor:** `PLAN:WorkstreamF.PackageF3.TranscriptIngestion`

---

## 8.4 Work Package F4 — Spoken briefing and interactive response flows

**Objective:** Implement spoken responses that make Glimmer useful during planning and preparation.

### In scope
- spoken briefing generation from project and focus artifacts
- conversational spoken responses for project status, priorities, and next steps
- voice response composition aligned to Glimmer’s tone and brevity expectations for speech

### Expected outputs
- briefing/response logic for voice sessions
- reusable formatter/composition layer for spoken outputs
- tests for key response-shape scenarios where deterministic enough

### Related anchors
- `ARCH:OperatingMode.Voice`
- `ARCH:BriefingSurfaceArchitecture`
- `ARCH:PreparedBriefings`

### Definition of done
- the operator can receive a meaningful spoken briefing or planning response instead of merely dictating text into the system

**Stable plan anchor:** `PLAN:WorkstreamF.PackageF4.SpokenBriefingFlows`

---

## 8.5 Work Package F5 — Voice-to-structured-output routing

**Objective:** Route spoken content into the same core internal flows used by the rest of Glimmer.

### In scope
- routing spoken updates into triage/planner/drafting entrypoints where appropriate
- conversion of spoken intent into imported signals, candidate actions, or draft requests
- alignment with shared orchestration flows instead of bespoke voice-only logic

### Expected outputs
- routing logic from voice session into shared internal workflows
- tests for correct downstream routing based on spoken intent category

### Related anchors
- `ARCH:VoiceToStructuredOutputPath`
- `ARCH:OrchestrationPrinciple.SharedCoreFlows`
- `ARCH:IntakeGraphRouting`

### Definition of done
- voice becomes a meaningful input mode to the same assistant core rather than a disconnected experience path

**Stable plan anchor:** `PLAN:WorkstreamF.PackageF5.VoiceToStructuredRouting`

---

## 8.6 Work Package F6 — Review-safe handling of voice-derived actions and interpretations

**Objective:** Preserve approval boundaries when spoken input generates meaningful downstream consequences.

### In scope
- review gating for voice-derived candidate actions, classifications, and draft requests
- handoff from voice into reviewable UI states when richer review is required
- explicit non-silent handling of ambiguity in spoken interpretation

### Expected outputs
- review-safe orchestration branch behavior for voice-origin artifacts
- tests for ambiguity and review-gate enforcement in voice flows

### Related anchors
- `ARCH:VoiceSessionReviewBoundary`
- `ARCH:ReviewGateArchitecture`
- `ARCH:CrossChannelReviewParity`

### Definition of done
- voice input cannot bypass the same review rules that protect the rest of the system

**Stable plan anchor:** `PLAN:WorkstreamF.PackageF6.ReviewSafeVoiceHandling`

---

## 8.7 Work Package F7 — Voice console in the web workspace

**Objective:** Expose voice interaction through the primary Glimmer control surface.

### In scope
- voice console UI in the web workspace
- display of live speaking/listening state
- transcript view or recent utterance display
- extracted-action or update visibility where useful
- transitions into review and related surfaces

### Expected outputs
- voice-console UI surface
- UI wiring to session state and relevant voice outputs
- Playwright-supportive structure where feasible

### Related anchors
- `ARCH:VoiceInteractionArchitecture`
- `ARCH:UiSurfaceMap`
- `ARCH:CrossSurfaceContinuity`

### Definition of done
- voice is present as a real workspace mode within the application instead of an external orphaned component

**Stable plan anchor:** `PLAN:WorkstreamF.PackageF7.VoiceConsole`

---

## 8.8 Work Package F8 — Voice session summaries and handoff support

**Objective:** Preserve useful continuity after a voice interaction ends or hands off.

### In scope
- voice-session summary artifact creation
- handoff into project, review, or draft surfaces
- concise recovery context for resumed voice interactions

### Expected outputs
- voice-session summary persistence behavior
- handoff logic into the main application surfaces
- tests for summary persistence and continuity usefulness

### Related anchors
- `ARCH:ChannelSessionSummaryStrategy`
- `ARCH:ChannelHandoffUx`
- `ARCH:SummaryArtifactTypes`

### Definition of done
- Glimmer can recover or hand off useful voice-session context instead of losing it at the end of the conversation

**Stable plan anchor:** `PLAN:WorkstreamF.PackageF8.VoiceSummaryAndHandoff`

---

## 9. Sequencing Inside the Workstream

The recommended internal order for Workstream F is:

1. F1 — Voice infrastructure boundary and session bootstrap
2. F2 — Voice session state and continuity core
3. F3 — Transcript ingestion and normalization
4. F5 — Voice-to-structured-output routing
5. F6 — Review-safe handling of voice-derived actions and interpretations
6. F4 — Spoken briefing and interactive response flows
7. F7 — Voice console in the web workspace
8. F8 — Voice session summaries and handoff support

This order keeps the work aligned to the layered strategy: first create the boundary and state model, then normalize voice input, then route it into shared workflows safely, then improve the spoken experience and UI integration on top.

**Stable plan anchor:** `PLAN:WorkstreamF.InternalSequence`

---

## 10. Human Dependencies

Workstream F has more practical human dependencies than the earlier non-voice workstreams.

Expected human actions include:

- choosing and provisioning the actual voice infrastructure or service credentials,
- confirming acceptable latency/quality tradeoffs,
- reviewing the voice interaction style and response brevity,
- and validating any manual-only aspects of audio quality or device behavior that are not yet worth automating.

The coding agent should still be able to implement the full structural voice path, session model, transcript path, and review-safe routing even before final production voice infrastructure is fully available.

**Stable plan anchor:** `PLAN:WorkstreamF.HumanDependencies`

---

## 11. Verification Expectations

Workstream F is complete only when voice behavior is proven to preserve continuity, structure, and review discipline rather than simply generating speech.

### Verification layers expected
- graph workflow verification for voice-session routing
- integration verification for transcript-to-artifact persistence
- API/application verification for voice-session endpoints where relevant
- browser-visible verification for the voice console where practical
- explicit `ManualOnly` or `Deferred` treatment for irreducibly environment-specific audio checks

### Minimum proof expectations
- a voice session can be created and bound to the correct operator/session context
- transcript segments become structured internal artifacts
- voice sessions preserve short-horizon context within an active session
- spoken input can route into planning, drafting, or triage-related pathways correctly
- voice-derived actions and interpretations do not bypass review gates
- voice-session summaries and handoffs preserve useful continuity
- any non-automated audio-quality or device-specific checks are explicitly recorded rather than implied

This aligns directly to the Glimmer testing strategy, which treats voice verification as behaviorally consistent routing and review-boundary proof rather than just audio novelty.

**Stable plan anchor:** `PLAN:WorkstreamF.VerificationExpectations`

---

## 12. Suggested Future Working Documents for This Workstream

This workstream should eventually be paired with:

- `WorkstreamF_Voice_DESIGN_AND_IMPLEMENTATION_PLAN.md`
- `WorkstreamF_Voice_DESIGN_AND_IMPLEMENTATION_PROGRESS.md`

Those files will hold the active implementation state, infrastructure assumptions, verification evidence, and remaining environment-dependent checks once coding begins.

**Stable plan anchor:** `PLAN:WorkstreamF.WorkingDocumentPair`

---

## 13. Definition of Done

Workstream F should be considered complete when all of the following are true:

1. a bounded voice-session boundary exists,
2. voice-session continuity state is real,
3. transcript input becomes structured internal artifacts,
4. spoken interaction can route into shared Glimmer workflows,
5. review-safe handling of voice-derived outputs is enforced,
6. the web workspace includes a usable voice console surface,
7. voice-session summaries and handoffs preserve useful continuity,
8. and the required automated and explicitly recorded manual/deferred verification evidence has been executed and captured.

If these are not true, Glimmer still lacks a trustworthy voice mode and has only a partial conversational layer.

**Stable plan anchor:** `PLAN:WorkstreamF.DefinitionOfDone`

---

## 14. Final Note

Workstream F should make voice useful, not magical.

If this workstream is done well, Glimmer will feel easier to use when the operator is moving, thinking aloud, or preparing quickly — without becoming a loose conversational side channel that bypasses structure and review.
If it is done badly, voice will either feel gimmicky or dangerous.

The right outcome is a bounded conversational mode that extends the same disciplined operating system the rest of Glimmer is building.

**Stable plan anchor:** `PLAN:WorkstreamF.Conclusion`

