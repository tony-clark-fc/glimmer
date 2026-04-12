# Glimmer — Testing Strategy

## Document Metadata

- **Document Title:** Glimmer — Testing Strategy
- **Document Type:** Split Architecture Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `ARCHITECTURE.md`
- **Primary Companion Documents:** Requirements, Build Plan, LangGraph Orchestration, Connectors and Ingestion, UI and Voice, Security and Permissions

---

## 1. Purpose

This document defines the project-specific testing and verification architecture for **Glimmer**.

It translates the verification model from the **Agentic Delivery Framework** and the **Testing Strategy Companion** into a concrete testing shape for Glimmer’s actual stack and product risks.

Glimmer is not a generic CRUD web app. It is a local-first, multi-account, multi-surface assistant system with:

- structured memory,
- graph-based orchestration,
- multi-provider ingestion,
- review-gated interpretation,
- draft-only communication support,
- and companion-channel interaction through Telegram.

The testing strategy must therefore prove not only code correctness, but also:

- provenance preservation,
- review-gate enforcement,
- graph routing correctness,
- cross-surface continuity,
- and no-auto-send boundaries.

**Stable architecture anchor:** `ARCH:TestingArchitecture`

---

## 2. Testing Strategy Intent

The purpose of Glimmer’s testing strategy is to ensure that implementation can be trusted as the product evolves under AI-assisted delivery.

The strategy must make it possible to prove:

1. the domain model behaves correctly,
2. connectors preserve multi-account provenance,
3. LangGraph workflows route, pause, and resume correctly,
4. the UI presents reviewable artifacts clearly,
5. Telegram and voice channels respect the same core rules as the main workspace,
6. and security boundaries prevent unsafe autonomous behavior.

Testing is therefore not just a code-quality activity. It is part of the control system for the product.

**Stable architecture anchor:** `ARCH:TestingStrategyIntent`

---

## 3. Testing Principles

### 3.1 Verification is part of implementation

No meaningful Glimmer workstream should be considered complete without explicit proof against the relevant `TEST:` scenarios.

**Stable architecture anchor:** `ARCH:TestingPrinciple.VerificationIsImplementation`

### 3.2 Automated proof is the default

Where behavior can be tested automatically, it should be.

Manual testing should be reserved for:

- genuinely hard-to-automate exploratory checks,
- visual confirmation where automation is not yet worth the effort,
- or environment-dependent scenarios that cannot reasonably be automated in the current phase.

**Stable architecture anchor:** `ARCH:TestingPrinciple.AutomationFirst`

### 3.3 Behavior matters more than coverage numbers

Tests must prove workflow behavior, state integrity, and decision correctness rather than merely executing lines of code.

**Stable architecture anchor:** `ARCH:TestingPrinciple.BehaviorOverCoverage`

### 3.4 Lower-level proof first, browser proof where it adds value

Prefer proving rules and orchestration at the lowest meaningful level first, then use browser automation for user-visible workflows and critical interaction continuity.

**Stable architecture anchor:** `ARCH:TestingPrinciple.LayeredProof`

### 3.5 Risk-heavy boundaries deserve direct proof

The most important Glimmer risks are not only business-rule defects. They include:

- misclassification,
- provenance loss,
- review-gate bypass,
- cross-account confusion,
- unsafe draft handling,
- and channel continuity drift.

These must be tested explicitly.

**Stable architecture anchor:** `ARCH:TestingPrinciple.RiskDirectedVerification`

---

## 4. Project Test Architecture by Default

The default test architecture for Glimmer should align to the actual technology stack described in the project document set and architecture baseline: Python + FastAPI, LangGraph, React / Next.js, PostgreSQL, Playwright, and companion-channel integration. fileciteturn9file2 fileciteturn9file4

A recommended structure is:

