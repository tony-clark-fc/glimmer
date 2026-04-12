# Glimmer — Workstream C Connectors Design and Implementation Progress

## Document Metadata

- **Document Title:** Glimmer — Workstream C Connectors Design and Implementation Progress
- **Document Type:** Working Progress Document
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** C — Connectors
- **Primary Companion Documents:** Workstream C Plan, Requirements, Architecture, Verification, Governance and Process

---

## 1. Purpose

This document is the active progress and evidence record for **Workstream C — Connectors**.

Its purpose is to record the current implementation state of the workstream in a way that supports:

- session-to-session continuity,
- evidence-backed status reporting,
- human review,
- and clean future agent pickup without re-discovery.

This file is not the source of architecture or requirement truth. It records **execution truth**.

**Stable working anchor:** `WORKC:Progress.ControlSurface`

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

**Stable working anchor:** `WORKC:Progress.StatusModel`

---

## 3. Current Overall Status

- **Overall Workstream Status:** `Designed`
- **Current Confidence Level:** Planning complete, implementation not yet started
- **Last Meaningful Update:** Initial creation of progress surface
- **Ready for Coding:** Yes, once Workstream A substrate and the core Workstream B memory structures are materially in place

### Current summary

Workstream C has a complete planning and verification posture, including:

- canonical Requirements,
- the current Architecture control surface,
- a Build Plan and Workstream C workstream document,
- canonical verification assets including the Workstream C pack and the cross-cutting Data Integrity and Release packs,
- global and module-scoped agent instructions,
- and the paired Workstream C implementation plan.

The workstream is therefore ready to move from planning into actual connector and normalization implementation as soon as the foundation/runtime substrate and the core memory spine are sufficiently real.

**Stable working anchor:** `WORKC:Progress.CurrentOverallStatus`

---

## 4. Control Anchors in Scope

### 4.1 Requirements anchors

- `REQ:MessageIngestion`
- `REQ:MultiAccountProfileSupport`
- `REQ:TelegramMobilePresence`
- `REQ:PrivacyAndLeastPrivilege`
- `REQ:SafeBehaviorDefaults`
- `REQ:TraceabilityAndAuditability`
- `REQ:StateContinuity`

### 4.2 Architecture anchors

- `ARCH:ApiFirstIntegration`
- `ARCH:ConnectorIsolation`
- `ARCH:GmailConnector`
- `ARCH:GoogleCalendarConnector`
- `ARCH:MicrosoftGraphConnector`
- `ARCH:TelegramConnector`
- `ARCH:ManualImportBoundary`
- `ARCH:NormalizationPipeline`
- `ARCH:AccountProvenanceModel`
- `ARCH:ConnectedAccountModel`
- `ARCH:TelegramCompanionChannel`
- `ARCH:LeastPrivilegeModel`
- `ARCH:NoAutoSendPolicy`
- `ARCH:ReviewGateArchitecture`
- `ARCH:SystemBoundaries`

### 4.3 Build-plan anchors

- `PLAN:WorkstreamC.Connectors`
- `PLAN:WorkstreamC.Objective`
- `PLAN:WorkstreamC.InternalSequence`
- `PLAN:WorkstreamC.VerificationExpectations`
- `PLAN:WorkstreamC.DefinitionOfDone`

### 4.4 Verification anchors

- `TEST:Connector.Framework.ProviderBoundaryIsolation`
- `TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile`
- `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount`
- `TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext`
- `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread`
- `TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext`
- `TEST:Connector.ManualImport.LabelingAndRouting`
- `TEST:Connector.Telegram.InboundBecomesBoundedSignal`
- `TEST:Connector.Normalization.PersistBeforeInterpretation`
- `TEST:Connector.IntakeHandoff.BoundedReferenceFlow`
- `TEST:Connector.SyncFailure.VisibleState`
- `TEST:Connector.Security.ReadFirstNoAutoSendPreserved`

**Stable working anchor:** `WORKC:Progress.ControlAnchors`

---

## 5. Work Package Status Table

| Work Package | Title | Status | Verification Status | Notes |
|---|---|---|---|---|
| WC1 | Connector framework baseline | `Designed` | Not started | First real connector substrate slice |
| WC2 | Connected-account execution context resolution | `Designed` | Not started | Makes multi-account support operational |
| WC3 | Gmail normalization path | `Designed` | Not started | Sensible first provider slice |
| WC4 | Google Calendar normalization path | `Designed` | Not started | Calendar/source-context semantics |
| WC5 | Microsoft mail normalization path | `Designed` | Not started | Multi-provider baseline |
| WC6 | Microsoft calendar normalization path | `Designed` | Not started | Event-context preservation |
| WC7 | Manual import path | `Designed` | Not started | Explicit unsupported-channel fallback |
| WC8 | Telegram companion intake path | `Designed` | Not started | Companion intake boundary |
| WC9 | Connector-to-intake bounded handoff | `Designed` | Not started | Critical boundary between integration and assistant core |
| WC10 | Sync-state, failure visibility, and read-first safeguards | `Designed` | Not started | Failure transparency and safety boundary |

**Stable working anchor:** `WORKC:Progress.PackageStatusTable`

---

## 6. What Already Exists Before Coding Starts

The following substantial control and support artifacts already exist and reduce execution ambiguity for Workstream C:

### 6.1 Planning and architecture surfaces

- Requirements document
- current Architecture control surface
- Build Plan
- Workstream C detailed build-plan document
- Governance and Process document

### 6.2 Verification surfaces

