# Glimmer — Build Strategy and Scope

## Document Metadata

- **Document Title:** Glimmer — Build Strategy and Scope
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Testing Strategy

---

## 1. Purpose

This document defines the practical delivery strategy for **Glimmer**.

It explains how the project should be built in sequenced phases, what the initial delivery scope includes and excludes, what assumptions guide the early implementation path, and how work should be staged so that Glimmer becomes useful quickly without collapsing into uncontrolled complexity.

This document is not the place for deep implementation detail per workstream. Its role is to define the operating strategy that all workstream plans should inherit.

**Stable plan anchor:** `PLAN:StrategyAndScope`

---

## 2. Strategic Delivery Intent

Glimmer should be delivered as a **local-first, review-first project chief-of-staff system** that becomes operationally useful early, then grows in sophistication without weakening trust, provenance, or operator control.

The delivery strategy must therefore balance two competing needs:

1. **Get to useful quickly**
   - so the system starts helping with real project coordination as early as possible.

2. **Avoid false progress**
   - where the system looks impressive on the surface but lacks durable memory, trustworthy triage, review gates, or provenance discipline.

The correct strategy is therefore to build Glimmer in a layered sequence:

- strong control surface first,
- then runtime and memory foundations,
- then external ingestion boundaries,
- then assistant core workflows,
- then richer interaction modes.

**Stable plan anchor:** `PLAN:StrategicDeliveryIntent`

---

## 3. Product Scope Posture

### 3.1 What Glimmer is trying to become

Glimmer is intended to become a durable personal project-operations system for a single operator managing multiple active projects, multiple communication accounts, and multiple interaction contexts.

It is not just:

- an email assistant,
- a task tracker,
- a chatbot,
- or a reminder app.

It is a memory-backed, workflow-aware, tactful execution partner.

**Stable plan anchor:** `PLAN:ProductScopeIntent`

### 3.2 MVP scope posture

The MVP should focus on the smallest product shape that is genuinely useful in daily work.

That means the MVP must be able to:

- ingest real project-relevant signals,
- preserve account provenance,
- classify and triage those signals,
- maintain structured project and stakeholder memory,
- generate priorities and focus packs,
- produce reviewable drafts,
- escalate tasks that exceed local model capability to a bounded deep-research path,
- and provide a mobile companion path through Telegram.

Anything that does not materially support those outcomes should be treated cautiously in early delivery.

**Stable plan anchor:** `PLAN:MvpScopePosture`

### 3.3 Deliberate non-goal posture

The project should explicitly resist early scope creep into:

- autonomous outbound communication,
- complex collaboration/multi-user tenancy,
- broad unsupported chat-platform integration,
- rich admin tooling before the core assistant loop works,
- or fancy voice/presence polish before memory, triage, and drafting are dependable.

**Stable plan anchor:** `PLAN:DeliberateNonGoalPosture`

---

## 4. Delivery Assumptions

The current strategy assumes the following.

### 4.1 Operator model assumptions

- There is one primary operator.
- The operator manages roughly six live projects in parallel.
- The operator has multiple Google and Microsoft 365 accounts or profiles.
- The operator is willing to review and guide Glimmer rather than expecting blind autonomy.

**Stable plan anchor:** `PLAN:Assumption.OperatorModel`

### 4.2 Source and channel assumptions

- Email and calendar are the dominant source systems for project signal.
- Manual import remains acceptable for unsupported channels such as WhatsApp in MVP.
- Telegram is the chosen MVP companion surface.
- Voice is valuable, but should be layered after the non-voice core is strong.

**Stable plan anchor:** `PLAN:Assumption.SourceAndChannelModel`

### 4.3 Technical assumptions

- Python + FastAPI is the backend baseline.
- LangGraph is the orchestration baseline.
- React / Next.js is the UI baseline.
- PostgreSQL is the primary operational store.
- pgvector or equivalent is the semantic retrieval baseline.
- Playwright is the browser workflow verification standard.

**Stable plan anchor:** `PLAN:Assumption.TechnologyBaseline`

### 4.4 Delivery assumptions

- A coding agent will do a large share of implementation work.
- The human operator remains accountable for architecture truth and scope decisions.
- Real external account authorization and secret provisioning will require human action.
- Verification must grow alongside implementation, not after it.

**Stable plan anchor:** `PLAN:Assumption.DeliveryModel`

---

## 5. Delivery Sequencing Logic

### 5.1 Why sequencing matters here

Glimmer has several parts that could easily be built in the wrong order:

- voice before memory,
- Telegram before the web workspace,
- semantic retrieval before structured domain truth,
- drafting polish before triage quality,
- or provider integrations before provenance rules exist.

That would create a flashy but unreliable system.

The strategy therefore enforces a sequencing model where each major layer is built on top of trustworthy lower layers.

**Stable plan anchor:** `PLAN:SequencingLogic`

