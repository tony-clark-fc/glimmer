# Glimmer — Workstream G Testing and Regression Design and Implementation Plan

## Document Metadata

- **Document Title:** Glimmer — Workstream G Testing and Regression Design and Implementation Plan
- **Document Type:** Working Implementation Plan
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** G — Testing and Regression
- **Primary Companion Documents:** Requirements, Architecture, Build Plan, Verification, Governance and Process, Global Copilot Instructions, Module Instructions, Workstream G Verification Expectations

---

## 1. Purpose

This document is the active working implementation plan for **Workstream G — Testing and Regression**.

Its purpose is to translate the canonical Workstream G build-plan intent into an execution-ready plan that a coding agent can use during real implementation sessions.

This file should remain practical and anchored. It is not the source of architecture truth. It is the working plan for how Glimmer’s executable test estate, regression routines, and verification evidence flows should be implemented and advanced slice by slice.

**Stable working anchor:** `WORKG:Plan.ControlSurface`

---

## 2. Workstream Objective

The objective of Workstream G is to turn Glimmer’s authored verification design into a real, repeatable, executable proof estate.

At the end of Workstream G, the repository should have real support for:

- automated unit, integration, API, graph, contract, and browser test execution,
- stable mapping from implementation work to `TEST:` anchors,
- executable smoke, workstream, data-integrity, and release pack routines,
- evidence capture for meaningful verification runs,
- explicit handling of `ManualOnly` and `Deferred` scenarios,
- and regression habits that let Glimmer evolve without shipping on guesswork.

This workstream is where the verification estate stops being well-written documentation and becomes operational truth.

**Stable working anchor:** `WORKG:Plan.Objective`

---

## 3. Control Anchors in Scope

### 3.1 Requirements anchors

- `REQ:ProductPurpose`
- `REQ:ProjectMemory`
- `REQ:MessageIngestion`
- `REQ:MultiAccountProfileSupport`
- `REQ:ContextualMessageClassification`
- `REQ:PrioritizationEngine`
- `REQ:DraftResponseWorkspace`
- `REQ:VoiceInteraction`
- `REQ:TelegramMobilePresence`
- `REQ:Explainability`
- `REQ:TraceabilityAndAuditability`
- `REQ:HumanApprovalBoundaries`
- `REQ:SafeBehaviorDefaults`

### 3.2 Architecture anchors

- `ARCH:TestingArchitecture`
- `ARCH:VerificationLayerModel`
- `ARCH:PlaywrightTestBoundary`
- `ARCH:GraphVerificationStrategy`
- `ARCH:RegressionPackModel`
- `ARCH:SystemBoundaries`
- `ARCH:StructuredMemoryModel`
- `ARCH:ConnectorIsolation`
- `ARCH:ReviewGateArchitecture`
- `ARCH:NoAutoSendPolicy`

### 3.3 Build-plan anchors

- `PLAN:WorkstreamG.TestingAndRegression`
- `PLAN:WorkstreamG.Objective`
- `PLAN:WorkstreamG.InternalSequence`
- `PLAN:WorkstreamG.VerificationExpectations`
- `PLAN:WorkstreamG.DefinitionOfDone`

### 3.4 Verification anchors

- `TESTCATALOG:ControlSurface`
- `TESTPACK:Smoke.ControlSurface`
- `TESTPACK:WorkstreamA.ControlSurface`
- `TESTPACK:WorkstreamB.ControlSurface`
- `TESTPACK:WorkstreamC.ControlSurface`
- `TESTPACK:WorkstreamD.ControlSurface`
- `TESTPACK:WorkstreamE.ControlSurface`
- `TESTPACK:WorkstreamF.ControlSurface`
- `TESTPACK:DataIntegrity.ControlSurface`
- `TESTPACK:Release.ControlSurface`

**Stable working anchor:** `WORKG:Plan.ControlAnchors`

---

## 4. Execution Principles for This Workstream

### 4.1 Automation first, honesty always

The default goal is executable automated proof. Where automation is not yet practical, `ManualOnly` or `Deferred` status must be explicit and evidence-backed.

### 4.2 Verification is implementation, not cleanup

Test harnesses, pack routines, and evidence capture should be built alongside the product, not postponed until the end.

### 4.3 Prefer meaningful scenario proof over shallow coverage theater

A small number of strong scenario tests is better than a large amount of fragile or superficial checking.

### 4.4 Cross-layer confidence matters

Regression should cover not just isolated code units, but also the handoffs between:

- connectors and memory,
- memory and assistant-core workflows,
- assistant-core workflows and workspace UI,
- and workspace and companion modes.

### 4.5 Pack execution must stay practical

Verification packs should remain runnable and useful. Avoid turning them into bloated wish lists that nobody executes.

