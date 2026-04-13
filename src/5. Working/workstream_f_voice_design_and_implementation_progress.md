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

- **Overall Workstream Status:** `Verified`
- **Current Confidence Level:** WF1-WF8 implemented and verified; 125 new tests (7 bootstrap + 6 transcript + 11 continuity + 10 graph/routing + 16 API + 21 briefing + 23 Telegram + 11 Telegram API + 20 handoff/safety) all pass; total backend 430/430
- **Last Meaningful Update:** 2026-04-13 — WF6-WF8 implemented: Telegram companion service, cross-surface handoff, safety parity
- **Ready for Coding:** Complete — all work packages verified

### Current summary

Workstream F has progressed from planning to active implementation. The first major slice covers the voice session foundation:

- **WF1** — Voice session bootstrap: `ChannelSession` + `VoiceSessionState` creation with operator binding, project context preservation, voice channel identity
- **WF2** — Transcript normalization: voice utterances converted to `ImportedSignal` records with `signal_type="voice_transcript"` and full provenance metadata
- **WF3** — Session continuity: bounded continuity state with capped topic history, merged project references, capped unresolved prompts, utterance counting, session summary creation
- **WF4** — Voice-to-core routing: voice signals flow through the shared `IntakeGraph` to triage, with `auto_send_blocked=True` enforced throughout
- **WF5** — Spoken briefing: bounded spoken output from FocusPack data (800 chars max, numbered structure), BriefingArtifact persistence, session context responses
- **WF6** — Telegram bounded companion: session bootstrap/reuse, message normalization into ImportedSignals with Telegram provenance, bounded context tracking, "what matters now" summary (500 chars max), handoff detection for review triggers, shared IntakeGraph routing
- **WF7** — Cross-surface handoff: workspace-visible continuation records from voice and Telegram sessions, BriefingArtifact(briefing_type="channel_handoff") persistence with full provenance, pending handoff retrieval
- **WF8** — Safety parity: auto_send_blocked enforcement across all channels and handoff records, review gate preservation verification, no-auto-send boundary proven at service and API levels

Backend additions: `VoiceSessionGraphState` TypedDict, `VoiceSessionGraph` LangGraph workflow, voice service layer (`app/services/voice.py`), voice REST API, briefing service (`app/services/briefing.py`), Telegram service (`app/services/telegram.py`), handoff service (`app/services/handoff.py`), Telegram REST API (`/telegram/sessions`, `/telegram/sessions/{id}/messages`, `/telegram/sessions/{id}/what-matters-now`, `/telegram/sessions/{id}/handoff`, `/telegram/handoffs/pending`), voice handoff endpoint (`/voice/sessions/{id}/handoff`).

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
| WF1 | Voice session bootstrap and binding | `Verified` | 7 integration tests + 3 API tests | Session creates correct ChannelSession + VoiceSessionState, binds operator |
| WF2 | Transcript and utterance normalization | `Verified` | 6 integration tests + 2 API tests | Utterances become ImportedSignals with voice provenance |
| WF3 | Voice continuity and session-state handling | `Verified` | 11 integration tests + 3 API tests | Bounded continuity, summary creation, session completion |
| WF4 | Voice-to-core routing | `Verified` | 10 graph/integration tests + 2 API tests | Signals route through IntakeGraph, auto_send_blocked enforced |
| WF5 | Spoken briefing and bounded response behavior | `Verified` | 21 integration tests + 6 API tests | Bounded briefings from focus-pack data, session context responses, BriefingArtifact persistence |
| WF6 | Telegram bounded companion interaction | `Verified` | 23 integration tests + 11 API tests | Session bootstrap/reuse, message normalization, bounded context, "what matters now", handoff detection, shared-core routing |
| WF7 | Cross-surface handoff into the workspace | `Verified` | 11 integration tests + handoff API tests | Voice/Telegram handoffs create BriefingArtifact(channel_handoff), pending retrieval |
| WF8 | Approval and safety parity across channels | `Verified` | 9 integration tests | auto_send_blocked across all channels, review gate verification, no-auto-send boundary proven |

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

### 7.2 Session 2026-04-13 — WF1-WF4 implementation

