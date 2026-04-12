# Glimmer — Workstream F Voice Design and Implementation Plan

## Document Metadata

- **Document Title:** Glimmer — Workstream F Voice Design and Implementation Plan
- **Document Type:** Working Implementation Plan
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** F — Voice
- **Primary Companion Documents:** Requirements, Architecture, Build Plan, Verification, Governance and Process, Global Copilot Instructions, Module Instructions, Workstream F Verification Pack

---

## 1. Purpose

This document is the active working implementation plan for **Workstream F — Voice**.

Its purpose is to translate the canonical Workstream F build-plan document into an execution-ready plan that a coding agent can use during real implementation sessions.

This file should remain practical and anchored. It is not the source of architecture truth. It is the working plan for how Glimmer’s voice and companion interaction layer should be implemented, verified, and advanced slice by slice.

**Stable working anchor:** `WORKF:Plan.ControlSurface`

---

## 2. Workstream Objective

The objective of Workstream F is to implement the bounded voice and companion layer that lets the operator interact with Glimmer away from the main workspace without weakening the core review, memory, and approval model.

At the end of Workstream F, the repository should have real support for:

- voice session bootstrap,
- transcript and utterance normalization into structured artifacts,
- short-horizon session continuity,
- spoken briefings and bounded spoken responses,
- routing from voice into the shared assistant core,
- Telegram companion interaction as a bounded mobile surface,
- cross-surface handoff into the main workspace,
- review-safe handling of voice- and Telegram-derived outcomes,
- channel-session summaries and continuity artifacts,
- and continued preservation of no-auto-send and approval boundaries across companion modes.

This workstream is where Glimmer becomes truly mobile and conversational without becoming unsafe or architecturally loose.

**Stable working anchor:** `WORKF:Plan.Objective`

---

## 3. Control Anchors in Scope

### 3.1 Requirements anchors

- `REQ:VoiceInteraction`
- `REQ:TelegramMobilePresence`
- `REQ:ProjectMemory`
- `REQ:StateContinuity`
- `REQ:Explainability`
- `REQ:PreparedBriefings`
- `REQ:HumanApprovalBoundaries`
- `REQ:SafeBehaviorDefaults`

### 3.2 Architecture anchors

- `ARCH:VoiceLayeringStrategy`
- `ARCH:VoiceInteractionArchitecture`
- `ARCH:VoiceSessionGraph`
- `ARCH:TelegramCompanionChannel`
- `ARCH:TelegramCompanionUx`
- `ARCH:TelegramConnector`
- `ARCH:ChannelSessionModel`
- `ARCH:ReviewGateArchitecture`
- `ARCH:UiSurfaceMap`
- `ARCH:LangGraphTopology`
- `ARCH:StructuredMemoryModel`
- `ARCH:NoAutoSendPolicy`
- `ARCH:SystemBoundaries`

### 3.3 Build-plan anchors

- `PLAN:WorkstreamF.Voice`
- `PLAN:WorkstreamF.Objective`
- `PLAN:WorkstreamF.InternalSequence`
- `PLAN:WorkstreamF.VerificationExpectations`
- `PLAN:WorkstreamF.DefinitionOfDone`

### 3.4 Verification anchors