### 4.6 Evidence capture is part of done

A test run that is not surfaced into an evidence trail or progress update is less useful than it should be.

**Stable working anchor:** `WORKG:Plan.ExecutionPrinciples`

---

## 5. Regression Estate Shape Target for Workstream G

By the end of this workstream, the implementation should materially support the following verification-estate categories or directly equivalent concrete shapes:

- unit and integration harnesses
- API test harnesses
- graph/workflow test harnesses
- browser/Playwright harnesses
- contract or fixture-driven connector tests
- pack-oriented execution routines
- test-to-anchor traceability support
- evidence collection and summary routines
- explicit manual/deferred scenario handling

These layers must remain executable, traceable, and honest about current confidence.

**Stable working anchor:** `WORKG:Plan.RegressionShapeTarget`

---

## 6. Work Packages to Execute

## 6.1 WG1 — Core test harness baseline

### Objective
Establish the shared baseline test harnesses for unit, integration, API, graph, and browser testing.

### Expected touch points
- test config/setup files
- fixture helpers
- test environment bootstrap
- browser automation setup

### Verification expectation
- smoke and foundational proof paths become executable

### Notes
This package is about making real proof possible everywhere else.

**Stable working anchor:** `WORKG:Plan.PackageWG1`

---

## 6.2 WG2 — `TEST:` anchor traceability support

### Objective
Implement the repo-local routines and conventions that connect executable tests, verification packs, and evidence surfaces back to stable `TEST:` anchors.

### Expected touch points
- test metadata conventions
- helper scripts or indexes
- verification-support tooling
- docs/tests alignment helpers

### Verification expectation
- representative `TEST:` anchors can be located from executable test surfaces

### Notes
This should reinforce, not replace, the canonical test catalog.

**Stable working anchor:** `WORKG:Plan.PackageWG2`

---

## 6.3 WG3 — Smoke and foundational pack execution routines

### Objective
Turn the smoke pack and Workstream A pack into real executable routines or clearly reproducible commands.

### Expected touch points
- smoke test scripts/commands
- browser smoke routines
- reporting helpers

### Verification expectation
- `verification-pack-smoke.md`
- `verification-pack-workstream-a.md`

### Notes
This is the first place where authored pack design must become actual repeatable execution.

**Stable working anchor:** `WORKG:Plan.PackageWG3`

---

## 6.4 WG4 — Workstream pack execution hardening

### Objective
Incrementally wire the authored Workstream B–F verification packs to real executable routines and representative coverage.

### Expected touch points
- graph/integration/browser test suites
- pack membership routines
- evidence helpers

### Verification expectation
- representative scenarios from each workstream pack become runnable and attributable

### Notes
Do not wait until every feature is complete before building the execution pattern.

**Stable working anchor:** `WORKG:Plan.PackageWG4`

---

## 6.5 WG5 — Data-integrity regression surface

### Objective
Turn the cross-cutting data-integrity pack into a durable regression routine that protects the memory spine over time.

### Expected touch points
- integration test suites
- seeded-state fixtures
- transition-sensitive integrity checks
- evidence summarization

### Verification expectation
- `verification-pack-data-integrity.md`

### Notes
This is one of the most important long-lived regression surfaces in the repo.

**Stable working anchor:** `WORKG:Plan.PackageWG5`

---

## 6.6 WG6 — Release-pack execution routine

### Objective
Turn the release pack into a repeatable representative confidence routine that can be used for milestone and release judgments.

### Expected touch points
- pack orchestration scripts/commands
- release evidence summary templates/helpers
- scope selection handling for companion/voice inclusion

### Verification expectation
- `verification-pack-release.md`

### Notes
The release pack must stay selective and honest, not exhaustive and ceremonial.

**Stable working anchor:** `WORKG:Plan.PackageWG6`

---

## 6.7 WG7 — Evidence collection and reporting support

### Objective
Implement the routines and helper artifacts needed to summarize executed proof into working progress files or release-status surfaces.

### Expected touch points
- evidence-collection scripts/helpers
- progress summary helpers
- verification-result formatting conventions

### Verification expectation
- meaningful test runs can be summarized into usable evidence outputs

### Notes
A test estate without readable evidence is weaker than it looks.

**Stable working anchor:** `WORKG:Plan.PackageWG7`

---

## 6.8 WG8 — ManualOnly and Deferred discipline

### Objective
Implement explicit conventions and, where useful, helper support for tracking manual-only and deferred checks without pretending they are automated proof.

### Expected touch points
- evidence routines
- verification summary helpers
- docs/test workflow conventions

### Verification expectation
- manual/deferred items remain visible and auditable in evidence output

### Notes
This is about honesty and release-confidence discipline.

