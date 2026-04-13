---
applyTo: "apps/backend/**/voice/**/*.py,apps/backend/**/telegram/**/*.py,apps/backend/**/channels/**/*.py,apps/backend/**/sessions/**/*.py,apps/web/**/voice/**/*.{ts,tsx,js,jsx},apps/web/**/telegram/**/*.{ts,tsx,js,jsx},apps/web/**/companion/**/*.{ts,tsx,js,jsx}"
---

# Glimmer — Voice and Companion Module Instructions

## Purpose

This instruction file defines the module-scoped rules for Glimmer voice interaction, Telegram companion behavior, channel-session handling, and cross-surface handoff implementation.

It supplements the global `.github/copilot-instructions.md` file and applies specifically to:

- voice session code,
- transcript ingestion and voice routing,
- Telegram companion connector and session code,
- channel-session models and continuity logic,
- web voice-console and companion-related UI surfaces,
- and cross-surface handoff behavior.

These rules are stricter than generic conversation or chatbot guidance because Glimmer’s voice and Telegram features are companion modes layered on top of a review-first project system. They must not become alternate unsafe control paths.

Framework alignment: Agentic Delivery Framework and Testing Strategy Companion.

---

## 1. Authority and Scope Rule

When working in this module area, the agent must stay aligned to the following control surfaces in order:

1. Requirements
2. Architecture
3. Build Plan
4. Verification
5. Global Copilot instructions
6. This module instruction file
7. Workstream working documents
8. Code

Do not let generic assistant-chat patterns silently override Glimmer’s documented review-first, workspace-first operating model.

---

## 2. What This Module Must Preserve

Voice and companion work must preserve these core Glimmer properties:

- **web workspace as the canonical review surface**,
- **voice layered onto the same memory and orchestration core**,
- **Telegram as a bounded companion channel rather than a full control-room replacement**,
- **channel-session continuity without hidden long-term shadow memory**,
- **review-safe handling of voice- and Telegram-derived outputs**,
- **explicit handoff into richer workspace review where needed**,
- **no-auto-send behavior**,
- and **provenance and session traceability for companion interactions**.

These are load-bearing product and safety rules.

---

## 3. Core Mode Rules

### 3.1 Companion modes extend the core; they do not replace it

Voice and Telegram exist to extend Glimmer’s usefulness when the operator is mobile, thinking aloud, or away from the main workspace.

They do not replace:

- the main review queue,
- the main draft workspace,
- the main project workspace,
- or the main provenance-visible triage surface.

### 3.2 All companion behavior must route through shared core flows

Do not create separate “Telegram logic” or “voice logic” that independently reimplements:

- project classification,
- prioritization,
- draft behavior,
- review-state handling,
- or memory mutation rules.

Companion and voice entrypoints should route into the same shared triage, planner, drafting, and review models where possible.

### 3.3 No lighter safety model for companion channels

Do not assume that because an interaction starts on Telegram or via voice, it can bypass:

- review gates,
- no-auto-send boundaries,
- provenance rules,
- or accepted-vs-interpreted separation.

---

## 4. Telegram Companion Rules

### 4.1 Telegram is a bounded companion surface

Telegram should support lightweight interaction such as:

- “what matters most today?”
- concise project status checks,
- quick note capture,
- quick clarification questions,
- and follow-up prompts that can later hand off to the workspace.

Do not expand Telegram into an unbounded replacement for the main web app.

### 4.2 Telegram messages become internal signal/session artifacts

Telegram-origin messages must normalize into bounded internal artifacts such as:

- `ImportedSignal`,
- `ChannelSession`,
- `TelegramConversationState`,
- and downstream interpreted artifacts where appropriate.

Do not leave meaningful Telegram interaction trapped in transient bot state.

### 4.3 Telegram replies must stay concise and context-aware

Telegram output should be optimized for mobile conversational usefulness:

- concise,
- high-signal,
- context-aware,
- and willing to hand off when the topic becomes too complex for safe inline handling.

### 4.4 Telegram should hand off, not overreach

When the operator needs:

- draft comparison,
- deeper provenance inspection,
- review of ambiguous interpretation,
- or rich project context,

Telegram should direct the operator to the relevant workspace surface rather than trying to do everything inside chat.

