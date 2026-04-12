# Glimmer — Verification Pack: Smoke

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Smoke
- **Document Type:** Canonical Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Test Catalog, Requirements, Architecture, Build Plan, Testing Strategy

---

## 1. Purpose

This document defines the **smoke verification pack** for **Glimmer**.

Its purpose is to provide the smallest meaningful executable proof set that answers a simple question:

**Is the system basically alive enough to continue?**

This pack is intended to fail fast when Glimmer’s runtime, workspace shell, or essential baseline wiring breaks.

It is not a substitute for deeper workstream, browser, graph, or data-integrity proof.

**Stable verification anchor:** `TESTPACK:Smoke.ControlSurface`

---

## 2. Role of the Smoke Pack

The smoke pack exists to provide a repeatable, high-signal baseline for:

- local development startup confidence,
- post-refactor sanity checking,
- early CI execution,
- and pre-release “is the floor still intact?” validation.

The smoke pack should remain:

- small,
- fast,
- highly reliable,
- and focused on core boot and reachability rather than feature depth.

If the smoke pack fails, deeper packs should usually not be trusted until the baseline issue is understood.

**Stable verification anchor:** `TESTPACK:Smoke.Role`

---

## 3. Relationship to the Test Catalog

This smoke pack is built from the canonical `TEST:` anchors defined in `TEST_CATALOG.md`.

It does not create new proof vocabulary unnecessarily.

The initial smoke pack should draw primarily from the foundation/startup scenario group and use those scenarios as the stable source of truth for what the smoke pack is proving. fileciteturn26file24

**Stable verification anchor:** `TESTPACK:Smoke.RelationshipToCatalog`

---

## 4. Why This Pack Exists Early

The Agentic Delivery Framework and the Testing Strategy Companion both treat testing as part of implementation rather than cleanup, and the Glimmer build plan explicitly places verification inside each workstream and calls for a smoke pack as part of the canonical verification set. fileciteturn26file0turn26file1turn26file2turn26file14

Workstream A also makes it clear that the earliest meaningful proof targets are backend startup, frontend startup, database connectivity, and base workspace reachability. fileciteturn26file8

That makes the smoke pack the correct first verification pack to define after the test catalog.

**Stable verification anchor:** `TESTPACK:Smoke.Rationale`

---

## 5. Smoke Pack Scope

### 5.1 In scope

The smoke pack should cover only the minimum baseline proof required to establish that Glimmer is operationally reachable at a foundational level.

This includes:

- backend application startup,
- frontend application startup,
- primary database connectivity,
- and basic workspace route reachability.

### 5.2 Out of scope

The smoke pack does **not** attempt to prove:

- domain correctness,
- connector normalization,
- graph workflow behavior,
- triage quality,
- draft quality,
- persona selection behavior,
- Telegram or voice behavior,
- or full browser workflow correctness.

Those belong in later workstream packs, data-integrity packs, browser packs, graph packs, and the release pack.

**Stable verification anchor:** `TESTPACK:Smoke.Scope`

---

## 6. Source `TEST:` Anchors Included in This Pack

The initial smoke pack includes the following canonical `TEST:` anchors from the Test Catalog. fileciteturn26file24

### 6.1 `TEST:Smoke.BackendStarts`
- **Scenario name:** Backend starts and exposes basic health/status behavior
- **Primary layers:** `integration`, `api`
- **Intent in this pack:** Prove the backend can boot in a minimal local configuration and expose a stable status surface.

### 6.2 `TEST:Smoke.FrontendStarts`
- **Scenario name:** Frontend workspace shell starts and renders
- **Primary layers:** `integration`, `browser`
- **Intent in this pack:** Prove the web shell starts cleanly and presents the base workspace frame.

### 6.3 `TEST:Smoke.DatabaseConnectivity`
- **Scenario name:** Primary relational store is reachable through the application
- **Primary layers:** `integration`
- **Intent in this pack:** Prove Glimmer can connect to the primary PostgreSQL store under the intended local-first baseline.

### 6.4 `TEST:Smoke.WorkspaceNavigationBasic`
- **Scenario name:** Core workspace routes are reachable
- **Primary layers:** `browser`
- **Intent in this pack:** Prove the base route structure is reachable at a minimal level.

**Stable verification anchor:** `TESTPACK:Smoke.IncludedTests`

---

## 7. Smoke Pack Entry Table

| TEST Anchor | Scenario | Layer | Automation Status | Pack Priority | Notes |
|---|---|---|---|---|---|
| `TEST:Smoke.BackendStarts` | Backend starts and exposes basic health/status behavior | `integration`, `api` | Planned | Critical | Must fail fast on backend boot/config breakage |
| `TEST:Smoke.FrontendStarts` | Frontend workspace shell starts and renders | `integration`, `browser` | Planned | Critical | Must fail fast on app shell/runtime breakage |
| `TEST:Smoke.DatabaseConnectivity` | Primary relational store is reachable through the application | `integration` | Planned | Critical | Must fail fast on DB/config/migration-baseline issues |
| `TEST:Smoke.WorkspaceNavigationBasic` | Core workspace routes are reachable | `browser` | Planned | High | Should stay small and stable, not deep-featured |