**Stable working anchor:** `WORKG:Plan.PackageWG8`

---

## 7. Recommended Execution Order

The recommended execution order inside this working plan is:

1. WG1 — Core test harness baseline
2. WG2 — `TEST:` anchor traceability support
3. WG3 — Smoke and foundational pack execution routines
4. WG4 — Workstream pack execution hardening
5. WG5 — Data-integrity regression surface
6. WG6 — Release-pack execution routine
7. WG7 — Evidence collection and reporting support
8. WG8 — ManualOnly and Deferred discipline

This sequence gets real proof running early while still building toward long-lived regression and release-confidence discipline.

**Stable working anchor:** `WORKG:Plan.ExecutionOrder`

---

## 8. Expected Files and Layers Likely to Change

The initial Workstream G implementation is likely to touch files or file groups such as:

- test harness setup files
- integration/API/graph/browser test suites
- verification-support scripts/helpers
- pack execution helpers
- evidence/reporting helpers
- repo-local tool outputs or support indexes
- Workstream G working documents

This list should be refined as implementation begins.

**Stable working anchor:** `WORKG:Plan.LikelyTouchPoints`

---

## 9. Verification Plan for Workstream G

### 9.1 Minimum required proof

At minimum, Workstream G implementation should produce executable proof for:

- harness bring-up
- smoke execution
- foundational pack execution
- representative workstream pack execution
- data-integrity pack execution
- release-pack execution
- evidence capture routines
- manual/deferred visibility discipline

### 9.2 Primary verification surfaces

The main verification references for this workstream are:

- `TEST_CATALOG.md`
- all canonical verification packs already authored
- `verification-pack-release.md` as the top-level representative confidence surface

### 9.3 Evidence expectation

Meaningful implementation slices in this workstream should update the Workstream G progress file with:

- what was implemented
- what proof was executed
- what passed
- what failed
- what remains blocked or deferred

**Stable working anchor:** `WORKG:Plan.VerificationPlan`

---

## 10. Human Dependencies and Likely Decisions

This workstream is mostly agent-executable, but a few human decisions may still be needed.

Likely human-dependent areas include:

- deciding how much release-pack breadth is realistic for early milestones
- reviewing whether some environment-bound checks should remain `ManualOnly` initially
- confirming preferred evidence-reporting format if a concise release-status summary is needed for human review

The coding agent should build the automated proof spine first before surfacing stylistic reporting questions as blockers.

**Stable working anchor:** `WORKG:Plan.HumanDependencies`

---

## 11. Known Risks in This Workstream

### 11.1 Risk — Verification remains on paper only

The biggest danger is that the pack family stays beautifully documented but weakly executable.

### 11.2 Risk — Coverage theater replaces scenario truth

If the workstream optimizes for counts instead of meaningful confidence, the estate will look healthier than it is.

### 11.3 Risk — Pack execution becomes too heavy to run routinely

If the routines are bloated, they will be ignored.

### 11.4 Risk — Evidence capture is too vague

If the outputs are hard to interpret, human decision-makers will still be forced to reconstruct confidence manually.

### 11.5 Risk — ManualOnly and Deferred discipline becomes dishonest

If these categories are hidden or blurred, release confidence will become unreliable.

**Stable working anchor:** `WORKG:Plan.Risks`

---

## 12. Immediate Next Session Recommendations

When actual coding for Workstream G begins, the first sensible execution slice is:

1. stand up the core test harness baseline,
2. wire a small amount of `TEST:` anchor traceability support,
3. make the smoke pack executable,
4. capture the first evidence output,
5. and then harden toward workstream-pack execution.

That creates immediate practical value without trying to solve the whole regression estate at once.

**Stable working anchor:** `WORKG:Plan.ImmediateNextSlice`

---

## 13. Definition of Ready for Workstream G Completion

Workstream G should only be considered ready for completion when all of the following are materially true:

- core automated harnesses are real
- `TEST:` anchor traceability is real enough to be useful
- smoke and Workstream A pack execution are real
- representative workstream pack execution is real
- data-integrity regression execution is real
- release-pack execution is real
- evidence capture and reporting are real
- manual/deferred discipline is explicit
- and the corresponding proof paths have been executed and recorded

If these are not true, Workstream G is not done, even if the verification docs themselves are complete.

**Stable working anchor:** `WORKG:Plan.DefinitionOfReadyForCompletion`

---

## 14. Final Note

This workstream is where Glimmer either earns the right to claim confidence or keeps relying on documentation and optimism.

That is the standard here.

The goal is not to produce the largest test estate. The goal is to produce one that is:

- executable,
- traceable,
- honest,
- and strong enough that real release decisions can be made from it.

**Stable working anchor:** `WORKG:Plan.Conclusion`