---

## 5. Voice Interaction Rules

### 5.1 Voice is a mode, not a separate product

Voice should be treated as a conversational operating mode over the same Glimmer system, not a separate assistant persona or standalone voice product.

### 5.2 Voice outputs should be spoken-useful, not essay-like

Spoken outputs should be:

- concise,
- structured for listening,
- high-signal,
- and appropriate for briefings, updates, and clarifications.

Do not generate long visually optimized paragraphs and treat them as acceptable spoken responses.

### 5.3 Spoken input must become structured internal state

Transcript segments, utterances, and spoken updates must route into bounded structured artifacts rather than remaining only as ephemeral session text.

### 5.4 Voice must hand off to the workspace when required

If the interaction requires:

- comparison of alternatives,
- approval of ambiguous classification,
- detailed draft review,
- or rich provenance/context inspection,

voice should hand off cleanly into the web workspace rather than faking a fully safe spoken-only resolution.

### 5.5 Voice infrastructure baseline

The voice layer targets **local multi-model inference using MLX on Apple Silicon** (reference hardware: M5 Max 128 GB unified memory).

The expected model topology is:

- **Voice I/O:** Gemma 4 E4B (native audio, 4.5B parameters) for low-latency, prosody-aware spoken interaction.
- **Reasoning tasks triggered from voice:** Gemma 4 31B or 26B A4B, routed through the shared orchestration core.

When implementing voice infrastructure code:

- treat the inference layer as a bounded dependency behind an abstraction,
- do not hardwire specific model checkpoint paths into session or routing logic,
- keep the pipeline shape (ASR → reasoning → TTS) and native audio shape (speech-to-speech) structurally separable so the system can use either or both,
- and do not introduce cloud voice service dependencies without explicit approval.

See `ARCH:VoiceInfrastructureDirection`, `ARCH:VoicePipelineArchitecture`, and `ARCH:LocalInferenceBaseline` for the full architecture context.

---

## 6. Channel Session and Continuity Rules

### 6.1 Session continuity is bounded and explicit

Maintain short-horizon session continuity for Telegram and voice, but do not create hidden shadow memory that bypasses the documented domain and summary model.

### 6.2 Channel sessions are first-class state

Use channel-session concepts explicitly, including where relevant:

- `ChannelSession`,
- `TelegramConversationState`,
- `VoiceSessionState`,
- session summaries,
- and continuation metadata.

### 6.3 Continuity should assist orientation, not invent truth

Session continuity may help the operator continue the topic, preserve recent references, or recover interrupted interaction.

It must not silently promote uncertain spoken/chat inferences into accepted project memory.

### 6.4 Channel handoff should preserve useful continuity

When handing from Telegram or voice into the workspace, preserve enough continuity that the operator can tell:

- what the conversation was about,
- what was inferred,
- what remains pending,
- and what review is needed next.

---

## 7. Review and Approval Rules

### 7.1 Review gates remain mandatory

Voice and Telegram flows must respect the same review requirements as the rest of Glimmer.

This includes at least:

- ambiguous project classification,
- uncertain stakeholder interpretation,
- materially uncertain action extraction,
- significant memory reinterpretation,
- and draft outputs that still require operator review.

### 7.2 Companion channels must not silently externalize action

Do not implement behavior that:

- sends external email,
- commits calendar changes,
- sends operator-like responses to third parties,
- or mutates accepted project state with no review path

just because the interaction came through Telegram or voice.

### 7.3 Review requests should be visible cross-surface

If a Telegram or voice interaction creates a review-needed state, that state must be visible in the main workspace review surface rather than remaining stranded in the originating channel.

---

## 8. UI Rules for Voice and Companion Surfaces

### 8.1 Voice console should feel integrated

The voice console in the web app should feel like part of the same control room as Today, Triage, Project, Drafts, and Review.

Do not present it as an isolated experimental toy surface.

### 8.2 Companion-related UI should emphasize handoff and state clarity

Where the UI shows Telegram or voice session state, it should help the operator understand:

- current topic,
- recent summary,
- pending review items,
- and the route back into the main workspace.

### 8.3 Do not hide important meaning in streaming theatrics

Live voice/chat motion is acceptable where useful, but not at the expense of:

