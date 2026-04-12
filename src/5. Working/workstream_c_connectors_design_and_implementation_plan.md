# Glimmer — Workstream C Connectors Design and Implementation Plan

## Document Metadata

- **Document Title:** Glimmer — Workstream C Connectors Design and Implementation Plan
- **Document Type:** Working Implementation Plan
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** C — Connectors
- **Primary Companion Documents:** Requirements, Architecture, Build Plan, Verification, Governance and Process, Global Copilot Instructions, Module Instructions, Workstream C Verification Pack

---

## 1. Purpose

This document is the active working implementation plan for **Workstream C — Connectors**.

Its purpose is to translate the canonical Workstream C build-plan document into an execution-ready plan that a coding agent can use during real implementation sessions.

This file should remain practical and anchored. It is not the source of architecture truth. It is the working plan for how Glimmer’s external-boundary, ingestion, normalization, and intake handoff layer should be implemented, verified, and advanced slice by slice.

**Stable working anchor:** `WORKC:Plan.ControlSurface`

---

## 2. Workstream Objective

The objective of Workstream C is to establish the bounded external-ingestion layer that allows Glimmer to receive real signals from supported channels without losing provenance, flattening account context, or leaking integration logic into the assistant core.

At the end of Workstream C, the repository should have a real connector substrate for:

- Google mail ingestion,
- Google Calendar ingestion,
- Microsoft mail ingestion,
- Microsoft calendar ingestion,
- Telegram companion intake,
- manual import for unsupported channels,
- normalization into Glimmer’s source-bearing model,
- sync/failure-state handling,
- and clean handoff into the intake/orchestration boundary.

This workstream is where Glimmer stops depending only on planned memory structures and begins receiving real external context through governed boundaries.

**Stable working anchor:** `WORKC:Plan.Objective`

---

## 3. Control Anchors in Scope

### 3.1 Requirements anchors

- `REQ:MessageIngestion`
- `REQ:MultiAccountProfileSupport`
- `REQ:TelegramMobilePresence`
- `REQ:PrivacyAndLeastPrivilege`
- `REQ:SafeBehaviorDefaults`
- `REQ:TraceabilityAndAuditability`
- `REQ:StateContinuity`

### 3.2 Architecture anchors

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

### 3.3 Build-plan anchors

- `PLAN:WorkstreamC.Connectors`
- `PLAN:WorkstreamC.Objective`
- `PLAN:WorkstreamC.InternalSequence`
- `PLAN:WorkstreamC.VerificationExpectations`
- `PLAN:WorkstreamC.DefinitionOfDone`

### 3.4 Verification anchors

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

**Stable working anchor:** `WORKC:Plan.ControlAnchors`

---

## 4. Execution Principles for This Workstream

### 4.1 Official API boundaries only

Use supported Google, Microsoft, and Telegram boundaries. Do not introduce scraping, UI automation, or other fragile acquisition paths into the core connector work.

### 4.2 Normalize before interpretation

Provider payloads should become explicit source-bearing records before any assistant-core classification or planning begins.

### 4.3 Provenance is load-bearing

Account identity, provider identity, profile context, remote item identity, thread or calendar context, and import metadata must be preserved as part of the normalized model.

### 4.4 Connector code is not business logic

Connectors may authenticate, fetch, normalize, persist, and hand off. They must not perform triage, planning, drafting, or accepted-state mutation.

### 4.5 Multi-account separation must be real in execution

The system must not just store multiple connected accounts. Connector execution must actually resolve and preserve the correct account/profile context.

### 4.6 Read-first and no-auto-send from day one

The connector layer must remain read-first and must not quietly create outbound side effects that violate Glimmer’s advisory/reviewable posture.

### 4.7 One provider path at a time

Prefer bounded provider slices rather than trying to light up every integration at once.

**Stable working anchor:** `WORKC:Plan.ExecutionPrinciples`

---

## 5. Connector Shape Target for Workstream C

By the end of this workstream, the implementation should materially support the following connector-layer categories or directly equivalent concrete shapes:

- provider-specific connector boundaries
- connected-account execution context resolution
- normalization contracts and mappers
- source-record persistence-before-interpretation
- bounded connector-to-intake handoff
- sync checkpoint/state tracking
- explicit failure-state visibility
- manual import path with explicit labeling
- Telegram companion intake path as bounded signal/session input

These layers must remain explicit and testable.

**Stable working anchor:** `WORKC:Plan.ConnectorShapeTarget`

---

## 6. Work Packages to Execute

## 6.1 WC1 — Connector framework baseline

### Objective
Establish the shared connector boundary structure, common contracts, and sync-state concepts without flattening provider-specific semantics.

### Expected touch points
- connector interfaces/contracts
- provider boundary modules
- common sync-state abstractions
- integration test fixtures

### Verification expectation
- `TEST:Connector.Framework.ProviderBoundaryIsolation`

### Notes
Keep common abstractions limited to real commonality.

**Stable working anchor:** `WORKC:Plan.PackageWC1`

---

## 6.2 WC2 — Connected-account execution context resolution