- `TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession`
- `TEST:Voice.Session.TranscriptBecomesStructuredSignal`
- `TEST:Voice.Session.ContinuityPreservedWithinSession`
- `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions`
- `TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant`
- `TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation`
- `TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary`
- `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded`
- `TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace`
- `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved`
- `TEST:ChannelSession.SummariesPersistWithTraceableOrigin`
- `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- `TEST:Security.NoAutoSend.GlobalBoundaryPreserved`
- `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`

**Stable working anchor:** `WORKF:Plan.ControlAnchors`

---

## 4. Execution Principles for This Workstream

### 4.1 Companion modes extend the core; they do not replace it

Voice and Telegram must remain layered on top of the same review, memory, and workflow core used by the main browser workspace.

### 4.2 Session continuity must be explicit and bounded

Short-horizon continuity is useful. Hidden shadow memory is not. Session state should be modeled explicitly and persisted where appropriate.

### 4.3 Conversational convenience must not weaken approval discipline

If a voice or Telegram interaction leads to a meaningful action, ambiguous interpretation, or externally relevant outcome, it must still respect the same review boundaries as the main system.

### 4.4 Spoken outputs should be listening-friendly, not essay-shaped

Voice behavior should favor concise, structured, useful spoken briefings rather than dumping visually optimized text into audio form.

### 4.5 Telegram is a companion surface, not a second control room

Telegram interactions should stay bounded, useful, and handoff-friendly. They must not evolve into a hidden full-featured operating surface that bypasses the main workspace.

### 4.6 Cross-surface handoff must preserve context

The operator should be able to move from voice or Telegram into the browser workspace without losing the relevant thread, review state, or origin context.

**Stable working anchor:** `WORKF:Plan.ExecutionPrinciples`

---

## 5. Voice and Companion Shape Target for Workstream F

By the end of this workstream, the implementation should materially support the following voice/companion categories or directly equivalent concrete shapes:

- voice session bootstrap and session identity binding
- transcript/utterance normalization into structured internal artifacts
- bounded voice routing into shared core workflows
- spoken briefing/response generation suitable for listening
- Telegram bounded interaction surface
- channel-session summaries and continuity artifacts
- workspace-visible handoff from companion interaction
- no-auto-send and approval parity across channels

These layers must remain bounded, review-safe, continuity-preserving, and testable.

**Stable working anchor:** `WORKF:Plan.VoiceShapeTarget`

---

## 6. Work Packages to Execute

## 6.1 WF1 — Voice session bootstrap and binding

### Objective
Implement the initial voice session bootstrap path so the system binds the correct operator, session, and bounded runtime context.

### Expected touch points
- voice session bootstrap code
- API/session setup
- channel-session integration
- integration/API tests

### Verification expectation
- `TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession`

### Notes
Session identity and operator context must be explicit from the start.

**Stable working anchor:** `WORKF:Plan.PackageWF1`

---

## 6.2 WF2 — Transcript and utterance normalization

### Objective
Implement transcript/utterance handling so spoken input becomes structured internal artifacts instead of remaining only ephemeral session text.

### Expected touch points
- transcript ingestion handlers
- normalization mappers
- source/session artifact creation
- graph/integration tests

### Verification expectation
- `TEST:Voice.Session.TranscriptBecomesStructuredSignal`

### Notes
This is the bridge from conversational input to structured system truth.

**Stable working anchor:** `WORKF:Plan.PackageWF2`

---

## 6.3 WF3 — Voice continuity and session-state handling

### Objective
Implement bounded voice continuity and short-horizon session state so spoken interaction is coherent without becoming an unbounded hidden memory layer.

### Expected touch points
- session-state persistence
- voice continuity helpers
- channel-session updates
- graph/integration tests

### Verification expectation
- `TEST:Voice.Session.ContinuityPreservedWithinSession`
- `TEST:ChannelSession.SummariesPersistWithTraceableOrigin`

### Notes
Continuity is useful only if it remains traceable and bounded.

**Stable working anchor:** `WORKF:Plan.PackageWF3`

---

## 6.4 WF4 — Voice-to-core routing

### Objective
Implement routing from voice interactions into the shared assistant-core workflows so voice behaves like a mode over the same system rather than a divergent code path.

### Expected touch points
- voice graph adapters
- shared workflow routing logic
- graph/integration tests

### Verification expectation
- `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved`
- `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions`

### Notes
The core should stay shared even when the interaction surface changes.

**Stable working anchor:** `WORKF:Plan.PackageWF4`

---

## 6.5 WF5 — Spoken briefing and bounded response behavior

### Objective
Implement spoken output behavior that is concise, relevant, and aligned to the actual project context and available artifacts.

### Expected touch points
- voice response formatting helpers
- briefing generation adapters
- voice response handlers
- graph/integration/manual checks

### Verification expectation
- `TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant`

### Notes
A good spoken response is shorter and more structured than a good screen paragraph.

**Stable working anchor:** `WORKF:Plan.PackageWF5`

---

## 6.6 WF6 — Telegram bounded companion interaction

### Objective
Implement Telegram as a bounded companion surface for quick check-ins, brief questions, and safe escalation into the main workspace.

### Expected touch points
- Telegram interaction handlers
- Telegram response shaping
- contract/integration tests

### Verification expectation
- `TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary`
- `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded`

### Notes
Telegram must remain useful without becoming an alternate hidden control room.

**Stable working anchor:** `WORKF:Plan.PackageWF6`

---

## 6.7 WF7 — Cross-surface handoff into the workspace

### Objective
Implement handoff behavior so voice- or Telegram-derived interactions can continue safely inside the main workspace with context preserved.

### Expected touch points
- handoff state creation
- workspace continuation links/routing
- browser/integration tests

### Verification expectation
- `TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation`
- `TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace`

### Notes
This is where companion convenience must reconnect to the canonical control surface.

**Stable working anchor:** `WORKF:Plan.PackageWF7`

---

## 6.8 WF8 — Approval and safety parity across channels

### Objective
Ensure that voice and Telegram respect the same no-auto-send and approval-boundary behavior as the rest of Glimmer.

### Expected touch points
- review gate adapters
- channel-specific safety handling
- graph/API/integration tests

### Verification expectation
- `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- `TEST:Security.NoAutoSend.GlobalBoundaryPreserved`
- `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`

### Notes
Companion convenience must not create safety exceptions.

**Stable working anchor:** `WORKF:Plan.PackageWF8`

---

## 7. Recommended Execution Order

The recommended execution order inside this working plan is:

1. WF1 — Voice session bootstrap and binding
2. WF2 — Transcript and utterance normalization
3. WF3 — Voice continuity and session-state handling
4. WF4 — Voice-to-core routing
5. WF5 — Spoken briefing and bounded response behavior
6. WF6 — Telegram bounded companion interaction
7. WF7 — Cross-surface handoff into the workspace
8. WF8 — Approval and safety parity across channels