- **State:** WF1-WF4 implemented and verified.
- **Meaningful accomplishment:**
  - Voice session bootstrap: creates `ChannelSession(channel_type="voice")` + `VoiceSessionState`, binds operator, preserves project context
  - Transcript normalization: converts voice utterances to `ImportedSignal(signal_type="voice_transcript")` with channel_session_id provenance, utterance index, timestamp in raw_metadata
  - Bounded session continuity: tracks current_topic (capped to 5 recent topics), referenced project IDs (merged set), unresolved prompts (capped to 10), utterance count; creates session summaries on session end
  - Voice-to-core routing: voice signals flow through shared `IntakeGraph` to triage; `auto_send_blocked=True` enforced at all levels
  - `VoiceSessionGraph` LangGraph workflow: bootstrap → load_context → normalize_transcript → update_continuity → route_to_core → check_review → END/review_interrupt
  - REST API: POST/GET/POST voice session lifecycle endpoints
- **Verification executed:**
  - 7 integration tests (bootstrap): session creation, operator binding, project context, channel identity — all pass
  - 6 integration tests (transcript): signal creation, provenance, multiple segments, empty skip, index/timestamp preservation — all pass
  - 11 integration tests (continuity): topic updates, bounded topics, project merge, capped prompts, utterance count, summary creation/completion/project references — all pass
  - 10 graph/integration tests (routing): graph compilation, execution, safety invariants, routing with/without signals, review conditional edges, intake graph integration, auto_send_blocked — all pass
  - 10 API tests: session create/get/404, utterance submit/404, end session/summary, completed session rejection, utterance counting, auto_send_blocked — all pass
  - Full backend suite: 349/349 pass
- **Files created:**
  - `app/services/__init__.py` (new — services package)
  - `app/services/voice.py` (new — voice service layer: bootstrap, normalize, continuity, routing)
  - `app/graphs/voice_session.py` (new — VoiceSessionGraph LangGraph workflow)
  - `app/api/voice.py` (new — voice REST API endpoints)
  - `tests/integration/test_voice_session_bootstrap.py` (new — 7 tests)
  - `tests/integration/test_voice_transcript_normalization.py` (new — 6 tests)
  - `tests/integration/test_voice_continuity.py` (new — 11 tests)
  - `tests/integration/test_voice_routing.py` (new — 10 tests)
  - `tests/api/test_voice_api.py` (new — 10 tests)
- **Files modified:**
  - `app/graphs/state.py` (VoiceSessionGraphState TypedDict added)
  - `app/main.py` (voice router registration)
- **Next expected change:** WF5 spoken briefing, WF6 Telegram companion, WF7 handoff, WF8 safety parity

### 7.3 Session 2026-04-13 — WF5 spoken briefing implementation

- **State:** WF5 implemented and verified.
- **Meaningful accomplishment:**
  - Spoken briefing service (`app/services/briefing.py`): formats FocusPack data into listening-friendly spoken text with bounded length (800 chars max), bounded item counts (3 actions, 2 risks, 2 waiting), and numbered structure
  - Section formatters: `_format_top_actions`, `_format_risks`, `_format_waiting`, `_format_pressure` — each produces concise spoken fragments, truncates long content, mentions remaining counts
  - `SpokenBriefingResult` with briefing text, artifact ID, section count, empty flag, source focus pack ID
  - `generate_spoken_briefing()`: resolves latest or specified FocusPack, formats all sections, enforces length bound, persists `BriefingArtifact(briefing_type="voice_spoken_briefing")` with full source scope metadata
  - `generate_session_context_response()`: quick "where are we?" spoken summary from session state (topic, utterance count, project count, open questions)
  - REST API: `POST /voice/sessions/{id}/briefing` → `SpokenBriefingResponse`, `GET /voice/sessions/{id}/context` → session orientation dict
  - All responses enforce `auto_send_blocked=True`
- **Verification executed:**
  - 10 unit tests (formatting): bounded output, empty handling, long title truncation, risk/waiting boundedness, pressure combinations
  - 7 integration tests (generation): empty focus pack graceful handling, populated briefing grounding, length enforcement, artifact persistence, latest-pack resolution, empty-pack clear state, section count accuracy
  - 4 integration tests (context response): active session, no topic, conciseness, singular forms
  - 6 API tests: briefing with/without data, 404 handling, auto_send_blocked, context endpoint, context 404
  - Full backend suite: 376/376 pass
- **Files created:**
  - `app/services/briefing.py` (new — spoken briefing service)
  - `tests/integration/test_voice_spoken_briefing.py` (new — 21 tests)
