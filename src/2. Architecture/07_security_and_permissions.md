# Glimmer — Security and Permissions

## Document Metadata

- **Document Title:** Glimmer — Security and Permissions
- **Document Type:** Split Architecture Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `ARCHITECTURE.md`
- **Primary Companion Documents:** Requirements, Connectors and Ingestion, Memory and Retrieval, UI and Voice, LangGraph Orchestration

---

## 1. Purpose

This document defines the security, privacy, permission, and approval-boundary architecture for **Glimmer**.

It explains how Glimmer should manage external identity and API access, how sensitive data should be protected under a local-first posture, how permissions and review gates should be enforced, and how the system prevents assistant convenience from becoming unsafe autonomous behavior.

This document does not define low-level cryptographic implementation detail or provider-specific OAuth setup screens. Its purpose is to define the canonical security and permission posture that downstream implementation, connectors, UI, orchestration, and verification must follow.

**Stable architecture anchor:** `ARCH:SecurityArchitectureIntent`

---

## 2. Security Architecture Intent

Glimmer handles sensitive operational context, including project plans, stakeholder context, message content, calendar data, draft responses, and cross-account provenance.

The security architecture must therefore preserve five things at the same time:

1. **local control of sensitive memory by default**
2. **bounded access to external systems**
3. **least-privilege permissions for all connectors**
4. **explicit human review for externally meaningful actions**
5. **traceable and governable use of assistant-generated outputs**

Glimmer is not intended to be a silent background actor. Its security posture must reinforce the broader product principle that the assistant is proactive and useful, but still bounded, reviewable, and under operator control.

**Stable architecture anchor:** `ARCH:SecurityIntent`

---

## 3. Security Principles

### 3.1 Local-first privacy boundary

The system should default to local storage and local control for project memory, drafts, normalized message content, and operator context wherever practical.

**Stable architecture anchor:** `ARCH:LocalFirstPrivacyBoundary`

### 3.2 Least privilege everywhere

Every external integration should request only the minimum scopes and permissions required for the approved behavior.

**Stable architecture anchor:** `ARCH:LeastPrivilegeModel`

### 3.3 Read-first external posture

For MVP, connected mail and calendar systems should be treated primarily as read-oriented sources. External write actions should remain heavily constrained and explicitly approved.

**Stable architecture anchor:** `ARCH:ReadFirstSecurityPosture`

### 3.4 No hidden side effects

The system must not silently send messages, mutate calendars, or commit non-trivial memory changes without visible workflow boundaries and review states.

**Stable architecture anchor:** `ARCH:NoHiddenSideEffects`

### 3.5 Secrets stay out of prompts

Tokens, credentials, secret material, and similar sensitive values must never be exposed casually through prompts, logs, summaries, or user-facing surfaces.

**Stable architecture anchor:** `ARCH:SecretHandlingBoundary`

### 3.6 Channel access must inherit core rules

Telegram and other companion surfaces must not bypass the same privacy, review, and permission rules that apply in the web workspace.

**Stable architecture anchor:** `ARCH:ChannelSecurityParity`

### 3.7 Review gates are security controls, not just UX choices

Review gates for drafts, ambiguous interpretation, and meaningful state mutation are part of the security posture because they prevent unsafe autonomous behavior.

**Stable architecture anchor:** `ARCH:ReviewGateArchitecture`

---

## 4. Security Boundary Map

The security architecture for Glimmer spans five main boundaries:

1. **Operator boundary**
   - the human operator using the system
2. **Local application boundary**
   - Glimmer backend, UI, local storage, local memory
3. **External API boundary**
   - Google APIs, Microsoft Graph, Telegram API, voice services where applicable
4. **Model execution boundary**
   - local model runtime and any optional remote model provider boundary
5. **Audit and review boundary**
   - review states, operator overrides, and traceability surfaces

Each of these boundaries should be made explicit in implementation and verification.

**Stable architecture anchor:** `ARCH:SecurityBoundaryMap`

---

## 5. Operator Identity and Access Model

### 5.1 Primary operator model

The initial Glimmer design assumes a single primary operator, but that does not eliminate the need for explicit local access control and session identity.

The system should preserve a distinct operator identity model for:

- account ownership,
- connected profile ownership,
- channel binding,
- review action attribution,
- and local preference/policy enforcement.

**Stable architecture anchor:** `ARCH:PrimaryOperatorAccessModel`

### 5.2 Local application access

Even in a single-operator deployment, the local application should be capable of protecting access to the Glimmer workspace and its stored operational memory.

The exact local-auth mechanism may vary by deployment, but the architecture should not assume that sensitive project memory is safely exposed merely because the system is running on the operator’s machine.

**Stable architecture anchor:** `ARCH:LocalWorkspaceAccessBoundary`

---

## 6. OAuth and External Identity Model

### 6.1 OAuth as the external authorization baseline

Access to Google and Microsoft services should be handled through their supported OAuth-based authorization flows.

**Stable architecture anchor:** `ARCH:OAuthAndTokenStorage`

### 6.2 Connected account consent model

Each `ConnectedAccount` should represent a separately authorized external account or profile context.

