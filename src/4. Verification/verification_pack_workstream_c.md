# Glimmer — Verification Pack: Workstream C Connectors

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Workstream C Connectors
- **Document Type:** Canonical Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Test Catalog, Requirements, Architecture, Build Plan, Testing Strategy, Workstream C Connectors, Workstream B Verification Pack

---

## 1. Purpose

This document defines the **Workstream C verification pack** for **Glimmer**.

Its purpose is to prove that the bounded external-ingestion layer created by **Workstream C — Connectors** is real, provenance-preserving, multi-account-aware, and safe enough for later triage, planning, drafting, UI, and companion workflows to depend on.

Where Workstream B proves that Glimmer has a trustworthy memory spine, this pack proves that real external signals can enter that spine without losing meaning.

**Stable verification anchor:** `TESTPACK:WorkstreamC.ControlSurface`

---

## 2. Role of the Workstream C Pack

This pack exists to verify the implementation outcomes expected from the Connectors workstream, including:

- connector boundary isolation,
- connected-account and profile linkage,
- provenance-preserving normalization,
- safe handoff into the intake boundary,
- Telegram companion intake behavior,
- manual import labeling and routing,
- and visible sync/failure state.

This pack is the first verification surface where Glimmer’s external boundary becomes real. If it is weak, later assistant-core workflows may still appear to function while actually depending on flattened source meaning, account confusion, or unsafe connector shortcuts.

**Stable verification anchor:** `TESTPACK:WorkstreamC.Role`

---

## 3. Relationship to the Control Surface

This verification pack is derived from and aligned to:

- the **Agentic Delivery Framework**, especially its authority model, verification model, evidence-of-completion rules, and structured control-surface posture, fileciteturn27file0
- the **Testing Strategy Companion**, especially automation-first proof, integration and contract testing, failure-path testing, and evidence-backed completion, fileciteturn27file1
- the **Glimmer Agentic Delivery Document Set**, which explicitly defines `verification-pack-workstream-c.md` as part of the canonical verification family, fileciteturn27file2
- the **Glimmer Requirements**, especially message ingestion, multi-account profile support, Telegram mobile presence, privacy and least privilege, traceability, and safe behavior defaults, fileciteturn27file3
- the latest **Architecture** state, especially connector isolation, normalization, provenance, least privilege, review boundaries, Telegram companion channel, and system-boundary anchors, including the current manually maintained architecture document, fileciteturn27file16turn27file5
- the **Build Plan**, **Build Strategy and Scope**, and **Workstream C — Connectors**, which explicitly position external-boundary and intake work after memory foundations and before assistant-core workflow sophistication, fileciteturn27file6turn27file7turn27file10
- the **Glimmer Testing Strategy** and **Workstream G — Testing and Regression**, which define connector/provenance verification, contract/integration testing, and regression-pack expectations, fileciteturn27file4turn27file14
- the **Governance and Process** document, which requires evidence-backed completion and surfaced drift for meaningful work, fileciteturn27file15
- and the current **Test Catalog**, which already defines the core connector/provenance `TEST:` anchors this pack should organize and extend. fileciteturn27file17

**Stable verification anchor:** `TESTPACK:WorkstreamC.ControlSurfaceAlignment`

---

## 4. Why This Pack Is Load-Bearing

The architecture and build plan are explicit that Glimmer must ingest real signals from multiple Google and Microsoft accounts, plus Telegram and manual imports, while preserving account identity, provider semantics, thread/event context, and safe no-auto-send posture. fileciteturn27file7turn27file10turn27file16

Workstream C is where those rules become real through:

- connector abstraction and provider boundary structure,
- account/profile linkage,
- Gmail and Google Calendar normalization,
- Microsoft mail and calendar normalization,
- Telegram companion intake,
- manual import handling,
- connector-to-intake handoff,
- and sync/failure observability. fileciteturn27file10

If this pack is weak, later workstreams may still appear to function while actually depending on:

- flattened account identity,
- erased provider semantics,
- ambiguous thread/event context,
- hidden connector failures,
- or business logic that leaked into integration code.

That is exactly what this pack is meant to prevent.

**Stable verification anchor:** `TESTPACK:WorkstreamC.Rationale`

---

## 5. Workstream C Verification Scope

### 5.1 In scope

This pack covers proof for the following Connectors concerns:

- connector abstraction and provider-boundary isolation,
- connected-account and account-profile linkage in connector flows,
- normalization of mail, calendar, Telegram, and manual-import source material,
- preservation of provider/account/profile/thread/event/source provenance,
- source-record persistence before business interpretation,
- explicit connector-to-intake handoff behavior,
- sync-state and failure-state visibility,
- and read-first / no-auto-send external-boundary discipline.

