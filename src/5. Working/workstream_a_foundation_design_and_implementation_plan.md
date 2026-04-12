# Glimmer — Workstream A Foundation Design and Implementation Plan

## Document Metadata

- **Document Title:** Glimmer — Workstream A Foundation Design and Implementation Plan
- **Document Type:** Working Implementation Plan
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** A — Foundation
- **Primary Companion Documents:** Requirements, Architecture, Build Plan, Verification, Governance and Process, Global Copilot Instructions, Module Instructions

---

## 1. Purpose

This document is the active working implementation plan for **Workstream A — Foundation**.

Its purpose is to translate the canonical Workstream A build-plan document into an execution-ready plan that a coding agent can use during actual implementation sessions.

This file should stay practical. It is not the source of architecture truth. It is the working plan for how Foundation will be implemented, verified, and advanced session by session.

**Stable working anchor:** `WORKA:Plan.ControlSurface`

---

## 2. Workstream Objective

The objective of Workstream A is to establish the minimum coherent implementation substrate required for all later Glimmer workstreams.

At the end of Workstream A, the repository should have:

- a real backend application shell,
- a real frontend workspace shell,
- a working primary database baseline,
- local-first configuration conventions,
- a clean repository structure aligned to the document set,
- initial automated verification scaffolding,
- and the operational support surfaces required for disciplined AI-assisted delivery.

This workstream is not where Glimmer becomes smart. It is where Glimmer becomes buildable.

**Stable working anchor:** `WORKA:Plan.Objective`

---

## 3. Control Anchors in Scope

The following anchor families are the primary control references for this workstream.

### 3.1 Requirements anchors

- `REQ:ProductPurpose`
- `REQ:LocalFirstOperatingModel`
- `REQ:PrivacyAndLeastPrivilege`
- `REQ:SafeBehaviorDefaults`

### 3.2 Architecture anchors

- `ARCH:SystemIntent`
- `ARCH:SystemBoundaries`
- `ARCH:TechnologyBaseline`
- `ARCH:LocalFirstBoundary`
- `ARCH:DeploymentPosture`
- `ARCH:MemoryStorageStrategy`
- `ARCH:TestingArchitecture`
- `ARCH:VerificationLayerModel`
- `ARCH:UiSurfaceMap`

### 3.3 Build-plan anchors

- `PLAN:WorkstreamA.Foundation`
- `PLAN:WorkstreamA.Objective`
- `PLAN:WorkstreamA.InternalSequence`
- `PLAN:WorkstreamA.VerificationExpectations`
- `PLAN:WorkstreamA.DefinitionOfDone`

### 3.4 Verification anchors

- `TEST:Smoke.BackendStarts`
- `TEST:Smoke.FrontendStarts`
- `TEST:Smoke.DatabaseConnectivity`
- `TEST:Smoke.WorkspaceNavigationBasic`
- `TEST:Foundation.Config.LocalFirstDefaultsResolve`
- `TEST:Foundation.Persistence.MigrationBaselineExists`
- `TEST:Foundation.Backend.StructureRespectsBoundaryShape`
- `TEST:Foundation.Frontend.WorkspaceShellExists`
- `TEST:Foundation.Testing.ScaffoldVisible`
- `TEST:Foundation.AgentSupport.CoreSurfacesPresent`

**Stable working anchor:** `WORKA:Plan.ControlAnchors`

---

## 4. Execution Principles for This Workstream

### 4.1 Build the substrate, not placeholder cleverness

The purpose of this workstream is to establish durable structure. Avoid decorative scaffolding that looks advanced but makes later work harder.

### 4.2 Favor clear boundaries early

Even in the first implementation slices, keep visible separation between:

- backend API/application code,
- orchestration entrypoints,
- domain/persistence code,
- frontend workspace shell,
- tests,
- and operational support surfaces.

### 4.3 Keep the local-first stance real from day one

Do not start with a remote-first or secret-heavy shortcut that later has to be undone to satisfy Glimmer’s local-first posture.

### 4.4 Treat verification as part of bring-up

Every meaningful foundational slice should include its corresponding proof path. Do not defer all verification until the end of the workstream.

### 4.5 Prefer one coherent vertical substrate slice at a time

This workstream should advance through bounded slices that leave the repo in a cleaner, more usable state after each session.

**Stable working anchor:** `WORKA:Plan.ExecutionPrinciples`

---

## 5. Repository Shape Target for Workstream A

By the end of this workstream, the repository should visibly support the following structure or its directly equivalent concrete form:

- `.github/`
- `.github/instructions/`
- `1. Requirements/`
- `2. Architecture/`
- `3. Build Plan/`
- `4. Verification/`
- `8. Agent Skills/`
- `9. Agent Tools/`
- backend application area
- frontend application area
- tests area
- workstream working-document area

This workstream does not need every future module implemented, but it must establish the skeleton they will grow inside.

**Stable working anchor:** `WORKA:Plan.RepoShapeTarget`

---

## 6. Work Packages to Execute

## 6.1 WA1 — Repository and directory baseline

### Objective
Create or align the repository structure so the control documents, support surfaces, application code, and tests have clear long-term homes.

### Expected touch points
- repo root structure
- application folders
- test folders
- `.github/` and `.github/instructions/`
- `8. Agent Skills/`
- `9. Agent Tools/`

### Verification expectation
- structural inspection
- `TEST:Foundation.AgentSupport.CoreSurfacesPresent`
- `TEST:Foundation.Backend.StructureRespectsBoundaryShape` where applicable

### Notes
This is about durable shape, not busywork. Avoid premature complexity.

**Stable working anchor:** `WORKA:Plan.PackageWA1`

---

## 6.2 WA2 — Backend application shell

### Objective
Create the initial FastAPI application shell with a stable startup path, health/status route, and room for later bounded modules.

### Expected touch points
- backend app entrypoint
- health/status route
- backend settings/config bootstrap
- initial app wiring

### Verification expectation
- `TEST:Smoke.BackendStarts`
- `TEST:Foundation.Config.LocalFirstDefaultsResolve`
- `TEST:Foundation.Backend.StructureRespectsBoundaryShape`

### Notes
Keep routes thin and avoid prematurely embedding business logic.

**Stable working anchor:** `WORKA:Plan.PackageWA2`

---

## 6.3 WA3 — Persistence baseline

### Objective
Establish PostgreSQL connectivity and the first durable migration/schema baseline so later domain work has a stable place to land.

### Expected touch points
- database connection/config
- migration tooling/configuration
- initial baseline schema/migration
- persistence bootstrap

### Verification expectation
- `TEST:Smoke.DatabaseConnectivity`
- `TEST:Foundation.Persistence.MigrationBaselineExists`

### Notes
The goal is not rich domain schema yet. The goal is a clean, trusted persistence baseline.

**Stable working anchor:** `WORKA:Plan.PackageWA3`

---

## 6.4 WA4 — Frontend workspace shell

### Objective
Create the initial React/Next.js workspace shell and route structure that will later hold Today, Portfolio, Project, Triage, Drafts, Review, and Voice surfaces.

### Expected touch points
- frontend app bootstrap
- root layout
- initial navigation or route shell
- placeholder workspace pages/routes

### Verification expectation
- `TEST:Smoke.FrontendStarts`
- `TEST:Smoke.WorkspaceNavigationBasic`
- `TEST:Foundation.Frontend.WorkspaceShellExists`

### Notes
Do not build a generic chatbot shell. Start with a workspace-first structure.

**Stable working anchor:** `WORKA:Plan.PackageWA4`

---

## 6.5 WA5 — Local configuration and developer baseline

### Objective
Make the local development posture explicit and repeatable, including environment-variable conventions and failure behavior when required config is missing.

### Expected touch points
- local env templates
- backend config loading
- frontend config conventions
- developer setup documentation where needed

### Verification expectation
- `TEST:Foundation.Config.LocalFirstDefaultsResolve`
- smoke checks as affected

### Notes
Configuration failure should be legible. Avoid silent fallback to mysterious defaults.

**Stable working anchor:** `WORKA:Plan.PackageWA5`

---

## 6.6 WA6 — Initial automated test scaffolding

### Objective
Create the first real test harnesses and conventions so later workstreams can extend proof rather than inventing it from scratch.

### Expected touch points
- backend test setup
- integration test setup
- browser/Playwright setup
- basic test execution commands or scripts

### Verification expectation
- `TEST:Foundation.Testing.ScaffoldVisible`
- smoke checks as affected

### Notes
The goal is not deep coverage yet. The goal is that real proof can start immediately in later workstreams.

**Stable working anchor:** `WORKA:Plan.PackageWA6`

---

## 6.7 WA7 — Operational support readiness

### Objective
Ensure the repo contains the minimum operational support surfaces required for agentic delivery to function cleanly during actual build execution.

### Expected touch points
- `.github/copilot-instructions.md`
- module instruction files
- `8. Agent Skills/README.md`
- `9. Agent Tools/README.md`
- verification directory baseline

