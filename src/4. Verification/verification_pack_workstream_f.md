# Glimmer — Verification Pack: Workstream F Voice

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Workstream F Voice
- **Document Type:** Canonical Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Test Catalog, Requirements, Architecture, Build Plan, Testing Strategy, Workstream F Voice, Workstream E Verification Pack

---

## 1. Purpose

This document defines the **Workstream F verification pack** for **Glimmer**.

Its purpose is to prove that the voice and companion layer created by **Workstream F — Voice** is bounded, review-safe, continuity-preserving, and consistent with Glimmer’s main web workspace and shared assistant core.

Where Workstream E proves that the main operator workspace is usable and trustworthy, this pack proves that voice and Telegram-style companion interaction can extend that workspace safely without becoming a hidden alternate control path.

**Stable verification anchor:** `TESTPACK:WorkstreamF.ControlSurface`

---

## 2. Role of the Workstream F Pack

This pack exists to verify the implementation outcomes expected from the Voice workstream, including:

- voice-session bootstrap and continuity,
- transcript ingestion into structured internal artifacts,
- voice-to-core-workflow routing,
- spoken briefing and response behavior,
- review-safe handling of voice-derived actions and interpretations,
- Telegram companion boundedness and handoff behavior,
- channel-session summaries and continuity artifacts,
- and workspace-integrated voice/companion handoff behavior.

This pack is the proof surface that stops Glimmer’s conversational modes from quietly becoming ungoverned side channels.

**Stable verification anchor:** `TESTPACK:WorkstreamF.Role`

---

## 3. Relationship to the Control Surface

This verification pack is derived from and aligned to:

- the **Agentic Delivery Framework**, especially its authority model, work-package operating model, verification model, evidence-of-completion posture, and traceability expectations,
- the **Testing Strategy Companion**, especially automation-first proof, graph/state-machine testing, Playwright/browser verification where appropriate, and explicit `ManualOnly` / `Deferred` handling,
- the **Glimmer Agentic Delivery Document Set**, which explicitly defines `verification-pack-workstream-f.md` as part of the canonical verification family,
- the **Glimmer Requirements**, especially voice interaction, Telegram mobile presence, project memory, state continuity, explainability, prepared briefings, and human approval boundaries,
- the latest **Architecture** state, especially the voice layering strategy, voice interaction architecture, Telegram companion channel and UX, channel-session model, review-gate architecture, and shared-core workflow boundaries,
- the **Build Plan**, **Build Strategy and Scope**, and **Workstream F — Voice**, which define voice as a layered mode built on the strong non-voice core,
- the **Glimmer Testing Strategy** and **Workstream G — Testing and Regression**, which define graph verification, companion/voice verification hardening, and explicit manual/deferred handling for environment-bound cases,
- the **Governance and Process** document, which requires evidence-backed completion and surfaced drift for meaningful work,
- and the current **Test Catalog**, which already defines the core voice, Telegram, review-boundary, and no-auto-send `TEST:` anchors this pack should organize and extend.

**Stable verification anchor:** `TESTPACK:WorkstreamF.ControlSurfaceAlignment`

---

## 4. Why This Pack Is Load-Bearing

The architecture is explicit that voice and Telegram are important, but they must remain **companion modes layered onto the same memory, review, and orchestration core** rather than becoming separate assistant products or alternative authority paths.

Workstream F is where that architectural rule becomes real through:

- voice-session lifecycle handling,
- transcript normalization,
- spoken briefing behavior,
- routing from voice into shared core workflows,
- review-safe handling of voice-derived artifacts,
- Telegram bounded interaction behavior,
- cross-surface handoff,
- and session-summary/continuity support.

If this pack is weak, Glimmer may still feel smooth conversationally while actually depending on:

- hidden session-only memory,
- unreviewed action interpretation,
- side-channel behavior that bypasses the workspace,
- or companion interactions that overreach beyond their safe scope.

That is exactly what this pack is meant to prevent.

**Stable verification anchor:** `TESTPACK:WorkstreamF.Rationale`

---

## 5. Workstream F Verification Scope

### 5.1 In scope

This pack covers proof for the following Voice concerns:

- voice session bootstrap and bounded lifecycle,
- short-horizon voice continuity state,
- transcript and utterance normalization into structured artifacts,
- routing from voice into shared internal workflows,
- spoken response and briefing usefulness at a bounded level,
- Telegram companion bounded interaction behavior,
- cross-surface handoff into the workspace,
- review-safe handling of voice- and Telegram-derived outputs,
- session summary persistence and handoff continuity,
- and no-auto-send / approval-boundary preservation across companion modes.

### 5.2 Out of scope

This pack does **not** attempt to prove:

