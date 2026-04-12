---
applyTo: "apps/backend/**/connectors/**/*.py,apps/backend/**/integrations/**/*.py,apps/backend/**/providers/**/*.py,apps/backend/**/ingestion/**/*.py,apps/backend/**/normalization/**/*.py,apps/backend/**/sync/**/*.py"
---

# Glimmer — Connectors and Ingestion Module Instructions

## Purpose

This instruction file defines the module-scoped rules for Glimmer connector, ingestion, normalization, and sync-related implementation.

It supplements the global `.github/copilot-instructions.md` file and applies specifically to:

- Google mail and calendar connector code,
- Microsoft Graph mail and calendar connector code,
- Telegram connector code,
- manual import flows,
- normalization mappers and provenance handling,
- sync-state handling,
- and connector-to-intake handoff code.

These rules are stricter than generic integration guidance because this part of Glimmer is where the system first touches the outside world. If connectors are weak, the rest of the product inherits flattened provenance, fuzzy state, and unsafe behavior.

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

Do not let provider SDK habits, sample-code shortcuts, or existing connector code silently override Glimmer’s documented connector boundaries.

---

## 2. What This Module Must Preserve

Connector and ingestion work must preserve these core Glimmer properties:

- **official API-first integration**,
- **multi-account and profile-aware handling**,
- **provenance-preserving normalization**,
- **connector isolation from business interpretation**,
- **explicit intake handoff**,
- **read-first / no-auto-send posture**,
- **manual import as a bounded fallback**,
- and **visible sync and failure state**.

These are load-bearing architectural and security rules.

---

## 3. Connector Boundary Rules

### 3.1 Connectors access and normalize; they do not decide

Connector code may:

- authenticate through approved provider boundaries,
- fetch source items,
- normalize payloads,
- preserve provenance,
- persist normalized source records,
- and hand those records into the intake boundary.

Connector code must not:

- classify project relevance,
- prioritize work,
- generate final drafts,
- merge stakeholder identities,
- or mutate accepted project memory directly.

### 3.2 Provider-specific code stays provider-specific

Keep provider SDK logic inside connector/provider modules.

Do not let Gmail-, Graph-, or Telegram-specific objects leak upward into:

- orchestration,
- domain services,
- UI contracts,
- or general planning logic.

Normalize at the boundary.

### 3.3 Shared abstractions must reflect real commonality

Use shared connector abstractions only where the behavior is genuinely shared, such as:

- sync-state handling,
- normalized item contracts,
- handoff contracts,
- or common retry/error categories.

Do not force fake uniformity across providers when their semantics differ materially.

---

## 4. Official API and Access Rules

### 4.1 Official APIs only

Use official provider APIs and supported SDKs or HTTP boundaries.

Do not introduce:

- brittle browser scraping,
- unofficial private endpoints,
- desktop UI automation as the normal connector path,
- or unsupported message-platform scraping for MVP.

### 4.2 Scope minimization is mandatory

Request only the scopes and permissions needed for the approved MVP behavior.

If a connector implementation seems to require broader scopes than currently documented, surface that explicitly rather than widening scope silently.

### 4.3 Read-first posture

Connector implementations should default to read and ingest behavior.

Do not implement outbound sends, calendar modifications, or other external side effects unless the control documents are intentionally revised.

### 4.4 Consent and authorization are explicit boundaries

Do not assume access is available. Connector flows must tolerate:

- unconfigured providers,
- expired authorization,
- partial provider setup,
- revoked consent,
- or account-specific failures.

---

## 5. Multi-Account and Profile Rules

### 5.1 One operator, many accounts

Assume the operator may have multiple:

- Google accounts,
- Google Workspace accounts,
- Microsoft 365 accounts,
- tenant contexts,
- mail profiles,
- and calendar profiles.

Connector logic must preserve that distinction explicitly.

### 5.2 Never flatten account provenance

For each ingested item, preserve or reliably resolve:

- connected account identity,
- provider type,
- account profile where relevant,
- remote item identifier,
- remote thread identifier where relevant,
- remote calendar/source identity where relevant,
- timestamps,
- and import or sync metadata.

### 5.3 Account-aware sync behavior

Sync routines must operate against the intended connected account/profile pair.

Do not assume one global inbox or one default calendar context.

### 5.4 Cross-account coexistence, not hidden merging

If similar-looking records come from different accounts, keep that distinction. The presence of duplicate senders, thread subjects, or event titles does not justify silent cross-account merging.

---

## 6. Normalization Rules

### 6.1 Normalize into Glimmer’s source model

Normalize provider payloads into Glimmer’s internal source-bearing model such as:

- `Message`
- `MessageThread`
- `CalendarEvent`
- `ImportedSignal`
- `ChannelSession` / Telegram conversation state where relevant

Do not treat raw provider payloads as the long-term system model.

### 6.2 Preserve meaning during normalization

Normalization should preserve operational meaning, not just content text.

That includes:

- threading/conversation context,
- participants,
- timestamps,
- labels/folder/source-calendar context where relevant,
- and source-account identity.

### 6.3 Persist source records before interpretation

As a rule, source records should be normalized and persisted before business interpretation begins.

Do not rely on transient connector-memory processing as the only representation of imported items.

### 6.4 Manual imports must be visibly manual

When ingesting manual pasted or uploaded content, label it clearly as manual import with explicit source metadata.

Do not make manual imports look indistinguishable from native provider records.

---

## 7. Connector-to-Intake Handoff Rules

### 7.1 Use a clear intake boundary

Once a source record is normalized and persisted, hand it into the intake/orchestration boundary through an explicit contract or service.