```text
tests/
  unit/
    domain/
    ranking/
    drafting/
    persona/
  integration/
    persistence/
    connectors/
    api/
    orchestration/
  playwright/
    web/
  contract/
    telegram/
    google/
    microsoft/
  packs/
    smoke/
    workstream/
    release/
    data_integrity/
```

This exact folder layout may evolve, but the layer separation should remain visible.

**Stable architecture anchor:** `ARCH:VerificationLayerModel`

---

## 5. Required Verification Layers

Glimmer should verify behavior across six layers.

### 5.1 Unit verification

Use unit tests for:

- domain rules,
- prioritization scoring logic,
- tone selection rules,
- persona-selection rules,
- normalization helpers,
- deadline interpretation helpers,
- and other deterministic logic.

**Stable architecture anchor:** `ARCH:VerificationLayer.Unit`

### 5.2 Integration verification

Use integration tests for:

- persistence behavior,
- state transitions,
- repository behavior,
- summary refresh behavior,
- connector normalization,
- and connector-to-intake handoff.

**Stable architecture anchor:** `ARCH:VerificationLayer.Integration`

### 5.3 API verification

Use API-level tests for:

- FastAPI route behavior,
- validation and error handling,
- authorization or local access controls,
- review action endpoints,
- draft retrieval/update endpoints,
- and system-visible contract behavior.

**Stable architecture anchor:** `ARCH:VerificationLayer.Api`

### 5.4 Graph workflow verification

Use graph-focused tests for:

- intake routing,
- triage decisions,
- planner output generation,
- drafting path behavior,
- interrupt creation,
- resume correctness,
- Telegram workflow routing,
- and voice-session continuity behavior.

This is a first-class Glimmer-specific layer because orchestration is central to product behavior. The Testing Strategy Companion emphasizes stateful workflows, decision logic, and failure-path proof, and Glimmer’s LangGraph design makes that non-optional. fileciteturn9file1 fileciteturn9file7

**Stable architecture anchor:** `ARCH:GraphVerificationStrategy`

### 5.5 Browser workflow verification

Use Playwright for:

- Today view workflows,
- triage review flows,
- draft workspace flows,
- project workspace navigation,
- review queue behavior,
- and user-visible handling of review gates or handoffs.

The framework’s testing companion establishes Playwright as the standard for browser-visible user workflows, and the Glimmer document set already assumes Playwright for UI workflow automation. fileciteturn9file1 fileciteturn9file2

**Stable architecture anchor:** `ARCH:PlaywrightTestBoundary`

### 5.6 Manual-only and deferred verification

Some checks may remain `ManualOnly` or `Deferred`, but those states must be explicit and justified.

Examples may include:

- early voice quality tuning,
- certain Telegram delivery edge cases under real network conditions,
- or one-off environment setup validation.

**Stable architecture anchor:** `ARCH:VerificationLayer.ManualAndDeferred`

---

## 6. Domain and Memory Verification

Because Glimmer’s behavior depends on structured memory and reviewable state layers, the domain and memory model require strong proof.

Tests in this area should prove:

- relationship correctness across `Project`, `Stakeholder`, `ConnectedAccount`, and `Message`,
- separation between interpreted candidate state and accepted operational memory,
- correct linkage between source records and summaries,
- summary refresh triggers and thresholds,
- retrieval boundaries,
- and audit trail creation for meaningful state changes.

This directly follows from the domain model and memory architecture, which explicitly separate source records, interpreted artifacts, accepted memory, and synthesized artifacts. fileciteturn9file6 fileciteturn9file10

**Stable architecture anchor:** `ARCH:DomainMemoryVerification`

---

## 7. Connector and Provenance Verification

The connector layer must be verified not just for data arrival, but for preservation of meaning.

Tests in this area should prove:

- Gmail normalization behavior,
- Google Calendar normalization behavior,
- Microsoft Graph mail and calendar normalization,
- preservation of `ConnectedAccount` and `AccountProfile` linkage,
- retention of remote item and thread IDs,
- manual import labeling,
- Telegram connector mapping into `ChannelSession` / `TelegramConversationState`,
- and observable failure behavior when authorization or normalization fails.

