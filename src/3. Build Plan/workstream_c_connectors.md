# Glimmer — Workstream C: Connectors

## Document Metadata

- **Document Title:** Glimmer — Workstream C: Connectors
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Build Strategy and Scope, Testing Strategy, Workstream B Domain and Memory

---

## 1. Purpose

This document defines the implementation strategy for **Workstream C — Connectors**.

Its purpose is to implement Glimmer’s bounded external-ingestion layer so that real signals from Google, Microsoft, Telegram, and manual imports can enter the system in a controlled, provenance-preserving, multi-account-aware way.

This workstream is where Glimmer becomes externally connected. It must therefore be implemented with tighter discipline than a normal "integration" workstream.

**Stable plan anchor:** `PLAN:WorkstreamC.Connectors`

---

## 2. Workstream Objective

Workstream C exists to implement the connector and intake substrate for Glimmer, including:

- Google mail and calendar connectivity,
- Microsoft Graph mail and calendar connectivity,
- Telegram companion-channel connectivity,
- manual import flow for unsupported sources,
- normalization into internal source records,
- provenance preservation across all ingested items,
- and clean handoff into the orchestration layer.

At the end of this workstream, Glimmer should be able to receive real or realistically simulated external signals and persist them into the structured domain model without flattening their source meaning.

**Stable plan anchor:** `PLAN:WorkstreamC.Objective`

---

## 3. Why This Workstream Comes After Domain and Memory

The build plan and strategy documents place external boundary and intake after runtime/memory foundations and before assistant-core workflow sophistication.

That order is correct because connectors need a real domain substrate to write into:

- `ConnectedAccount`
- `AccountProfile`
- `Message`
- `MessageThread`
- `CalendarEvent`
- `ImportedSignal`
- channel session state
- and provenance-bearing source linkage

If connectors are built first, they tend to invent their own partial storage model or push provider-specific assumptions upward into orchestration and UI layers. This workstream depends on Workstream B making the source-bearing domain model real first.

**Stable plan anchor:** `PLAN:WorkstreamC.Rationale`

---

## 4. Related Requirements Anchors

This workstream directly supports the following requirements:

- `REQ:MessageIngestion`
- `REQ:MultiAccountProfileSupport`
- `REQ:TelegramMobilePresence`
- `REQ:ContextualMessageClassification`
- `REQ:TraceabilityAndAuditability`
- `REQ:PrivacyAndLeastPrivilege`
- `REQ:SafeBehaviorDefaults`

These requirements make connector behavior more demanding than simple data import. The system must preserve account identity, provenance, review boundaries, and a safe no-auto-send posture from the start.

**Stable plan anchor:** `PLAN:WorkstreamC.RequirementsAlignment`

---

## 5. Related Architecture Anchors

This workstream is primarily implementing the architecture described by:

- `ARCH:ConnectorIsolation`
- `ARCH:GmailConnector`
- `ARCH:GoogleCalendarConnector`
- `ARCH:MicrosoftGraphConnector`
- `ARCH:TelegramConnector`
- `ARCH:ManualImportBoundary`
- `ARCH:NormalizationPipeline`
- `ARCH:AccountProvenanceModel`
- `ARCH:OAuthAndTokenStorage`
- `ARCH:LeastPrivilegeModel`

These anchors define the connector-family split, normalization discipline, multi-account provenance model, and the security boundary that all connector code must respect.

**Stable plan anchor:** `PLAN:WorkstreamC.ArchitectureAlignment`

---

## 6. Workstream Scope

### 6.1 In scope

This workstream includes:

- connector abstractions and provider-specific connector implementations,
- connected-account and account-profile linkage in connector flows,
- normalization of inbound source payloads,
- thread/event/source metadata preservation,
- connector-to-intake handoff behavior,
- Telegram companion-channel adapter behavior,
- manual import behavior,
- sync-state tracking for connected accounts,
- and connector-focused verification scaffolding.

**Stable plan anchor:** `PLAN:WorkstreamC.InScope`

### 6.2 Out of scope

This workstream does **not** include:

- final triage/planner business behavior,
- polished UI workflows for triage review,
- final voice-session orchestration,
- autonomous outbound communication,
- unsupported unofficial personal-message scraping,
- or broad enterprise admin tooling for connector management.

This workstream establishes the bounded external signal layer. It does not yet deliver the full assistant loop.

**Stable plan anchor:** `PLAN:WorkstreamC.OutOfScope`

---

## 7. Implementation Outcome Expected from This Workstream