- `TEST_CATALOG.md`
- `verification-pack-workstream-c.md`
- `verification-pack-data-integrity.md`
- `verification-pack-release.md`
- upstream smoke and Workstream A/B packs already prepared
- downstream Workstream D/E/F packs already prepared

### 6.3 Operational support surfaces

- global copilot instructions
- backend/orchestration module instructions
- data/retrieval module instructions
- connectors module instructions
- testing/verification module instructions
- voice/companion module instructions
- Agent Skills README
- Agent Tools README

### 6.4 Workstream execution surfaces

- Workstream C implementation plan
- this Workstream C progress file

This means connector implementation can begin with unusually high clarity once the runtime and memory substrate are materially available.

**Stable working anchor:** `WORKC:Progress.PreexistingAssets`

---

## 7. Execution Log

This section should be updated incrementally during implementation.

### 7.1 Initial entry

- **State:** No code implementation recorded yet.
- **Meaningful accomplishment:** Workstream C planning, verification, and operational support surfaces are complete enough to begin execution cleanly once Foundation and core Domain/Memory structures are sufficiently real.
- **Next expected change:** Stand up the connector framework baseline and the first provider slice, most likely Gmail normalization.

**Stable working anchor:** `WORKC:Progress.ExecutionLog`

---

## 8. Verification Log

This section records **executed** verification, not merely intended verification.

### 8.1 Current verification state

- `TEST:Connector.Framework.ProviderBoundaryIsolation` — Not executed yet
- `TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile` — Not executed yet
- `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount` — Not executed yet
- `TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext` — Not executed yet
- `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread` — Not executed yet
- `TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext` — Not executed yet
- `TEST:Connector.ManualImport.LabelingAndRouting` — Not executed yet
- `TEST:Connector.Telegram.InboundBecomesBoundedSignal` — Not executed yet
- `TEST:Connector.Normalization.PersistBeforeInterpretation` — Not executed yet
- `TEST:Connector.IntakeHandoff.BoundedReferenceFlow` — Not executed yet
- `TEST:Connector.SyncFailure.VisibleState` — Not executed yet
- `TEST:Connector.Security.ReadFirstNoAutoSendPreserved` — Not executed yet

### 8.2 Verification interpretation

The verification design is ready, but no executable connector or normalization proof has been recorded yet. Therefore the workstream remains in a pre-implementation state.

**Stable working anchor:** `WORKC:Progress.VerificationLog`

---

## 9. Known Risks and Watchpoints

### 9.1 Risk — Provider semantics get flattened

This is the most likely shortcut that would quietly damage provenance and later classification quality.

### 9.2 Risk — Connector logic leaks into business logic

If connectors start classifying, prioritizing, or drafting, the boundary between integration and assistant-core logic will be muddled.

### 9.3 Risk — Multi-account support stays conceptual only

If account/profile separation is modeled but not exercised in execution, later provenance assumptions will be unreliable.

### 9.4 Risk — Source records are not persisted before interpretation

This would undermine traceability and make debugging and review much harder later.

### 9.5 Risk — Failure handling becomes silent

If authorization or sync failures are swallowed, the product becomes untrustworthy very quickly.

### 9.6 Risk — Read-first stance gets weakened by convenience

Any quiet introduction of outbound side effects at the connector layer would violate a core product rule.

**Stable working anchor:** `WORKC:Progress.Risks`

---

## 10. Human Dependencies

At this point, no hard blocker is known, but this workstream is more likely than A or B to encounter real setup dependencies.

Likely future human dependencies may include:

- OAuth app registration or provider-app setup
- confirmation of initial scope/permission choices
- environment-specific connector configuration not yet present locally
- confirmation of which channels are highest priority if execution needs to be staged tightly

No live-provider dependency should be raised as a blocker until the agent has completed fixture-driven, contract-driven, and structure-safe work first.

**Stable working anchor:** `WORKC:Progress.HumanDependencies`

---

## 11. Immediate Next Slice

The recommended first implementation slice is:

1. define the connector framework baseline,
2. wire execution context resolution for connected accounts/profiles,
3. implement one provider path first — Gmail is the most sensible initial slice,
4. persist normalized records before interpretation,
5. and execute the first connector normalization proof.

That slice gives the project one real governed ingestion path quickly and creates a repeatable pattern for the remaining providers.

**Stable working anchor:** `WORKC:Progress.ImmediateNextSlice`

---

## 12. Pickup Guidance for the Next Session

When the next implementation session begins for Workstream C, the coding agent should:

1. read the Workstream C implementation plan,
2. confirm the latest Architecture control surface,
3. inspect the actual Foundation and Domain/Memory substrate that exists by then,
4. implement the connector framework baseline,
5. add connected-account execution-context resolution,
6. implement the first provider normalization slice,
7. persist normalized records before any interpretation handoff,
8. execute the first connector verification proof,
9. then return here and update:
   - execution log,
   - package status,
   - verification log,
   - and current overall status.

**Stable working anchor:** `WORKC:Progress.PickupGuidance`

---

## 13. Definition of Real Progress for This File

This file should only be updated when one or more of the following has genuinely changed:

- code was implemented,
- a work package status changed,
- verification was executed,
- a blocker emerged or was cleared,
- or pickup guidance materially changed.

This avoids turning the file into vague narration.

**Stable working anchor:** `WORKC:Progress.DefinitionOfRealProgress`

---

## 14. Final Note

Right now, Workstream C is well-prepared but not yet earned.

That is the honest status.

The connector model, verification posture, and support surfaces are strong on paper. The next step is to convert that advantage into a real governed ingestion path and begin recording actual evidence here.

**Stable working anchor:** `WORKC:Progress.Conclusion`

