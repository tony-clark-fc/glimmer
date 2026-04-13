# Glimmer — Workstream F Voice Design and Implementation Progress

## Document Metadata

- **Document Title:** Glimmer — Workstream F Voice Design and Implementation Progress
- **Document Type:** Working Progress Document
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** F — Voice
- **Primary Companion Documents:** Workstream F Plan, Requirements, Architecture, Verification, Governance and Process

---

## 1. Purpose

This document is the active progress and evidence record for **Workstream F — Voice**.

Its purpose is to record the current implementation state of the workstream in a way that supports:

- session-to-session continuity,
- evidence-backed status reporting,
- human review,
- and clean future agent pickup without re-discovery.

This file is not the source of architecture or requirement truth. It records **execution truth**.

**Stable working anchor:** `WORKF:Progress.ControlSurface`

---

## 2. Status Model

The following status vocabulary should be used consistently in this file.

- `Designed`
- `InProgress`
- `Implemented`
- `Verified`
- `Blocked`
- `HumanReviewRequired`
- `Deferred`

A work item should not be treated as complete merely because code exists. Verification status must be recorded explicitly.

**Stable working anchor:** `WORKF:Progress.StatusModel`

---

## 3. Current Overall Status

- **Overall Workstream Status:** `Designed`
- **Current Confidence Level:** Planning complete, implementation not yet started
- **Last Meaningful Update:** Initial creation of progress surface
- **Ready for Coding:** Yes, once Workstream A substrate, core Workstream B memory structures, Workstream D assistant-core flows, and the main Workstream E workspace are materially in place

### Current summary

Workstream F has a complete planning and verification posture, including:

- canonical Requirements,
- the current Architecture control surface,
- a Build Plan and Workstream F workstream document,
- canonical verification assets including the Workstream F pack and the cross-cutting Release pack,
- global and module-scoped agent instructions,
- and the paired Workstream F implementation plan.

The workstream is therefore ready to move from planning into actual voice and companion implementation as soon as the non-voice core and main workspace are sufficiently real.

**Stable working anchor:** `WORKF:Progress.CurrentOverallStatus`

---

## 4. Control Anchors in Scope

### 4.1 Requirements anchors

- `REQ:VoiceInteraction`
- `REQ:TelegramMobilePresence`
- `REQ:ProjectMemory`
- `REQ:StateContinuity`
- `REQ:Explainability`
- `REQ:PreparedBriefings`
- `REQ:HumanApprovalBoundaries`
- `REQ:SafeBehaviorDefaults`

### 4.2 Architecture anchors

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

### 4.3 Build-plan anchors

- `PLAN:WorkstreamF.Voice`
- `PLAN:WorkstreamF.Objective`
- `PLAN:WorkstreamF.InternalSequence`
- `PLAN:WorkstreamF.VerificationExpectations`
- `PLAN:WorkstreamF.DefinitionOfDone`

### 4.4 Verification anchors

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

**Stable working anchor:** `WORKF:Progress.ControlAnchors`

---

## 5. Work Package Status Table

| Work Package | Title | Status | Verification Status | Notes |
|---|---|---|---|---|
| WF1 | Voice session bootstrap and binding | `Designed` | Not started | First real conversational substrate slice |
| WF2 | Transcript and utterance normalization | `Designed` | Not started | Structured-input bridge from voice to system state |
| WF3 | Voice continuity and session-state handling | `Designed` | Not started | Bounded, traceable continuity only |
| WF4 | Voice-to-core routing | `Designed` | Not started | Must remain shared-core, not a side path |
| WF5 | Spoken briefing and bounded response behavior | `Designed` | Not started | Listening-friendly, context-grounded responses |
| WF6 | Telegram bounded companion interaction | `Designed` | Not started | Mobile companion, not second control room |
| WF7 | Cross-surface handoff into the workspace | `Designed` | Not started | Preserve context and review visibility |
| WF8 | Approval and safety parity across channels | `Designed` | Not started | No-auto-send and approval parity are non-negotiable |

**Stable working anchor:** `WORKF:Progress.PackageStatusTable`

---

## 6. What Already Exists Before Coding Starts

The following substantial control and support artifacts already exist and reduce execution ambiguity for Workstream F:

