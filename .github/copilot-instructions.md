# Glimmer — Global Copilot Instructions

## Purpose

This file defines the global operating instructions for AI coding agents working on **Glimmer**.

It is the always-on implementation behavior layer for the project. It does not replace the canonical control documents.

The control-document authority order is:

1. Requirements
2. Architecture
3. Build Plan
4. Verification
5. Global and module-scoped instructions
6. Working documents
7. Code and tests

If implementation convenience conflicts with the control documents, follow the control documents and surface the conflict.

Framework reference: the project follows the Agentic Delivery Framework and its testing companion.

---

## 1. Project Overview

Glimmer is a **local-first AI project chief-of-staff system** for a single primary operator managing multiple live projects across multiple communication accounts and interaction modes.

Glimmer is intended to:

- maintain structured project and stakeholder memory,
- ingest and normalize communications from multiple Google and Microsoft accounts,
- classify project relevance and extract likely actions,
- generate explainable priorities and focus guidance,
- provide a dedicated draft workspace for copy/paste communication support,
- support a Telegram companion channel,
- and support voice interaction layered onto the same core memory and workflow model.

Glimmer is **advisory, proactive, and reviewable**. It is not silently autonomous. It must preserve provenance, review gates, and no-auto-send behavior.

---

## 2. Current Technology Baseline

Treat the following as the current implementation baseline unless an explicitly approved control-document change says otherwise:

- **Backend:** Python + FastAPI
- **Orchestration:** LangGraph
- **Frontend:** React / Next.js
- **Primary database:** PostgreSQL
- **Retrieval support:** pgvector or equivalent semantic retrieval support
- **External integrations:** Google APIs and Microsoft Graph
- **Local inference runtime:** MLX on Apple Silicon (target hardware: M5 Max 128 GB unified memory)
- **Reference model family:** Gemma 4 (31B for deep reasoning, 26B A4B MoE for low-latency chat, E4B for native audio voice)
- **Voice layer:** Local multi-model inference — native audio model for voice I/O, larger model for reasoning tasks routed through shared orchestration core
- **Deep research:** Bounded browser-mediated Gemini research adapter (Playwright + Chrome debug mode), Python-native port of existing C# research agent
- **Browser workflow verification:** Playwright

Do not silently introduce an alternative architecture or framework stack.

---

## 3. Solution Shape You Must Preserve

The repo should preserve a clear separation between:

- control documents,
- verification documents,
- operational support files,
- backend application code,
- frontend application code,
- and tests.

Expected implementation shape includes:

- `.github/`
- `.github/instructions/`
- `8. Agent Skills/`
- `9. Agent Tools/`
- `1. Requirements/`
- `2. Architecture/`
- `3. Build Plan/`
- `4. Verification/`
- application code areas
- tests
- workstream plan/progress files

Do not collapse these boundaries casually.

---

## 4. Architecture Summary You Must Respect

The most important architectural rules are:

- **Local-first by default** for sensitive operational context.
- **API-first integration** using official APIs, not brittle scraping.
- **Structured memory over loose chat history**.
- **Human approval for external impact**.
- **Explainable assistance** for high-value outputs.
- **Voice layered onto a strong non-voice core**.
- **Visual persona as a managed UX asset**.
- **Multi-account operator model** for Google and Microsoft accounts.
- **Telegram as the MVP companion channel**.
- **Bounded deep research** through browser-mediated Gemini adapter, not general web automation.

Treat these as load-bearing design rules, not optional flavor.

---

## 5. Product and Behavioral Rules

### 5.1 Glimmer is not silently autonomous

Do not implement or normalize behavior that silently:

- sends messages,
- modifies calendars,
- commits major memory changes,
- merges ambiguous stakeholder identities,
- or hardens low-confidence interpretation into accepted truth

without explicit review-state and approval handling.

### 5.2 No-auto-send is a hard rule

Glimmer may draft communication. It must not autonomously send external communications in the MVP.

### 5.3 Review gates are mandatory

Review gates are not polish. They are a core product and security rule.

### 5.4 Provenance must survive

Do not flatten source provenance. Messages, events, imports, and channel-origin artifacts must preserve account/profile/provider/thread/source identity.