By the end of Workstream C, Glimmer should be able to do the following in a structurally real way:

- register and persist multiple Google and Microsoft connected accounts,
- preserve separate mail and calendar profile context where relevant,
- ingest mail and calendar source material into normalized source records,
- ingest Telegram operator messages into companion-channel source records/session state,
- accept manual imported text for unsupported channels such as WhatsApp,
- preserve remote identifiers, thread identifiers, timestamps, provider type, and account provenance,
- track sync status and connector errors per connected account,
- and hand normalized records into the Intake Graph boundary without embedding business classification logic into connector code.

At that point, Glimmer’s external boundary becomes real and later orchestration work can build on a stable substrate.

**Stable plan anchor:** `PLAN:WorkstreamC.ExpectedOutcome`

---

## 8. Connector Implementation Packages

## 8.1 Work Package C1 — Connector abstraction and provider boundary framework

**Objective:** Establish the connector contracts and provider-boundary structure that all connector implementations will follow.

### In scope
- connector interface model
- provider-specific adapter boundary
- normalized handoff contracts
- sync-state and error-state abstraction
- account/profile-aware connector invocation model

### Expected outputs
- connector abstraction layer
- provider-boundary package structure
- typed normalized-handoff contracts
- tests for base connector contract behavior where meaningful

### Related anchors
- `ARCH:ConnectorIsolation`
- `ARCH:ConnectorLayerScope`
- `ARCH:ConnectorToIntakeHandoff`

### Definition of done
- connector code has a clear bounded shape that later provider implementations plug into
- the rest of the system does not depend directly on provider SDK details

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC1.ConnectorFramework`

---

## 8.2 Work Package C2 — Connected account registration and profile linkage

**Objective:** Make connected accounts and profiles operationally usable by the connector layer.

### In scope
- application-level handling for `ConnectedAccount`
- account-profile resolution and lookup for connector execution
- sync-state metadata updates
- authorization-status representation at the connector boundary

### Expected outputs
- service/repository flows for connector account lookup
- account/profile binding logic for connector runs
- sync-state update path
- tests for multi-account separation and profile resolution

### Related anchors
- `ARCH:ConnectedAccountModel`
- `ARCH:AccountProfileModel`
- `ARCH:MultiAccountConnectivityModel`
- `ARCH:ConnectedAccountConsentModel`

### Definition of done
- connector flows can be executed against the correct account/profile without ambiguity
- multi-account separation is real in code, not implied

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC2.AccountAndProfileLinkage`

---

## 8.3 Work Package C3 — Gmail / Google Workspace mail connector

**Objective:** Implement Google mail ingestion into normalized message/thread records.

### In scope
- Gmail/Workspace mail connector implementation
- account-aware fetch behavior
- mapping into `Message` and `MessageThread`
- Gmail message/thread identifier preservation
- account/label context retention where relevant

### Expected outputs
- Gmail connector implementation
- normalization mapper(s)
- provider-specific tests/fakes or controlled fixtures
- provenance-preserving persistence into source records

### Related anchors
- `ARCH:GmailConnector`
- `ARCH:GmailThreadContext`
- `ARCH:NormalizationPipeline`

### Definition of done
- Google mail messages can be ingested into normalized internal records with provenance and thread linkage preserved

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC3.GmailConnector`

---

## 8.4 Work Package C4 — Google Calendar connector

**Objective:** Implement Google Calendar event ingestion into normalized calendar-event records.

### In scope
- Google Calendar connector implementation
- source-calendar/profile context preservation
- mapping into `CalendarEvent`
- event identity and account linkage preservation

### Expected outputs
- Google Calendar connector implementation
- normalization mapper(s)
- test coverage for event normalization and provenance retention

### Related anchors
- `ARCH:GoogleCalendarConnector`
- `ARCH:GoogleCalendarProfileContext`
- `ARCH:NormalizationPipeline`

### Definition of done
- Google calendar events can be ingested with account/profile/source-calendar meaning preserved

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC4.GoogleCalendarConnector`

---

## 8.5 Work Package C5 — Microsoft Graph mail connector

**Objective:** Implement Microsoft 365 / Graph mail ingestion into normalized message/thread records.

### In scope
- Microsoft Graph mail connector implementation
- conversation/thread context preservation where available
- tenant/mailbox context retention
- mapping into normalized source records

### Expected outputs
- Microsoft mail connector implementation
- provider-specific normalization mapper(s)
- tests for multi-tenant/mailbox provenance retention

