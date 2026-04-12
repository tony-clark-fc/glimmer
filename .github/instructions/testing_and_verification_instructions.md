---
applyTo: "tests/**/*,4. Verification/**/*.md,**/*_DESIGN_AND_IMPLEMENTATION_PROGRESS.md,**/*_DESIGN_AND_IMPLEMENTATION_PLAN.md"
---

# Glimmer — Testing and Verification Module Instructions

## Purpose

This instruction file defines the module-scoped rules for Glimmer testing, verification-pack authoring, evidence capture, and workstream verification reporting.

It supplements the global `.github/copilot-instructions.md` file and applies specifically to:

- automated test code,
- verification documents under `4. Verification/`,
- test helpers and fixtures,
- regression-pack definitions,
- and workstream plan/progress files where verification status is recorded.

These rules are stricter than generic testing guidance because Glimmer’s verification model is part of the product control system, not a cleanup step after code is written.

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
8. Code and tests

Do not let existing weak tests, missing automation, or convenience shortcuts silently redefine what Glimmer considers “done.”

---

## 2. What This Module Must Preserve

Testing and verification work must preserve these core Glimmer properties:

- **verification as part of implementation**,
- **automation-first proof**,
- **behavior over shallow coverage theater**,
- **traceability from `REQ:` to `ARCH:` to `PLAN:` to `TEST:`**,
- **explicit handling of `ManualOnly` and `Deferred` cases**,
- **evidence-backed completion**,
- and **cross-workstream regression discipline**.

These are load-bearing delivery rules, not QA preferences.

---

## 3. Verification Architecture Rules

### 3.1 Verification is a control surface

The verification area under `4. Verification/` is part of the canonical project control surface.

It is not just a documentation add-on for tests.

### 3.2 `TEST:` anchors are durable references

When defining or updating meaningful scenarios, use stable `TEST:` anchors.

Do not rely on vague scenario names that drift across workstreams and progress files.

### 3.3 Verification packs organize proof, they do not replace tests

Verification packs should define:

- what scenarios matter,
- how they are grouped,
- what level of automation exists,
- what environment assumptions apply,
- and what release confidence they support.

The packs are not substitutes for the actual automated test estate.

### 3.4 Cross-workstream packs matter

Smoke, data-integrity, connector, graph, browser, and release packs must be treated as cross-cutting proof surfaces, not as isolated workstream afterthoughts.

---

## 4. Automation-First Rules

### 4.1 Default automation order

Prefer this order when deciding how to prove behavior:

1. unit automation
2. integration automation
3. API automation
4. graph/workflow automation
5. Playwright automation
6. manual-only or deferred proof only where automation is not yet practical

### 4.2 Manual checks must be explicit

If a scenario cannot yet be automated, classify it explicitly as:

- `ManualOnly`, or
- `Deferred`

with a real reason.

### 4.3 No false-green from test existence alone

A scenario is not considered proven because a test file exists.

The proof must be executed, and the execution status must be recorded.

---

## 5. Required Test-Layer Rules for Glimmer

### 5.1 Unit tests

Use unit tests for deterministic behavior such as:

- domain rules,
- prioritization helpers,
- extraction helpers,
- tone and persona selection helpers,
- normalization helpers,
- state transition guards,
- and ranking or threshold logic.

### 5.2 Integration tests

Use integration tests for:

- persistence behavior,
- migrations,
- repository and service collaboration,
- summary refresh,
- connector normalization,
- and data-integrity rules.

### 5.3 API tests

Use API tests for:

- FastAPI route behavior,
- validation,
- error handling,
- authorization/local access rules,
- review actions,
- and stable application contracts.

### 5.4 Graph workflow tests

Use graph/workflow tests for:

- intake routing,
- triage behavior,
- planner behavior,
- drafting paths,
- interrupt/resume behavior,
- Telegram routing,
- and voice-session routing/continuity.

### 5.5 Browser workflow tests

Use Playwright for:

- Today view workflows,
- triage review flows,
- project navigation,
- draft workspace flows,
- review queue flows,
- and other browser-visible operator journeys.

### 5.6 Manual/deferred checks

Reserve manual or deferred checks for genuinely environment-bound scenarios such as:

- certain audio-quality checks,
- one-off provider environment validation,
- or narrow visual confirmation not yet worth automating.

---

## 6. Glimmer-Specific Proof Rules

### 6.1 Domain and memory proof

Changes touching domain or memory must prove:

- accepted-vs-interpreted separation,
- provenance retention,
- relationship correctness,
- summary refresh lineage,
- and audit behavior where applicable.

### 6.2 Connector proof

Changes touching connectors must prove:

- normalization correctness,
- multi-account separation,
- provenance preservation,
- manual-import labeling,
- and visible failure/sync-state behavior.

### 6.3 Orchestration proof

Changes touching graphs or workflow logic must prove:

- correct routing,
- interrupt/resume behavior,
- review-gate enforcement,
- explainable outputs where relevant,
- and no-auto-send boundary preservation.

### 6.4 UI proof

Changes touching UI must prove:

- review visibility,
- provenance visibility,
- accepted-vs-pending distinction,
- draft workspace usability,
- and browser-visible workflow correctness.

### 6.5 Voice and Telegram proof

Changes touching voice or Telegram must prove:

- they reuse the core review/safety model,
- they preserve continuity appropriately,
- and they do not create side-channel behavior that bypasses the main workspace and approval boundaries.

---

## 7. Verification Document Rules

### 7.1 `TEST_CATALOG.md` is canonical for scenarios

The test catalog should define the stable scenario vocabulary.

It should not be a random backlog of ideas.

### 7.2 Verification packs should map to workstreams and cross-cutting risk

At minimum, Glimmer’s verification set should support:

- smoke,
- workstream-level packs,
- release,
- and data-integrity.

### 7.3 Pack entries should be concrete

Each meaningful pack entry should make clear:

- scenario name,
- stable `TEST:` anchor,
- target test layer,
- automation status,
- and any environment prerequisites.

### 7.4 Keep pack definitions aligned to current architecture and build plan

Do not leave verification packs describing old workstream boundaries or obsolete architecture assumptions.

---

## 8. Evidence and Completion Rules

### 8.1 Evidence must be recorded in working documents

When meaningful proof is executed, update the relevant progress file with at least:

- what was tested,
- what passed,
- what failed,
- what remains deferred/manual,
- and what that means for confidence.

### 8.2 Work is not complete without proof status

A work package or workstream should not be recorded as complete unless:

- implementation is present,
- relevant proof was executed or explicitly classified,
- and the progress file reflects the current truth.

### 8.3 Be honest about gaps

Do not disguise unrun tests, flaky tests, missing browser coverage, or deferred environment checks as full verification.

### 8.4 Release confidence is a judgment informed by packs

Release or phase-exit confidence should be based on:

- pack status,
- unresolved failures,
- deferred/manual items,
- and the seriousness of the remaining gaps.

---

## 9. Test Data, Fixture, and Environment Rules

### 9.1 Prefer reproducible fixture setup

Tests should use clear, reproducible fixtures and setup patterns.

Do not rely on undocumented local magic, hidden seed data, or fragile cross-test state.

### 9.2 Keep environment assumptions explicit

If a test pack depends on:

- a local database,
- provider fakes,
- a Telegram bot test setup,
- Playwright browser dependencies,
- or audio infrastructure assumptions,

state that explicitly in the verification pack and/or test helper docs.

### 9.3 Isolate failure diagnosis

Test failures should be diagnosable.

Prefer fixtures and assertions that make it obvious whether the problem is:

- routing,
- persistence,
- provenance,
- review-state behavior,
- browser interaction,
- or environment configuration.

---

## 10. Working-Document Verification Rules

### 10.1 Plan files should declare intended proof

When a workstream plan file is updated, include the intended verification approach for the current slice.

### 10.2 Progress files should record executed proof

Progress files should distinguish clearly between:

- planned tests,
- implemented tests,
- executed tests,
- passing evidence,
- failing evidence,
- and deferred/manual checks.

### 10.3 Do not leave verification implicit

If you changed something meaningful and did not run proof, say so explicitly.

---

## 11. Preferred Verification Session Workflow

When working in this module area, the default session sequence should be:

1. identify relevant `REQ:` anchors,
2. identify relevant `ARCH:` anchors,
3. identify relevant `PLAN:` anchors,
4. identify or propose relevant `TEST:` anchors,
5. implement or update the proof,
6. execute the proof,
7. record the evidence,
8. report remaining gaps honestly.

---

## 12. What to Do When the Docs Are Incomplete

If testing work requires a verification rule that does not yet have a stable anchor:

1. do not invent the verification model silently,
2. propose the missing anchor,
3. make the smallest safe improvement that still increases proof quality,
4. and record the gap in the relevant working document.

Typical examples include:

- a missing `TEST:` anchor for a high-risk workflow,
- a missing regression-pack category,
- a missing release-gate rule,
- or a missing policy for `ManualOnly` vs `Deferred` classification.

---

## 13. Anti-Patterns to Avoid in This Module

Do not:

- confuse line coverage with meaningful proof,
- write shallow tests that only assert “not null” for important behavior,
- leave graph flows untested because unit tests exist,
- rely on manual clicking for core workspace regression,
- hide environment assumptions,
- mark unrun tests as effectively passed,
- or treat verification packs as static paperwork with no relationship to executed proof.

---

## 14. Final Rule

When in doubt, make verification more:

- scenario-based,
- automated,
- explicit,
- evidence-backed,
- and honest about remaining gaps.

Do not optimize for reassuring appearances.
Optimize for proof that Glimmer’s behavior is actually trustworthy as the system evolves.

