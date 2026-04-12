# Glimmer — Verification Pack: Workstream A Foundation

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Workstream A Foundation
- **Document Type:** Canonical Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Test Catalog, Requirements, Architecture, Build Plan, Testing Strategy, Workstream A Foundation, Smoke Pack

---

## 1. Purpose

This document defines the **Workstream A verification pack** for **Glimmer**.

Its purpose is to prove that the foundational implementation substrate created by **Workstream A — Foundation** is real, coherent, and stable enough for later workstreams to build on safely.

Where the smoke pack answers "is the system basically alive?", this pack answers a stricter question:

**Is the foundation strong enough to extend without rethinking the basics?**

**Stable verification anchor:** `TESTPACK:WorkstreamA.ControlSurface`

---

## 2. Role of the Workstream A Pack

This pack exists to verify the implementation outcomes expected from the Foundation workstream, including:

- repository and application skeleton integrity,
- backend and frontend baseline startup,
- local-first configuration posture,
- PostgreSQL baseline wiring,
- initial route/shell reachability,
- initial test-estate scaffolding posture,
- and the presence of the agent-operational support surfaces that controlled AI-assisted delivery depends on.

This pack is broader than smoke, but still intentionally foundation-scoped. It should not attempt to prove domain richness, connector correctness, assistant-core workflow quality, or full workspace UX behavior.

**Stable verification anchor:** `TESTPACK:WorkstreamA.Role`

---

## 3. Relationship to the Control Surface

This verification pack is derived from and aligned to:

- the **Agentic Delivery Framework**, especially its authority model, verification model, evidence-of-completion rules, and repository document hierarchy, fileciteturn27file0
- the **Testing Strategy Companion**, especially automation-first proof, layered testing, Playwright for browser-visible workflows, and evidence-backed completion, fileciteturn27file1
- the **Glimmer Agentic Delivery Document Set**, which explicitly calls for `verification-pack-workstream-a.md` as part of the canonical verification family, fileciteturn27file2
- the **Glimmer Requirements**, especially the product-purpose, local-first, state-continuity, privacy, and safe-behavior posture that Foundation must support, fileciteturn27file3
- the **Glimmer Testing Strategy**, especially the verification-layer model and startup/foundation verification expectations, fileciteturn27file4
- the **Glimmer Architecture**, especially the system boundary, technology baseline, local-first boundary, and verification architecture, fileciteturn27file5turn27file16
- the **Build Plan** and **Build Strategy**, which place Foundation first and explicitly tie it to runtime, persistence, control-surface, and testing substrate setup, fileciteturn27file6turn27file7
- the detailed **Workstream A: Foundation** plan, which defines the concrete substrate outcomes this pack must verify, fileciteturn27file8
- and the already-defined **Test Catalog** and **Smoke Pack**, which this pack extends without duplicating blindly. fileciteturn27file17turn27file18

**Stable verification anchor:** `TESTPACK:WorkstreamA.ControlSurfaceAlignment`

---

## 4. Why This Pack Exists Separately from Smoke

The smoke pack is intentionally shallow. It proves that Glimmer can start, that the shell renders, that the database is reachable, and that the base workspace routes are not dead on arrival. fileciteturn27file18

That is necessary, but it is not sufficient for Workstream A completion.

Workstream A is meant to establish:

- coherent repository structure,
- backend and frontend skeletons,
- local runtime conventions,
- persistence baseline,
- initial testing scaffolding,
- and the agent-operational support surfaces under `.github/`, `8. Agent Skills/`, and `9. Agent Tools/`. fileciteturn27file8turn27file6turn27file0

This pack therefore goes beyond smoke by proving that the foundational substrate is not just alive, but structurally usable.

**Stable verification anchor:** `TESTPACK:WorkstreamA.Rationale`

---

## 5. Workstream A Verification Scope

### 5.1 In scope

This pack covers proof for the following Foundation concerns:

- backend startup and basic health/status exposure,
- frontend startup and base workspace shell render,
- database connectivity baseline,
- basic workspace route reachability,
- local-first configuration resolution,
- persistence baseline and migration-path existence,
- backend structural boundary coherence,
- frontend shell coherence,
- initial test-estate scaffolding visibility,
- and the presence/shape of the core agent-operational surfaces.

### 5.2 Out of scope

This pack does **not** attempt to prove:

- rich domain correctness,
- connected-account semantics,
- connector normalization,
- triage quality,
- planner behavior,
- draft quality,
- review queue behavior,
- Telegram companion usefulness,
- or voice-session correctness.

Those belong to later workstream packs and cross-cutting packs.

**Stable verification anchor:** `TESTPACK:WorkstreamA.Scope`

---

## 6. Source `TEST:` Anchors Included in This Pack

The Workstream A pack includes the smoke scenarios and adds additional foundation-scoped checks around configuration, persistence baseline, structure, and delivery-control surfaces.

### 6.1 Included foundational smoke anchors

#### `TEST:Smoke.BackendStarts`
- **Scenario name:** Backend starts and exposes basic health/status behavior
- **Layers:** `integration`, `api`
- **Role in this pack:** Baseline proof that the backend runtime exists and can boot reliably. fileciteturn27file17

#### `TEST:Smoke.FrontendStarts`
- **Scenario name:** Frontend workspace shell starts and renders
- **Layers:** `integration`, `browser`
- **Role in this pack:** Baseline proof that the frontend shell exists and is reachable. fileciteturn27file17

#### `TEST:Smoke.DatabaseConnectivity`
- **Scenario name:** Primary relational store is reachable through the application
- **Layers:** `integration`
- **Role in this pack:** Baseline proof that the persistence substrate is wired. fileciteturn27file17

#### `TEST:Smoke.WorkspaceNavigationBasic`
- **Scenario name:** Core workspace routes are reachable
- **Layers:** `browser`
- **Role in this pack:** Baseline proof that the workspace shell and route skeleton are not broken. fileciteturn27file17

### 6.2 Additional Workstream A-specific anchors introduced by this pack

#### `TEST:Foundation.Config.LocalFirstDefaultsResolve`
- **Scenario name:** Local-first configuration defaults resolve safely
- **Primary layers:** `integration`, `api`
- **Primary drivers:** `REQ:LocalFirstOperatingModel`, `REQ:PrivacyAndLeastPrivilege`, `ARCH:LocalFirstBoundary`, `ARCH:SecretHandlingBoundary`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove the application can resolve required local-first configuration without unsafe secret assumptions or remote-first drift.

#### `TEST:Foundation.Persistence.MigrationBaselineExists`
- **Scenario name:** Persistence baseline and migration path exist
- **Primary layers:** `integration`
- **Primary drivers:** `ARCH:MemoryStorageStrategy`, `ARCH:TechnologyBaseline`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove later domain work can extend the relational substrate without rethinking the baseline.

#### `TEST:Foundation.Backend.StructureRespectsBoundaryShape`
- **Scenario name:** Backend skeleton respects documented boundary shape
- **Primary layers:** `integration`, `manual_only`
- **Primary drivers:** `ARCH:SystemBoundaries`, `ARCH:TechnologyBaseline`, `PLAN:WorkstreamA.PackageA4.BackendApplicationStructure`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove the backend is not a single tangled boot file and that the intended API/orchestration/domain/infrastructure separation is visible.

#### `TEST:Foundation.Frontend.WorkspaceShellExists`
- **Scenario name:** Frontend shell supports workspace-first route structure
- **Primary layers:** `browser`, `integration`
- **Primary drivers:** `ARCH:UiSurfaceMap`, `PLAN:DeliveryPrinciple.WebBeforeCompanion`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove the frontend begins as a workspace shell rather than a generic chatbot stub.

