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

- **Overall Workstream Status:** `Verified`
- **Current Confidence Level:** All 10 work packages implemented and verified; 93 connector tests pass; total backend suite 190/190
- **Last Meaningful Update:** 2026-04-13 — All WC1-WC10 connector layer packages implemented and verified
- **Ready for Coding:** Workstream C is complete. Workstream D — Triage and Prioritization is next.

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
| WC1 | Connector framework baseline | `Verified` | 10/10 structural tests pass | BaseConnector ABC, contracts, provider boundaries, read-first enforcement |
| WC2 | Connected-account execution context resolution | `Verified` | 11/11 integration tests pass | ConnectorContextResolver with multi-account, profile, error handling |
| WC3 | Gmail normalization path | `Verified` | 15/15 contract tests pass | GmailConnector with message + thread normalization, fixture-driven |
| WC4 | Google Calendar normalization path | `Verified` | 9/9 contract tests pass | GoogleCalendarConnector with event normalization, all-day, online meeting |
| WC5 | Microsoft mail normalization path | `Verified` | 13/13 contract tests pass | MicrosoftMailConnector with message + thread normalization, tenant context |
| WC6 | Microsoft calendar normalization path | `Verified` | 8/8 contract tests pass | MicrosoftCalendarConnector with event normalization, Teams links |
| WC7 | Manual import path | `Verified` | 7/7 integration tests pass | ManualImportHandler with explicit labeling and metadata |
| WC8 | Telegram companion intake path | `Verified` | 6/6 contract tests pass | TelegramIntakeConnector with bounded signal normalization |
| WC9 | Connector-to-intake bounded handoff | `Verified` | 9/9 integration tests pass | IntakeHandoffService with persist-before-interpretation, bounded references |
| WC10 | Sync-state, failure visibility, and read-first safeguards | `Verified` | 6/6 integration tests pass + framework read-first tests | SyncStateManager with checkpoint, failure, and recovery tracking |

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

### 7.2 Session — 2026-04-13 — WC1-WC10 complete connector layer

- **State:** All 10 work packages implemented and verified. Workstream C complete.
- **Meaningful accomplishments:**
  - **WC1** — `app/connectors/base.py`: BaseConnector ABC with provider_type, connector_type, supported_profile_types, fetch_and_normalize, validate_credentials
  - **WC1** — `app/connectors/contracts.py`: Pydantic DTOs — ConnectorExecutionContext, NormalizedMessageData, NormalizedThreadData, NormalizedEventData, NormalizedSignalData, SyncCheckpoint, IntakeReference, FetchResult
  - **WC2** — `app/connectors/context.py`: ConnectorContextResolver — resolves ConnectedAccount + AccountProfile into execution context, with AccountNotFoundError, AccountInactiveError, ProfileNotFoundError, resolve_all_profiles, list_active_accounts
  - **WC3** — `app/connectors/google/gmail.py`: GmailConnector with normalize_gmail_payload (message) and normalize_gmail_thread (thread), preserving Gmail message/thread IDs, labels, sender/recipient, body extraction
  - **WC4** — `app/connectors/google/calendar.py`: GoogleCalendarConnector with normalize_gcal_event, preserving event ID, calendar profile, participants, location/conferencing links, all-day events
  - **WC5** — `app/connectors/microsoft/mail.py`: MicrosoftMailConnector with normalize_graph_message and normalize_graph_thread, preserving conversationId as thread, tenant context, folder context, importance
  - **WC6** — `app/connectors/microsoft/calendar.py`: MicrosoftCalendarConnector with normalize_graph_event, preserving attendees, online meeting links, body preview, calendar profile
  - **WC7** — `app/connectors/manual/importer.py`: ManualImportHandler with normalize_manual_import, always marking signal_type="manual_paste", preserving source_channel and operator_notes
  - **WC8** — `app/connectors/telegram/intake.py`: TelegramIntakeConnector with normalize_telegram_message, preserving Telegram chat/message/sender IDs, username, timestamp
  - **WC9** — `app/connectors/intake.py`: IntakeHandoffService — persists normalized records as source-layer entities BEFORE interpretation, returns bounded IntakeReferences with record IDs (not raw payloads)
  - **WC10** — `app/connectors/sync.py`: SyncStateManager — applies checkpoints to ConnectedAccount.sync_metadata, tracks success/failed/partial status, clears errors on success, record_failure convenience
  - **Tests**: 8 new test files totaling 93 connector tests; all pass
  - **Total backend suite**: 190/190 pass
  - All 12 Workstream C verification anchors now have executed proof
