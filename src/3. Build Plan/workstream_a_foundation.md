# Glimmer — Workstream A: Foundation

## Document Metadata

- **Document Title:** Glimmer — Workstream A: Foundation
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Build Strategy and Scope, Testing Strategy

---

## 1. Purpose

This document defines the implementation strategy for **Workstream A — Foundation**.

Its purpose is to establish the runtime, repository, persistence, and delivery-control foundations required before Glimmer’s higher-order assistant behavior can be built safely.

This workstream is not where Glimmer becomes clever. It is where Glimmer becomes buildable, testable, and governable.

**Stable plan anchor:** `PLAN:WorkstreamA.Foundation`

---

## 2. Workstream Objective

Workstream A exists to create the foundational implementation substrate for Glimmer, including:

- repository structure,
- backend and frontend application skeletons,
- local development/runtime setup,
- primary persistence baseline,
- shared configuration conventions,
- initial testing scaffolding,
- and the agent-operational support surfaces needed for controlled AI-assisted delivery.

At the end of this workstream, Glimmer should have a coherent implementation skeleton that future workstreams can safely extend.

**Stable plan anchor:** `PLAN:WorkstreamA.Objective`

---

## 3. Why This Workstream Comes First

The Glimmer build strategy explicitly prioritizes foundations before feature layering, domain before orchestration complexity, and web control surface before companion convenience.

That means Workstream A must establish:

- the repo/app structure the rest of the project will inherit,
- the persistence baseline that later domain work will depend on,
- the local-first runtime posture,
- and the initial testing/project tooling structure that prevents uncontrolled drift.

If this workstream is weak, later workstreams will either duplicate infrastructure decisions or encode assumptions that have to be unpicked later.

**Stable plan anchor:** `PLAN:WorkstreamA.Rationale`

---

## 4. Related Requirements Anchors

This workstream directly supports the following requirements:

- `REQ:ProductPurpose`
- `REQ:LocalFirstOperatingModel`
- `REQ:StateContinuity`
- `REQ:PrivacyAndLeastPrivilege`
- `REQ:SafeBehaviorDefaults`

These requirements are part of why the foundation must be local-first, review-friendly, and built around durable state rather than a disposable prototype shell.

**Stable plan anchor:** `PLAN:WorkstreamA.RequirementsAlignment`

---

## 5. Related Architecture Anchors

This workstream is primarily implementing the practical substrate implied by:

- `ARCH:SystemBoundaries`
- `ARCH:TechnologyBaseline`
- `ARCH:LocalFirstBoundary`
- `ARCH:ArchitectureControlSurface`
- `ARCH:PrimaryRelationalMemoryStore`
- `ARCH:VerificationLayerModel`
- `ARCH:SecurityBoundaryMap`

These anchors establish Glimmer as a local-first Python/FastAPI + React/Next.js + PostgreSQL + LangGraph system with explicit verification and security boundaries.

**Stable plan anchor:** `PLAN:WorkstreamA.ArchitectureAlignment`

---

## 6. Workstream Scope

### 6.1 In scope

This workstream includes:

- repository implementation structure,
- backend application skeleton,
- frontend application skeleton,
- local runtime conventions,
- PostgreSQL baseline wiring,
- base configuration and environment strategy,
- initial migration approach,
- initial test project structure,
- and the first agent-operational files under `.github/`, `8. Agent Skills/`, and `9. Agent Tools/`.

**Stable plan anchor:** `PLAN:WorkstreamA.InScope`

### 6.2 Out of scope

This workstream does **not** include:

- real Google/Microsoft account connectivity,
- real Telegram bot behavior,
- project/domain entities beyond what is necessary for baseline bootstrapping,
- production-grade triage/planner/drafting logic,
- full UI workflows,
- or complete voice interaction.

Those belong to later workstreams.

**Stable plan anchor:** `PLAN:WorkstreamA.OutOfScope`

---

## 7. Expected Repository Shape

The target repository shape at the end of this workstream should roughly support the following implementation surfaces:

```text
.github/
  copilot-instructions.md
  instructions/

8. Agent Skills/
9. Agent Tools/

1. Requirements/
2. Architecture/
3. Build Plan/
4. Verification/

apps/
  backend/
  web/

packages/ or shared/
  shared types / common contracts where appropriate

tests/
  unit/
  integration/
  api/
  playwright/
  contract/
  packs/

working documents at repo root
```

The exact folder names may be refined during implementation, but the structural separation between code, control documents, verification, and agent-operational surfaces should remain intact. This follows the framework’s recommended document hierarchy and the Glimmer document set.

**Stable plan anchor:** `PLAN:WorkstreamA.RepositoryShape`

---

## 8. Foundation Work Packages

## 8.1 Work Package A1 — Repository and runtime skeleton

**Objective:** Establish the base application skeleton for backend and frontend delivery.