The connectors document explicitly requires official APIs, source isolation, multi-account handling, normalization with provenance, and connector-to-intake handoff discipline. That makes provenance-preserving connector tests load-bearing, not optional. fileciteturn9file8

**Stable architecture anchor:** `ARCH:ConnectorVerificationStrategy`

---

## 8. LangGraph Workflow Verification

The orchestration model is central to Glimmer. Graph verification should therefore be treated as a named and durable test concern.

Tests should prove at least:

- Intake Graph routes correctly based on signal type,
- Triage Graph creates expected classification and extraction artifacts,
- low-confidence cases create reviewable pending states,
- Planner Graph produces explainable priority artifacts,
- Drafting Graph never crosses the no-auto-send boundary,
- Voice Session Graph preserves session continuity,
- Telegram Companion Graph supports lightweight interaction while handing back richer review to the web workspace,
- and interrupt/resume behavior persists and continues correctly.

This follows directly from the LangGraph orchestration architecture, which defines six primary graphs, explicit review gates, interrupt/resume behavior, and channel-aware workflows. fileciteturn9file7

**Stable architecture anchor:** `ARCH:GraphWorkflowVerification`

---

## 9. UI and Browser Verification

The browser-visible verification strategy should focus on user journeys, not low-value clicking.

Playwright coverage should target:

- loading the Today view and seeing current priorities,
- reviewing a triage item and accepting/amending it,
- opening a project workspace and seeing synthesized context,
- reviewing a generated draft and selecting/editing a variant,
- navigating review-required artifacts,
- confirming that provenance is visible in triage and related views,
- and confirming that the UI clearly distinguishes between suggestions and accepted state.

This aligns with the UI architecture, which treats the web workspace as the primary operating surface and requires visible reviewable artifacts, context-before-action, and account-aware provenance display. fileciteturn9file9turn9file5

**Stable architecture anchor:** `ARCH:BrowserWorkflowVerification`

---

## 10. Telegram and Voice Verification

### 10.1 Telegram verification

Telegram tests should prove:

- operator message intake,
- correct session binding,
- creation of normalized internal signal records,
- concise but contextually correct reply generation,
- safe handoff to the web workspace when richer review is needed,
- and avoidance of overexposing sensitive context in companion replies.

The system overview, UI/voice document, connectors document, and security document all treat Telegram as a real companion surface but explicitly not the full control center. The tests should enforce that boundary. fileciteturn9file5turn9file8turn9file9

**Stable architecture anchor:** `ARCH:TelegramVerificationStrategy`

### 10.2 Voice verification

Voice tests should prove:

- transcript intake behavior,
- continuity across one voice session,
- conversion of spoken content into structured artifacts,
- correct routing into planner or drafting flows,
- and review-boundary preservation.

Because voice is layered onto the same underlying memory/orchestration core, the proof target is not “nice speech quality” alone. It is that voice interaction remains behaviorally consistent with the rest of the system. fileciteturn9file5turn9file7

**Stable architecture anchor:** `ARCH:VoiceVerificationStrategy`

---

## 11. Security and Permission Verification

Security verification for Glimmer must cover delivery-level trust boundaries, not just abstract policy statements.

Tests should prove:

- least-privilege connector behavior where testable,
- no-auto-send enforcement,
- review-gate enforcement,
- multi-account token isolation behavior at the application boundary,
- manual import privacy handling,
- Telegram channel parity with core review rules,
- and safe visible behavior when authorization fails or session identity is uncertain.

The security architecture explicitly treats review gates as security controls, tokens as connector-bound secrets, and no-auto-send as a core policy. Those things need direct proof. fileciteturn9file0turn9file1

**Stable architecture anchor:** `ARCH:SecurityAccessVerification`

---

## 12. Data Integrity and Provenance Pack