#### `TEST:Foundation.Testing.ScaffoldVisible`
- **Scenario name:** Initial test-estate scaffolding is present and runnable
- **Primary layers:** `integration`, `manual_only`
- **Primary drivers:** `ARCH:TestingArchitecture`, `ARCH:VerificationLayerModel`, `PLAN:WorkstreamA.PackageA6.InitialTestingScaffolding`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`, `PLAN:WorkstreamG.TestingAndRegression`
- **Intent:** Prove the project has made room for unit, integration, API, browser, contract, and pack-level proof rather than deferring testing structure indefinitely.

#### `TEST:Foundation.AgentSupport.CoreSurfacesPresent`
- **Scenario name:** Core agent-operational support surfaces are present
- **Primary layers:** `manual_only`
- **Primary drivers:** `PLAN:AuthorityModel.OperationalSupport`, `PLAN:WorkingDocs.RequiredPair`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`, `PLAN:GovernanceAndProcess`
- **Intent:** Prove the repo includes the control-support surfaces required for disciplined AI-assisted delivery.

**Stable verification anchor:** `TESTPACK:WorkstreamA.IncludedTests`

---

## 7. Workstream A Pack Entry Table

| TEST Anchor | Scenario | Layer | Automation Status | Pack Priority | Notes |
|---|---|---|---|---|---|
| `TEST:Smoke.BackendStarts` | Backend starts and exposes basic health/status behavior | `integration`, `api` | Planned | Critical | Reused from smoke |
| `TEST:Smoke.FrontendStarts` | Frontend workspace shell starts and renders | `integration`, `browser` | Planned | Critical | Reused from smoke |
| `TEST:Smoke.DatabaseConnectivity` | Primary relational store is reachable through the application | `integration` | Planned | Critical | Reused from smoke |
| `TEST:Smoke.WorkspaceNavigationBasic` | Core workspace routes are reachable | `browser` | Planned | High | Reused from smoke |
| `TEST:Foundation.Config.LocalFirstDefaultsResolve` | Local-first configuration defaults resolve safely | `integration`, `api` | Planned | Critical | Prevents remote-first or secret-assuming drift |
| `TEST:Foundation.Persistence.MigrationBaselineExists` | Persistence baseline and migration path exist | `integration` | Planned | Critical | Protects later domain work |
| `TEST:Foundation.Backend.StructureRespectsBoundaryShape` | Backend skeleton respects documented boundary shape | `integration`, `manual_only` | Planned | High | May require brief human structural review early on |
| `TEST:Foundation.Frontend.WorkspaceShellExists` | Frontend shell supports workspace-first route structure | `browser`, `integration` | Planned | High | Distinct from mere frontend startup |
| `TEST:Foundation.Testing.ScaffoldVisible` | Initial test-estate scaffolding is present and runnable | `integration`, `manual_only` | Planned | High | Supports Workstream G growth |
| `TEST:Foundation.AgentSupport.CoreSurfacesPresent` | Core agent-operational support surfaces are present | `manual_only` | Planned | Medium | Control-surface check rather than runtime behavior |

**Stable verification anchor:** `TESTPACK:WorkstreamA.EntryTable`

---

## 8. Expected Automation Shape

### 8.1 Backend startup and health proof

This proof should verify that:

- the backend can start in a minimal local/test configuration,
- a health or status path responds correctly,
- and application boot does not fail on import or initial dependency wiring.

### 8.2 Database baseline proof

This proof should verify that:

- PostgreSQL connectivity is real,
- baseline schema access works,
- and the migration path or equivalent baseline setup is not missing.

### 8.3 Frontend shell and route proof

This proof should verify that:

- the frontend can start,
- the base workspace shell renders,
- and at least the minimal route family or primary entry route is reachable.

### 8.4 Configuration proof

This proof should verify that:

- required local-first configuration values are discoverable,
- the application fails clearly when required config is missing,
- and there is no silent dependency on production-style secrets for basic local boot.

### 8.5 Structural and support-surface checks

Some Workstream A checks may remain partly `ManualOnly` at first because they concern:

- repository/control-surface presence,
- structural coherence,
- and early-stage test-estate visibility.

Those should still be explicit, named, and evidence-backed rather than implied.

**Stable verification anchor:** `TESTPACK:WorkstreamA.AutomationShape`

---

## 9. Environment Assumptions

The Workstream A pack assumes the smallest realistic foundation environment required to prove the substrate.