### In scope
- create backend app skeleton using Python + FastAPI
- create frontend app skeleton using React / Next.js
- establish top-level folder conventions
- define baseline local run commands/scripts
- ensure the solution can boot in a minimal local mode

### Expected outputs
- backend application entrypoint
- frontend application entrypoint
- baseline README/run notes if appropriate
- basic health/startup behavior

### Related anchors
- `PLAN:WorkstreamA.Foundation`
- `ARCH:TechnologyBaseline`
- `ARCH:SystemBoundaries`

### Definition of done
- backend app starts cleanly
- frontend app starts cleanly
- repo structure is coherent enough for later workstreams
- smoke verification target is identified

**Stable plan anchor:** `PLAN:WorkstreamA.PackageA1.RepositoryAndRuntimeSkeleton`

---

## 8.2 Work Package A2 — Configuration and local-first environment baseline

**Objective:** Establish Glimmer’s local-first configuration posture.

### In scope
- local configuration model for backend and frontend
- environment file conventions
- secrets boundary strategy for local dev
- initial model/config feature flags where useful
- local-first defaults in app startup/config wiring

### Expected outputs
- configuration classes or config module structure
- example environment templates
- explicit separation between normal config and secret-bearing config
- initial policy for optional remote model routing

### Related anchors
- `ARCH:LocalFirstBoundary`
- `ARCH:SecretHandlingBoundary`
- `ARCH:RemoteModelBoundary`

### Definition of done
- local-first configuration baseline exists
- secrets are not expected in committed config
- app startup can resolve required local config safely

**Stable plan anchor:** `PLAN:WorkstreamA.PackageA2.ConfigurationBaseline`

---

## 8.3 Work Package A3 — PostgreSQL persistence baseline

**Objective:** Establish the primary relational persistence substrate.

### In scope
- database connectivity baseline
- ORM/data-access baseline decision as implemented code
- migration approach scaffold
- base persistence/session wiring
- initial persistence health check or readiness path

### Expected outputs
- persistence module or package
- DB connection wiring
- first migration scaffold or baseline schema setup approach
- local DB startup instructions or dev assumptions

### Related anchors
- `ARCH:PrimaryRelationalMemoryStore`
- `ARCH:RelationalFirstRationale`
- `ARCH:MemoryStorageStrategy`

### Definition of done
- backend can connect to Postgres in local development
- migration path is established
- later domain work can add entities without rethinking the persistence substrate

**Stable plan anchor:** `PLAN:WorkstreamA.PackageA3.PersistenceBaseline`

---

## 8.4 Work Package A4 — Backend application structure and service boundaries

**Objective:** Create the first clean backend structure aligned to Glimmer’s architecture.

### In scope
- app/module separation for API, orchestration, domain, infrastructure, and persistence boundaries
- initial dependency-injection wiring
- health/status endpoint(s)
- baseline error-handling and logging conventions
- placeholder orchestration/service interfaces where useful

### Expected outputs
- coherent backend package layout
- shared app bootstrap conventions
- initial service registration pattern
- initial structured logging/error middleware

### Related anchors
- `ARCH:SystemBoundaries`
- `ARCH:SecurityBoundaryMap`
- `ARCH:ConnectorLayerScope`
- `ARCH:OrchestrationRole`

### Definition of done
- backend structure reflects the intended architecture well enough to avoid early drift
- future workstreams can add domain, connectors, and graphs without major restructuring

**Stable plan anchor:** `PLAN:WorkstreamA.PackageA4.BackendStructure`

---

## 8.5 Work Package A5 — Frontend application structure and base shell

**Objective:** Create the first usable web shell for Glimmer.

### In scope
- base React / Next.js app structure
- top-level layout and routing shell
- placeholder navigation for primary surfaces
- styling baseline and component conventions
- initial local API wiring strategy

### Expected outputs
- root layout
- app navigation shell
- placeholder pages for Today / Portfolio / Project / Triage / Drafts
- frontend configuration baseline

### Related anchors
- `ARCH:UiSurfaceMap`
- `ARCH:TodayViewArchitecture`
- `ARCH:ProjectWorkspaceArchitecture`
- `ARCH:DraftWorkspaceArchitecture`

### Definition of done
- web shell exists and loads cleanly
- main surface placeholders are visible
- future UI work can proceed inside a stable app shell

**Stable plan anchor:** `PLAN:WorkstreamA.PackageA5.FrontendShell`

---

## 8.6 Work Package A6 — Baseline testing structure

**Objective:** Create the first real verification substrate rather than leaving testing for later.

### In scope
- create test folder/project structure aligned to the Glimmer testing strategy
- add smoke tests for backend startup and basic API health
- add initial frontend/browser test harness setup
- add integration test harness skeleton for persistence work
- define how tests are run locally

### Expected outputs
- initial `tests/` structure
- smoke tests
- Playwright harness baseline
- initial test runner commands/docs