The security model must preserve:

- which account was authorized,
- which scopes were granted,
- when authorization was obtained or refreshed,
- and whether connector access remains valid.

**Stable architecture anchor:** `ARCH:ConnectedAccountConsentModel`

### 6.3 Multi-account separation

Because Glimmer supports multiple connected Google and Microsoft accounts, the token and connector model must preserve clean separation between those identities.

The system must not accidentally blur:

- one mailbox with another,
- one calendar with another,
- or one tenant context with another.

**Stable architecture anchor:** `ARCH:MultiAccountTokenIsolation`

---

## 7. Token and Secret Handling

### 7.1 Token storage posture

OAuth access tokens, refresh tokens, and similar connector credentials should be stored in a secure local secret boundary rather than in plain project storage or user-visible configuration.

**Stable architecture anchor:** `ARCH:TokenStoragePosture`

### 7.2 Token usage discipline

Tokens should be used only by the bounded connector layer and should not be passed through the wider application or orchestration layers unnecessarily.

Graphs and UI surfaces should deal in account references and domain-linked records, not raw connector credentials.

**Stable architecture anchor:** `ARCH:TokenUsageDiscipline`

### 7.3 Secret exposure prevention

The system must avoid exposing secrets through:

- logs,
- prompts,
- summaries,
- telemetry payloads,
- screenshots,
- or debugging views.

**Stable architecture anchor:** `ARCH:SecretExposurePrevention`

### 7.4 Revocation and failure handling

Where connector authorization expires or is revoked, the system should fail safely and visibly rather than degrading into silent partial behavior.

**Stable architecture anchor:** `ARCH:TokenRevocationHandling`

---

## 8. Provider Permission Boundaries

### 8.1 Google mail and calendar scopes

The MVP should request only the minimum Google scopes needed for the approved read-oriented mail and calendar ingestion behavior.

This means the architecture should avoid assuming broad mailbox control or write privileges where they are not required.

**Stable architecture anchor:** `ARCH:GoogleScopeMinimization`

### 8.2 Microsoft Graph scope minimization

The MVP should request only the minimum Microsoft Graph scopes needed for read-oriented mail and calendar ingestion and any explicitly approved metadata access.

**Stable architecture anchor:** `ARCH:MicrosoftScopeMinimization`

### 8.3 Telegram permission boundary

Telegram access should be constrained to the scoped bot/channel interaction required for the companion-channel experience.

Telegram should not be treated as a privileged administrative surface that can bypass the main system’s review and permission rules.

**Stable architecture anchor:** `ARCH:TelegramPermissionBoundary`

---

## 9. No-Auto-Send Policy

### 9.1 Core policy

Glimmer shall not autonomously send outbound emails, Telegram messages on behalf of the operator to third parties, calendar updates, or other externally meaningful communications in the MVP.

**Stable architecture anchor:** `ARCH:NoAutoSendPolicy`

### 9.2 Draft-only external communication posture

The assistant may generate drafts and prepare content for operator use, but actual external communication should remain under explicit human control.

This applies to:

- email replies,
- messages prepared for manual paste,
- calendar-related wording,
- and similar operator-facing communication outputs.

**Stable architecture anchor:** `ARCH:DraftOnlyCommunicationBoundary`

### 9.3 Rationale

This policy exists because Glimmer is designed to assist with nuanced, stakeholder-sensitive work. Draft generation can be highly valuable; silent sending is too risky at this stage.

**Stable architecture anchor:** `ARCH:NoAutoSendRationale`

---

## 10. Review Gate Enforcement

### 10.1 Review-required categories

The system should require review for:

- outgoing draft use,
- ambiguous project classification,
- extracted action acceptance when meaning is unclear,
- stakeholder merge or identity consolidation with non-trivial uncertainty,
- major project-memory reinterpretation,
- and any proposed external write action introduced in future phases.

**Stable architecture anchor:** `ARCH:ReviewRequiredCategories`

### 10.2 Enforcement posture

Review gates should be enforced through:

- domain review-state records,
- orchestration interrupts,
- UI review queues,
- and explicit operator actions to accept, amend, reject, or defer.

**Stable architecture anchor:** `ARCH:ReviewGateEnforcement`

### 10.3 Channel parity

If a workflow originates in Telegram or voice but requires richer review, the system should hand the operator into the web workspace rather than pretending a lightweight channel can safely approve everything.

**Stable architecture anchor:** `ARCH:CrossChannelReviewParity`

---

## 11. Data Privacy and Classification Posture

### 11.1 Sensitive data classes

Glimmer may hold data such as:

- project plans,
- stakeholder notes,
- message bodies,
- calendar details,
- draft responses,
- and account provenance.

These should be treated as sensitive operational data by default.

**Stable architecture anchor:** `ARCH:OperationalDataSensitivity`

### 11.2 Data minimization posture

The system should avoid collecting or retaining more external data than is useful to the approved product behavior.

This means:

- only ingesting the fields actually needed,
- avoiding unnecessary duplication,
- and preferring summaries or scoped retrieval where full raw context is not required for repeated use.