### 5.2 Required order of maturity

Glimmer should mature in this order:

1. **Control documents and build discipline**
2. **Runtime and persistence skeleton**
3. **Structured domain and memory model**
4. **Connector and ingestion boundaries**
5. **Triage and prioritization workflows**
6. **Core web workspace UX**
7. **Deep research and escalated reasoning**
8. **Telegram companion UX**
9. **Voice interaction layer**
10. **Broader hardening and regression expansion**

**Stable plan anchor:** `PLAN:RequiredOrderOfMaturity`

### 5.3 Why web comes before companion/voice

The web application is the canonical control surface. It is the only place where rich review, project orientation, draft comparison, provenance visibility, and broad memory navigation can all coexist cleanly.

Telegram and voice must therefore grow on top of that control surface, not replace it.

**Stable plan anchor:** `PLAN:WebBeforeCompanionRationale`

---

## 6. Phase-by-Phase Strategy

### 6.1 Phase 0 — Control Surface and Delivery Foundations

**Intent:** Establish the authoritative project control system before implementation depth begins.

This phase includes:

- requirements,
- architecture,
- build-plan index,
- testing strategy,
- and the later instruction/verification surfaces that make AI-assisted delivery stable.

This phase is largely complete once the core control docs exist and are consistent.

**Stable plan anchor:** `PLAN:PhaseStrategy.Phase0`

### 6.2 Phase 1 — Runtime and Memory Foundation

**Intent:** Create a functioning implementation skeleton and the durable state model Glimmer depends on.

This phase should prioritize:

- repo and app structure,
- backend and frontend baseline setup,
- persistence baseline,
- domain entities,
- repositories,
- review-state scaffolding,
- and summary scaffolding.

The output of this phase is not yet a compelling assistant, but it creates the substrate the assistant needs.

**Stable plan anchor:** `PLAN:PhaseStrategy.Phase1`

### 6.3 Phase 2 — External Boundary and Intake

**Intent:** Make Glimmer capable of receiving real external signals safely.

This phase should prioritize:

- Google and Microsoft account integration,
- multi-account account/profile linkage,
- normalization,
- provenance preservation,
- Telegram connector baseline,
- and manual import flow.

At the end of this phase, Glimmer should be able to ingest meaningfully and preserve what each signal actually is.

**Stable plan anchor:** `PLAN:PhaseStrategy.Phase2`

### 6.4 Phase 3 — Assistant Core Workflows

**Intent:** Make the system operationally useful in day-to-day project work.

This phase should prioritize:

- triage,
- classification,
- extracted actions,
- prioritization,
- project summary refresh,
- focus packs,
- draft generation,
- and the key web UX surfaces that expose those artifacts.

At the end of this phase, Glimmer should begin to feel like a working chief-of-staff assistant rather than just a structured data layer.

**Stable plan anchor:** `PLAN:PhaseStrategy.Phase3`

### 6.4A Phase 3A — Deep Research and Escalated Reasoning

**Intent:** Give Glimmer the ability to reach beyond local model capability when a task warrants deeper research.

This phase should prioritize:

- Python port of the existing C# research agent,
- browser-mediated Gemini adapter boundary,
- research domain models and persistence,
- orchestration integration for research escalation,
- failure and degraded-mode handling,
- and research visibility in the web workspace.

This phase sits after the core assistant workflows and web workspace because research results need somewhere structured to land — the triage, project, and review surfaces must exist first.

**Stable plan anchor:** `PLAN:PhaseStrategy.Phase3A`

### 6.5 Phase 4 — Companion and Voice Expansion

**Intent:** Extend the useful assistant experience into mobile and spoken interaction without weakening trust or review discipline.

This phase should prioritize:

- Telegram companion usefulness,
- channel handoff behavior,
- voice session handling,
- transcript-to-structure pathways,
- and cross-surface continuity.

At the end of this phase, Glimmer should be meaningfully usable when away from the main workspace.

**Stable plan anchor:** `PLAN:PhaseStrategy.Phase4`

---

## 7. MVP Capability Threshold

The MVP should not be declared real simply because it can ingest messages and produce AI text.

For Glimmer to count as a meaningful MVP, it should meet the following threshold:

1. **Multi-project orientation exists**
2. **Multi-account provenance exists**
3. **Structured project memory exists**
4. **Triage produces reviewable outputs**
5. **Drafts are generated in a reviewable workspace**
6. **The Today / Portfolio / Project / Triage control surfaces exist**
7. **Telegram can retrieve or capture meaningful lightweight interaction**
8. **Review boundaries and no-auto-send behavior are real**

If these are not true, the product is still in an internal shaping phase rather than true MVP.

**Stable plan anchor:** `PLAN:MvpCapabilityThreshold`

---

## 8. Early Deferral Strategy

The strategy should explicitly defer some things so the core becomes strong.

### 8.1 Defer for later unless forced earlier