### Related anchors
- `ARCH:TestingArchitecture`
- `ARCH:VerificationLayerModel`
- `ARCH:PlaywrightTestBoundary`

### Definition of done
- at least one backend smoke proof exists
- browser test harness exists
- test estate structure is ready for later workstreams

**Stable plan anchor:** `PLAN:WorkstreamA.PackageA6.TestingBaseline`

---

## 8.7 Work Package A7 — Agent-operational support surfaces

**Objective:** Establish the initial operational files that make AI-assisted delivery stable.

### In scope
- `.github/copilot-instructions.md`
- initial module-scoped instruction files
- `8. Agent Skills/README.md` and initial skills stubs or first real skills
- `9. Agent Tools/README.md`
- retrieval/indexing helper baseline
- freshness/integrity validation helper baseline

### Expected outputs
- first project-specific agent instructions
- first module-scoped rules
- agent tools scaffold
- repo-local retrieval convention baseline

### Related anchors
- `ARCH:ArchitectureControlSurface`
- `PLAN:AgentDeliveryZone`
- `PLAN:SharedDeliveryZone`

### Definition of done
- the repo contains enough instruction/tooling support that future agent sessions can navigate and work with lower drift
- local retrieval rule is reflected in the operational surfaces

**Stable plan anchor:** `PLAN:WorkstreamA.PackageA7.AgentOperationalSurfaces`

---

## 9. Sequencing Inside the Workstream

The recommended internal order for Workstream A is:

1. A1 — Repository and runtime skeleton
2. A2 — Configuration and local-first environment baseline
3. A3 — PostgreSQL persistence baseline
4. A4 — Backend structure and service boundaries
5. A5 — Frontend shell
6. A6 — Baseline testing structure
7. A7 — Agent-operational support surfaces

Some overlap is acceptable, but this order protects against premature UI polish and avoids building features before the app can boot, persist, and be verified.

**Stable plan anchor:** `PLAN:WorkstreamA.InternalSequence`

---

## 10. Human Dependencies

This workstream is mostly agent-executable, but a few areas may require human action or confirmation.

### Expected human inputs
- preferred repo/package naming if not already settled
- local Postgres instance or dev DB availability
- any environment-specific local runtime constraints
- confirmation of the chosen frontend scaffolding path where multiple equivalent options exist
- later external secrets or provider registration steps, though those should not block most of this workstream

The work should be structured so the coding agent can make substantial progress before any such human intervention becomes blocking. This is consistent with the strategy document’s human-intervention model.

**Stable plan anchor:** `PLAN:WorkstreamA.HumanDependencies`

---

## 11. Verification Expectations

Workstream A is complete only when the foundation is not just created, but proven to be usable.

### Verification layers expected
- smoke verification
- API/startup verification
- persistence-baseline verification
- initial Playwright/browser harness verification

### Minimum proof expectations
- backend boots and exposes at least a basic health/status path
- frontend boots and renders the base shell
- Postgres connectivity is proven in local development or controlled integration environment
- baseline automated test commands execute successfully

This follows the Glimmer testing strategy’s requirement for automated proof, layered verification, and evidence-backed completion.

**Stable plan anchor:** `PLAN:WorkstreamA.VerificationExpectations`

---

## 12. Suggested Future Working Documents for This Workstream

This workstream should eventually be paired with:

- `WorkstreamA_Foundation_DESIGN_AND_IMPLEMENTATION_PLAN.md`
- `WorkstreamA_Foundation_DESIGN_AND_IMPLEMENTATION_PROGRESS.md`

Those files will hold the current implementation state, session handoff, blockers, and verification evidence once coding starts. This follows the framework’s working-document convention.

**Stable plan anchor:** `PLAN:WorkstreamA.WorkingDocumentPair`

---

## 13. Definition of Done

Workstream A should be considered complete when all of the following are true:

1. the repository contains a coherent backend and frontend implementation skeleton,
2. local-first configuration and secret boundaries are established,
3. PostgreSQL baseline persistence is operational,
4. backend structure reflects the intended architectural layers closely enough for later workstreams,
5. the frontend shell exists with primary-surface placeholders,
6. the initial automated testing substrate is working,
7. the first project-specific agent-operational support files exist,
8. and the relevant verification evidence has been executed and recorded.

If these are not true, the project is still in pre-foundation shaping rather than true implementation readiness.

**Stable plan anchor:** `PLAN:WorkstreamA.DefinitionOfDone`

---

## 14. Final Note

Workstream A is not glamorous, but it is load-bearing.

If Glimmer is going to become a durable, trustworthy, multi-account chief-of-staff system, it needs a foundation that protects architecture, memory, provenance, security, and verification from the very start.

This workstream should therefore be implemented with discipline rather than speed-chasing. A boringly solid foundation is exactly what Glimmer needs here.

**Stable plan anchor:** `PLAN:WorkstreamA.Conclusion`