### Objective
Implement runtime resolution of the correct connected account and profile context for connector execution.

### Expected touch points
- account/profile loading logic
- connector execution context builders
- provenance context helpers
- integration tests

### Verification expectation
- `TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile`

### Notes
This is the place where multi-account support becomes operational, not just modeled.

**Stable working anchor:** `WORKC:Plan.PackageWC2`

---

## 6.3 WC3 — Gmail normalization path

### Objective
Implement Gmail ingestion and normalization into explicit Glimmer source records while preserving thread and account meaning.

### Expected touch points
- Gmail connector code
- Gmail normalization mapper
- source-record persistence
- integration/contract fixtures

### Verification expectation
- `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount`
- `TEST:Connector.Normalization.PersistBeforeInterpretation`

### Notes
Preserve message identity and thread identity separately.

**Stable working anchor:** `WORKC:Plan.PackageWC3`

---

## 6.4 WC4 — Google Calendar normalization path

### Objective
Implement Google Calendar ingestion and normalization into explicit event-bearing records while preserving profile and calendar context.

### Expected touch points
- Google Calendar connector code
- event normalization mapper
- source-record persistence
- integration/contract fixtures

### Verification expectation
- `TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext`
- `TEST:Connector.Normalization.PersistBeforeInterpretation`

### Notes
Calendar/source identity is meaningful and must survive normalization.

**Stable working anchor:** `WORKC:Plan.PackageWC4`

---

## 6.5 WC5 — Microsoft mail normalization path

### Objective
Implement Microsoft mail ingestion and normalization while preserving mailbox and conversation semantics.

### Expected touch points
- Microsoft Graph mail connector code
- mail normalization mapper
- source-record persistence
- integration/contract fixtures

### Verification expectation
- `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread`
- `TEST:Connector.Normalization.PersistBeforeInterpretation`

### Notes
Do not force Gmail assumptions onto Graph mail behavior.

**Stable working anchor:** `WORKC:Plan.PackageWC5`

---

## 6.6 WC6 — Microsoft calendar normalization path

### Objective
Implement Microsoft calendar ingestion and normalization while preserving account and event semantics.

### Expected touch points
- Microsoft Graph calendar connector code
- event normalization mapper
- source-record persistence
- integration/contract fixtures

### Verification expectation
- `TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext`
- `TEST:Connector.Normalization.PersistBeforeInterpretation`

### Notes
Keep event identity, participant meaning, and source context explicit.

**Stable working anchor:** `WORKC:Plan.PackageWC6`

---

## 6.7 WC7 — Manual import path

### Objective
Implement the bounded manual-import path for unsupported channels such as WhatsApp, with explicit labeling and safe routing.

### Expected touch points
- manual import endpoint/service
- manual import metadata handling
- source-record persistence
- integration/API tests

### Verification expectation
- `TEST:Connector.ManualImport.LabelingAndRouting`

### Notes
Manual import is a bounded fallback, not a vague catch-all bucket.

**Stable working anchor:** `WORKC:Plan.PackageWC7`

---

## 6.8 WC8 — Telegram companion intake path

### Objective
Implement Telegram as a bounded companion intake surface that produces internal signal/session artifacts and routes into the shared core model safely.

### Expected touch points
- Telegram connector code
- Telegram normalization or inbound mapping
- session linkage
- integration/contract/graph tests

### Verification expectation
- `TEST:Connector.Telegram.InboundBecomesBoundedSignal`
- `TEST:Connector.IntakeHandoff.BoundedReferenceFlow`

### Notes
Telegram is a companion channel, not a hidden control room.

**Stable working anchor:** `WORKC:Plan.PackageWC8`

---

## 6.9 WC9 — Connector-to-intake bounded handoff

### Objective
Implement the explicit handoff boundary from normalized source records into the intake/orchestration layer using bounded references and contracts.

### Expected touch points
- handoff service/contracts
- intake entrypoint integrations
- graph handoff adapters if needed
- integration/graph tests

### Verification expectation
- `TEST:Connector.IntakeHandoff.BoundedReferenceFlow`

### Notes
This is where connector code must stop and assistant-core code must begin.

**Stable working anchor:** `WORKC:Plan.PackageWC9`

---

## 6.10 WC10 — Sync-state, failure visibility, and read-first safeguards

### Objective
Implement explicit sync-state visibility, diagnosable failure handling, and the guardrails that preserve read-first / no-auto-send external-boundary behavior.

### Expected touch points
- sync state models or update logic
- authorization/failure categorization
- diagnostics surfaces or repository fields
- integration/contract tests

### Verification expectation
- `TEST:Connector.SyncFailure.VisibleState`
- `TEST:Connector.Security.ReadFirstNoAutoSendPreserved`

### Notes
Failures should be visible and bounded, not swallowed.

**Stable working anchor:** `WORKC:Plan.PackageWC10`

---

## 7. Recommended Execution Order

The recommended execution order inside this working plan is:

1. WC1 — Connector framework baseline
2. WC2 — Connected-account execution context resolution
3. WC3 — Gmail normalization path
4. WC4 — Google Calendar normalization path
5. WC5 — Microsoft mail normalization path
6. WC6 — Microsoft calendar normalization path
7. WC7 — Manual import path
8. WC8 — Telegram companion intake path
9. WC9 — Connector-to-intake bounded handoff
10. WC10 — Sync-state, failure visibility, and read-first safeguards

This sequence keeps the provider boundary and provenance model coherent while allowing connector paths to light up incrementally.

**Stable working anchor:** `WORKC:Plan.ExecutionOrder`

---

## 8. Expected Files and Layers Likely to Change

The initial Workstream C implementation is likely to touch files or file groups such as:

- connector/provider modules
- normalization mappers
- connector contracts/interfaces
- connected-account execution helpers
- source-record persistence services
- intake handoff services/adapters
- sync/failure-state support files
- integration/contract/graph test fixtures
- Workstream C working documents

This list should be refined as implementation begins.

**Stable working anchor:** `WORKC:Plan.LikelyTouchPoints`

---

## 9. Verification Plan for Workstream C

### 9.1 Minimum required proof

At minimum, Workstream C implementation should produce executable proof for:

- provider boundary isolation
- correct account/profile execution resolution
- Gmail normalization
- Google Calendar normalization
- Microsoft mail normalization
- Microsoft calendar normalization
- manual-import labeling and routing
- Telegram bounded intake
- normalized-record persistence-before-interpretation
- bounded connector-to-intake handoff
- sync/failure visibility
- read-first / no-auto-send preservation

### 9.2 Primary verification surfaces

The main verification references for this workstream are:

- `verification-pack-workstream-c.md`
- `verification-pack-data-integrity.md`
- `verification-pack-release.md` for representative release-level checks later

### 9.3 Evidence expectation

Meaningful implementation slices in this workstream should update the Workstream C progress file with:

- what was implemented
- what proof was executed
- what passed
- what failed
- what remains blocked or deferred

**Stable working anchor:** `WORKC:Plan.VerificationPlan`

---

## 10. Human Dependencies and Likely Decisions

This workstream is mostly agent-executable, but several human decisions may still be needed.

Likely human-dependent areas include:

- OAuth app registration or provider-app setup
- confirmation of desired initial scope sets/permissions
- any environment-specific connector configuration not yet present locally
- confirmation of which channels are actually in scope for early implementation order if prioritization is needed

The coding agent should complete all fixture-driven, contract-driven, and structure-safe work before surfacing live-provider dependencies as blockers.

**Stable working anchor:** `WORKC:Plan.HumanDependencies`

---

## 11. Known Risks in This Workstream

### 11.1 Risk — Provider semantics get flattened

This is the most likely shortcut that would quietly damage provenance and later classification quality.

### 11.2 Risk — Connector logic leaks into business logic

If connectors start classifying or planning, the core boundary becomes muddled and harder to test.

### 11.3 Risk — Multi-account support stays conceptual only

If account/profile separation is not exercised in execution, later provenance assumptions will be unreliable.

### 11.4 Risk — Source records are not persisted before interpretation

This would undermine traceability and make later debugging much harder.

### 11.5 Risk — Failure handling becomes silent

If authorization/sync failures are swallowed, the system becomes untrustworthy very quickly.

### 11.6 Risk — Read-first stance gets weakened by convenience

Any quiet introduction of outbound side effects at the connector layer would violate a core product rule.

**Stable working anchor:** `WORKC:Plan.Risks`

---

## 12. Immediate Next Session Recommendations

When actual coding for Workstream C begins, the first sensible execution slice is:

1. define the connector framework baseline,
2. wire execution context resolution for connected accounts/profiles,
3. implement one provider path first — Gmail is the most sensible initial slice,
4. persist normalized records before interpretation,
5. and execute the first connector normalization proof.

That gives the project one real governed ingestion path quickly and creates a repeatable pattern for the remaining providers.

**Stable working anchor:** `WORKC:Plan.ImmediateNextSlice`

---

## 13. Definition of Ready for Workstream C Completion

Workstream C should only be considered ready for completion when all of the following are materially true:

- connector framework boundary is real
- multi-account execution context is real
- Google and Microsoft mail/calendar normalization paths are real
- manual import path is real
- Telegram intake path is real
- normalized records persist before interpretation
- connector-to-intake handoff is real and bounded
- sync/failure visibility is real
- read-first / no-auto-send safeguards are real
- and the corresponding proof paths have been executed and recorded

If these are not true, Workstream C is not done, even if connector code exists.

**Stable working anchor:** `WORKC:Plan.DefinitionOfReadyForCompletion`

---

## 14. Final Note

This workstream is where Glimmer begins touching the outside world in earnest.

That is why the standard here is not just “can it fetch data?”

The real standard is whether Glimmer can ingest external context in a way that remains:

- bounded,
- provenance-preserving,
- multi-account-aware,
- traceable,
- and safe for the assistant core to trust.

**Stable working anchor:** `WORKC:Plan.Conclusion`
