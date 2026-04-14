# Glimmer — Connectors and Ingestion

## Document Metadata

- **Document Title:** Glimmer — Connectors and Ingestion
- **Document Type:** Split Architecture Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `ARCHITECTURE.md`
- **Primary Companion Documents:** Requirements, System Overview, Domain Model, LangGraph Orchestration, Security and Permissions

---

## 1. Purpose

This document defines the connector architecture and ingestion model for **Glimmer**.

It explains how Glimmer connects to external communication and calendar systems, how source material is imported and normalized, how multi-account provenance is preserved, and how channel-specific inputs such as Telegram interactions and manual imports enter the system.

This document is not intended to define internal orchestration graphs in detail or final storage schemas. Its purpose is to define the canonical external-boundary model for source ingestion and connector behavior.

**Stable architecture anchor:** `ARCH:ConnectorIsolation`

---

## 2. Connector Architecture Intent

Glimmer must connect to multiple external sources without flattening source meaning or allowing integration logic to bleed across the rest of the system.

The connector layer therefore has four core jobs:

1. authenticate and connect to supported external systems,
2. fetch or receive source material in a controlled manner,
3. normalize that material into Glimmer’s internal source models,
4. preserve provenance so the system always knows where information came from.

The connector layer must remain bounded. It should not become the place where project classification, prioritization, or drafting logic is decided. Its responsibility is controlled access, normalization, provenance, and reliable handoff into the orchestration layer.

**Stable architecture anchor:** `ARCH:ConnectorLayerIntent`

---

## 3. Connector Principles

### 3.1 Official API first

The connector layer shall prefer official and supported APIs over browser scraping or fragile UI automation.

**Stable architecture anchor:** `ARCH:ConnectorPrinciple.OfficialApiFirst`
**Stable architecture anchor:** `ARCH:ApiFirstIntegration`

### 3.2 Connectors are isolated by source

Each external integration should have a bounded connector implementation with clear contracts and minimal leakage of provider-specific behavior into the rest of the system.

**Stable architecture anchor:** `ARCH:ConnectorPrinciple.SourceIsolation`

### 3.3 Normalize once, preserve provenance always

Imported source material shall be normalized into internal models, but normalization must not erase account, provider, channel, or thread provenance.

**Stable architecture anchor:** `ARCH:ConnectorPrinciple.NormalizeWithProvenance`

### 3.4 Multi-account support is a first-class requirement

Connectors must be designed to handle multiple accounts and profiles for the same operator without collapsing them into one generic inbox.

**Stable architecture anchor:** `ARCH:ConnectorPrinciple.MultiAccountFirstClass`

### 3.5 Read-first external posture

For MVP, external mail and calendar integrations should default to read-oriented access patterns. Outward actions should remain heavily constrained and explicitly reviewed.

**Stable architecture anchor:** `ARCH:ConnectorPrinciple.ReadFirst`

### 3.6 Channel-specific interactions should enter through bounded adapters

Interactive companion channels such as Telegram should enter through their own connector/adapter boundary and then route into shared internal orchestration flows.

**Stable architecture anchor:** `ARCH:ConnectorPrinciple.ChannelAdapters`

---

## 4. Connector Layer Scope

The connector layer is responsible for:

- account connectivity and connector registration,
- source-specific fetching or receipt of remote items,
- mapping remote payloads into normalized internal source records,
- maintaining linkage to `ConnectedAccount` and `AccountProfile`,
- preserving remote identifiers, thread identifiers, and import metadata,
- and handing normalized source records to the Intake Graph.

The connector layer is not responsible for:

- project classification,
- stakeholder inference beyond basic identity extraction,
- priority decisions,
- draft generation,
- or silent mutation of accepted project memory.

**Stable architecture anchor:** `ARCH:ConnectorLayerScope`

---

## 5. Supported Connector Families

The MVP connector family set consists of:

1. **Gmail / Google Workspace mail connector**
2. **Google Calendar connector**
3. **Microsoft Graph mail connector**
4. **Microsoft Graph calendar connector**
5. **Telegram companion connector**
6. **Manual import connector**
7. **Research tool adapter** (browser-mediated Gemini deep-research boundary)

These families reflect the current requirements posture and should be treated as the active source boundary for early delivery.

The research tool adapter is distinguished from the other connectors because it is an **invoked capability** rather than a passive source connector. It does not poll for incoming signals. It is invoked by the orchestration layer when a task requires escalated research, and it returns structured research artifacts.

**Stable architecture anchor:** `ARCH:SupportedConnectorFamilies`

---

## 6. Multi-Account Connectivity Model

### 6.1 One operator, many connected accounts

Glimmer is designed for one primary operator who may connect multiple Google and Microsoft accounts in one deployment.

A connector implementation must therefore operate against `ConnectedAccount` records rather than assuming a single mailbox or single calendar source.

**Stable architecture anchor:** `ARCH:MultiAccountConnectivityModel`

### 6.2 Account-aware ingestion

Every imported item shall retain at minimum:

- connected account identifier,
- provider type,
- account profile or source calendar/inbox context where relevant,
- remote item identifier,
- thread identifier where applicable,
- and import timestamp.

This is necessary so the operator can later understand:

- which account the item came from,
- which tenant or workspace context applied,
- and whether source-account identity influences project meaning.

**Stable architecture anchor:** `ARCH:AccountProvenanceModel`

### 6.3 Account profile support

Where a provider exposes multiple logical profiles or subcontexts under one account, the connector layer should preserve this distinction through `AccountProfile` or equivalent profile metadata.

Examples include:

- primary vs secondary calendar,
- folder or label context,
- inbox segment,
- shared calendar identity.

**Stable architecture anchor:** `ARCH:AccountProfileConnectorSupport`

---

## 7. Gmail / Google Workspace Mail Connector

### 7.1 Scope

The Gmail connector is responsible for importing mail messages and thread context from personal Google accounts and Google Workspace mailboxes that the operator has connected.

**Stable architecture anchor:** `ARCH:GmailConnector`

### 7.2 Responsibilities

The Gmail connector shall:

- authenticate against the connected Google account,
- retrieve message metadata and body content as allowed,
- preserve Gmail message and thread identifiers,
- preserve account and label context where relevant,
- map the payload into normalized `Message` and `MessageThread` forms,
- and emit normalized records into the Intake Graph boundary.

### 7.3 Notes on thread context

Because project classification often depends on prior thread context, the connector model should preserve enough thread linkage for downstream graph logic to access the relevant thread history.

**Stable architecture anchor:** `ARCH:GmailThreadContext`

---

## 8. Google Calendar Connector

### 8.1 Scope

The Google Calendar connector is responsible for importing calendar events from connected Google accounts and Google Workspace calendars.

**Stable architecture anchor:** `ARCH:GoogleCalendarConnector`

### 8.2 Responsibilities

The Google Calendar connector shall:

- retrieve upcoming and relevant calendar events,
- preserve source calendar identity,
- preserve account linkage,
- map event payloads into normalized `CalendarEvent` records,
- and make those records available for briefing, prioritization, and planning flows.

### 8.3 Calendar profile context

The connector should preserve which calendar profile or calendar identity an event came from, because this may affect how the operator interprets the event.

**Stable architecture anchor:** `ARCH:GoogleCalendarProfileContext`

---

## 9. Microsoft Graph Mail Connector

### 9.1 Scope

The Microsoft Graph mail connector is responsible for importing Outlook / Microsoft 365 mail for connected accounts.

**Stable architecture anchor:** `ARCH:MicrosoftGraphConnector`

### 9.2 Responsibilities

The Microsoft Graph mail connector shall:

- authenticate against the relevant Microsoft 365 account,
- import message metadata and body content as allowed,
- preserve Microsoft message and conversation/thread identifiers where available,
- preserve account/folder context where relevant,
- and map the result into normalized internal message records.