Glimmer should include a dedicated data-integrity verification pack covering at minimum:

- persistence correctness,
- state-boundary discipline,
- provenance preservation,
- uniqueness and linking integrity,
- accepted-vs-interpreted state separation,
- and audit record creation.

This is explicitly called for in the Glimmer document set through a dedicated `verification-pack-data-integrity.md`, and it fits the memory/provenance-heavy nature of the product. fileciteturn9file2

**Stable architecture anchor:** `ARCH:DataIntegrityVerificationPack`

---

## 13. Test Data and Environment Control

The testing architecture should make environment assumptions visible.

Each meaningful verification pack should state:

- required fixture data,
- required connected-account test doubles or controlled fixtures,
- whether provider APIs are stubbed, mocked, emulated, or live,
- reset strategy for persistence,
- and any prerequisites for Playwright, Telegram, or voice-related execution.

The framework’s testing companion is explicit that automated verification becomes fragile when environment and data assumptions are implicit. Glimmer should follow that rule closely. fileciteturn9file1

**Stable architecture anchor:** `ARCH:TestDataAndEnvironmentModel`

---

## 14. Regression Pack Model

Glimmer should adopt named regression packs rather than vague “test everything” expectations.

Recommended default packs:

1. **Smoke Pack**
   - startup health
   - core route availability
   - basic persistence readiness

2. **Workstream Packs**
   - Foundation
   - Domain and Memory
   - Connectors
   - Triage and Prioritization
   - Drafting UI
   - Voice

3. **Data Integrity Pack**
   - provenance, linking, accepted-state correctness, auditability

4. **Release Pack**
   - cross-workstream critical-path regression

This aligns directly to both the framework’s verification model and the Glimmer document set’s expected verification structure. fileciteturn9file0turn9file2

**Stable architecture anchor:** `ARCH:RegressionPackModel`

---

## 15. Verification Evidence and Completion Rules

A Glimmer feature or work package should not be marked complete merely because code and tests were written.

Evidence should normally include:

- implemented test code,
- executed tests,
- visible pass/fail status,
- explicit note of `ManualOnly` or `Deferred` scenarios where relevant,
- and updated progress-file verification status.

The framework is explicit that completion must be evidence-backed, and the testing companion reinforces that writing tests without running them is incomplete work. Glimmer should inherit that operating standard directly. fileciteturn9file0turn9file1

**Stable architecture anchor:** `ARCH:VerificationEvidenceModel`

---

## 16. Relationship to Build Plan and Verification Catalog

This document defines the project-specific testing architecture, but it does not replace:

- `4. Verification/TEST_CATALOG.md`
- verification pack documents
- workstream-specific progress-file verification summaries
- or build-plan traceability.

Those artifacts should map back to this architecture and to the framework traceability chain:

`REQ:` → `ARCH:` → `PLAN:` → `TEST:` → evidence

That chain is a core principle of the framework and should be preserved for Glimmer. fileciteturn9file0

**Stable architecture anchor:** `ARCH:TestingTraceabilityModel`

---

## 17. Relationship to the Rest of the Architecture Set

This document defines Glimmer’s testing architecture, but it does not define:

- the canonical `TEST:` catalog itself,
- exact workstream verification pack contents,
- or detailed build-plan sequencing.

Those concerns belong in the verification and build-plan layers.

This document instead defines the architectural expectations that those later documents must satisfy.

**Stable architecture anchor:** `ARCH:TestingDocumentBoundary`

---

## 18. Final Note

Glimmer’s testing strategy must prove more than code execution.

It must prove that the assistant remains:

- reviewable,
- provenance-aware,
- explainable,
- safe across multiple accounts and channels,
- and behaviorally consistent across web, Telegram, and voice.

If later implementation drifts toward shallow unit coverage, untested graph logic, or unproven review boundaries, this document should be treated as the corrective reference.

**Stable architecture anchor:** `ARCH:TestingConclusion`