### 9.1 Required assumptions

Expected baseline assumptions include:

- backend runtime dependencies installed,
- frontend runtime dependencies installed,
- reachable PostgreSQL instance or test equivalent,
- local environment/config templates available,
- and Playwright/browser dependencies installed if browser proof is executed.

### 9.2 Allowed independence from live provider integrations

This pack must not depend on live:

- Google connectivity,
- Microsoft Graph connectivity,
- Telegram bot setup,
- or voice infrastructure.

Those are explicitly later-phase concerns.

### 9.3 Documentation/control-surface assumption

This pack also assumes the Phase 0 control surface exists and is coherent enough to guide Workstream A delivery, consistent with the governance phase-exit model. fileciteturn27file15

**Stable verification anchor:** `TESTPACK:WorkstreamA.EnvironmentAssumptions`

---

## 10. Execution Guidance

### 10.1 When to run this pack

This pack should normally be run:

- when establishing the first real app skeleton,
- after major foundation refactors,
- after persistence-baseline changes,
- after configuration/bootstrap changes,
- and before declaring Workstream A substantively complete.

### 10.2 Relationship to smoke execution

The smoke pack remains the smallest quick baseline and may run more frequently.

The Workstream A pack is broader and should be used when validating the full Foundation workstream outcome rather than only boot sanity.

### 10.3 Failure handling

If this pack fails:

- later workstream confidence should be treated cautiously,
- the failure should usually be resolved before deep connector/orchestration work proceeds,
- and progress reporting should explicitly state which substrate concern remains unstable.

**Stable verification anchor:** `TESTPACK:WorkstreamA.ExecutionGuidance`

---

## 11. Evidence Expectations

When the Workstream A pack is executed, evidence reporting should capture at minimum:

- execution date/time,
- environment posture used,
- which included `TEST:` anchors were executed,
- pass/fail outcome,
- any `ManualOnly` checks performed,
- any `Deferred` entries and why,
- and a brief statement of whether the foundation is considered stable enough for Workstream B extension.

This should be summarized in the relevant Workstream A progress file and, where meaningful, referenced in broader phase-exit or release-confidence reporting. fileciteturn27file15turn27file1

**Stable verification anchor:** `TESTPACK:WorkstreamA.EvidenceExpectations`

---

## 12. Operational Ready Definition for This Pack

The Workstream A verification pack should be considered operationally established when:

1. all included `TEST:` anchors are defined and mapped,
2. smoke scenarios are executable through stable proof paths,
3. local-first configuration proof exists,
4. persistence-baseline proof exists,
5. frontend shell and route proof exists,
6. test-estate scaffolding proof exists,
7. core agent-operational surfaces are visibly present,
8. and the pack can be executed repeatably without undocumented setup.

At that point, Workstream A has a meaningful verification surface rather than just a startup demo.

**Stable verification anchor:** `TESTPACK:WorkstreamA.DefinitionOfOperationalReady`

---

## 13. Relationship to Later Packs

This pack establishes the proof surface for Foundation only.

Later packs should build on it as follows:

- **Workstream B** should deepen domain and memory correctness,
- **Workstream C** should prove connector and provenance behavior,
- **Workstream D** should prove triage and prioritization workflows,
- **Workstream E** should prove browser-visible workspace behavior,
- **Workstream F** should prove voice and companion behavior,
- **Data Integrity** should protect the memory spine across releases,
- and **Release** should compose representative proof from all major risk areas.

This progression is consistent with the Glimmer build plan and the cross-cutting verification estate defined by Workstream G. fileciteturn27file14turn27file6

**Stable verification anchor:** `TESTPACK:WorkstreamA.RelationshipToLaterPacks`

---

## 14. Final Note

Workstream A is not glamorous, and its verification pack should not pretend otherwise.

Its job is to prove that Glimmer is:

- structurally real,
- locally runnable,
- persistence-capable,
- workspace-shaped,
- and ready for real domain work.

If this pack tells the truth, the rest of the project gets safer.

**Stable verification anchor:** `TESTPACK:WorkstreamA.Conclusion`