- **Workstream C is complete. Proceeding to Workstream D — Triage and Prioritization.**

### 7.3 Session — 2026-04-15 — Live OAuth connector integration (Google + Microsoft)

- **State:** Live connector integration infrastructure implemented. Connectors can now perform real OAuth authorization and fetch live data from Google (Gmail + Calendar) and Microsoft (Outlook + Calendar).
- **Meaningful accomplishments:**
  - **OAuth Configuration** — `app/config.py`: Added Google OAuth (client_id, client_secret, redirect_uri, scopes), Microsoft OAuth (client_id, client_secret, redirect_uri, tenant_id, scopes), and token encryption key settings with GLIMMER_ env prefix
  - **Token Manager** — `app/connectors/token_manager.py`: Fernet-encrypted token storage/retrieval on ConnectedAccount.auth_metadata, with store_tokens, get_tokens, clear_tokens, is_expired methods
  - **OAuth Providers** — `app/connectors/oauth_providers.py`: GoogleOAuthProvider (google-auth-oauthlib) and MicrosoftOAuthProvider (MSAL) with get_authorization_url, exchange_code, refresh_access_token, get_user_info
  - **Connector API** — `app/api/connectors.py`: Full connector management API router with 9 endpoints — accounts CRUD, Google/Microsoft OAuth flows (auth-url + callback), manual sync trigger, connector status
  - **Live Gmail Fetch** — `app/connectors/google/gmail.py`: fetch_and_normalize now calls Gmail API (messages.list + messages.get + threads.get), with incremental sync cursor support via historyId
  - **Live Google Calendar Fetch** — `app/connectors/google/calendar.py`: fetch_and_normalize calls Calendar API (events.list) for next 7 days
  - **Live Microsoft Mail Fetch** — `app/connectors/microsoft/mail.py`: fetch_and_normalize calls Graph /me/messages with $filter for last 24h, groups by conversationId for threads
  - **Live Microsoft Calendar Fetch** — `app/connectors/microsoft/calendar.py`: fetch_and_normalize calls Graph /me/events for next 7 days
  - **Sync Orchestration** — `app/services/sync_orchestration.py`: Coordinates token refresh, connector dispatch, IntakeHandoffService persistence, SyncStateManager checkpoint updates
  - **Frontend — Settings/Connectors** — `src/app/settings/connectors/page.tsx`: Full connector management UI with Google/Microsoft connect buttons, account list, sync status, disconnect, sync-now actions
  - **Frontend — API Client** — Updated api-client.ts and types.ts with connector management functions and types
  - **Frontend — Nav** — Added Settings nav item to workspace-nav.tsx
  - **Dependencies** — Added google-auth-oauthlib, google-api-python-client, msal, cryptography, httpx to pyproject.toml
  - **Environment** — Updated .env.example with Google/Microsoft OAuth setup instructions and token encryption key generation hint
  - **All 785 existing tests still pass** (zero regressions)
  - **Frontend builds successfully** with new /settings/connectors route
- **Architecture compliance:**
  - Read-first: all connectors use read-only scopes (gmail.readonly, calendar.readonly, Mail.Read, Calendars.Read)
  - No-auto-send: no write/send capabilities in any connector
  - Provenance: account/provider/tenant context preserved through execution context
  - Token isolation: encrypted tokens stay in connector layer, never exposed in API responses
  - Multi-account: supports multiple Google + multiple Microsoft accounts
  - Least privilege: minimum OAuth scopes requested