### 9.3 Tenant and mailbox context

Where multiple Microsoft tenants or mailbox contexts exist, the connector must preserve that context as part of account provenance rather than hiding it inside generic labels.

**Stable architecture anchor:** `ARCH:MicrosoftTenantMailboxContext`

---

## 10. Microsoft Graph Calendar Connector

### 10.1 Scope

The Microsoft Graph calendar connector is responsible for importing calendar events from connected Microsoft 365 calendars.

**Stable architecture anchor:** `ARCH:MicrosoftCalendarConnector`

### 10.2 Responsibilities

The connector shall:

- retrieve events from the relevant calendar profile,
- preserve account and tenant context,
- normalize event data into internal `CalendarEvent` records,
- and support downstream use in planning and briefings.

**Stable architecture anchor:** `ARCH:MicrosoftCalendarProfileContext`

---

## 11. Telegram Companion Connector

### 11.1 Scope

The Telegram connector is the interactive companion-channel adapter for Glimmer’s MVP mobile interaction mode.

**Stable architecture anchor:** `ARCH:TelegramConnector`

### 11.2 Responsibilities

The Telegram connector shall:

- receive inbound operator messages from Telegram,
- map Telegram identity and chat context into a `ChannelSession` / `TelegramConversationState` boundary,
- normalize inbound text into `ImportedSignal` or equivalent internal source records,
- hand off those inputs to the Telegram Companion Graph,
- and relay outbound Glimmer responses back through Telegram after the relevant internal workflow completes.

### 11.3 Scope limits

The Telegram connector is not intended to expose the full web application surface. It should remain optimized for:

- conversational access,
- lightweight summary retrieval,
- note capture,
- and short-turn interaction.

**Stable architecture anchor:** `ARCH:TelegramConnectorScope`

### 11.4 Identity and session continuity

The connector must preserve enough Telegram identity and session context to support:

- operator recognition,
- current session continuity,
- recent topic continuity,
- and safe routing of follow-up messages.

**Stable architecture anchor:** `ARCH:TelegramIdentitySessionBinding`

---

## 12. Manual Import Boundary

### 12.1 Scope

The Manual Import boundary is the deliberate MVP solution for unsupported or intentionally unintegrated communication sources, such as personal WhatsApp content.

**Stable architecture anchor:** `ARCH:ManualImportBoundary`

### 12.2 Responsibilities

The manual import mechanism shall:

- accept pasted or uploaded communication text,
- preserve that it was manually imported,
- create an `ImportedSignal` or equivalent source record,
- allow optional source labeling,
- and route the content into normal triage and planning flows.

### 12.3 Boundary discipline

Manual import is an explicit product boundary, not a placeholder for unsupported scraping or unofficial API behavior.

**Stable architecture anchor:** `ARCH:ManualImportDiscipline`

---

## 12A. Research Tool Adapter (Browser-Mediated Gemini)

### 12A.1 Purpose

The research tool adapter provides Glimmer with bounded external reasoning capabilities by controlling the operator's browser to interact with Gemini for tasks that exceed the local model's practical capability.

This adapter supports two distinct interaction modes:

1. **Deep research** — long-running, asynchronous interaction with Gemini's Deep Research mode, producing comprehensive research documents exported to Google Docs.
2. **Expert advice (synchronous chat)** — short-lived, synchronous interaction with Gemini in Fast, Thinking, or Pro mode, returning a text response for a specific question or reasoning task.

Both modes share the same Chrome debug-mode attachment and browser provider. Only one Gemini operation may execute at a time, enforced by an internal operation lock.

This adapter is structurally different from passive source connectors. It is an **invoked capability** rather than a polling/subscription boundary.

**Stable architecture anchor:** `ARCH:GeminiBrowserMediatedAdapter`
**Stable architecture anchor:** `ARCH:GeminiChatAdapter`

### 12A.2 Adapter scope

The research tool adapter is responsible for:

- attaching to a Chrome browser running in debug mode on the operator's local machine,
- navigating to Gemini and managing the interaction session,
- **deep research mode:** submitting research prompts, activating Deep Research mode, waiting for completion, exporting to Google Docs, and renaming the document,
- **expert advice mode:** selecting the Gemini mode (Fast / Thinking / Pro), submitting a prompt, waiting for the response, and capturing the response text via clipboard or DOM extraction,
- normalizing research results into Glimmer's research artifact model (`ResearchRun`, `ResearchFinding`, `ResearchSourceReference`, `ResearchSummaryArtifact`),
- recording expert-advice exchanges as `ExpertAdviceExchange` records with full provenance,
- and returning results to the orchestration layer.

The research tool adapter is not responsible for:

- deciding when research should be escalated (that belongs to orchestration),
- project classification or prioritization of results,
- direct mutation of accepted project memory,
- or any action beyond bounded research queries through the browser.

### 12A.3 Implementation approach

The research tool adapter shall be implemented as a Python-native module using Playwright for browser automation, ported from an existing C# / .NET research agent.

The port must:

- be idiomatic to the Glimmer Python backend,
- expose a stable internal service interface or adapter contract,
- not leak raw Playwright automation details into the rest of the codebase,
- be testable without always requiring a live browser (through contract-level mocks/fakes),
- and follow Glimmer's existing coding conventions and dependency-injection patterns.

### 12A.4 Browser attachment model

The adapter attaches to a Chrome instance running in debug mode on the operator's machine. This means:

- the operator must have Chrome running with remote debugging enabled,
- the adapter connects to the existing browser session (it does not launch a sandboxed browser),
- and the adapter uses the operator's own browser context, cookies, and authentication state to access Gemini.

This approach is local-first and avoids requiring separate Gemini API credentials for the deep-research path.

### 12A.5 Failure and degraded-mode behavior

The adapter must surface visible failure states including:

- browser not available or debug port not reachable,
- Gemini interaction failure (page load failure, unexpected UI state, session timeout),
- response capture failure,
- and timeout.

When the adapter cannot complete a research run, the orchestration layer must receive a clear failure signal so it can handle graceful degradation (e.g., falling back to local model, reporting the failure to the operator).

### 12A.6 Safety boundaries

The research tool adapter:

- must only interact with whitelisted destinations (Gemini) unless explicitly expanded,
- must not submit content that sends external messages from the operator's account,
- must not modify the operator's browser state beyond the bounded research interaction,
- and must preserve an auditable record of each research interaction.

**Stable architecture anchor:** `ARCH:ResearchAdapterSafetyBoundary`

---

## 13. Normalization Pipeline

### 13.1 Purpose

The normalization pipeline converts heterogeneous external payloads into a small number of consistent internal source models.

These include:

- `Message`
- `MessageThread`
- `CalendarEvent`
- `ImportedSignal`

**Stable architecture anchor:** `ARCH:NormalizationPipeline`

### 13.2 Normalization goals

Normalization should achieve the following:

- consistent internal handling,
- reduced provider-specific branching outside connectors,
- durable provenance retention,
- and clean handoff into the orchestration layer.

### 13.3 Information that must survive normalization

Normalization must not erase:

- source provider,
- source account,
- source profile,
- source thread/conversation identity,
- remote identifiers,
- time metadata,
- sender/recipient identity values,
- and any import-mode flags such as manual import or channel-origin type.

**Stable architecture anchor:** `ARCH:NormalizationPreservesMeaning`

### 13.4 Normalization output boundary

The output of normalization should be persisted as a domain-linked source artifact before higher-order interpretation is attempted.

This ensures that downstream classification and planning flows always have a recoverable, reviewable starting point.

**Stable architecture anchor:** `ARCH:NormalizationOutputBoundary`

---

## 14. Source Provenance Model

The provenance model is a mandatory part of the ingestion architecture.

### 14.1 Provenance dimensions

At minimum, provenance should preserve:

- provider type,
- connected account,
- account profile where relevant,
- remote item ID,
- remote thread/conversation ID where relevant,
- import time,
- import mode (`api`, `manual`, `telegram`, etc.),
- and optional folder/label/calendar context.

### 14.2 Why provenance matters

Provenance is required for:

- trustworthy operator review,
- correct cross-account triage,
- explainable classification,
- reliable debugging,
- and safe auditability.

Flattened ingestion would make Glimmer less useful and less trustworthy.

**Stable architecture anchor:** `ARCH:SourceProvenanceImportance`

---

## 15. Connector-to-Orchestration Handoff

### 15.1 Handoff contract

Connectors should hand off normalized source records into the Intake Graph rather than calling deeper business workflows directly.

This preserves:

- orchestration consistency,
- reviewability,
- and a clean separation between source-boundary logic and decision logic.

**Stable architecture anchor:** `ARCH:ConnectorToIntakeHandoff`

### 15.2 Handoff payload posture

The handoff payload should be reference-friendly and domain-linked.

Where possible, downstream graphs should load the persisted source record rather than relying on oversized transient payload passing.

**Stable architecture anchor:** `ARCH:HandoffPayloadPosture`

---

## 16. Background Sync and Intake Scheduling

### 16.1 Background sync posture

Mail and calendar connectors may run through scheduled sync cycles or event-driven intake, depending on source capability and implementation practicality.

The architecture does not require one universal mechanism for all sources. It does require that each source intake strategy be:

- explicit,
- observable,
- and safe to resume.

**Stable architecture anchor:** `ARCH:BackgroundSyncPosture`

### 16.2 Sync-state tracking

Each connected account should preserve sync-state metadata such as:

- last successful sync time,
- last attempted sync time,
- last error state,
- and checkpoint/continuation indicators where needed.

**Stable architecture anchor:** `ARCH:ConnectorSyncStateTracking`

---

## 17. Error Handling and Recovery

### 17.1 Connector failure classes

Relevant connector failure classes include:

- expired authorization,
- provider API failure,
- malformed payload,
- normalization failure,
- duplicate import detection issue,
- and outbound Telegram delivery failure.

### 17.2 Failure posture

Connector failures should:

- be observable,
- preserve enough information for retry or diagnosis,
- avoid silent data loss,
- and avoid corrupting accepted project memory.

Where a source artifact cannot be fully interpreted, the system should still preserve the raw or minimally normalized input where feasible.

**Stable architecture anchor:** `ARCH:ConnectorFailureRecovery`

---

## 18. Security and Permission Posture at the Connector Boundary

The connector layer must operate under a least-privilege model.

For MVP, the external connector posture should favor:

- read access for mail and calendar ingestion,
- no autonomous sending,
- explicit account-level consent,
- and bounded token use.

Detailed OAuth, token-storage, and secret-handling rules are defined in the security document, but connectors must be designed so those controls can be enforced cleanly.

**Stable architecture anchor:** `ARCH:ConnectorSecurityPosture`

---

## 19. Relationship to the Rest of the Architecture Set

This document defines the source-boundary model for Glimmer, but it does not define:

- graph behavior in detail,
- UI rendering,
- persistence engine specifics,
- or detailed test-pack design.

Those concerns are handled in:

- `03_langgraph_orchestration.md`
- `05_memory_and_retrieval.md`
- `06_ui_and_voice.md`
- `07_security_and_permissions.md`
- `08_testing_strategy.md` (housed under `4. Verification/`)

**Stable architecture anchor:** `ARCH:ConnectorDocumentBoundary`

---

## 20. Final Note

The connector architecture is where Glimmer touches the outside world.

If it is too loose, provenance will be lost, source meaning will be flattened, and the rest of the system will become brittle.
If it is well-bounded, Glimmer will be able to support multiple accounts, multiple providers, Telegram companion interaction, and manual import workflows without sacrificing traceability or reviewability.

That is the standard this document is intended to protect.

**Stable architecture anchor:** `ARCH:ConnectorConclusion`