- low-level provider normalization already covered by Workstream C,
- full browser-workspace richness already covered by Workstream E,
- subjective production-grade voice quality beyond explicitly named manual checks,
- or unrestricted autonomous desktop/OS control by voice.

Those are outside this workstream or belong to broader release decisions.

**Stable verification anchor:** `TESTPACK:WorkstreamF.Scope`

---

## 6. Source `TEST:` Anchors Included in This Pack

The Workstream F pack is built primarily from the voice-and-companion, security-and-approval, and selected drafting/review scenario groups in the canonical Test Catalog, with a small number of workstream-specific extensions where needed.

### 6.1 Canonical voice and companion anchors already defined in the Test Catalog

#### `TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary`
- **Scenario name:** Telegram “what matters now” flow returns bounded companion summary
- **Layers:** `graph`, `contract`, `integration`
- **Role in this pack:** Proves Telegram gives useful mobile support without becoming a hidden control room.

#### `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded`
- **Scenario name:** Telegram interaction hands off to workspace when richer review is required
- **Layers:** `graph`, `browser`, `contract`
- **Role in this pack:** Proves Telegram does not overreach beyond its safe scope.

#### `TEST:Voice.Session.TranscriptBecomesStructuredSignal`
- **Scenario name:** Voice transcript becomes structured internal artifact
- **Layers:** `integration`, `graph`
- **Role in this pack:** Proves spoken input enters the core model rather than remaining ephemeral.

#### `TEST:Voice.Session.ContinuityPreservedWithinSession`
- **Scenario name:** Voice session preserves short-horizon continuity
- **Layers:** `integration`, `graph`
- **Role in this pack:** Proves voice interaction is not a sequence of stateless one-shots.

#### `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions`
- **Scenario name:** Voice-derived meaningful actions still require review where appropriate
- **Layers:** `graph`, `integration`
- **Role in this pack:** Proves voice does not bypass approval discipline.

### 6.2 Canonical security/drafting anchors already defined in the Test Catalog

#### `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- **Scenario name:** Draft workflow does not create outbound send behavior
- **Layers:** `graph`, `api`, `integration`
- **Role in this pack:** Proves companion and voice pathways still respect the same no-auto-send boundary.

#### `TEST:Security.NoAutoSend.GlobalBoundaryPreserved`
- **Scenario name:** No-auto-send boundary is preserved across all channels
- **Layers:** `integration`, `graph`, `api`
- **Role in this pack:** Proves companion modes do not create hidden externalization paths.

#### `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`
- **Scenario name:** Externally meaningful actions require structured approval
- **Layers:** `graph`, `api`, `browser`
- **Role in this pack:** Proves review-gate protection stays intact when interaction starts in a conversational channel.

### 6.3 Additional Workstream F-specific anchors introduced by this pack

#### `TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession`
- **Scenario name:** Voice session bootstrap binds the correct operator and session context
- **Primary layers:** `integration`, `api`
- **Primary drivers:** `REQ:VoiceInteraction`, `REQ:StateContinuity`, `ARCH:VoiceInteractionArchitecture`, `ARCH:ChannelSessionModel`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove voice starts inside the correct bounded identity/session context.

#### `TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant`
- **Scenario name:** Spoken briefing output is bounded, relevant, and aligned to available project context
- **Primary layers:** `graph`, `integration`, `manual_only`
- **Primary drivers:** `REQ:PreparedBriefings`, `REQ:Explainability`, `ARCH:VoiceLayeringStrategy`, `ARCH:VoiceInteractionArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove voice output is useful for listening rather than bloated or detached from the real state model.

#### `TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation`
- **Scenario name:** Voice interaction handoff creates a workspace-visible continuation path
- **Primary layers:** `graph`, `browser`, `integration`
- **Primary drivers:** `REQ:StateContinuity`, `REQ:HumanApprovalBoundaries`, `ARCH:VoiceInteractionArchitecture`, `ARCH:UiSurfaceMap`, `ARCH:TelegramCompanionUx`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove the operator can move from voice into richer workspace review without losing context.

#### `TEST:ChannelSession.SummariesPersistWithTraceableOrigin`
- **Scenario name:** Voice and companion session summaries persist with traceable origin
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:ProjectMemory`, `REQ:StateContinuity`, `ARCH:ChannelSessionModel`, `ARCH:AuditAndTraceLayer`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`, `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove channel summaries are durable artifacts, not transient runtime leftovers.