- **Human dependencies remaining:**
  - Google Cloud Console: Create OAuth 2.0 "Web application" client, enable Gmail + Calendar APIs
  - Azure Portal: Register app, add redirect URI, grant Mail.Read + Calendars.Read + User.Read delegated permissions
  - Generate and set GLIMMER_TOKEN_ENCRYPTION_KEY in backend .env

**Stable working anchor:** `WORKC:Progress.ExecutionLog`

---

## 8. Verification Log

This section records **executed** verification, not merely intended verification.

### 8.1 Current verification state

- `TEST:Connector.Framework.ProviderBoundaryIsolation` — **PASS** — 7 tests (ABC inheritance, provider types, connector types, profiles, module isolation, contract location, interface check)
- `TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile` — **PASS** — 11 tests (active account, with profile, different accounts, nonexistent, inactive, missing profile, wrong-account profile, all profiles, list active, filter by provider)
- `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount` — **PASS** — 15 tests (message ID, thread ID, source type, subject, sender, recipients, body text, account label, labels, timestamp, thread ID, thread source type, derived subject, participants, last activity)
- `TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext` — **PASS** — 9 tests (event ID, title, description, time range, participants, location, profile source calendar, all-day event, online meeting link)
- `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread` — **PASS** — 13 tests (message ID, conversation ID, source type, subject, sender with name, recipients, body text, tenant context, folder, timestamps, thread conversation ID, thread source type, thread participants)
- `TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext` — **PASS** — 8 tests (event ID, title, body preview, time range, attendees, physical location, profile source calendar, Teams link)
- `TEST:Connector.ManualImport.LabelingAndRouting` — **PASS** — 7 tests (signal type, content, source label, manual metadata, source channel, operator notes, minimal import)
- `TEST:Connector.Telegram.InboundBecomesBoundedSignal` — **PASS** — 6 tests (signal type, content, source label, Telegram IDs, sender identity, provider label)
- `TEST:Connector.Normalization.PersistBeforeInterpretation` — **PASS** — 5 tests (messages, threads, events, signals all persisted before handoff, provenance preserved)
- `TEST:Connector.IntakeHandoff.BoundedReferenceFlow` — **PASS** — 4 tests (references with record IDs, provenance included, separate refs per type, empty fetch)
- `TEST:Connector.SyncFailure.VisibleState` — **PASS** — 6 tests (success updates metadata, failure preserves error, success clears error, convenience method, partial status, nonexistent account)
- `TEST:Connector.Security.ReadFirstNoAutoSendPreserved` — **PASS** — 3 tests (no send methods on base, no send on connectors, fetch result read-only shape)

### 8.2 Verification interpretation

All twelve verification targets have executed proof. Workstream C is fully verified.

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

Workstream C is complete. The recommended next work is:

1. Begin Workstream D — Triage and Prioritization,
2. Follow the WS-D implementation plan and progress file,
3. Start with WD1 — Intake graph foundation.

**Stable working anchor:** `WORKC:Progress.ImmediateNextSlice`

---

## 12. Pickup Guidance for the Next Session

Workstream C is complete. The next session should:

1. read the Workstream D implementation plan,
2. read the Workstream D progress file,
3. inspect the connector and domain substrate now available,
4. begin WD1 — Intake graph foundation.

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

Workstream C is complete. The Glimmer connector layer is now a real, bounded, provenance-preserving ingestion boundary covering all 6 planned connector families:

- Gmail mail connector (message + thread normalization)
- Google Calendar connector (event normalization including all-day and online meetings)
- Microsoft Graph mail connector (message + thread normalization with tenant context)
- Microsoft Graph calendar connector (event normalization with Teams links)
- Telegram companion intake connector (bounded signal normalization)
- Manual import handler (explicit labeling and routing)

Plus the shared framework:
- BaseConnector ABC with clear contract
- ConnectorExecutionContext with multi-account resolution
- IntakeHandoffService with persist-before-interpretation
- SyncStateManager with failure visibility
- Read-first / no-auto-send enforcement

All 12 verification targets have executed proof. 93 connector tests pass. The connector layer is strong enough for triage, orchestration, UI, and companion modes to build on.

**Stable working anchor:** `WORKC:Progress.Conclusion`