### 6.1 Planning and architecture surfaces

- Requirements document
- current Architecture control surface
- Build Plan
- Workstream F detailed build-plan document
- Governance and Process document

### 6.2 Verification surfaces

- `TEST_CATALOG.md`
- `verification-pack-workstream-f.md`
- `verification-pack-release.md`
- upstream smoke and Workstream A/B/C/D/E packs already prepared
- data-integrity pack already prepared

### 6.3 Operational support surfaces

- global copilot instructions
- voice/companion module instructions
- connectors module instructions
- backend/orchestration module instructions
- testing/verification module instructions
- frontend workspace module instructions
- Agent Skills README
- Agent Tools README

### 6.4 Workstream execution surfaces

- Workstream F implementation plan
- this Workstream F progress file

This means voice and companion implementation can begin with unusually high clarity once the non-voice core and workspace are materially available.

**Stable working anchor:** `WORKF:Progress.PreexistingAssets`

---

## 7. Execution Log

This section should be updated incrementally during implementation.

### 7.1 Initial entry

- **State:** No code implementation recorded yet.
- **Meaningful accomplishment:** Workstream F planning, verification, and operational support surfaces are complete enough to begin execution cleanly once the core non-voice Glimmer substrate is sufficiently real.
- **Next expected change:** Stand up voice session bootstrap and the first transcript-to-structured-artifact path.

### 7.2 Voice infrastructure direction decision — 2026-04-13

- **State:** Design decision recorded, no code change.
- **Source:** Operator-relayed stakeholder analysis of local inference capabilities on the target hardware profile (Apple M5 Max, 128 GB unified memory).
- **Decision:** The voice infrastructure direction has moved from "LiveKit Agents or equivalent" to **local multi-model inference using MLX on Apple Silicon**, with the Gemma 4 model family as the reference baseline.
- **Key design points:**
  - **Voice I/O** will target a native-audio model (Gemma 4 E4B, 4.5B parameters at FP16) for low-latency, prosody-aware spoken interaction. This model can process raw audio input, detecting tone, emotion, and urgency — not just transcribed words.
  - **Deep reasoning** (triage, prioritization, drafting, planning) will route to a larger local model (Gemma 4 31B at Q8/FP16, or Gemma 4 26B A4B MoE for faster interactive use). These models use the pipeline approach (ASR → text reasoning → TTS) when invoked from voice context.
  - **Both directions** of the voice pipeline are affected: recognition (operator → Glimmer) and generation (Glimmer → operator).
  - The target hardware can run the 31B model at ~40–60 tokens/sec and the 26B MoE at 100+ tokens/sec, both well above conversational speech speed.
  - All model inference runs locally — cloud model providers become optional enhancement, not structural dependency.
- **Documents updated:**
  - `01_system_overview.md` — §6.2, §6.2A (target hardware profile and local inference baseline), §6.3 (voice removed from external dependencies)
  - `06_ui_and_voice.md` — §11.5 (voice infrastructure direction, pipeline vs native audio, hybrid architecture)
  - `07_security_and_permissions.md` — §12.1, §12.2, §12.3 (local multi-model routing, remote models now optional)
  - `workstream_f_voice.md` — §8.1 Work Package F1 (updated scope and anchors for local inference)
  - `.github/copilot-instructions.md` — §2 technology baseline (MLX, Gemma 4, local multi-model voice)
- **Architecture anchors added:**
  - `ARCH:TargetHardwareProfile`
  - `ARCH:LocalInferenceBaseline`
  - `ARCH:VoiceInfrastructureDirection`
  - `ARCH:VoicePipelineArchitecture`
  - `ARCH:LocalModelRouting`
- **Assumption:** Specific model versions and quantization levels may evolve. The architecture treats the model layer as a bounded dependency behind an inference abstraction.

**Stable working anchor:** `WORKF:Progress.ExecutionLog`

---

## 8. Verification Log

This section records **executed** verification, not merely intended verification.

### 8.1 Current verification state