**Stable verification anchor:** `TESTPACK:Smoke.EntryTable`

---

## 8. Expected Automation Shape

The smoke pack should be implemented primarily through a small set of stable automated checks.

### 8.1 Backend startup proof

This proof should verify that:

- the backend process or test host can start,
- required baseline configuration can be resolved,
- a minimal health or status route responds successfully,
- and the app does not fail immediately on import/startup.

### 8.2 Database baseline proof

This proof should verify that:

- the backend can establish a database connection,
- baseline schema access works,
- and the application does not fail at first DB touch.

This should remain shallow in the smoke pack. Schema semantics and migration correctness belong in deeper packs.

### 8.3 Frontend startup proof

This proof should verify that:

- the frontend can start in a minimal local or test mode,
- the base app shell renders,
- and a recognizable workspace frame is present.

### 8.4 Basic browser route proof

This proof should verify that:

- the root workspace or base route is reachable,
- at least one or more key routes can be opened,
- and the operator is not immediately blocked by a broken shell.

The smoke pack browser checks should remain intentionally shallow. They are not a replacement for Workstream E browser journeys.

**Stable verification anchor:** `TESTPACK:Smoke.AutomationShape`

---

## 9. Environment Assumptions

The smoke pack should declare and keep stable the smallest realistic environment assumptions needed for execution.

### 9.1 Required assumptions

Expected baseline assumptions include:

- local backend runtime dependencies are available,
- local frontend runtime dependencies are available,
- a reachable PostgreSQL instance or equivalent test DB setup exists,
- minimal environment/config values are present,
- and browser automation dependencies for Playwright are installed where browser smoke is executed.

### 9.2 Avoid hidden environment magic

The smoke pack should not rely on undocumented setup, operator memory, or ad hoc manual steps that are not recorded in the verification surface.

### 9.3 Provider independence at smoke level

The smoke pack should not depend on live Google, Microsoft, Telegram, or voice infrastructure.

Those are out of scope for smoke and belong to deeper packs or explicit manual/deferred checks where appropriate.

**Stable verification anchor:** `TESTPACK:Smoke.EnvironmentAssumptions`

---

## 10. Execution Guidance

### 10.1 When to run this pack

The smoke pack should normally be run:

- after foundational environment or startup changes,
- after dependency or configuration changes,
- after refactors touching app boot or routing,
- before trusting deeper verification results,
- and as part of pre-release baseline sanity checking.

### 10.2 Execution posture

This pack should be:

- quick to run,
- quick to diagnose,
- and stable enough to become part of a repeated regression habit.

### 10.3 Failure handling

If the smoke pack fails, treat that as a baseline stability issue.

Do not present deeper passing tests as strong confidence until the baseline smoke failure is understood.

**Stable verification anchor:** `TESTPACK:Smoke.ExecutionGuidance`

---

## 11. Evidence Expectations

When the smoke pack is executed, evidence reporting should capture at minimum:

- date/time of execution,
- environment posture used,
- which smoke entries were executed,
- which passed,
- which failed,
- and whether any entries were explicitly `ManualOnly` or `Deferred`.

This should be summarized in the relevant workstream progress file or release/status summary when meaningful, following the framework and verification instruction rules. fileciteturn26file0turn26file22

**Stable verification anchor:** `TESTPACK:Smoke.EvidenceExpectations`

---

## 12. Exit Condition for This Pack

The smoke pack should be considered operationally established when:

1. all included `TEST:` anchors are mapped into executable proof paths,
2. backend startup proof exists,
3. frontend startup proof exists,
4. database connectivity proof exists,
5. basic browser route proof exists,
6. environment assumptions are explicit,
7. and the pack can be run repeatably without undocumented setup.

At that point, Glimmer has a real minimum-baseline proof surface.

**Stable verification anchor:** `TESTPACK:Smoke.DefinitionOfOperationalReady`

---

## 13. Relationship to Later Packs

The smoke pack is intentionally narrow.

Later verification packs should build on it rather than overload it.

In particular:

- Workstream A pack should deepen foundation verification,
- Workstream B pack should cover domain and memory integrity,
- Workstream C pack should cover connectors and provenance,
- Workstream D pack should cover triage/planner workflows,
- Workstream E pack should cover browser-visible workspace behavior,
- Workstream F pack should cover voice and companion behavior,
- the data-integrity pack should protect the memory spine,
- and the release pack should compose representative high-value proof from across the system.

This matches the document set and Workstream G’s verification-estate design. fileciteturn26file2turn26file14

**Stable verification anchor:** `TESTPACK:Smoke.RelationshipToLaterPacks`

---

## 14. Final Note

The smoke pack is meant to be boring in the best possible way.

It should not try to impress anyone. It should tell the truth quickly:

- does Glimmer start,
- does the shell render,
- does the database connect,
- and are the base routes alive?

That is enough for this pack.

**Stable verification anchor:** `TESTPACK:Smoke.Conclusion`