### 5.2 Out of scope

This pack does **not** attempt to prove:

- deep assistant-core classification/planner behavior,
- browser-visible triage UX,
- draft workspace quality,
- rich Telegram conversational usefulness beyond bounded intake/handoff,
- or full voice-session interaction quality.

Those belong to later workstream packs.

**Stable verification anchor:** `TESTPACK:WorkstreamC.Scope`

---

## 6. Source `TEST:` Anchors Included in This Pack

The Workstream C pack is built primarily from the connector-and-provenance scenario group in the canonical Test Catalog and adds a small number of connector-boundary scenarios needed to cover the full Workstream C shape. fileciteturn27file17

### 6.1 Canonical connector/provenance anchors already defined in the Test Catalog

#### `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount`
- **Scenario name:** Google mail normalization preserves thread and account meaning
- **Layers:** `integration`, `contract`
- **Role in this pack:** Proves Gmail normalization retains operationally meaningful metadata. fileciteturn27file17

#### `TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext`
- **Scenario name:** Google Calendar normalization preserves profile and calendar context
- **Layers:** `integration`, `contract`
- **Role in this pack:** Proves event meaning is preserved rather than flattened into generic text. fileciteturn27file17

#### `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread`
- **Scenario name:** Microsoft mail normalization preserves mailbox and conversation context
- **Layers:** `integration`, `contract`
- **Role in this pack:** Proves Graph mail semantics remain intact. fileciteturn27file17

#### `TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext`
- **Scenario name:** Microsoft calendar normalization preserves account and event context
- **Layers:** `integration`, `contract`
- **Role in this pack:** Proves Microsoft calendar semantics survive normalization. fileciteturn27file17

#### `TEST:Connector.ManualImport.LabelingAndRouting`
- **Scenario name:** Manual imports are explicitly labeled and routed safely
- **Layers:** `integration`, `api`
- **Role in this pack:** Proves unsupported-channel input remains explicit and auditable. fileciteturn27file17

#### `TEST:Connector.Telegram.InboundBecomesBoundedSignal`
- **Scenario name:** Telegram inbound interaction becomes bounded internal signal/session state
- **Layers:** `integration`, `contract`, `graph`
- **Role in this pack:** Proves Telegram does not bypass the core intake model. fileciteturn27file17

#### `TEST:Connector.SyncFailure.VisibleState`
- **Scenario name:** Connector sync failure is visible and does not silently disappear
- **Layers:** `integration`
- **Role in this pack:** Proves sync and authorization failures are observable. fileciteturn27file17

### 6.2 Additional Workstream C-specific anchors introduced by this pack

#### `TEST:Connector.Framework.ProviderBoundaryIsolation`
- **Scenario name:** Connector framework preserves provider-boundary isolation from downstream business logic
- **Primary layers:** `integration`, `manual_only`
- **Primary drivers:** `REQ:MessageIngestion`, `ARCH:ConnectorIsolation`, `ARCH:NormalizationPipeline`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove provider SDK details do not leak upward into orchestration, domain, or UI layers.

#### `TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile`
- **Scenario name:** Connector execution resolves the correct account/profile context
- **Primary layers:** `integration`
- **Primary drivers:** `REQ:MultiAccountProfileSupport`, `ARCH:ConnectedAccountModel`, `ARCH:AccountProfileModel`, `ARCH:AccountProvenanceModel`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove multi-account separation is real in execution, not merely stored metadata.

#### `TEST:Connector.Normalization.PersistBeforeInterpretation`
- **Scenario name:** Normalized source records persist before assistant-core interpretation begins
- **Primary layers:** `integration`, `graph`
- **Primary drivers:** `REQ:TraceabilityAndAuditability`, `ARCH:NormalizationPipeline`, `ARCH:IntakeGraph`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`, `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove source truth exists as a durable layer before classification/planning begins.

#### `TEST:Connector.IntakeHandoff.BoundedReferenceFlow`
- **Scenario name:** Connector-to-intake handoff uses bounded references instead of provider payload sprawl
- **Primary layers:** `integration`, `graph`
- **Primary drivers:** `ARCH:NormalizationPipeline`, `ARCH:IntakeGraph`, `ARCH:StructuredMemoryModel`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`, `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove integration code hands off cleanly without becoming an orchestration shortcut.