Do not let connectors directly call deep business decision logic in an ad hoc way.

### 7.2 Handoff should use bounded references

Prefer passing:

- source record identifiers,
- connected account identifiers,
- source type,
- and bounded workflow context

rather than huge raw payload blobs.

### 7.3 Connectors should not become orchestration shortcuts

The existence of provider metadata should not tempt the connector to “helpfully” do planner or triage logic that belongs in Workstream D and the graph layer.

---

## 8. Provider-Specific Rules

### 8.1 Gmail / Google Workspace mail

- Preserve message identity and thread identity separately.
- Preserve account and label/folder context where relevant.
- Do not assume Gmail semantics are universal across other providers.

### 8.2 Google Calendar

- Preserve source-calendar context where relevant.
- Preserve event identity, start/end times, participants, and meeting context.
- Distinguish calendar-profile meaning from generic event text.

### 8.3 Microsoft Graph mail

- Preserve mailbox and tenant context where relevant.
- Preserve conversation/thread semantics where available.
- Do not force Graph mail into Gmail-specific assumptions.

### 8.4 Microsoft Graph calendar

- Preserve account/profile/calendar context.
- Preserve event identity and participant information.
- Handle provider-specific event semantics explicitly rather than hiding them.

### 8.5 Telegram

- Telegram is a companion interaction channel, not a full control-room replacement.
- Telegram connector code must create or update bounded channel-session state.
- Telegram messages should normalize into internal signal/session artifacts, not bypass the intake/review model.

### 8.6 Manual import

- Manual import is a bounded fallback for unsupported channels such as WhatsApp.
- Preserve operator-supplied metadata where relevant.
- Keep this path explicit and auditable.

---

## 9. Sync, Failure, and Observability Rules

### 9.1 Sync state is first-class operational data

Connector code should track meaningful sync state such as:

- last sync time,
- sync cursor/checkpoint where relevant,
- success/failure state,
- recent error reason,
- and authorization state.

### 9.2 Fail visibly, not silently

If a connector cannot fetch, normalize, or persist correctly, surface the failure through explicit state or diagnostic records.

Do not silently drop items just because provider responses were awkward.

### 9.3 Retry with discipline

Retry behavior should be bounded and observable.

Do not create endless retry loops or invisible failure swallowing.

### 9.4 Partial failure is normal

Design for the reality that one account or provider may fail while others continue to work. Connector code should not assume all configured sources are healthy at the same time.

---

## 10. Security Rules for Connector Work

### 10.1 Secrets and tokens stay bounded

Do not:

- log raw tokens,
- expose secrets in DTOs,
- include raw provider credentials in prompts,
- or place provider auth material in general-purpose domain tables unless the security design explicitly requires it.

### 10.2 Least privilege always

If code changes imply a need for new scopes, permissions, or webhook/subscription abilities, surface the change clearly.

### 10.3 Companion channels do not soften rules

Telegram-origin interaction must still respect review gates, privacy boundaries, and no-auto-send posture.

### 10.4 Manual import should not become a security loophole

Keep manual import bounded and explicit. Do not use it as a backdoor to bypass source labeling, auditability, or review discipline.

---

## 11. Testing Expectations for This Module

When editing connector or ingestion code, the default proof target should include as appropriate:

- **integration tests** for normalization and persistence,
- **contract tests** for provider-boundary behavior,
- **data-integrity tests** for provenance retention,
- **workflow-adjacent tests** for connector-to-intake handoff,
- and **failure-path tests** for authorization, normalization, and sync-state behavior.

### 11.1 Connector-specific proof rules

- Gmail/Graph changes must prove provider/account provenance survives normalization.
- Calendar changes must prove event identity and profile/source-calendar meaning survive normalization.
- Telegram changes must prove messages become bounded internal signal/session artifacts.
- Manual import changes must prove explicit labeling and safe routing.
- Sync-state changes must prove visible failure behavior and checkpoint/update correctness.

### 11.2 Do not mark connector work complete without executed proof

If meaningful connector behavior changed and there is no executed verification, the work is not done.

---

## 12. Preferred Connector Session Workflow

When working in this module area, the default session sequence should be:

1. identify relevant `REQ:` anchors,
2. identify relevant `ARCH:` anchors,
3. identify relevant `PLAN:` anchors,
4. inspect current connector, normalization, and handoff boundaries,
5. implement one bounded connector slice,
6. run the relevant proof,
7. update the workstream progress file,
8. report assumptions, blockers, and evidence clearly.

---

## 13. What to Do When the Docs Are Incomplete

If connector work requires a rule that does not yet have a stable anchor:

1. do not invent connector architecture silently,
2. propose the missing anchor,
3. make only the smallest safe implementation move,
4. and record the gap in the relevant working document.

Typical examples include:

- a new provider-specific failure category,
- a new sync checkpoint concept,
- a new profile-scoping rule,
- or a new normalization metadata requirement.

---

## 14. Anti-Patterns to Avoid in This Module

Do not:

- bury business triage logic inside connector code,
- flatten multiple accounts into one generic source stream,
- discard provenance during normalization,
- force one provider’s semantics onto another,
- let Telegram bypass the main intake/review model,
- create hidden write-back behavior to external systems,
- hide sync failures,
- or use manual import as a vague “other” bucket with weak metadata.

---

## 15. Final Rule

When in doubt, make connector code more:

- bounded,
- provenance-preserving,
- provider-aware,
- failure-visible,
- and easy to hand off cleanly into the rest of Glimmer.

Do not optimize for convenient integration shortcuts.
Optimize for trustworthy external boundaries that the rest of the product can safely build on.