### Verification expectation
- `TEST:Foundation.AgentSupport.CoreSurfacesPresent`

### Notes
These surfaces are support layers, not architecture truth. But they matter for implementation quality.

**Stable working anchor:** `WORKA:Plan.PackageWA7`

---

## 7. Recommended Execution Order

The recommended execution order inside this working plan is:

1. WA1 — Repository and directory baseline
2. WA2 — Backend application shell
3. WA3 — Persistence baseline
4. WA4 — Frontend workspace shell
5. WA5 — Local configuration and developer baseline
6. WA6 — Initial automated test scaffolding
7. WA7 — Operational support readiness

This sequence keeps the foundational substrate coherent while still allowing fast early proof.

**Stable working anchor:** `WORKA:Plan.ExecutionOrder`

---

## 8. Expected Files and Layers Likely to Change

The initial Workstream A implementation is likely to touch files or file groups such as:

- backend app bootstrap files
- backend config/settings files
- backend health/status routes
- persistence bootstrap and migration config
- frontend app bootstrap/layout files
- frontend base route files
- Playwright/test config files
- repo-local env templates
- test harness setup files
- working-document files for Workstream A

This list should be refined as implementation starts.

**Stable working anchor:** `WORKA:Plan.LikelyTouchPoints`

---

## 9. Verification Plan for Workstream A

### 9.1 Minimum required proof

At minimum, Workstream A implementation should produce executable proof for:

- backend boot
- frontend boot
- database connectivity
- base workspace route reachability
- local config resolution
- migration baseline existence
- visible testing scaffold
- visible operational support surfaces

### 9.2 Primary verification surfaces

The main verification references for this workstream are:

- `verification-pack-smoke.md`
- `verification-pack-workstream-a.md`

### 9.3 Evidence expectation

Meaningful implementation slices in this workstream should update the Workstream A progress file with:

- what was implemented
- what proof was executed
- what passed
- what failed
- what remains blocked or deferred

**Stable working anchor:** `WORKA:Plan.VerificationPlan`

---

## 10. Human Dependencies and Likely Decisions

This workstream is mostly agent-executable, but a few human decisions may still be needed.

Likely human-dependent areas include:

- confirmation of concrete repo layout choices if multiple good options exist
- confirmation of local environment defaults if dev-machine assumptions differ
- installation or provision of any local dependencies not already present

The coding agent should complete all code-safe and structure-safe work before surfacing human dependencies as blockers.

**Stable working anchor:** `WORKA:Plan.HumanDependencies`

---

## 11. Known Risks in This Workstream

### 11.1 Over-building too early

There is a risk of turning Foundation into premature architecture implementation instead of substrate establishment.

### 11.2 Generic chatbot drift in the UI shell

There is a risk of building a generic chat-first frontend because it is faster initially than a workspace-first shell.

### 11.3 Weak persistence baseline

There is a risk of keeping the DB layer too vague, which makes Workstream B harder later.

### 11.4 Verification procrastination

There is a risk of setting up app shells without a real executable proof path.

### 11.5 Support-surface drift

There is a risk of treating instructions, skills, and tools as side work rather than as enabling substrate for later agentic implementation.

**Stable working anchor:** `WORKA:Plan.Risks`

---

## 12. Immediate Next Session Recommendations

When actual coding starts, the first sensible execution slice is:

1. confirm concrete repo layout,
2. stand up the backend shell,
3. add the health/status path,
4. wire local config loading,
5. and execute the first backend startup proof.

That gives the project a real bootable foundation quickly and creates a clean base for persistence and frontend work.

**Stable working anchor:** `WORKA:Plan.ImmediateNextSlice`

---

## 13. Definition of Ready for Workstream A Completion

Workstream A should only be considered ready for completion when all of the following are materially true:

- repo structure is coherent
- backend shell is real
- frontend shell is real
- PostgreSQL baseline is wired
- local-first config conventions are real
- test harness scaffolding is real
- operational support surfaces are present
- and the foundational proof paths have been executed and recorded

If these are not true, Workstream A is not done, even if the repo looks busy.

**Stable working anchor:** `WORKA:Plan.DefinitionOfReadyForCompletion`

---

## 14. Final Note

This workstream is where Glimmer stops being a good idea on paper and becomes a real thing you can stand up, run, test, and extend.

That is the standard.

The goal is not to be fancy here. The goal is to be solid enough that the rest of the system has somewhere trustworthy to land.

**Stable working anchor:** `WORKA:Plan.Conclusion`