- review clarity,
- provenance visibility,
- or actionability.

### 8.4 Persona support must remain bounded here too

Persona presentation may support warmth and continuity in Telegram or voice-related UI, but it must not dominate the task surface or obscure pending review/action state.

---

## 9. Data and Provenance Rules for Companion Modes

### 9.1 Preserve origin and session context

Telegram and voice-origin artifacts should preserve:

- channel type,
- session identity,
- timestamps,
- linked operator context,
- and origin metadata needed for traceability.

### 9.2 Voice/Telegram artifacts still belong in the core memory model

Do not create a separate hidden memory universe for companion channels. Their meaningful artifacts should connect to the same source, interpreted, accepted, and summary layers as the rest of the product.

### 9.3 Summaries and handoffs must remain traceable

If a voice session creates a session summary or a Telegram exchange creates a captured note, the system should support traceable linkage back to the originating interaction state.

---

## 10. Security and Privacy Rules

### 10.1 No softened privacy posture for convenience

Do not weaken privacy boundaries just because Telegram or voice workflows are more conversational.

### 10.2 Channel credentials stay bounded

Do not log or expose Telegram bot secrets, voice-service credentials, tokens, or session secrets in prompts, DTOs, or casual debug output.

### 10.3 Companion channels must respect least privilege

If a feature requires additional Telegram or voice-service permissions/capabilities, surface that explicitly rather than expanding scope silently.

### 10.4 Manual and environment-dependent behavior should be explicit

Where real-device, real-network, or live audio behavior introduces environment-specific risk, document it explicitly rather than pretending it is fully controlled.

---

## 11. Testing Expectations for This Module

When editing voice or companion code, the default proof target should include as appropriate:

- **integration tests** for session-state handling, transcript/signal normalization, and persistence,
- **graph/workflow tests** for routing into shared core flows,
- **contract/integration tests** for Telegram boundaries,
- **browser tests** for voice-console and review handoff behavior where applicable,
- and **explicit `ManualOnly` / `Deferred` checks** for environment-bound audio/device/network scenarios.

### 11.1 Companion-specific proof rules

- Telegram changes must prove bounded session handling and safe routing into internal artifacts.
- Voice changes must prove transcript/utterance routing into structured state.
- Cross-surface changes must prove handoff continuity.
- Review-related changes must prove companion modes do not bypass the main approval model.
- Any messaging-related behavior must continue to respect no-auto-send boundaries.

### 11.2 Do not mark companion-mode work complete without honest proof status

If meaningful voice or Telegram behavior changed and there is no executed proof or explicit manual/deferred classification, the work is not done.

---

## 12. Preferred Voice/Companion Session Workflow

When working in this module area, the default session sequence should be:

1. identify relevant `REQ:` anchors,
2. identify relevant `ARCH:` anchors,
3. identify relevant `PLAN:` anchors,
4. inspect current channel/session, routing, and handoff boundaries,
5. implement one bounded voice or companion slice,
6. run the relevant proof,
7. update the workstream progress file,
8. report assumptions, blockers, and evidence clearly.

---

## 13. What to Do When the Docs Are Incomplete

If voice or companion work requires a rule that does not yet have a stable anchor:

1. do not invent the interaction architecture silently,
2. propose the missing anchor,
3. make only the smallest safe implementation move,
4. and record the gap in the relevant working document.

Typical examples include:

- a new handoff-state rule,
- a new voice-session summary requirement,
- a new Telegram clarification-state concept,
- or a new cross-surface review pattern.

---

## 14. Anti-Patterns to Avoid in This Module

Do not:

- turn Telegram into a full hidden control room,
- let voice become a separate ungoverned assistant path,
- keep session meaning only in transient runtime memory,
- bypass review gates because chat feels conversational,
- create voice or Telegram-specific business logic that diverges from the shared core model,
- imply autonomous external action,
- or make companion surfaces feel more authoritative than the workspace.

---

## 15. Final Rule

When in doubt, make companion behavior more:

- bounded,
- review-safe,
- continuity-preserving,
- handoff-friendly,
- and aligned to the same core system as the web workspace.

Do not optimize for magical assistant theater.
Optimize for useful mobility and spoken convenience without sacrificing trust, structure, or control.
