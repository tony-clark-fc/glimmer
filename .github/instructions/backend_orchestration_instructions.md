---
applyTo: "apps/backend/**/*.py,apps/backend/**/orchestration/**/*.py,apps/backend/**/graphs/**/*.py,apps/backend/**/services/**/*.py,apps/backend/**/api/**/*.py"
---

# Glimmer — Backend and Orchestration Module Instructions

## Purpose

This instruction file defines the module-scoped rules for Glimmer backend, orchestration, application-service, and API work.

It supplements the global `.github/copilot-instructions.md` file and applies specifically to:

- FastAPI backend code,
- LangGraph orchestration code,
- application services,
- API handlers,
- connector-to-intake handoff services,
- and domain-adjacent backend coordination code.

These rules are stricter than generic backend guidance because this part of Glimmer is where the system’s most important guarantees live:

- structured memory,
- provenance preservation,
- review gates,
- multi-account separation,
- and no-auto-send behavior.

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

Do not let existing code patterns silently override the current Glimmer control documents. The project authority model explicitly treats requirements, architecture, build plan, and verification as the authoritative control surfaces.

---

## 2. What This Module Must Preserve

Backend and orchestration work must preserve these core Glimmer properties:

- **local-first posture** for sensitive project context,
- **structured relational memory** as the operational source of truth,
- **multi-account provenance** for all imported items,
- **reviewable interpreted artifacts** rather than hidden model thoughts,
- **explicit review interrupts** for ambiguous or externally meaningful actions,
- **no-auto-send behavior**,
- and **shared core flows across channels** rather than bespoke channel-specific logic.

These are not optional stylistic preferences. They are load-bearing architecture and security constraints.

---

## 3. Backend Boundary Rules

### 3.1 Keep API handlers thin

FastAPI route handlers should:

- validate and bind inputs,
- call application services or orchestration entrypoints,
- return typed responses,
- and avoid embedding business logic, connector logic, or long-lived workflow logic.

### 3.2 Keep orchestration out of connectors

Connector implementations may normalize and hand off source records, but they must not make project-classification, prioritization, or drafting decisions. Connector boundaries are explicitly limited to controlled access, normalization, provenance, and intake handoff.

### 3.3 Keep graphs out of persistence internals

LangGraph flows should coordinate behavior, not replace repositories or become ad hoc data stores. Durable truth belongs in the domain/persistence layer, not in graph-local state.

### 3.4 Keep domain truth separate from interpreted outputs

The backend must preserve the distinction between:

- normalized source records,
- interpreted candidate artifacts,
- accepted operational state,
- and synthesized summaries.

Do not write code that quietly collapses these layers together.

---

## 4. FastAPI Rules

### 4.1 Typed contracts only

Use explicit typed request/response models.

- Prefer Pydantic models or equivalent typed schemas.
- Do not return loosely shaped dicts for meaningful endpoints.
- Make error responses explicit where possible.

### 4.2 Route grouping by capability

Organize API routes by capability boundaries that match the architecture and workstreams, such as:

- projects
- triage
- drafts
- reviews
- connected accounts
- voice sessions
- focus/briefings

Do not create one giant generic “assistant” router.

### 4.3 No connector credentials in handlers

Do not pass raw OAuth tokens, provider secrets, or connector credentials through route handlers or DTOs. Token handling belongs in bounded security/connector infrastructure.

### 4.4 No long-running orchestration in-request unless clearly intended

If a workflow is resumable, review-gated, or long-running, design the route boundary so it triggers or resumes the workflow safely rather than trying to complete everything inline in a fragile request cycle.

---

## 5. LangGraph Rules

### 5.1 Graphs by business workflow

Graphs must follow the Glimmer orchestration topology:

- Intake Graph
- Triage Graph
- Planner Graph
- Drafting Graph
- Voice Session Graph
- Telegram Companion Graph

Do not invent technical-layer graphs that cut across the documented business workflow boundaries without a clear approved reason.

### 5.2 Use shared downstream flows

When implementing channel-specific entrypoints, reuse shared planning, drafting, and memory-update logic wherever possible. Web, Telegram, and voice differ at entry and interaction shape, not at the level of core business meaning.

### 5.3 Interrupts are first-class

If a workflow reaches a state requiring operator judgment, create a structured interrupt/review state.

Do not:

- silently guess,
- self-commit low-confidence outcomes,
- or bypass the review queue because the next step “seems obvious.”

### 5.4 Graph state should pass references, not giant blobs

Prefer graph state that carries domain references and bounded workflow context rather than duplicating entire project or message payloads everywhere. This matches the documented graph-state model and keeps flows resumable and inspectable.

### 5.5 Persist visible artifacts

Graph outputs must result in visible and reviewable domain artifacts where appropriate, such as:

- `MessageClassification`
- `ExtractedAction`
- `ExtractedDecision`
- `ExtractedDeadlineSignal`
- `FocusPack`
- `Draft`
- `BriefingArtifact`

Do not rely on hidden graph-only conclusions for important behavior.

---

## 6. Multi-Account and Provenance Rules

### 6.1 Never flatten source identity

All backend workflows must preserve, directly or indirectly:

- connected account identifier,
- provider type,
- account profile where relevant,
- remote item identity,
- thread/event/source identity where relevant,
- and source timestamps/import metadata.

This is mandatory because Glimmer explicitly supports one operator with multiple Google and Microsoft accounts and treats source provenance as meaningful, not incidental.

### 6.2 Classification may use provenance, but not erase it

Project classification, urgency interpretation, stakeholder resolution, and drafting tone may all use account provenance as input, but backend code must not discard that provenance after interpretation.