**Stable architecture anchor:** `ARCH:DataMinimizationPosture`

### 11.3 Manual import handling

Manual imports such as WhatsApp text should preserve that they were manually supplied and should be treated with the same privacy and review posture as other ingested communication.

**Stable architecture anchor:** `ARCH:ManualImportPrivacyBoundary`

---

## 12. Local-First Privacy and Model Routing

### 12.1 Default local execution posture

The preferred baseline is that project memory, summaries, and other sensitive operational context remain locally stored and, where possible, locally processed.

**Stable architecture anchor:** `ARCH:LocalProcessingBaseline`

### 12.2 Optional remote model boundary

If a remote model provider is used for selected high-value tasks, that boundary must be:

- explicit,
- policy-driven,
- and understandable to the operator.

The architecture should support model-routing policy rather than assuming one universal execution boundary.

**Stable architecture anchor:** `ARCH:RemoteModelBoundary`

### 12.3 Prompt-content discipline

Whether using local or remote models, Glimmer should avoid unnecessarily broad prompt stuffing of sensitive operational context.

The system should prefer:

- bounded context hydration,
- structured references,
- summary use where appropriate,
- and least-necessary context for the task at hand.

**Stable architecture anchor:** `ARCH:PromptContentDiscipline`

---

## 13. Audit, Attribution, and Override Traceability

### 13.1 Audit purpose

The audit layer should preserve enough evidence to explain how meaningful assistant behavior happened.

**Stable architecture anchor:** `ARCH:SecurityAuditPurpose`

### 13.2 Security-relevant events to trace

The system should trace at minimum:

- connected-account authorization events,
- connector failure and revocation events,
- review decisions,
- operator overrides,
- draft-generation events,
- major accepted-memory changes,
- and channel/session handoffs where relevant.

**Stable architecture anchor:** `ARCH:SecurityRelevantAuditEvents`

### 13.3 Attribution posture

When the operator approves, amends, or rejects assistant outputs, the system should preserve that distinction rather than rewriting history as if the assistant’s first output had always been the final truth.

**Stable architecture anchor:** `ARCH:OperatorOverrideAttribution`

---

## 14. Telegram-Specific Security Considerations

### 14.1 Telegram as companion surface only

Telegram should be treated as a lower-complexity companion interaction surface, not the authoritative place for complex approval decisions or unrestricted administrative control.

**Stable architecture anchor:** `ARCH:TelegramCompanionSecurityRole`

### 14.2 Session binding and identity confidence

The system should bind Telegram interactions to the correct operator identity and session context with sufficient confidence before allowing sensitive assistant responses to be delivered.

**Stable architecture anchor:** `ARCH:TelegramSessionIdentityBinding`

### 14.3 Concision and leakage control

Because Telegram is a mobile companion surface, responses should be concise and should avoid dumping excessive sensitive context into a chat channel when a safer handoff to the web workspace would be more appropriate.

**Stable architecture anchor:** `ARCH:TelegramLeakageControl`

---

## 15. Failure and Recovery Posture

### 15.1 Security-related failure classes

Relevant failure classes include:

- expired or revoked OAuth consent,
- invalid token storage state,
- account mismatch,
- review-state loss,
- channel misbinding,
- accidental privilege escalation through future features,
- and unintended context leakage to a remote model or external channel.

### 15.2 Recovery posture

The system should fail in a way that is:

- visible,
- bounded,
- diagnosable,
- and safe by default.

It should not silently continue with weakened guarantees.

**Stable architecture anchor:** `ARCH:SecurityFailureRecovery`

---

## 16. Relationship to Verification

The verification model for Glimmer must explicitly test:

- least-privilege connector behavior,
- review-gate enforcement,
- no-auto-send constraints,
- token isolation across multiple accounts,
- provenance-preserving channel behavior,
- and safe fallback when authorization or channel state fails.

This aligns with the Agentic Delivery Framework and its testing companion, which treat verification as a first-class design concern and require evidence-backed completion rather than assumption-backed confidence. fileciteturn8file0 fileciteturn8file1

**Stable architecture anchor:** `ARCH:SecurityVerificationImplications`

---

## 17. Relationship to the Rest of the Architecture Set

This document defines Glimmer’s security and permission posture, but it does not define:

- provider-specific OAuth implementation screens,
- UI layout specifics,
- low-level storage implementation,
- or test-pack structure.

Those concerns are handled in:

- `04-connectors-and-ingestion.md`
- `06-ui-and-voice.md`
- `08-testing-strategy.md`
- and later build-plan and verification artifacts.

**Stable architecture anchor:** `ARCH:SecurityDocumentBoundary`

---

## 18. Final Note

Glimmer’s usefulness depends on trust.

That trust will not come from polished assistant language alone. It will come from disciplined boundaries:

- local-first memory,
- least-privilege integrations,
- review-first behavior,
- no hidden side effects,
- and visible attribution for what the assistant suggested versus what the operator accepted.

If later implementation drifts toward convenience at the expense of control, this document should be treated as the corrective reference.

**Stable architecture anchor:** `ARCH:SecurityConclusion`