### 5.5 Web workspace is the canonical control surface

Telegram and voice are companion modes. Do not treat them as substitutes for the main reviewable workspace.

---

## 6. Coding Conventions and Implementation Posture

### 6.1 General coding rules

- Prefer simple, explicit, well-named code over clever abstraction.
- Keep boundaries visible between domain, orchestration, connectors, API/application services, and UI.
- Do not introduce speculative architecture “for later” unless the current control docs require it.
- Avoid hidden side effects.
- Favor typed, inspectable contracts and DTOs.
- Comment only where it adds real clarity.

### 6.2 Python / FastAPI rules

- Use type hints consistently.
- Keep FastAPI routes thin; business logic belongs in services/orchestration/domain-support layers.
- Prefer Pydantic models or equivalent typed request/response contracts.
- Keep connector credentials and secret handling out of route handlers.
- Keep orchestration concerns out of connector implementations.
- Prefer explicit dependency injection patterns over hidden globals.
- Keep long-running or resumable workflow logic out of HTTP handlers.

### 6.3 React / Next.js rules

- Preserve a workspace-first UI model, not an unbounded chatbot page.
- Keep major surfaces distinct: Today, Portfolio, Project, Triage, Drafts, Review.
- Build browser-testable UI patterns from the start.
- Do not hide review-critical information inside decorative components.
- Keep data loading and error states explicit.
- Favor clarity and inspectability over visual cleverness.

### 6.4 Persistence rules

- PostgreSQL is the primary operational store.
- Structured relational records are primary truth.
- Retrieval/vector support is secondary and must not replace structured state.
- Preserve migration discipline and data integrity.
- Keep interpreted artifacts separate from accepted operational state.

### 6.5 LangGraph rules

- Graphs are business workflow coordinators, not memory stores.
- Persist visible artifacts from graph outputs.
- Use explicit interrupt/resume handling for review gates.
- Reuse shared core flows across channels where practical.
- Do not allow low-confidence graph output to silently mutate accepted memory.

---

## 7. Verification Expectations

Verification is part of implementation, not follow-up cleanup.

You must:

- identify relevant `TEST:` anchors when they exist,
- propose missing `TEST:` anchors when risky work has no stable proof target,
- implement automated tests wherever reasonably possible,
- run the tests you add or modify,
- inspect and resolve failures where you can,
- and record verification status in working documents.

Do not mark meaningful work complete if critical proof is missing, unless it is explicitly classified as `ManualOnly` or `Deferred` with a real reason.

Use this verification priority order:

1. unit proof for rules and deterministic helpers
2. integration proof for persistence and collaboration behavior
3. API proof for application boundaries
4. graph/workflow proof for orchestration behavior
5. Playwright proof for browser-visible workflows
6. manual-only or deferred proof only where automation is not yet practical

### 7.1 Proof expectations by type of work

- **Domain and memory work** must prove state separation, provenance, persistence correctness, and audit behavior.
- **Connector work** must prove normalization, provenance retention, multi-account separation, and visible failure behavior.
- **Graph work** must prove routing, interrupt/resume behavior, review-gate enforcement, and no-auto-send boundaries.
- **UI work** must prove browser-visible review flows, provenance visibility, and distinction between pending and accepted state.
- **Voice and Telegram work** must prove they do not bypass the main review and safety model.

### 7.2 Evidence rule

A feature is not complete because tests were written. It is complete when relevant proof has been executed and recorded.

---

## 8. Work Package Operating Model

### 8.1 Always anchor your work

When implementing meaningful work, explicitly identify the relevant:

- `REQ:` anchors
- `ARCH:` anchors
- `PLAN:` anchors
- `TEST:` anchors

If one of these layers is missing for risky work, surface the gap.

### 8.2 Delivery sequence inside a session

The default sequence is:

1. review the relevant control documents,
2. review the active workstream plan/progress files if they exist,
3. identify the anchors in scope,
4. inspect the current code before editing,
5. implement a bounded slice,
6. run relevant verification,
7. update working documents,
8. report assumptions, blockers, and evidence clearly.

### 8.3 Prefer bounded vertical slices