#### `TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace`
- **Scenario name:** Telegram-generated review-needed state becomes visible in the main workspace
- **Primary layers:** `graph`, `browser`, `integration`
- **Primary drivers:** `REQ:TelegramMobilePresence`, `REQ:HumanApprovalBoundaries`, `ARCH:TelegramCompanionChannel`, `ARCH:ReviewGateArchitecture`, `ARCH:UiSurfaceMap`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`, `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove review-needed outcomes do not remain stranded in Telegram.

#### `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved`
- **Scenario name:** Voice and Telegram both route into the same shared core review and planning model
- **Primary layers:** `graph`, `integration`
- **Primary drivers:** `REQ:VoiceInteraction`, `REQ:TelegramMobilePresence`, `ARCH:VoiceLayeringStrategy`, `ARCH:TelegramCompanionChannel`, `ARCH:LangGraphTopology`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove companion modes are extensions of the core, not divergent implementations.

**Stable verification anchor:** `TESTPACK:WorkstreamF.IncludedTests`

---

## 7. Workstream F Pack Entry Table

| TEST Anchor | Scenario | Layer | Automation Status | Pack Priority | Notes |
|---|---|---|---|---|---|
| `TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession` | Voice session bootstrap binds the correct operator and session context | `integration`, `api` | Planned | Critical | Session-boundary baseline |
| `TEST:Voice.Session.TranscriptBecomesStructuredSignal` | Voice transcript becomes structured internal artifact | `integration`, `graph` | Planned | Critical | Structured-input baseline |
| `TEST:Voice.Session.ContinuityPreservedWithinSession` | Voice session preserves short-horizon continuity | `integration`, `graph` | Planned | High | Continuity baseline |
| `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions` | Voice-derived meaningful actions still require review where appropriate | `graph`, `integration` | Planned | Critical | Review-safety baseline |
| `TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant` | Spoken briefing output is bounded, relevant, and aligned to available project context | `graph`, `integration`, `manual_only` | Planned | Medium | Some human judgment likely useful |
| `TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation` | Voice interaction handoff creates a workspace-visible continuation path | `graph`, `browser`, `integration` | Planned | High | Cross-surface continuity |
| `TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary` | Telegram “what matters now” flow returns bounded companion summary | `graph`, `contract`, `integration` | Planned | High | Mobile companion baseline |
| `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded` | Telegram interaction hands off to workspace when richer review is required | `graph`, `browser`, `contract` | Planned | Critical | Prevents overreach |
| `TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace` | Telegram-generated review-needed state becomes visible in the main workspace | `graph`, `browser`, `integration` | Planned | High | Cross-surface review parity |
| `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved` | Voice and Telegram both route into the same shared core review and planning model | `graph`, `integration` | Planned | Critical | Shared-core discipline |
| `TEST:ChannelSession.SummariesPersistWithTraceableOrigin` | Voice and companion session summaries persist with traceable origin | `integration` | Planned | High | Continuity artifacts |
| `TEST:Drafting.NoAutoSend.BoundaryPreserved` | Draft workflow does not create outbound send behavior | `graph`, `api`, `integration` | Planned | Critical | Safety boundary reuse |
| `TEST:Security.NoAutoSend.GlobalBoundaryPreserved` | No-auto-send boundary is preserved across all channels | `integration`, `graph`, `api` | Planned | Critical | Cross-channel safety proof |
| `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` | Externally meaningful actions require structured approval | `graph`, `api`, `browser` | Planned | Critical | Approval parity |

**Stable verification anchor:** `TESTPACK:WorkstreamF.EntryTable`

---

## 8. Expected Automation Shape

### 8.1 Integration and graph proof by default

Most Workstream F proof should be implemented through integration and graph/workflow testing because this workstream is fundamentally about:

- session-state handling,
- transcript/signal normalization,
- routing into shared workflows,
- review safety,
- and continuity/handoff behavior.

### 8.2 Browser proof where handoff and review visibility matter

Where companion or voice behavior is only trustworthy if it becomes visible in the main workspace, browser proof should verify that:

- handoff links or navigation work,
- review-needed state becomes visible in the workspace,
- and the operator can continue safely from companion interaction into the canonical control surface.

### 8.3 Explicit `manual_only` use for environment-bound checks

A small amount of `ManualOnly` classification is reasonable here for:

- subjective spoken-briefing quality checks,
- live audio/device/network behavior,
- or environment-specific validation that is not yet practical to automate.

These should remain explicit and evidence-backed rather than implied.

### 8.4 No conversational-theater proof

This pack should prioritize:

- structure,
- routing,
- review safety,
- handoff continuity,
- and boundedness,

rather than vague testing of whether Glimmer “sounds smart.”

**Stable verification anchor:** `TESTPACK:WorkstreamF.AutomationShape`

---

## 9. Environment Assumptions

The Workstream F pack assumes the foundation, memory, connector, assistant-core, and main workspace substrate are already in place.