### Related anchors
- `ARCH:MicrosoftGraphConnector`
- `ARCH:MicrosoftTenantMailboxContext`
- `ARCH:NormalizationPipeline`

### Definition of done
- Microsoft mail messages can be ingested into normalized internal records with tenant/mailbox provenance preserved

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC5.MicrosoftMailConnector`

---

## 8.6 Work Package C6 — Microsoft Graph calendar connector

**Objective:** Implement Microsoft 365 calendar ingestion into normalized calendar-event records.

### In scope
- Microsoft calendar connector implementation
- tenant/account/calendar-profile context retention
- mapping into `CalendarEvent`
- event identity preservation

### Expected outputs
- Microsoft calendar connector implementation
- normalization mapper(s)
- tests for calendar provenance retention

### Related anchors
- `ARCH:MicrosoftCalendarConnector`
- `ARCH:MicrosoftCalendarProfileContext`
- `ARCH:NormalizationPipeline`

### Definition of done
- Microsoft calendar events can be ingested into normalized internal records with the correct account/profile provenance

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC6.MicrosoftCalendarConnector`

---

## 8.7 Work Package C7 — Telegram companion connector

**Objective:** Implement Telegram as Glimmer’s MVP mobile companion-channel connector.

### In scope
- inbound Telegram message receipt path
- operator identity/session binding
- mapping into `ChannelSession` / `TelegramConversationState`
- normalization into `ImportedSignal` or equivalent source records
- outbound Glimmer reply relay to Telegram after internal workflow completion

### Expected outputs
- Telegram connector implementation
- Telegram-specific session binding logic
- source-record creation path for Telegram input
- tests for session continuity, safe routing, and concise reply handling

### Related anchors
- `ARCH:TelegramConnector`
- `ARCH:TelegramIdentitySessionBinding`
- `ARCH:TelegramCompanionChannel`
- `ARCH:TelegramCompanionUx`

### Definition of done
- Telegram functions as a bounded companion adapter rather than an ad hoc side-channel
- operator Telegram messages become normalized internal signal/session artifacts

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC7.TelegramConnector`

---

## 8.8 Work Package C8 — Manual import flow for unsupported channels

**Objective:** Implement the manual import boundary for unsupported or intentionally unintegrated sources.

### In scope
- pasted or uploaded text import flow
- source labeling and manual-import metadata
- normalization into `ImportedSignal`
- handoff into intake/orchestration entry boundary

### Expected outputs
- manual import service or endpoint
- import metadata handling
- tests for manual-import labeling and safe persistence

### Related anchors
- `ARCH:ManualImportBoundary`
- `ARCH:ManualImportDiscipline`
- `ARCH:NormalizationPipeline`

### Definition of done
- unsupported communication can be brought into Glimmer explicitly without unofficial scraping behavior

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC8.ManualImportFlow`

---

## 8.9 Work Package C9 — Normalization pipeline and connector-to-intake handoff

**Objective:** Make normalization and orchestration handoff consistent across all connector families.

### In scope
- shared normalization contracts
- source-model persistence-before-interpretation rule
- connector-to-Intake-Graph handoff implementation
- import-mode flags and source-type tagging

### Expected outputs
- shared normalization pipeline code
- handoff service/queue/path into intake boundary
- tests proving normalization preserves required meaning
- tests proving downstream handoff is reference-friendly rather than oversized/transient

### Related anchors
- `ARCH:NormalizationPipeline`
- `ARCH:NormalizationPreservesMeaning`
- `ARCH:NormalizationOutputBoundary`
- `ARCH:ConnectorToIntakeHandoff`