- `TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession` — Not executed yet
- `TEST:Voice.Session.TranscriptBecomesStructuredSignal` — Not executed yet
- `TEST:Voice.Session.ContinuityPreservedWithinSession` — Not executed yet
- `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions` — Not executed yet
- `TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant` — Not executed yet
- `TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation` — Not executed yet
- `TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary` — Not executed yet
- `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded` — Not executed yet
- `TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace` — Not executed yet
- `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved` — Not executed yet
- `TEST:ChannelSession.SummariesPersistWithTraceableOrigin` — Not executed yet
- `TEST:Drafting.NoAutoSend.BoundaryPreserved` — Not executed yet
- `TEST:Security.NoAutoSend.GlobalBoundaryPreserved` — Not executed yet
- `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` — Not executed yet

### 8.2 Verification interpretation

The verification design is ready, but no executable voice or companion proof has been recorded yet. Therefore the workstream remains in a pre-implementation state.

**Stable working anchor:** `WORKF:Progress.VerificationLog`

---

## 9. Known Risks and Watchpoints

### 9.1 Risk — Voice becomes a side-channel assistant

If voice evolves as a separate logic path, the system will drift away from the shared-core architecture.

### 9.2 Risk — Session continuity becomes shadow memory

If session state is too implicit or too sticky, it will undermine traceability and the memory model.

### 9.3 Risk — Telegram overreaches

If Telegram becomes too capable without handoff back to the main workspace, it will turn into an ungoverned second control room.

### 9.4 Risk — Spoken output becomes bloated or vague

If spoken responses are too long or too generic, the user experience will feel worse even if technically functional.

### 9.5 Risk — Approval boundaries weaken under conversational pressure

This is the most dangerous class of regression in the workstream and must be resisted explicitly.

### 9.6 Risk — Environment-bound testing gets confused with automated proof

Manual audio/network checks may be necessary, but they must not masquerade as broad automated confidence.

**Stable working anchor:** `WORKF:Progress.Risks`

---

## 10. Human Dependencies

The voice infrastructure direction has been confirmed (2026-04-13): local multi-model inference using MLX and Gemma 4 on Apple M5 Max. This resolves the first and most significant infrastructure decision for the workstream.

Remaining likely human dependencies:

- Telegram bot setup and secrets/config for live validation
- decisions about preferred spoken verbosity in early iterations
- explicit confirmation of which voice/companion behaviors are truly in scope for a given release claim
- final TTS approach selection (native audio model output vs. dedicated TTS vs. Apple system speech) — may require hands-on quality evaluation

No live environment dependency should be raised as a blocker until the agent has completed fixture-driven, routing, continuity, and handoff work first.

**Stable working anchor:** `WORKF:Progress.HumanDependencies`

---

## 11. Immediate Next Slice

The recommended first implementation slice is:

1. implement voice session bootstrap and binding,
2. normalize transcript/utterance input into structured artifacts,
3. persist bounded channel-session state,
4. route the first voice-derived interaction into the shared core,
5. and execute the first voice session proof.

That slice creates a real conversational extension of Glimmer without trying to solve all companion behavior at once.

**Stable working anchor:** `WORKF:Progress.ImmediateNextSlice`

---

## 12. Pickup Guidance for the Next Session

When the next implementation session begins for Workstream F, the coding agent should:

1. read the Workstream F implementation plan,
2. confirm the latest Architecture control surface,
3. inspect the actual non-voice core and workspace available by then,
4. implement voice session bootstrap and transcript normalization,
5. persist bounded session artifacts,
6. add the first shared-core routing path,
7. execute the first voice/companion proof slice,
8. then return here and update:
   - execution log,
   - package status,
   - verification log,
   - and current overall status.

**Stable working anchor:** `WORKF:Progress.PickupGuidance`

---

## 13. Definition of Real Progress for This File

This file should only be updated when one or more of the following has genuinely changed:

- code was implemented,
- a work package status changed,
- verification was executed,
- a blocker emerged or was cleared,
- or pickup guidance materially changed.

This avoids turning the file into vague narration.

**Stable working anchor:** `WORKF:Progress.DefinitionOfRealProgress`

---

## 14. Final Note

Right now, Workstream F is well-prepared but not yet earned.

That is the honest status.

The voice and companion model, verification posture, and support surfaces are strong on paper. The next step is to convert that advantage into a real bounded conversational layer and begin recording actual evidence here.

**Stable working anchor:** `WORKF:Progress.Conclus