### 9.1 Required assumptions

Expected baseline assumptions include:

- backend runtime and persistence substrate already working,
- controlled graph/application test harnesses,
- executable browser harness for workspace handoff proof,
- session-state persistence available,
- and, where needed, a controllable voice/Telegram test boundary or fixtures.

### 9.2 Core proof should not depend on live production infrastructure

This pack should not require live production Google, Microsoft, or full production voice/Telegram environments for its core proof.

Controlled fixtures, mocks, or test boundaries should be sufficient for the main safety and continuity behaviors.

### 9.3 Explicit environment-bound exceptions

Where real-device, real-network, or live-audio behavior materially matters, those checks may be marked `ManualOnly` or `Deferred`, but they must be named explicitly and not confused with automated proof.

### 9.4 Earlier proof should already exist

This pack assumes Workstream E has already established that the workspace control surface is trustworthy enough that handoff failures can be interpreted as voice/companion integration problems rather than baseline UI instability.

**Stable verification anchor:** `TESTPACK:WorkstreamF.EnvironmentAssumptions`

---

## 10. Execution Guidance

### 10.1 When to run this pack

This pack should normally be run:

- after meaningful voice-session or Telegram routing changes,
- after session-state or continuity changes,
- after handoff behavior changes,
- after review-safe handling changes for voice/companion outputs,
- before declaring Workstream F substantially complete,
- and before claiming that Glimmer’s mobile/spoken modes are safe enough for regular use.

### 10.2 Failure handling

If this pack fails:

- the main workspace may still be trustworthy, but companion/voice claims should be treated cautiously,
- the failure should usually be resolved before broader “anywhere interaction” claims are made,
- and progress reporting should explicitly state whether the problem affects session binding, structured input capture, review safety, handoff continuity, or cross-channel parity.

### 10.3 Relationship to later packs

This Workstream F pack proves voice and companion behavior in the workstream context.

The later release pack should build on it rather than rediscovering conversational/companion failures indirectly.

**Stable verification anchor:** `TESTPACK:WorkstreamF.ExecutionGuidance`

---

## 11. Evidence Expectations

When the Workstream F pack is executed, evidence reporting should capture at minimum:

- execution date/time,
- environment posture used,
- which included `TEST:` anchors were executed,
- pass/fail outcome,
- any `ManualOnly` checks performed,
- any `Deferred` entries and why,
- and a brief statement of whether the voice and companion layer is considered bounded and trustworthy enough for regular extension of the main workspace.

This should be summarized in the relevant Workstream F progress file and referenced in broader phase-exit or regression summaries where appropriate.

**Stable verification anchor:** `TESTPACK:WorkstreamF.EvidenceExpectations`

---

## 12. Operational Ready Definition for This Pack

The Workstream F verification pack should be considered operationally established when:

1. all included `TEST:` anchors are defined and mapped,
2. voice-session bootstrap and continuity proof exists,
3. transcript-to-structured-artifact proof exists,
4. Telegram bounded-summary and handoff proof exists,
5. workspace-visible continuation and review-surfacing proof exists,
6. shared-core parity proof exists,
7. no-auto-send and approval-boundary proof exists,
8. and the pack can be run repeatably against controlled fixtures, workflow harnesses, and browser handoff checks, with any live-audio exceptions explicitly classified.

At that point, Workstream F has a meaningful verification surface that release-confidence work can trust.

**Stable verification anchor:** `TESTPACK:WorkstreamF.DefinitionOfOperationalReady`

---

## 13. Relationship to Later Packs

This pack completes the workstream-pack family for the main Glimmer product surfaces.

Later packs should build on it as follows:

- the **data-integrity** pack should absorb the most important continuity, traceability, and origin-linkage protections that matter across channels,
- the **release** pack should compose representative proof from workspace, assistant-core, connector, and companion layers,
- and ongoing browser/graph regression should treat the most important handoff and review-parity behaviors here as durable confidence checks.

This progression is consistent with the Glimmer build plan, workstream map, and Workstream G verification-estate design.

**Stable verification anchor:** `TESTPACK:WorkstreamF.RelationshipToLaterPacks`

---

## 14. Final Note

If Workstream F is implemented but not properly verified, Glimmer may feel convenient while quietly opening up exactly the kind of hidden side-channel behavior the architecture is trying to avoid.

That is the danger this pack is meant to prevent.

Its job is to prove that Glimmer’s voice and companion layer is:

- bounded,
- continuity-preserving,
- review-safe,
- handoff-friendly,
- and genuinely subordinate to the same trustworthy core as the main workspace.

**Stable verification anchor:** `TESTPACK:WorkstreamF.Conclusion`