Do not sprawl across many unrelated parts of the repo without need. Prefer small, coherent, testable slices that move one work package forward.

### 8.4 Surface blockers properly

If you hit a human dependency, finish all code-safe work first, then report:

- what is needed,
- why it is needed,
- what is already complete,
- and what remains blocked.

---

## 9. Working Document Rules

### 9.1 Working-document pair

Each major workstream should eventually have:

- `WorkstreamX_*_DESIGN_AND_IMPLEMENTATION_PLAN.md`
- `WorkstreamX_*_DESIGN_AND_IMPLEMENTATION_PROGRESS.md`

### 9.2 Plan-file role

Use the plan file to record:

- active scope,
- intended implementation approach,
- linked anchors,
- expected tests,
- file-level change areas,
- and human dependencies.

### 9.3 Progress-file role

Use the progress file to record:

- completed work,
- current state,
- verification results,
- blockers,
- assumptions,
- and next-session pickup guidance.

### 9.4 Keep them current

Do not let working documents drift behind the code. Update them during meaningful progress, not as an afterthought.

---

## 10. Assumption and Uncertainty Handling

### 10.1 Acceptable assumptions

You may make bounded implementation assumptions when:

- the control docs strongly imply the answer,
- the choice is low-risk and reversible,
- and it does not weaken security, provenance, reviewability, or architecture shape.

### 10.2 When you must surface uncertainty

You must surface uncertainty when it affects:

- schema semantics,
- connector/provider behavior,
- security/privacy posture,
- review-gate behavior,
- major UX behavior,
- model-routing policy,
- or release confidence.

### 10.3 Do not silently simplify load-bearing rules

If implementation becomes awkward, do not silently simplify:

- multi-account provenance,
- review states,
- accepted-vs-interpreted separation,
- no-auto-send boundaries,
- or cross-surface continuity expectations.

Surface the tradeoff instead.

---

## 11. Human Assistance Protocol

When human action is required, ask in a structured way.

Use this format:

- **Need:** what human action is required
- **Why:** why the agent cannot complete this alone
- **Already done:** what is already implemented or verified
- **Blocked remainder:** what remains blocked until the human action happens

Typical human-required categories include:

- OAuth app registration,
- provider credentials/secrets,
- Telegram bot provisioning,
- production voice infrastructure choices,
- approval of material architecture changes,
- and acceptance of manual/deferred verification.

---

## 12. Safety Guardrails

You must not:

- invent credentials, secrets, tokens, tenants, or provider configuration,
- silently widen permissions or scopes,
- bypass review gates for convenience,
- invent external integration behavior without documenting the assumption,
- silently collapse multiple accounts into one logical source,
- treat retrieved semantic context as accepted truth,
- or mark unverified work as complete.

You must prefer:

- explicitness,
- bounded changes,
- stable anchors,
- reproducible verification,
- and honest reporting of uncertainty.

---

## 13. Retrieval and Local Context Rule

If the repository contains a local retrieval/indexing layer under `9. Agent Tools/`, use it before broadly opening large document sets.

Preferred retrieval order:

1. exact anchor match
2. matching heading/section
3. bounded query-based fallback
4. full-document open only when the bounded result is insufficient

Treat generated retrieval maps as helpers, not authorities. The Markdown control documents remain the source of truth.

If freshness is uncertain, validate or regenerate the local retrieval/index before trusting it.

---

## 14. Module Instruction Rule

When a module-scoped instruction file exists for the files you are editing, you must follow both:

- this global instruction file, and
- the relevant module-scoped instruction file.

If they conflict:

1. requirements / architecture / build plan / verification win,
2. then the more specific module instruction wins over the global instruction,
3. then working documents and code follow.

---

## 15. Final Operating Standard

Act like a disciplined implementation partner, not an improvising co-architect.

That means:

- follow the control docs,
- preserve Glimmer’s local-first and review-first posture,
- keep provenance and multi-account meaning intact,
- make progress in bounded, testable slices,
- prove what you build,
- and surface drift or uncertainty early.

The goal is not to produce the most code quickly.
The goal is to deliver Glimmer in a way that remains aligned, explainable, and trustworthy as the system grows.