### 6.3 Account-aware queries

When writing repository or service logic over source records, be explicit about account/profile scoping where it matters. Do not assume one undifferentiated inbox or one default tenant.

---

## 7. Review and Approval Rules

### 7.1 Review gates are mandatory backend behavior

Review-required categories include at least:

- ambiguous project classification,
- uncertain stakeholder identity merging,
- materially uncertain extraction,
- major project-memory reinterpretation,
- and any externally meaningful action.

Backend code must treat these as structured states, not as UI-only concepts.

### 7.2 No-auto-send is hard policy

Do not implement backend flows that send emails, send Telegram messages to third parties on behalf of the operator, modify external calendars, or otherwise create external side effects unless and until the control docs are intentionally changed. Draft generation is allowed; autonomous sending is not.

### 7.3 Accepted state must remain distinct

Review acceptance, amendment, rejection, and deferral should operate on persisted reviewable artifacts. Do not treat the first model guess as if it was already accepted truth.

---

## 8. Domain and Persistence Rules

### 8.1 Relational truth first

Use PostgreSQL-backed structured state as the primary truth model.

- Projects, stakeholders, connected accounts, source records, interpreted artifacts, accepted artifacts, summaries, drafts, persona metadata, and audit records belong in structured persistence.
- Retrieval/vector support is secondary and must not replace explicit domain state.

### 8.2 Preserve domain layering

When implementing repositories or services, respect the documented memory layers:

- source layer
- interpretation layer
- accepted operational state layer
- synthesized artifacts layer

### 8.3 Summary refresh must be explicit

Summary refresh should happen via documented triggers, thresholds, and services. Do not make summaries silently rewrite themselves with invisible side effects.

### 8.4 Auditability is required

Meaningful memory evolution, review decisions, draft generation, and other important backend actions should create durable traceable records where the architecture calls for them.

---

## 9. Security Rules for Backend Work

### 9.1 Least privilege assumptions only

Never widen requested connector scopes casually in code or config. If a scope/permission expansion seems necessary, surface it for explicit review.

### 9.2 Secrets stay bounded

Do not:

- log tokens,
- include secrets in prompts,
- store provider credentials in normal tables unless the security design explicitly says so,
- or expose sensitive connector state via debug endpoints.

### 9.3 Local-first defaults

When there is a choice between a local-controlled implementation path and a casual remote dependency for sensitive operational context, prefer the local-controlled path unless the control docs specify otherwise.

### 9.4 Companion channels do not bypass rules

Telegram or voice-origin flows must inherit the same review, privacy, and approval rules as web-origin flows. There is no “lighter” safety model just because the interaction started on a companion channel.

---

## 10. Testing Expectations for This Module

When editing backend/orchestration code, the default proof target should include as appropriate:

- **unit tests** for deterministic helpers, ranking rules, extraction helpers, tone logic, and state-transition rules,
- **integration tests** for persistence behavior, provenance retention, summary refresh, repository/service coordination,
- **API tests** for route validation and review-action behavior,
- **graph workflow tests** for routing, interrupts, resume behavior, planner outputs, drafting paths, Telegram and voice routing,
- and **browser tests** only where the change affects a UI-consumed workflow boundary.

The Glimmer testing strategy explicitly treats graph verification, provenance preservation, review-gate enforcement, and cross-surface continuity as load-bearing proof targets.

### 10.1 Backend-specific proof rules

- Connector-facing changes must prove provenance preservation and visible failure behavior.
- Domain-memory changes must prove accepted-vs-interpreted separation.
- Triage/planner changes must prove honest ambiguity handling and explainable outputs.
- Drafting-path changes must prove no-auto-send boundaries remain intact.
- Voice/Telegram changes must prove they reuse the core model rather than bypass it.

### 10.2 Do not mark backend work complete without executed proof

If meaningful backend behavior changed and there is no executed verification, the work is not done.

---

## 11. Preferred Backend Session Workflow

When working in this module area, the default session sequence should be:

1. identify relevant `REQ:` anchors,
2. identify relevant `ARCH:` anchors,
3. identify relevant `PLAN:` anchors,
4. inspect current code and data model boundaries,
5. implement one bounded slice,
6. run the relevant proof,
7. update the workstream progress file,
8. report assumptions, blockers, and evidence clearly.

This matches the framework’s work-package operating model and the Glimmer governance/process expectations.

---

## 12. What to Do When the Docs Are Incomplete

If a backend change requires a design rule that does not yet have a stable anchor:

1. do not invent architecture silently,
2. propose the missing anchor,
3. make only the smallest safe implementation move that does not weaken Glimmer’s posture,
4. and record the gap in the relevant working document.

Typical examples include:

- new graph-state semantics,
- new review-state types,
- new connector failure categories,
- or new voice-session persistence rules.

---

## 13. Anti-Patterns to Avoid in This Module

Do not:

- bury business logic in FastAPI handlers,
- mix connector SDK calls directly into planner or triage logic,
- let graphs become long-term memory stores,
- collapse raw signals and accepted truth into one model,
- silently merge multi-account data into a generic inbox abstraction,
- hide review-required ambiguity behind a single confidence number with no review path,
- create “temporary” autonomous send paths,
- or add speculative abstractions with no active workstream need.

---

## 14. Final Rule

When in doubt, make the backend more:

- explicit,
- provenance-preserving,
- reviewable,
- resumable,
- and testable.

Do not optimize for magical behavior.
Optimize for durable, explainable, governable assistant behavior that the rest of Glimmer can safely build on.