### Definition of done
- all supported source families reach the same clean intake boundary through a consistent normalization path

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC9.NormalizationAndHandoff`

---

## 8.10 Work Package C10 — Connector sync-state, failure handling, and observability baseline

**Objective:** Implement the minimum operational substrate needed to trust connector execution.

### In scope
- sync-state tracking per connected account
- failure-state recording
- visible connector error semantics
- retry-safe metadata where appropriate
- observability hooks for connector runs

### Expected outputs
- sync-state update logic
- failure recording model at connector layer
- tests for visible failure behavior and non-silent degradation

### Related anchors
- `ARCH:BackgroundSyncPosture`
- `ARCH:ConnectorSyncStateTracking`
- `ARCH:ConnectorFailureRecovery`
- `ARCH:ConnectorSecurityPosture`

### Definition of done
- connector runs and failures are operationally visible enough for later diagnosis and verification

**Stable plan anchor:** `PLAN:WorkstreamC.PackageC10.SyncStateAndFailureHandling`

---

## 9. Sequencing Inside the Workstream

The recommended internal order for Workstream C is:

1. C1 — Connector abstraction and provider boundary framework
2. C2 — Connected account registration and profile linkage
3. C9 — Normalization pipeline and connector-to-intake handoff
4. C3 — Gmail / Google Workspace mail connector
5. C4 — Google Calendar connector
6. C5 — Microsoft Graph mail connector
7. C6 — Microsoft Graph calendar connector
8. C8 — Manual import flow
9. C7 — Telegram companion connector
10. C10 — Connector sync-state, failure handling, and observability baseline

This order ensures the connector framework and normalization contract exist before provider-specific implementations accumulate. It also keeps Telegram companion behavior from becoming the accidental template for the rest of the connector layer.

**Stable plan anchor:** `PLAN:WorkstreamC.InternalSequence`

---

## 10. Human Dependencies

Workstream C has more human dependencies than Workstreams A and B because it touches real external systems.

Expected human actions include:

- creating and approving Google API app credentials and consent configuration,
- creating and approving Microsoft Graph app registration and permissions,
- provisioning Telegram bot credentials and configuration,
- confirming exact scope minimization decisions,
- and supplying or approving any environment-specific secret-handling setup.

The workstream should still be structured so the coding agent can make major progress with abstractions, local flows, fakes, and controlled fixtures before those human actions are completed. This is consistent with the framework’s human–agent responsibility model and the Glimmer strategy doc.

**Stable plan anchor:** `PLAN:WorkstreamC.HumanDependencies`

---

## 11. Verification Expectations

Workstream C is complete only when connector behavior is proven to preserve meaning, not merely to move data.

### Verification layers expected
- integration verification for normalization and persistence
- contract verification for provider and Telegram boundaries
- graph-adjacent verification for connector-to-intake handoff
- security-focused verification for permission and no-auto-send boundaries where applicable
- data-integrity verification for provenance retention

### Minimum proof expectations
- multiple connected accounts can be distinguished and persisted cleanly
- normalized source records preserve provider/account/profile/thread/event provenance
- manual imports are explicitly labeled and routed safely
- Telegram input becomes normalized internal signal/session state without bypassing review rules
- connector failures are visible and do not silently corrupt accepted memory
- connector code respects the read-first/no-auto-send boundary

This aligns directly to the Glimmer testing strategy’s connector, provenance, Telegram, and security verification requirements.

**Stable plan anchor:** `PLAN:WorkstreamC.VerificationExpectations`

---

## 12. Suggested Future Working Documents for This Workstream

This workstream should eventually be paired with:

- `WorkstreamC_Connectors_DESIGN_AND_IMPLEMENTATION_PLAN.md`
- `WorkstreamC_Connectors_DESIGN_AND_IMPLEMENTATION_PROGRESS.md`

Those files will hold the active implementation state, session handoff, human dependency tracking, and executed verification evidence once coding begins. This follows the framework’s working-document convention.

**Stable plan anchor:** `PLAN:WorkstreamC.WorkingDocumentPair`

---

## 13. Definition of Done

Workstream C should be considered complete when all of the following are true:

1. the connector abstraction layer is in place,
2. Google and Microsoft mail/calendar connectors are implemented or credibly integrated against the agreed boundary,
3. Telegram companion connectivity is implemented as a bounded adapter,
4. manual import is available for unsupported channels,
5. normalization consistently preserves provider/account/profile/thread/event provenance,
6. normalized source records are handed into the intake boundary cleanly,
7. sync-state and connector failure behavior are visible,
8. connector security boundaries remain read-first and no-auto-send,
9. and the required automated verification evidence has been executed and recorded.

If these are not true, Glimmer still lacks a trustworthy external-boundary and intake layer.

**Stable plan anchor:** `PLAN:WorkstreamC.DefinitionOfDone`

---

## 14. Final Note

Workstream C is where Glimmer first touches the outside world in earnest.

That means this workstream is not just about “integrating APIs.” It is about preserving trust at the boundary:

- one account must not blur into another,
- one source must not lose its meaning during normalization,
- one channel must not bypass core review rules,
- and connector convenience must not quietly weaken the product’s local-first, review-first posture.

If this workstream is done well, later orchestration and UX layers can rely on trustworthy inputs.
If it is done badly, the rest of the product will inherit flattened provenance, fuzzy state, and integration drift.

**Stable plan anchor:** `PLAN:WorkstreamC.Conclusion`