The following should generally be deferred until the earlier layers are sound:

- advanced voice polish,
- rich Telegram command menus beyond what is useful,
- more chat-channel integrations,
- advanced analytics/reporting screens,
- multi-user access models,
- heavy personalization systems,
- autonomous workflow execution,
- or speculative enterprise deployment features.

**Stable plan anchor:** `PLAN:EarlyDeferralList`

### 8.2 Why deferral matters

Glimmer’s risk is not under-featured novelty. Its risk is over-featured fragility.

Deliberate deferral protects the assistant from becoming theatrical before it becomes dependable.

**Stable plan anchor:** `PLAN:DeferralRationale`

---

## 9. Human Intervention Model

### 9.1 Human intervention is expected, not exceptional

Because Glimmer touches real communication systems and uses a coding-agent-heavy delivery model, some human interventions are a normal part of the strategy.

Expected human actions include:

- external account authorization,
- secret or token provisioning,
- Telegram bot provisioning,
- model-routing policy decisions,
- approval of major scope or architecture changes,
- and acceptance of any `ManualOnly` or `Deferred` verification outcomes.

**Stable plan anchor:** `PLAN:HumanInterventionModel`

### 9.2 Build around what the agent can and cannot do

The work should be structured so the coding agent can make maximal progress inside the repo even when external setup work is pending.

That means:

- use abstractions and fakes where possible,
- complete code-safe work before raising a blocker,
- and keep human dependencies explicit in workstream plans and progress files.

**Stable plan anchor:** `PLAN:AgentBoundaryAwarePlanning`

---

## 10. Verification Strategy at the Strategy Layer

### 10.1 Proof must grow with implementation

The strategy requires that verification maturity grows alongside feature maturity.

That means:

- domain work brings domain tests,
- connector work brings provenance tests,
- graph work brings routing and interrupt/resume tests,
- UI work brings Playwright workflow proof,
- and security boundaries bring direct enforcement tests.

**Stable plan anchor:** `PLAN:VerificationGrowthRule`

### 10.2 No false green posture

The project should avoid a false sense of progress caused by:

- broad claims of completion without executed proof,
- shallow unit tests standing in for workflow verification,
- or a polished UI sitting on top of weak memory and orchestration behavior.

**Stable plan anchor:** `PLAN:NoFalseGreenPosture`

---

## 11. Implementation Strategy Rules for Workstreams

All detailed workstream plans should inherit the following rules.

### 11.1 Prefer bounded vertical slices

Build slices that can be reviewed and verified cleanly, rather than giant partially connected feature slabs.

**Stable plan anchor:** `PLAN:WorkstreamRule.BoundedSlices`

### 11.2 Prefer source-of-truth correctness over convenience

When in conflict, preserve domain clarity, provenance, reviewability, and trust before optimizing for speed or flashy UX.

**Stable plan anchor:** `PLAN:WorkstreamRule.SourceTruthBeforeConvenience`

### 11.3 Preserve traceability across the chain

Each meaningful work package should be traceable through the chain:

`REQ:` → `ARCH:` → `PLAN:` → `TEST:`

**Stable plan anchor:** `PLAN:WorkstreamRule.Traceability`

### 11.4 Do not overfit to temporary stubs

Temporary fakes, mock flows, or simplified connectors must not quietly become the architecture.

**Stable plan anchor:** `PLAN:WorkstreamRule.NoStubDrift`

### 11.5 Treat review gates as load-bearing

Review-first behavior is central to Glimmer. Workstream plans must not treat review gates as optional polish.

**Stable plan anchor:** `PLAN:WorkstreamRule.ReviewGatesLoadBearing`

---

## 12. Scope Boundaries for the Next Build-Plan Files

This strategy document is the parent posture for the detailed workstream files, but it does not define:

- exact implementation tasks per workstream,
- precise file-level change plans,
- verification-pack contents,
- or working-document handoff content.

Those belong in:

- `workstream_a_foundation.md`
- `workstream_b_domain_and_memory.md`
- `workstream_c_connectors.md`
- `workstream_d_triage_and_prioritization.md`
- `workstream_e_drafting_ui.md`
- `workstream_f_voice.md`
- `workstream_g_testing_and_regression.md`
- `workstream_h_deep_research.md`
- and later verification documents.

**Stable plan anchor:** `PLAN:StrategyDocumentBoundary`

---

## 13. Final Note

The correct delivery strategy for Glimmer is not to chase the most visibly impressive feature first.

It is to build a system that becomes more useful as it becomes more trustworthy.

That means:

- strong foundations,
- explicit boundaries,
- phased capability growth,
- real review-first behavior,
- and verification that keeps up with ambition.

If later delivery pressure pushes the project toward flashy companion behavior without durable memory, provenance, and review discipline underneath it, this document should be treated as the corrective reference.

**Stable plan anchor:** `PLAN:StrategyConclusion`

