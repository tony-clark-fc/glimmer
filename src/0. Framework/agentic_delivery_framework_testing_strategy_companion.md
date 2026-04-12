# Agentic Delivery Framework — Testing Strategy Companion

**Purpose:** This document is the testing companion to the **Agentic Delivery Framework**. It defines how testing is designed, implemented, automated, executed, and evidenced when software is delivered using AI coding agents within this framework.

**Version:** 1.0  
**Date:** 2026-03-13  
**Status:** Reference  
**Primary Stack Assumption:** Microsoft .NET, Azure, JetBrains Rider, GitHub Copilot plugin in Agent mode  
**UI Automation Standard:** Playwright  
**Primary Delivery Principle:** Testing is a first principle of design and build, not a cleanup activity after code is written.

---

## Table of Contents

1. [What This Companion Is](#1-what-this-companion-is)
2. [Core Testing Principles](#2-core-testing-principles)
3. [Testing Objectives in the Agentic Delivery Model](#3-testing-objectives-in-the-agentic-delivery-model)
4. [Test Architecture by Default](#4-test-architecture-by-default)
5. [The Automation-First Rule](#5-the-automation-first-rule)
6. [Human vs Agent Role in Testing](#6-human-vs-agent-role-in-testing)
7. [Required Test Layers](#7-required-test-layers)
8. [Unit Testing Standard for .NET Solutions](#8-unit-testing-standard-for-net-solutions)
9. [Integration Testing Standard for .NET and Azure Solutions](#9-integration-testing-standard-for-net-and-azure-solutions)
10. [API Testing Strategy](#10-api-testing-strategy)
11. [Frontend and User Workflow Testing with Playwright](#11-frontend-and-user-workflow-testing-with-playwright)
12. [End-to-End Test Design](#12-end-to-end-test-design)
13. [Testing State Machines, Rules, and Decision Logic](#13-testing-state-machines-rules-and-decision-logic)
14. [Database Testing](#14-database-testing)
15. [Azure Dependency Testing](#15-azure-dependency-testing)
16. [Background Jobs, Messaging, and Time-Based Processing](#16-background-jobs-messaging-and-time-based-processing)
17. [Observability and Diagnostics as Test Targets](#17-observability-and-diagnostics-as-test-targets)
18. [Failure-Path and Resilience Testing](#18-failure-path-and-resilience-testing)
19. [Security and Access Testing](#19-security-and-access-testing)
20. [ABP.IO-Specific Testing Guidance](#20-abpio-specific-testing-guidance)
21. [Test Data, Fixtures, and Environment Control](#21-test-data-fixtures-and-environment-control)
22. [Test Execution in Rider by GitHub Copilot Agent](#22-test-execution-in-rider-by-github-copilot-agent)
23. [Test Evidence and Completion Rules](#23-test-evidence-and-completion-rules)
24. [Regression Packs and Release Gates](#24-regression-packs-and-release-gates)
25. [Recommended Repository Structure](#25-recommended-repository-structure)
26. [Copilot Instruction Expectations for Testing](#26-copilot-instruction-expectations-for-testing)
27. [Verification Pack Design for .NET and Azure Solutions](#27-verification-pack-design-for-net-and-azure-solutions)
28. [Anti-Patterns to Avoid](#28-anti-patterns-to-avoid)
29. [Templates](#29-templates)
30. [Final Operating Standard](#30-final-operating-standard)

---

## 1. What This Companion Is

This document defines the **testing operating model** for projects delivered under the Agentic Delivery Framework.

The main framework already establishes:

- anchor-based traceability,
- workstream-driven delivery,
- verification as a first-class concern,
- and evidence-backed completion.

This companion goes deeper on **how testing should actually be approached** when the delivery environment is:

- primarily **.NET**,
- often integrated with **Azure**,
- sometimes built on **ABP.IO**,
- implemented in **JetBrains Rider**,
- and executed with **GitHub Copilot Agent** as the active coding assistant.

It is intentionally practical. It is designed to help humans and agents build systems where automated testing does most of the heavy lifting and manual testing is kept to the smallest reasonable footprint.

---

## 2. Core Testing Principles

### 2.1 Testing begins at design time

A feature is not fully designed until the team understands:

- how it can fail,
- what the success path looks like,
- what contracts it exposes,
- what state transitions it allows,
- and how the intended behavior will be proven.

### 2.2 Automated testing is the default

The default assumption for every meaningful feature is that the proof of correctness should be **automated wherever reasonably possible**.

Manual testing is a fallback for:

- highly visual confirmation that is not yet worth automating,
- external vendor flows that cannot practically be controlled,
- or one-off exploratory checks during early shaping.

### 2.3 Tests must prove behavior, not just execution

A shallow test that calls a method and asserts `not null` is not evidence of meaningful correctness.

Tests must prove:

- business rules,
- workflow behavior,
- state integrity,
- contract correctness,
- and resilience under expected failure conditions.

### 2.4 API surfaces should be testable by design

If an API surface cannot be tested automatically, that is usually a design smell.

Controllers, minimal APIs, Razor Page handlers, background service triggers, webhooks, and application services should all be designed so that their core behavior can be exercised in automated tests.

### 2.5 Playwright is the standard for frontend user testing

For browser-visible user workflows, **Playwright is the required standard**.

Do not rely on manual clicking as the primary proof of UI correctness when a workflow can be automated through Playwright.

### 2.6 The AI assistant must execute the testing work

Under this framework, the AI coding assistant is not just allowed to write tests. It is expected to:

- derive the test plan from the linked `TEST:` anchors,
- implement the test automation,
- run the tests in the IDE,
- inspect failures,
- fix the code or the tests where appropriate,
- and record the evidence in the working documents.

---

## 3. Testing Objectives in the Agentic Delivery Model

The testing strategy exists to achieve six things:

1. **Reduce reliance on human regression effort**
2. **Catch drift quickly as agent-written code evolves**
3. **Make behavior explicit and durable across sessions**
4. **Give AI agents a concrete proof target, not a vague quality goal**
5. **Protect the architecture from silent erosion**
6. **Support safe iteration in code-heavy .NET and Azure systems**

This means testing is not just about defect detection. It is also about delivery control.

---

## 4. Test Architecture by Default

A typical solution delivered under this framework should assume the following testing shape by default:

```text
src/
  MyApp.Web/
  MyApp.Application/
  MyApp.Domain/
  MyApp.Infrastructure/
  ...

tests/
  MyApp.Domain.Tests/
  MyApp.Application.Tests/
  MyApp.Infrastructure.IntegrationTests/
  MyApp.Api.IntegrationTests/
  MyApp.Web.PlaywrightTests/
  MyApp.EndToEndTests/
```

Not every project needs every test project on day one. But the architecture should make room for:

- fast unit tests,
- integration tests around persistence and application boundaries,
- API contract tests,
- Playwright-driven browser tests,
- and end-to-end workflow tests where the feature is operationally important.

---

## 5. The Automation-First Rule

### 5.1 Default hierarchy

When deciding how to prove a requirement, prefer this order:

1. **Unit automation** for rules and calculations
2. **Integration automation** for persistence, infrastructure, and service collaboration
3. **API automation** for external contracts and application surfaces
4. **Playwright automation** for browser-visible workflows
5. **Manual verification** only where the above is impractical or temporarily deferred

### 5.2 Manual testing is not the main regression mechanism

Humans should not be expected to repeatedly perform broad regression passes just because the automated test estate is weak.

That is exactly the kind of delivery drag this framework is intended to eliminate.

### 5.3 Manual checks must be explicit when still needed

If a scenario remains manual, it must be recorded as:

- `ManualOnly`, or
- `Deferred`

with a clear reason.

---

## 6. Human vs Agent Role in Testing

### 6.1 Agent responsibilities

The AI coding assistant is expected to:

- identify relevant `TEST:` anchors before implementation,
- propose missing test anchors when required,
- create test projects and test infrastructure,
- write unit, integration, API, and Playwright tests,
- execute tests in Rider,
- inspect results and failures,
- iterate on fixes,
- and update the verification evidence in progress files.

### 6.2 Human responsibilities

The human remains accountable for:

- agreeing the intended test strategy,
- approving the level of automation for high-value workflows,
- provisioning external environments the agent cannot create,
- supplying secrets or Azure access where required,
- approving truly manual deferrals,
- and deciding release readiness.

### 6.3 Shared responsibility areas

The human defines the seriousness of the scenario. The agent does the mechanical testing work.

That is the right split.

---

## 7. Required Test Layers

Every meaningful solution should think in terms of these layers.

### 7.1 Unit tests
For pure domain rules, calculation logic, validators, mappers, normalization rules, policy decisions, state-transition guards.

### 7.2 Integration tests
For repositories, EF Core mappings, application services, transaction boundaries, Azure client wrappers, storage interactions, queue/message boundaries, cache interactions.

### 7.3 API tests
For controllers, minimal APIs, Razor Page post handlers where appropriate, request/response contracts, authorization, validation, error behavior.

### 7.4 Browser workflow tests
For user journeys through the actual UI using Playwright.

### 7.5 End-to-end tests
For high-value business workflows that cross multiple layers and infrastructure boundaries.

### 7.6 Non-functional tests
For resilience, performance-sensitive behaviors, migrations, concurrency, operability, and observability.

---

## 8. Unit Testing Standard for .NET Solutions

### 8.1 Scope of unit tests

Unit tests should focus on code that can run:

- in-process,
- without external infrastructure,
- with deterministic inputs,
- and with fast execution.

Typical targets:

- domain entities,
- value objects,
- business rules,
- validators,
- mapping helpers,
- scoring/calculation logic,
- date/time policies with clock abstraction,
- state-transition rules,
- normalization logic.

### 8.2 Preferred characteristics

Unit tests should be:

- fast,
- deterministic,
- isolated,
- explicit about expected behavior,
- and easy for an agent to read and repair.

### 8.3 Structure

Use clear arrange/act/assert flow. Prefer one behavior focus per test.

### 8.4 What should not be called a unit test

A test that touches:

- a real database,
- a live Azure service,
- an HTTP endpoint,
- or full application startup

is not a unit test.

### 8.5 Typical .NET tool choice

The exact framework can vary by project standard, but the default should be a mainstream .NET testing stack with strong ecosystem support. The framework is less important than the discipline.

---

## 9. Integration Testing Standard for .NET and Azure Solutions

### 9.1 What integration tests prove

Integration tests prove that important pieces collaborate correctly.

This includes:

- EF Core mappings,
- database writes and reads,
- transaction behavior,
- infrastructure wrappers,
- application service orchestration,
- configuration wiring,
- and bounded infrastructure interactions.

### 9.2 Integration tests are mandatory for data-sensitive work

If the feature changes persistence, versioning, uniqueness, audit logging, or workflow state, unit tests alone are not enough.

### 9.3 Integration test design rules

- Use realistic infrastructure substitutes where possible.
- Avoid brittle shared state.
- Control setup and teardown.
- Prefer isolated test data per scenario.
- Make failures diagnostic, not mysterious.

### 9.4 Database-backed integration tests

For .NET systems using EF Core, integration tests should verify:

- entity mappings,
- migrations,
- required vs optional fields,
- uniqueness constraints,
- soft delete or supersession behavior,
- concurrency handling where relevant,
- and audit writes.

### 9.5 Azure-aware integration tests

Where infrastructure wrappers call Azure services, integration tests should usually stop at the wrapper boundary unless a controlled environment exists.

That means:

- test your own abstraction thoroughly,
- use fake or emulated dependencies where practical,
- and reserve true live-service tests for focused environment checks, not the default regression path.

---

## 10. API Testing Strategy

### 10.1 API surfaces must be designed for automation

All meaningful API surfaces should be automatically testable.

This includes:

- request validation,
- success responses,
- failure responses,
- authorization behavior,
- idempotency where relevant,
- contract shape,
- and side effects.

### 10.2 What to test on APIs

At minimum, API tests should cover:

- happy path,
- validation rejection,
- not found behavior,
- conflict behavior,
- unauthorized or forbidden behavior where applicable,
- and any critical state transition side effects.

### 10.3 Contract discipline

The API test estate should protect against accidental changes in:

- status codes,
- payload shape,
- required fields,
- validation semantics,
- and error contract behavior.

### 10.4 API-first delivery advantage

When APIs are well tested, they reduce the regression burden on browser tests. This is important because API automation is usually faster, more stable, and easier for the AI assistant to maintain.

---

## 11. Frontend and User Workflow Testing with Playwright

### 11.1 Playwright is the required browser automation standard

Any meaningful browser workflow should be automated with Playwright.

This includes applications built with:

- Razor Pages,
- MVC,
- Blazor,
- SPA front ends,
- and ABP.IO web fronts.

### 11.2 What Playwright should cover

Playwright should focus on:

- critical user journeys,
- visible success/failure outcomes,
- form submissions,
- navigation and workflow continuity,
- user-visible validation,
- and high-value operational scenarios.

### 11.3 What Playwright should not try to prove alone

Do not overload Playwright with proof that belongs in unit or integration tests.

A browser test should not be the first place a business rule is exercised if a faster lower-level test can prove it.

### 11.4 Playwright design rules

- Prefer stable selectors.
- Avoid brittle timing assumptions.
- Use explicit waits on meaningful UI state.
- Keep scenarios readable.
- Separate common setup from scenario intent.
- Focus on business workflows, not every pixel.

### 11.5 Minimum browser coverage expectation

Each major user-facing feature should usually have:

- one Playwright happy path,
- and one critical rejection or failure path,

unless there is a documented reason not to.

---

## 12. End-to-End Test Design

### 12.1 What counts as end-to-end

An end-to-end test proves a real workflow across multiple layers.

Examples:

- user submits a request in UI, record is created, audit entry is written, visible status updates,
- API receives a command, background process runs, storage is updated, notification is emitted,
- admin approves an item, state changes, prior active record is superseded, UI reflects the result.

### 12.2 Keep end-to-end coverage selective but strong

End-to-end tests are expensive compared to unit and integration tests. Use them intentionally.

Target:

- business-critical flows,
- stateful workflows,
- approval workflows,
- financial or operationally sensitive operations,
- and cross-boundary workflows with meaningful risk.

### 12.3 End-to-end tests should be scenario-driven

They should map cleanly to `TEST:` anchors and business meaning, not just technical plumbing.

---

## 13. Testing State Machines, Rules, and Decision Logic

State-heavy systems need stronger testing than CRUD-heavy systems.

### 13.1 Required patterns

Where workflows have state models, tests should explicitly prove:

- valid transitions,
- invalid transitions,
- terminal states,
- retry behavior,
- reprocessing behavior,
- and side effects of state change.

### 13.2 Decision tables deserve direct tests

If a workflow depends on combinations of conditions, write tests from the decision table rather than relying on accidental coverage.

This is especially important for:

- approvals,
- policy enforcement,
- scoring decisions,
- retry rules,
- and status derivation.

---

## 14. Database Testing

### 14.1 Database behavior is part of the system contract

Persistence logic is not just plumbing. In many .NET business systems it is a large part of the real behavior.

### 14.2 Test these things explicitly

Where relevant, integration tests should cover:

- migration success,
- schema compatibility,
- default values,
- required fields,
- uniqueness constraints,
- supersession/versioning,
- audit trail creation,
- delete behavior,
- and query resolution logic.

### 14.3 EF Core-specific expectation

If a repository or application service depends on EF Core semantics, the test should prove those semantics under realistic conditions, not assume them.

### 14.4 Dangerous database gap

A feature that compiles and passes unit tests but has not been proven against actual persistence behavior is not ready.

---

## 15. Azure Dependency Testing

### 15.1 Azure services should sit behind your own abstractions

For agentic delivery, Azure integrations should usually be wrapped so they can be:

- tested more easily,
- replaced with fakes where appropriate,
- and diagnosed more cleanly.

### 15.2 Three-level Azure testing model

Use this mental model:

1. **Unit test your own logic** around Azure interactions
2. **Integration test your wrapper behavior** with controlled substitutes or emulators where possible
3. **Run focused live-environment checks** only where actual Azure behavior must be confirmed

### 15.3 Live Azure tests are not the default regression engine

They are useful but should be narrow and explicit because they are slower, more fragile, and depend on environment access the AI agent may not always have.

### 15.4 Common Azure areas to test

Depending on the solution, this may include:

- Azure SQL connectivity and migration readiness,
- Blob storage upload/download behavior,
- queue or messaging behavior,
- App Configuration retrieval,
- Managed Identity or `DefaultAzureCredential` behavior,
- Key Vault access path,
- service-client timeout/retry handling,
- Azure-hosted AI or API integration wrappers.

---

## 16. Background Jobs, Messaging, and Time-Based Processing

### 16.1 These flows need dedicated proof

Background workers, scheduled jobs, asynchronous handlers, and timed workflows often break quietly because teams focus too much on request/response paths.

### 16.2 Required testing concerns

Where relevant, test:

- job pickup behavior,
- idempotency,
- duplicate message handling,
- retry logic,
- poison message behavior,
- safe pause/resume,
- time-window logic,
- and observable status changes.

### 16.3 Time control

Any meaningful time-based behavior should be testable through clock abstraction rather than real wall-clock waiting.

---

## 17. Observability and Diagnostics as Test Targets

Observability is not just an operational bonus. It is part of correctness for serious systems.

### 17.1 What should be testable

For high-value workflows, the system should be testable for:

- meaningful logs,
- status updates,
- audit records,
- trace correlation where relevant,
- and operator-visible error states.

### 17.2 Why this matters in AI-assisted delivery

When the AI agent fixes failing tests, it needs diagnostics that are clear enough to reason about. Poor observability slows the repair loop and increases false confidence.

---

## 18. Failure-Path and Resilience Testing

### 18.1 Failure paths are first-class scenarios

Every high-value feature should have proof for more than the happy path.

### 18.2 Typical required failure scenarios

Depending on context:

- invalid input,
- duplicate request,
- missing dependency,
- permission failure,
- transient external outage,
- timeout,
- retry exhausted,
- conflicting state,
- data integrity violation,
- partial failure recovery.

### 18.3 Retry behavior must be intentional

If the architecture includes retry policies, test:

- what is retried,
- what is not retried,
- how many times,
- what happens after exhaustion,
- and what the operator can see.

---

## 19. Security and Access Testing

Even where a local-only app has reduced authentication complexity, access behavior still matters where present.

### 19.1 Test what actually exists

If the solution includes:

- authentication,
- role checks,
- policy authorization,
- tenant isolation,
- admin-only actions,
- approval-only actions,
- or destructive operation safeguards,

those behaviors should be tested explicitly.

### 19.2 Security testing does not mean full penetration testing here

This framework is about delivery-level proof. The minimum standard is that coded access rules and safety boundaries are actually verified.

---

## 20. ABP.IO-Specific Testing Guidance

ABP.IO is the heaviest common stack this framework expects, so it gets explicit treatment.

### 20.1 Why ABP.IO needs stronger testing discipline

ABP.IO brings productivity and structure, but it also introduces:

- framework conventions,
- module boundaries,
- dependency injection layers,
- authorization patterns,
- application services,
- repository abstractions,
- generated code surfaces,
- and sometimes multi-tenancy concerns.

That means more places where teams can assume the framework is covering behavior that still needs proof.

### 20.2 Testing priorities in ABP.IO solutions

For ABP.IO projects, testing should explicitly cover:

- application services,
- authorization and permission behavior,
- DTO validation,
- object mapping assumptions,
- repository behavior,
- unit of work boundaries,
- background jobs,
- module wiring,
- tenant-sensitive behavior where applicable,
- and generated UI or endpoint flows where they matter operationally.

### 20.3 Application service tests

ABP.IO application services are often the true API boundary of the business logic. They should be heavily covered.

Tests should verify:

- permission enforcement,
- validation,
- state changes,
- repository effects,
- returned DTO shape,
- and important failure conditions.

### 20.4 Domain vs application layer proof

Do not let ABP.IO encourage all meaningful behavior into application services alone. Core rules should still be testable at domain or policy level where that makes sense.

### 20.5 Repository and data access testing in ABP.IO

Because ABP.IO abstracts data access, it becomes even more important to prove repository behavior under realistic persistence conditions, not just mocks.

### 20.6 Multi-tenancy

If multi-tenancy is enabled, tests must explicitly prove:

- tenant isolation,
- tenant-specific queries,
- cross-tenant access rejection,
- and behavior of host vs tenant context.

### 20.7 Permission and policy testing

ABP.IO permission systems can appear correct while still being misconfigured. Tests should explicitly verify:

- allowed access,
- forbidden access,
- host/admin-only flows,
- and approval-role constraints.

### 20.8 ABP.IO UI testing

If the UI is operationally meaningful, Playwright should cover the generated or scaffolded user workflows that matter most, especially:

- create/edit/delete flows,
- approval flows,
- admin workflows,
- and validation/error behavior.

### 20.9 Generated code is not self-proving

Scaffolded or generated code from ABP.IO still requires verification. Generation reduces typing effort, not testing responsibility.

---

## 21. Test Data, Fixtures, and Environment Control

### 21.1 Test data must be intentional

Random uncontrolled data leads to fragile automation.

### 21.2 Every meaningful verification pack should declare

- required fixture data,
- environment assumptions,
- reset approach,
- dependency mode (real/fake/emulated/stubbed),
- and known limitations.

### 21.3 Reset and isolation

Test runs should be isolated enough that the AI assistant can trust failures.

### 21.4 Avoid hidden magic

If a test depends on a seeded admin, feature flag, environment variable, database state, blob container, or queue name, that dependency should be visible.

---

## 22. Test Execution in Rider by GitHub Copilot Agent

### 22.1 Execution expectation

The AI assistant is expected to execute the testing work from within the IDE workflow.

That means it should:

- run unit and integration tests,
- run API tests,
- run Playwright tests where configured,
- inspect build and test failures,
- and continue iterating until the scoped verification target is satisfied or a genuine blocker is reached.

### 22.2 The agent must not stop at “tests written”

Writing tests without executing them is incomplete work.

### 22.3 Preferred working rhythm

For each slice:

1. identify linked `TEST:` anchors,
2. implement code,
3. implement tests,
4. run tests in Rider,
5. fix failures,
6. record evidence.

### 22.4 When the agent hits environment blockers

If execution requires:

- Azure credentials,
- provisioned cloud resources,
- unavailable secrets,
- missing browsers,
- or a controlled environment the agent cannot create,

it must:

- complete all code-safe test preparation first,
- classify the scenario accurately,
- and issue a structured human assistance request.

### 22.5 Playwright in the IDE workflow

The agent should be able to run Playwright test commands, inspect failures, and repair brittle selectors or timing issues rather than leaving UI automation half-finished.

---

## 23. Test Evidence and Completion Rules

### 23.1 Evidence is mandatory

A feature is not complete because the test file exists. It is complete when the intended automated proof has been executed and its status is visible.

### 23.2 Minimum evidence categories

Each meaningful work package should leave behind:

- implemented tests,
- execution result,
- known gaps,
- and verification status updates in the progress file.

### 23.3 Completion language

Use precise completion labels:

- Designed
- Implemented
- Verified
- Blocked
- ManualOnly
- Deferred
- Complete ✅

### 23.4 Honest status over optimistic status

If the Playwright suite is written but not run, or the integration tests require unavailable Azure access, the work is not `Complete ✅`.

---

## 24. Regression Packs and Release Gates

### 24.1 Default regression packs

Every meaningful solution should define:

- **Smoke Pack**
- **Workstream Regression Pack(s)**
- **Release Regression Pack**
- **Data Integrity Pack** where data behavior matters

### 24.2 Suggested content

#### Smoke Pack
- app starts
- core endpoint or page responds
- essential configuration wiring is healthy

#### Workstream Pack
- critical scenarios for that workstream

#### Release Pack
- the minimal cross-feature set needed to trust a release candidate

#### Data Integrity Pack
- migrations,
- uniqueness,
- supersession or versioning,
- audit records,
- rollback-safe behavior where relevant

### 24.3 Gate philosophy

Release gates should be based on scenario proof, not vague confidence.

---

## 25. Recommended Repository Structure

```text
.github/
  copilot-instructions.md
  instructions/

1. Requirements/
2. Architecture/
3. Build Plan/
4. Verification/
  TEST_CATALOG.md
  verification-pack-smoke.md
  verification-pack-release.md
  verification-pack-workstream-x.md

src/
  MyApp.Web/
  MyApp.Application/
  MyApp.Domain/
  MyApp.Infrastructure/

tests/
  MyApp.Domain.Tests/
  MyApp.Application.Tests/
  MyApp.Infrastructure.IntegrationTests/
  MyApp.Api.IntegrationTests/
  MyApp.Web.PlaywrightTests/
  MyApp.EndToEndTests/
```

---

## 26. Copilot Instruction Expectations for Testing

The project’s `copilot-instructions.md` should explicitly tell the AI assistant to:

- treat testing as part of implementation scope,
- prefer automation first,
- use Playwright for front-end user testing,
- keep API surfaces testable,
- run tests, not just write them,
- update progress files with verification status,
- avoid declaring completion without evidence,
- and request human help only when true environment boundaries are reached.

Suggested language themes:

- prefer tests that prove behavior,
- protect contracts and workflows,
- keep manual testing minimal,
- and maintain regression packs as durable assets.

---

## 27. Verification Pack Design for .NET and Azure Solutions

Each verification pack should clearly state:

- linked `REQ:`, `ARCH:`, `PLAN:`, and `TEST:` anchors,
- whether it covers unit, integration, API, Playwright, or end-to-end proof,
- required environment state,
- whether Azure dependencies are real or substituted,
- required seed data,
- and exit criteria.

Example classification set:

- Unit
- Integration
- Api
- Playwright
- EndToEnd
- ManualOnly
- Deferred

The exact labels can be standardized per project, but they must remain explicit.

---

## 28. Anti-Patterns to Avoid

Avoid these patterns:

- treating tests as a later workstream instead of a parallel proof activity,
- relying on manual clicking for primary regression,
- writing browser tests for logic that should be proven lower down,
- mocking everything until the integration risks disappear from sight,
- calling a database-backed test a unit test,
- trusting scaffolded ABP.IO code without proof,
- letting live Azure environments become the only place behavior is tested,
- writing tests but not executing them,
- marking work complete when the execution evidence is missing,
- and allowing the AI assistant to produce optimistic testing summaries.

---

## 29. Templates

### 29.1 Test Strategy Block for a Work Package

```markdown
## Testing Approach
- Relevant `TEST:` anchors:
- Unit proof required:
- Integration proof required:
- API proof required:
- Playwright proof required:
- End-to-end proof required:
- Manual-only items:
- Environment blockers:
```

### 29.2 Progress File Verification Block

```markdown
## Verification Status
- `TEST:Feature.HappyPath` — Passing
- `TEST:Feature.InvalidRequestRejected` — Passing
- `TEST:Feature.UiWorkflow` — Pending Playwright execution
- `TEST:Feature.AzureDependencyFailure` — Deferred by environment

## Evidence Summary
- Unit tests: Passing
- Integration tests: Passing
- API tests: Passing
- Playwright tests: Pending
- End-to-end tests: Not required for this slice
- Manual checks: None
- Known gaps: Azure live check not yet executed
```

### 29.3 Playwright Scenario Template

```markdown
<!-- TEST:Feature.UiWorkflow.HappyPath -->
## Feature UI workflow — happy path

**Purpose:** Prove the user can complete the workflow successfully in the browser.

**Preconditions:**
- Test user exists
- Required seed data exists
- Application starts successfully

**Action:**
- Navigate to page
- Enter required data
- Submit

**Expected outcome:**
- Success message displayed
- New record visible
- Expected backend side effect confirmed
```

### 29.4 API Scenario Template

```markdown
<!-- TEST:Feature.Api.InvalidRequestRejected -->
## Feature API rejects invalid request

**Purpose:** Prove the API returns the correct rejection behavior.

**Preconditions:**
- Application started in test host

**Action:**
- Send invalid request payload

**Expected outcome:**
- Correct status code
- Correct validation contract
- No incorrect side effects
```

### 29.5 ABP.IO Application Service Scenario Template

```markdown
<!-- TEST:Feature.AppService.PermissionDenied -->
## Feature application service rejects caller without permission

**Purpose:** Prove the ABP.IO permission model is enforced.

**Preconditions:**
- Caller identity exists without required permission

**Action:**
- Invoke application service method

**Expected outcome:**
- Access is denied
- No persistence side effect occurs
- Error path is observable and correct
```

---

## 30. Final Operating Standard

The testing standard for this framework is simple:

> Every solution should be designed and built so that automated testing does the bulk of the verification work, the AI assistant can execute that testing work inside the IDE, API and browser-visible behavior are testable by design, Playwright covers user workflows, and humans are left with only the minimum irreducible role in end-to-end delivery.

And one more rule matters just as much:

> A feature is not complete when the code exists. It is complete when the automated proof exists, has been executed, and the evidence is visible.