#### `TEST:Connector.Security.ReadFirstNoAutoSendPreserved`
- **Scenario name:** Connector implementation remains read-first and preserves no-auto-send boundaries
- **Primary layers:** `integration`, `contract`, `manual_only`
- **Primary drivers:** `REQ:SafeBehaviorDefaults`, `REQ:PrivacyAndLeastPrivilege`, `ARCH:LeastPrivilegeModel`, `ARCH:NoAutoSendPolicy`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove external-boundary behavior does not silently create outbound side effects.

**Stable verification anchor:** `TESTPACK:WorkstreamC.IncludedTests`

---

## 7. Workstream C Pack Entry Table

| TEST Anchor | Scenario | Layer | Automation Status | Pack Priority | Notes |
|---|---|---|---|---|---|
| `TEST:Connector.Framework.ProviderBoundaryIsolation` | Connector framework preserves provider-boundary isolation from downstream business logic | `integration`, `manual_only` | Planned | High | Structural boundary check early on |
| `TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile` | Connector execution resolves the correct account/profile context | `integration` | Planned | Critical | Protects multi-account semantics |
| `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount` | Google mail normalization preserves thread and account meaning | `integration`, `contract` | Planned | Critical | Gmail ingestion baseline |
| `TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext` | Google Calendar normalization preserves profile and calendar context | `integration`, `contract` | Planned | High | Calendar provenance baseline |
| `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread` | Microsoft mail normalization preserves mailbox and conversation context | `integration`, `contract` | Planned | Critical | Graph mail baseline |
| `TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext` | Microsoft calendar normalization preserves account and event context | `integration`, `contract` | Planned | High | Calendar provenance baseline |
| `TEST:Connector.ManualImport.LabelingAndRouting` | Manual imports are explicitly labeled and routed safely | `integration`, `api` | Planned | High | Protects explicit unsupported-channel path |
| `TEST:Connector.Telegram.InboundBecomesBoundedSignal` | Telegram inbound interaction becomes bounded internal signal/session state | `integration`, `contract`, `graph` | Planned | High | Companion intake boundary |
| `TEST:Connector.Normalization.PersistBeforeInterpretation` | Normalized source records persist before assistant-core interpretation begins | `integration`, `graph` | Planned | Critical | Protects source-truth layer |
| `TEST:Connector.IntakeHandoff.BoundedReferenceFlow` | Connector-to-intake handoff uses bounded references instead of provider payload sprawl | `integration`, `graph` | Planned | High | Protects clean orchestration boundary |
| `TEST:Connector.SyncFailure.VisibleState` | Connector sync failure is visible and does not silently disappear | `integration` | Planned | Critical | Failure transparency |
| `TEST:Connector.Security.ReadFirstNoAutoSendPreserved` | Connector implementation remains read-first and preserves no-auto-send boundaries | `integration`, `contract`, `manual_only` | Planned | Critical | External-impact protection |

**Stable verification anchor:** `TESTPACK:WorkstreamC.EntryTable`

---

## 8. Expected Automation Shape

### 8.1 Integration and contract proof by default

Most Workstream C proof should be implemented through integration and contract-style testing because this workstream is fundamentally about:

- provider-boundary behavior,
- normalization,
- provenance retention,
- account/profile resolution,
- sync/failure handling,
- and safe intake handoff.

### 8.2 Normalization and persistence proof

This proof should verify that:

- provider payloads become explicit internal records,
- provenance fields survive round trips,
- source-bearing records remain distinct,
- and normalization does not flatten thread/event/account meaning.

### 8.3 Handoff and boundedness proof

This proof should verify that:

- normalized records persist before downstream interpretation,
- connectors hand off via bounded references or contracts,
- and provider-specific payload shapes do not leak into the business workflow layer.

### 8.4 Failure and sync-state proof

This proof should verify that:

- connector failures are visible,
- authorization issues remain diagnosable,
- and sync metadata is updated in a clear and bounded way.

### 8.5 Limited `manual_only` use

A small amount of `ManualOnly` classification may still be appropriate here for:

- provider-boundary structural inspection,
- explicit scope/permission review,
- or narrow environment-specific integration checks.

However, the core normalization, provenance, and handoff behaviors should be automated wherever reasonably possible.

**Stable verification anchor:** `TESTPACK:WorkstreamC.AutomationShape`

---

## 9. Environment Assumptions

The Workstream C pack assumes the foundation and memory substrate are already in place.

### 9.1 Required assumptions

Expected baseline assumptions include:

- backend runtime and persistence substrate already working,
- controlled integration-test database or equivalent persistence environment,
- test doubles, fixtures, or controlled provider payload samples for Gmail, Google Calendar, Microsoft mail, Microsoft calendar, and Telegram where live dependencies are not practical,
- and a clear way to execute connector normalization and handoff tests without depending on production credentials.