- **Files modified:**
  - `app/api/voice.py` (briefing + context endpoints, SpokenBriefingResponse model)
  - `tests/api/test_voice_api.py` (6 new API tests)
- **Next expected change:** WF6 Telegram companion, WF7 handoff, WF8 safety parity

### 7.4 Session 2026-04-13 — WF6-WF8 implementation (Telegram, handoff, safety parity)

- **State:** WF6-WF8 implemented and verified. Workstream F is complete.
- **Meaningful accomplishment:**
  - **WF6 — Telegram bounded companion** (`app/services/telegram.py`):
    - Session bootstrap/reuse: `ChannelSession(channel_type="telegram")` + `TelegramConversationState`, reuses existing active sessions for the same chat_id
    - Message normalization: Telegram text → `ImportedSignal(signal_type="telegram_import")` with chat_id, message_id, provider provenance
    - Bounded context tracking: message count, bounded topic history (last 5), current topic updates
    - "What matters now" summary: reuses voice briefing focus-pack data, further truncated to 500 chars for mobile delivery
    - Handoff detection: keyword triggers (`review`, `approve`, `compare`, `detailed`, etc.) → workspace handoff
    - Shared-core routing: Telegram signals flow through same IntakeGraph as voice, `auto_send_blocked=True` always enforced
  - **WF7 — Cross-surface handoff** (`app/services/handoff.py`):
    - `create_handoff_from_voice()` and `create_handoff_from_telegram()`: persist `BriefingArtifact(briefing_type="channel_handoff")` with source_scope_metadata including channel, session, reason, topic, and pending items
    - Handoff records update the source ChannelSession metadata (handoff_created, artifact_id, reason)
    - `get_pending_handoffs()`: retrieves all channel_handoff artifacts for workspace visibility
    - `HandoffRecord` class with `to_dict()` serialization for API responses
  - **WF8 — Approval and safety parity** (`app/services/handoff.py`):
    - `verify_auto_send_blocked()`: asserts auto_send_blocked=True in any routing result
    - `verify_review_gate_preserved()`: asserts review path exists when review is needed
    - Safety proven at service level (all handoff records have auto_send_blocked=True) and API level (all responses enforce auto_send_blocked)
  - **REST APIs added:**
    - Telegram: `POST /telegram/sessions`, `GET /telegram/sessions/{id}`, `POST /telegram/sessions/{id}/messages`, `POST /telegram/sessions/{id}/what-matters-now`, `POST /telegram/sessions/{id}/handoff`, `GET /telegram/handoffs/pending`
    - Voice: `POST /voice/sessions/{id}/handoff`
- **Verification executed:**
  - 23 integration tests (Telegram): session bootstrap/reuse/operator-binding, message normalization/provenance/empty, context increments/topics/bounded, what-matters-now empty/data/shorter, handoff detection triggers/non-triggers/response, shared-core routing/auto_send_blocked — all pass
  - 11 API tests (Telegram): session create/get/404/reuse, message process/handoff-trigger/404/auto_send, what-matters-now empty/data/404 — all pass
  - 20 integration tests (handoff/safety): voice handoff artifact/context/session-update/serialization, Telegram handoff artifact/context/session-update, pending handoffs empty/voice/telegram/mixed, auto_send verification pass/fail/missing, review gate pass/fail/ok, handoff auto_send voice/telegram/all — all pass
  - Full backend suite: **430/430 pass**
- **Files created:**
  - `app/services/telegram.py` (new — Telegram companion service)
  - `app/services/handoff.py` (new — cross-surface handoff + safety parity)
  - `app/api/telegram.py` (new — Telegram REST API)
  - `tests/integration/test_telegram_companion.py` (new — 23 tests)
  - `tests/integration/test_cross_surface_handoff.py` (new — 20 tests)
  - `tests/api/test_telegram_api.py` (new — 11 tests)
- **Files modified:**
  - `app/api/voice.py` (handoff endpoint + import)
  - `app/main.py` (telegram router registration)
- **Next expected change:** Workstream F is complete. Live environment testing (Telegram bot provisioning, real audio) requires human dependencies.

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