This sequence keeps the session/state foundation stable before more visible conversational behavior is layered on top.

**Stable working anchor:** `WORKF:Plan.ExecutionOrder`

---

## 8. Expected Files and Layers Likely to Change

The initial Workstream F implementation is likely to touch files or file groups such as:

- voice session modules
- transcript/session-state handlers
- Telegram interaction modules
- channel-session persistence adapters
- graph routing/adapters
- voice/companion response helpers
- browser handoff surfaces
- graph/integration/browser/manual test fixtures
- Workstream F working documents

This list should be refined as implementation begins.

**Stable working anchor:** `WORKF:Plan.LikelyTouchPoints`

---

## 9. Verification Plan for Workstream F

### 9.1 Minimum required proof

At minimum, Workstream F implementation should produce executable proof for:

- voice session bootstrap and operator/session binding
- transcript-to-structured-artifact behavior
- bounded session continuity
- spoken briefing relevance and boundedness
- Telegram bounded summary behavior
- workspace handoff and review-state surfacing
- shared-core parity between voice/Telegram and the main assistant core
- no-auto-send preservation and approval-boundary parity across channels

### 9.2 Primary verification surfaces

The main verification references for this workstream are:

- `verification-pack-workstream-f.md`
- `verification-pack-release.md` for representative release-level checks later
- `verification-pack-data-integrity.md` where continuity/traceability protections intersect with durable state

### 9.3 Evidence expectation

Meaningful implementation slices in this workstream should update the Workstream F progress file with:

- what was implemented
- what proof was executed
- what passed
- what failed
- what remains blocked or deferred

**Stable working anchor:** `WORKF:Plan.VerificationPlan`

---

## 10. Human Dependencies and Likely Decisions

This workstream is partly agent-executable, but several human or environment-dependent decisions may still be needed.

Likely human-dependent areas include:

- confirmation of the first voice infrastructure path if alternatives are available
- Telegram bot setup and secrets/config where live validation is needed
- decisions about how much spoken verbosity is desirable in early iterations
- explicit confirmation of which voice/companion behaviors are actually in-scope for a given release claim

The coding agent should complete all fixture-driven, session-state, routing, and handoff work before surfacing live environment dependencies as blockers.

**Stable working anchor:** `WORKF:Plan.HumanDependencies`

---

## 11. Known Risks in This Workstream

### 11.1 Risk — Voice becomes a side-channel assistant

If voice evolves as a separate logic path, the system will drift away from the shared-core architecture.

### 11.2 Risk — Session continuity becomes shadow memory

If session state is too implicit or too sticky, it will undermine traceability and the memory model.

### 11.3 Risk — Telegram overreaches

If Telegram becomes too capable without handoff back to the main workspace, it will turn into an ungoverned second control room.

### 11.4 Risk — Spoken output becomes bloated or vague

If spoken responses are too long or too generic, the user experience will feel worse even if technically functional.

### 11.5 Risk — Approval boundaries weaken under conversational pressure

This is the most dangerous class of regression in the workstream and must be resisted explicitly.

### 11.6 Risk — Environment-bound testing gets confused with automated proof

Manual audio/network checks may be necessary, but they must not masquerade as broad automated confidence.

**Stable working anchor:** `WORKF:Plan.Risks`

---

## 12. Immediate Next Session Recommendations

When actual coding for Workstream F begins, the first sensible execution slice is:

1. implement voice session bootstrap and binding,
2. normalize transcript/utterance input into structured artifacts,
3. persist bounded channel-session state,
4. route the first voice-derived interaction into the shared core,
5. and execute the first voice session proof.

That slice creates a real conversational extension of Glimmer without trying to solve all companion behavior at once.

**Stable working anchor:** `WORKF:Plan.ImmediateNextSlice`

---

## 13. Definition of Ready for Workstream F Completion

Workstream F should only be considered ready for completion when all of the following are materially true:

- voice session bootstrap is real
- transcript/utterance normalization is real
- bounded continuity/session state is real
- voice-to-core routing is real
- spoken briefing behavior is real and bounded
- Telegram companion interaction is real and bounded
- workspace handoff is real
- approval and no-auto-send parity is real
- and the corresponding proof paths have been executed and recorded

If these are not true, Workstream F is not done, even if conversational demos appear to work.

**Stable working anchor:** `WORKF:Plan.DefinitionOfReadyForCompletion`

---

## 14. Final Note

This workstream is where Glimmer either becomes a disciplined conversational companion or turns into the kind of loosely governed side-channel assistant the architecture is explicitly trying to avoid.

That is the standard here.

The goal is not to make interaction merely feel futuristic. The goal is to make the voice and companion layer:

- bounded,
- review-safe,
- continuity-preserving,
- and genuinely subordinate to the same trustworthy core as the main workspace.

**Stable working anchor:** `WORKF:Plan.Conclusion`