### 9.2 Live-provider posture

This pack should not require live production Google, Microsoft, Telegram, or voice environments for its core proof.

Live-environment validation may exist as supplementary `ManualOnly` proof where necessary, but the main pack should be executable against controlled fixtures or test boundaries.

### 9.3 Domain/memory proof should already exist

This pack assumes the Workstream B memory substrate is sufficiently stable that connector issues can be interpreted as connector-boundary problems rather than failures of the underlying data model. fileciteturn27file9turn27file18

**Stable verification anchor:** `TESTPACK:WorkstreamC.EnvironmentAssumptions`

---

## 10. Execution Guidance

### 10.1 When to run this pack

This pack should normally be run:

- after meaningful connector or normalization changes,
- after changes to account/profile resolution logic,
- after sync/failure handling changes,
- after manual-import or Telegram intake changes,
- before declaring Workstream C substantially complete,
- and before trusting triage/planner behavior built on imported source records.

### 10.2 Failure handling

If this pack fails:

- later triage, planner, drafting, and UI confidence should be treated cautiously,
- the failure should usually be resolved before deep assistant-core behavior is trusted,
- and progress reporting should explicitly state whether the problem affects provenance, provider semantics, account separation, handoff boundedness, or sync/failure visibility.

### 10.3 Relationship to later connector/provenance regression

This Workstream C pack proves the external-boundary substrate within the workstream context.

Later cross-cutting connector/provenance regression should harden the most important protections here into a broader release-oriented confidence surface.

**Stable verification anchor:** `TESTPACK:WorkstreamC.ExecutionGuidance`

---

## 11. Evidence Expectations

When the Workstream C pack is executed, evidence reporting should capture at minimum:

- execution date/time,
- environment posture used,
- which included `TEST:` anchors were executed,
- pass/fail outcome,
- any `ManualOnly` checks performed,
- any `Deferred` entries and why,
- and a brief statement of whether the external-boundary layer is considered stable enough for assistant-core extension.

This should be summarized in the relevant Workstream C progress file and referenced in broader phase-exit or regression summaries where appropriate. fileciteturn27file15turn27file1

**Stable verification anchor:** `TESTPACK:WorkstreamC.EvidenceExpectations`

---

## 12. Operational Ready Definition for This Pack

The Workstream C verification pack should be considered operationally established when:

1. all included `TEST:` anchors are defined and mapped,
2. provider-boundary and account/profile resolution proof exists,
3. Gmail, Google Calendar, Microsoft mail, and Microsoft calendar normalization proof exists,
4. manual-import and Telegram intake proof exists,
5. normalized-record persistence-before-interpretation proof exists,
6. connector-to-intake bounded handoff proof exists,
7. sync/failure visibility proof exists,
8. read-first / no-auto-send external-boundary proof exists,
9. and the pack can be run repeatably against controlled fixtures or equivalent test boundaries.

At that point, Workstream C has a meaningful verification surface that later assistant-core work can trust.

**Stable verification anchor:** `TESTPACK:WorkstreamC.DefinitionOfOperationalReady`

---

## 13. Relationship to Later Packs

This pack establishes the proof surface for the external-boundary and intake layer only.

Later packs should build on it as follows:

- **Workstream D** should prove triage, extraction, planner, and review-interrupt behavior on top of the normalized records protected here,
- **Workstream E** should prove UI visibility of provenance and review controls using the artifacts safely ingested here,
- **Workstream F** should prove voice and companion interaction continues to route through the same bounded intake/review model,
- **Connector/Provenance regression** should later harden the most important protections here into long-lived release confidence,
- and **Release** should compose representative external-boundary proof into cross-workstream confidence.

This progression is consistent with the Glimmer build plan, workstream map, and Workstream G verification-estate design. fileciteturn27file11turn27file12turn27file13turn27file14

**Stable verification anchor:** `TESTPACK:WorkstreamC.RelationshipToLaterPacks`

---

## 14. Final Note

If Workstream C is implemented but not properly verified, Glimmer may still look intelligent while quietly depending on broken provenance, ambiguous intake, or unsafe external-boundary assumptions.

That is the danger this pack is meant to prevent.

Its job is to prove that Glimmer’s connector layer is:

- bounded,
- provenance-preserving,
- multi-account-aware,
- failure-visible,
- and safe to hand off into the assistant core.

**Stable verification anchor:** `TESTPACK:WorkstreamC.Conclusion`