- `TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession` — **Pass** (7 integration tests: session creation, operator binding, project context, channel identity, state linkage; 3 API tests: create/get/404)
- `TEST:Voice.Session.TranscriptBecomesStructuredSignal` — **Pass** (6 integration tests: signal creation, provenance, multiple segments, empty skip, index/timestamp preservation; 2 API tests: utterance submit)
- `TEST:Voice.Session.ContinuityPreservedWithinSession` — **Pass** (6 integration tests: topic updates, bounded topics, project merge, capped prompts, utterance count, nonexistent raises)
- `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions` — **Pass** (3 integration tests: review conditional edges, auto_send_blocked on routing)
- `TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant` — **Pass** (21 integration tests: formatting boundedness, data grounding, length enforcement, artifact persistence, latest-pack resolution, empty-state handling, section-count accuracy, context-response conciseness; 6 API tests: briefing with/without data, 404 handling, auto_send_blocked, context endpoint)
- `TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation` — **Pass** (4 integration tests: artifact creation, context preservation, channel session update, serialization; 1 API test: voice handoff endpoint)
- `TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary` — **Pass** (3 integration tests: empty state, bounded summary with data, shorter than voice briefing; 2 API tests: what-matters-now empty/with-data)
- `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded` — **Pass** (6 integration tests: review/approve/compare triggers, no-trigger for simple queries and notes, workspace URL; 1 API test: message triggers handoff)
- `TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace` — **Pass** (4 integration tests: pending handoffs empty/voice/telegram/mixed; 1 API test: pending handoffs endpoint)
- `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved` — **Pass** (4 integration tests: voice + Telegram both route through shared IntakeGraph to triage with auto_send_blocked)
- `TEST:ChannelSession.SummariesPersistWithTraceableOrigin` — **Pass** (5 integration tests: summary creation, completion marking, channel session update, utterance count, project references; 2 API tests: end session + summary)
- `TEST:Drafting.NoAutoSend.BoundaryPreserved` — **Pass** (2 API tests: auto_send_blocked even for explicit "send" utterances, voice + Telegram)
- `TEST:Security.NoAutoSend.GlobalBoundaryPreserved` — **Pass** (9 tests: voice service/API/handoff + Telegram service/API/handoff all enforce auto_send_blocked=True; verify_auto_send_blocked helper)
- `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` — **Pass** (3 tests: review gate verification pass/fail/ok; review conditional edges in VoiceSessionGraph)

### 8.2 Verification interpretation

WF1-WF8 verification is complete. 125 new tests pass across 8 work packages. All 14 TEST anchors are now fully proven. The voice session foundation, spoken briefing layer, Telegram companion, cross-surface handoff, and safety parity are all verified with auto_send_blocked enforced throughout. Full backend suite: 430/430 pass.

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

The recommended next implementation slice is:

1. **Workstream F is complete.** All 8 work packages (WF1-WF8) are implemented and verified.
2. Remaining work is **live environment validation** (human-dependent):
   - Telegram bot provisioning and secrets for live integration testing
   - Real audio pipeline testing (MLX inference, Gemma 4 models)
   - End-to-end voice-to-workspace handoff with real hardware
3. Future enhancement candidates:
   - WebSocket streaming for real-time voice (currently POST-per-utterance)
   - Telegram webhook integration for real bot updates
   - Visual persona rendering for voice mode

**Stable working anchor:** `WORKF:Progress.ImmediateNextSlice`

---

## 12. Pickup Guidance for the Next Session

When the next implementation session begins for Workstream F, the coding agent should:

1. **Note that WF1-WF8 are complete and verified** (430/430 tests pass).
2. The workstream is waiting on **human dependencies** for live environment validation:
   - Telegram bot provisioning (bot token, webhook setup)
   - Real audio hardware testing (MLX, Gemma 4 on M5 Max)
3. If picking up for enhancement work:
   - Review the services: `voice.py`, `briefing.py`, `telegram.py`, `handoff.py`
   - Review the APIs: `api/voice.py`, `api/telegram.py`
   - Review the graphs: `graphs/voice_session.py`
   - Run `pytest tests/ -v` to confirm baseline (expect 430 pass)

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

Workstream F is complete. All 8 work packages are implemented and verified with 125 new tests (430 total backend).

The voice and companion model is real: voice sessions bootstrap and normalize into structured signals, spoken briefings are bounded and grounded, Telegram is a bounded companion (not a second control room), cross-surface handoffs create workspace-visible artifacts, and auto_send_blocked is proven at every layer.

Remaining live-environment validation (Telegram bot provisioning, real audio inference) requires human dependencies that are clearly documented.

**Stable working anchor:** `WORKF:Progress.Conclus