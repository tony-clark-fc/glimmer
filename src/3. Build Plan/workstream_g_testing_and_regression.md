# Glimmer — Workstream G: Testing and Regression

## Document Metadata

- **Document Title:** Glimmer — Workstream G: Testing and Regression
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Build Strategy and Scope, Testing Strategy, Workstreams A–F

---

## 1. Purpose

This document defines the implementation strategy for **Workstream G — Testing and Regression**.

Its purpose is to turn Glimmer’s testing architecture into a real, cross-workstream verification estate with named regression packs, evidence routines, environment discipline, and durable proof of behavior across the whole system.

This workstream is not a cleanup pass. It is the workstream that makes every other workstream trustworthy over time.

**Stable plan anchor:** `PLAN:WorkstreamG.TestingAndRegression`

---

## 2. Workstream Objective

Workstream G exists to implement Glimmer’s cross-cutting verification and regression substrate, including:

- the canonical test-catalog and verification-pack structure,
- automation of core proof across unit, integration, API, graph, browser, and contract layers,
- regression-pack composition,
- test-data and environment control,
- evidence capture and completion routines,
- and cross-workstream verification hardening as Glimmer’s implementation grows.

At the end of this workstream, Glimmer should have a coherent and enforceable proof model rather than a scattered collection of tests.

**Stable plan anchor:** `PLAN:WorkstreamG.Objective`

---

## 3. Why This Workstream Exists as Its Own Stream

The framework and its testing companion both treat testing as a first principle of design and build, not as after-the-fact reassurance. The Glimmer architecture and build plan also make verification explicit at every layer.

That means some testing work belongs inside each workstream, but there is also a distinct body of cross-cutting work that must exist above them:

- shared regression-pack structure,
- canonical `TEST:` scenario management,
- Playwright conventions,
- connector contract fixtures,
- graph-workflow proof patterns,
- data-integrity pack design,
- evidence-of-completion discipline,
- and release-confidence routines.

Without a dedicated workstream for that cross-cutting substrate, the test estate will fragment and become uneven across the project.

**Stable plan anchor:** `PLAN:WorkstreamG.Rationale`

---

## 4. Related Requirements Anchors

This workstream directly supports the following requirements:

- `REQ:Explainability`
- `REQ:HumanApprovalBoundaries`
- `REQ:PrivacyAndLeastPrivilege`
- `REQ:SafeBehaviorDefaults`
- `REQ:ProjectMemory`
- `REQ:MessageIngestion`
- `REQ:MultiAccountProfileSupport`
- `REQ:VoiceInteraction`
- `REQ:TelegramMobilePresence`
- `REQ:TraceabilityAndAuditability`

These requirements are not satisfied merely because features exist. They must be proven under regression conditions, especially where behavior crosses memory, review, security, and multi-channel boundaries.

**Stable plan anchor:** `PLAN:WorkstreamG.RequirementsAlignment`

---

## 5. Related Architecture Anchors

This workstream is primarily implementing the architecture described by:

- `ARCH:TestingArchitecture`
- `ARCH:VerificationLayerModel`
- `ARCH:GraphVerificationStrategy`
- `ARCH:PlaywrightTestBoundary`
- `ARCH:RegressionPackModel`
- `ARCH:DomainMemoryVerification`
- `ARCH:ConnectorVerificationStrategy`
- `ARCH:SecurityVerificationImplications`
- `ARCH:MemoryVerificationImplications`

These anchors define the project-specific proof model, the required verification layers, the cross-workstream regression strategy, and the specific high-risk behaviors that must be verified repeatedly over time.

**Stable plan anchor:** `PLAN:WorkstreamG.ArchitectureAlignment`

---

## 6. Workstream Scope

### 6.1 In scope

This workstream includes:

- creation of canonical verification documents,
- design and implementation of regression packs,
- test-estate expansion across all required layers,
- shared test helpers, fixtures, and environment conventions,
- evidence-of-completion routines,
- workstream-level verification hardening,
- and release-confidence verification composition.

**Stable plan anchor:** `PLAN:WorkstreamG.InScope`

### 6.2 Out of scope

This workstream does **not** replace feature workstream ownership of their own proof obligations.

It does **not** mean:

- pushing all tests to the end,
- centralizing every feature-level test in one place,
- or treating testing as a separate QA project after implementation.

Instead, this workstream creates the cross-cutting verification structure that feature workstreams plug into.

**Stable plan anchor:** `PLAN:WorkstreamG.OutOfScope`

---

## 7. Implementation Outcome Expected from This Workstream

By the end of Workstream G, Glimmer should have:

- a canonical `TEST_CATALOG.md`,
- named verification packs for smoke, workstreams, release, and data integrity,
- durable test structure across unit, integration, API, graph, Playwright, and contract layers,
- shared fixture and environment-control patterns,
- reproducible regression execution flows,
- explicit `ManualOnly` and `Deferred` handling rules,
- and an evidence model that ties implemented work back to executed proof.

At that point, Glimmer’s quality posture becomes systematic rather than ad hoc.

**Stable plan anchor:** `PLAN:WorkstreamG.ExpectedOutcome`

---

## 8. Testing and Regression Implementation Packages

## 8.1 Work Package G1 — Canonical verification document set

**Objective:** Create the primary verification control documents defined in the document set.

### In scope
- `4. Verification/TEST_CATALOG.md`
- `4. Verification/verification-pack-smoke.md`
- `4. Verification/verification-pack-workstream-a.md`
- `4. Verification/verification-pack-workstream-b.md`
- `4. Verification/verification-pack-workstream-c.md`
- `4. Verification/verification-pack-workstream-d.md`
- `4. Verification/verification-pack-workstream-e.md`
- `4. Verification/verification-pack-workstream-f.md`
- `4. Verification/verification-pack-release.md`
- `4. Verification/verification-pack-data-integrity.md`

### Expected outputs
- canonical verification document set created and aligned to `TEST:` anchors
- verification pack map aligned to build-plan workstreams
- regression-pack intent documented before full automation is complete

### Related anchors
- `ARCH:TestingArchitecture`
- `ARCH:RegressionPackModel`
- `PLAN:WorkstreamMap`

### Definition of done
- the verification area exists as a real project control surface and not just an implied future task list

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG1.VerificationDocumentSet`

---

## 8.2 Work Package G2 — Canonical `TEST:` anchor catalog and traceability model

**Objective:** Create the stable scenario catalog that ties requirements and plans to proof.

### In scope
- define canonical `TEST:` anchors
- map them to workstreams and architecture anchors
- establish scenario naming conventions
- distinguish feature-scope tests from regression-pack composition

### Expected outputs
- `TEST_CATALOG.md` with stable scenario identifiers
- first-pass traceability chain from `REQ:` → `ARCH:` → `PLAN:` → `TEST:`
- conventions for adding and evolving test anchors

### Related anchors
- `ARCH:TestingTraceabilityModel`
- `ARCH:VerificationEvidenceModel`
- `PLAN:VerificationPosture`

### Definition of done
- the project has a durable test-scenario vocabulary that future implementation and reporting can reference consistently

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG2.TestCatalogAndTraceability`

---

## 8.3 Work Package G3 — Smoke and startup proof pack

**Objective:** Implement and stabilize the minimal proof needed to show Glimmer can boot and basic surfaces function.

### In scope
- backend startup checks
- database readiness proof
- frontend shell availability
- minimal browser smoke path
- command-level pack execution support

### Expected outputs
- smoke pack document and automated implementation
- baseline execution script/command path
- evidence routine for repeated smoke verification

### Related anchors
- `ARCH:VerificationLayerModel`
- `PLAN:WorkstreamA.VerificationExpectations`
- `ARCH:TestingPrinciple.AutomationFirst`

### Definition of done
- Glimmer has a durable smoke pack that can fail fast when the baseline system breaks

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG3.SmokePack`

---

## 8.4 Work Package G4 — Domain and memory data-integrity pack

**Objective:** Prove the correctness of Glimmer’s most load-bearing state model and persistence rules.

### In scope
- relationship correctness
- accepted-vs-interpreted state separation
- provenance retention across persistence round trips
- summary refresh lineage
- audit record creation
- migration and persistence integrity checks where relevant

### Expected outputs
- data-integrity verification pack document
- automated tests for memory/state invariants
- explicit failure coverage for integrity regressions

### Related anchors
- `ARCH:DomainMemoryVerification`
- `ARCH:DataIntegrityVerificationPack`
- `PLAN:WorkstreamB.VerificationExpectations`

### Definition of done
- the domain and memory spine is protected by repeatable regression proof instead of only one-time implementation tests

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG4.DataIntegrityPack`

---

## 8.5 Work Package G5 — Connector and provenance regression pack

**Objective:** Prove that Glimmer’s external-boundary behaviors preserve meaning over time.

### In scope
- Gmail normalization proof
- Google Calendar normalization proof
- Microsoft mail/calendar normalization proof
- Telegram connector mapping proof
- manual import labeling proof
- multi-account separation proof
- connector failure and sync-state observability checks

### Expected outputs
- connector verification pack document
- contract/integration tests for connector behaviors
- repeatable fixtures/fakes for provider-specific scenarios where needed

### Related anchors
- `ARCH:ConnectorVerificationStrategy`
- `PLAN:WorkstreamC.VerificationExpectations`
- `ARCH:AccountProvenanceModel`

### Definition of done
- the connector estate is protected against provenance loss, account confusion, and normalization drift

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG5.ConnectorRegressionPack`

---

## 8.6 Work Package G6 — Graph workflow verification pack

**Objective:** Prove the orchestrated assistant-core behaviors rather than just their helper functions.

### In scope
- intake routing proof
- triage and extraction proof
- planner/focus-pack generation proof
- interrupt/resume proof
- voice and Telegram graph-adjacent continuity proof where applicable
- drafting no-auto-send boundary proof

### Expected outputs
- workstream-oriented graph verification pack(s)
- automated graph/path tests
- failure-path scenarios for ambiguity and review gating

### Related anchors
- `ARCH:GraphVerificationStrategy`
- `PLAN:WorkstreamD.VerificationExpectations`
- `PLAN:WorkstreamF.VerificationExpectations`

### Definition of done
- Glimmer’s key graph flows are protected by durable workflow-level proof, not just unit tests around helper logic

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG6.GraphWorkflowPack`

---

## 8.7 Work Package G7 — Browser workflow regression pack

**Objective:** Build durable browser-visible proof for the main operator control surface.

### In scope
- Today view flows
- Portfolio and Project navigation flows
- triage review flows
- draft workspace flows
- review queue flows
- visible provenance and accepted-vs-pending state distinctions

### Expected outputs
- Playwright workstream/release tests
- browser-pack documents aligned to user journeys
- stable selector and environment patterns for repeatable browser automation

### Related anchors
- `ARCH:PlaywrightTestBoundary`
- `PLAN:WorkstreamE.VerificationExpectations`
- `ARCH:BrowserWorkflowVerification`

### Definition of done
- the main web workspace has durable browser regression proof instead of relying on manual clicking

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG7.BrowserRegressionPack`

---

## 8.8 Work Package G8 — Voice and companion verification hardening

**Objective:** Prove the non-primary interaction modes without allowing them to escape the main control model.

### In scope
- Telegram companion verification hardening
- voice-session proof expansion
- channel handoff verification
- explicit `ManualOnly` / `Deferred` treatment for audio/device-specific checks

### Expected outputs
- workstream-f verification pack completion
- Telegram/voice-specific regression scenarios
- clear record of automated vs manual/deferred boundaries

### Related anchors
- `ARCH:TelegramVerificationStrategy`
- `ARCH:VoiceVerificationStrategy`
- `ARCH:VerificationLayer.ManualAndDeferred`

### Definition of done
- companion and voice modes are verified in a way that is honest about what is automated and what is still environment-dependent

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG8.CompanionAndVoiceVerification`

---

## 8.9 Work Package G9 — Test data, fixture, and environment control layer

**Objective:** Make the verification estate repeatable and diagnosable.

### In scope
- test data strategy
- fixture conventions
- environment assumptions documentation
- provider fakes/stubs/emulators where needed
- database reset or isolation strategy
- Playwright environment controls

### Expected outputs
- environment-control conventions
- shared fixture helpers
- explicit pack prerequisites
- reduction of flaky or environment-murky testing behavior

### Related anchors
- `ARCH:TestDataAndEnvironmentModel`
- `ARCH:VerificationLayer.Integration`
- `ARCH:TestingPrinciple.LayeredProof`

### Definition of done
- major test packs can be run reproducibly without relying on undocumented local magic

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG9.TestDataAndEnvironmentControl`

---

## 8.10 Work Package G10 — Evidence and completion routines

**Objective:** Make executed proof part of the delivery control surface rather than a private developer action.

### In scope
- evidence recording conventions
- progress-file verification summary patterns
- pass/fail/deferred/manual status handling
- release-pack evidence expectations
- completion gating rules tied to executed proof

### Expected outputs
- evidence routines documented and reusable
- progress/workstream file conventions aligned to proof status
- repeatable way to summarize verification state for human review

### Related anchors
- `ARCH:VerificationEvidenceModel`
- `ARCH:TestingPrinciple.VerificationIsImplementation`
- `PLAN:VerificationPosture`

### Definition of done
- the project has a durable way to show what was proven, what was deferred, and what still blocks confidence

**Stable plan anchor:** `PLAN:WorkstreamG.PackageG10.EvidenceAndCompletionRoutines`

---

## 9. Sequencing Inside the Workstream

The recommended internal order for Workstream G is:

1. G1 — Canonical verification document set
2. G2 — Canonical `TEST:` anchor catalog and traceability model
3. G3 — Smoke and startup proof pack
4. G4 — Domain and memory data-integrity pack
5. G5 — Connector and provenance regression pack
6. G6 — Graph workflow verification pack
7. G7 — Browser workflow regression pack
8. G8 — Voice and companion verification hardening
9. G9 — Test data, fixture, and environment control layer
10. G10 — Evidence and completion routines

This order creates the verification control surface first, then builds pack coverage from the lowest-risk baseline outward to the most cross-cutting and environment-sensitive areas.

**Stable plan anchor:** `PLAN:WorkstreamG.InternalSequence`

---

## 10. Human Dependencies

Workstream G is mostly agent-executable, but several areas require human involvement or approval.

Expected human actions include:

- approving which scenarios are acceptable as `ManualOnly` or `Deferred`,
- provisioning any environment access needed for live-integration checks,
- approving release-confidence thresholds,
- and reviewing whether the automated proof level is sufficient for the seriousness of a given feature or phase.

The coding agent should still be able to create most of the verification estate, execute local proof, and clearly surface the remaining human-dependent gaps.

**Stable plan anchor:** `PLAN:WorkstreamG.HumanDependencies`

---

## 11. Verification Expectations

Workstream G is complete only when the test and regression substrate itself is proven to be usable.

### Verification layers expected
- automated proof of representative packs actually executing
- meta-verification of traceability and evidence routines
- browser and graph pack execution sanity checks
- explicit documentation of manual/deferred gaps

### Minimum proof expectations
- verification documents exist and align to the workstream/build-plan structure
- canonical `TEST:` anchors exist for major scenarios
- smoke, data-integrity, connector, graph, browser, and release packs are defined and at least partially automated
- pack prerequisites and environment assumptions are explicit
- evidence can be captured and reported coherently
- remaining manual/deferred items are visible rather than implied

This aligns directly to the framework and companion testing standard, both of which insist that completion is evidence-backed and that automated proof should do the majority of the heavy lifting.

**Stable plan anchor:** `PLAN:WorkstreamG.VerificationExpectations`

---

## 12. Suggested Future Working Documents for This Workstream

This workstream should eventually be paired with:

- `WorkstreamG_TestingAndRegression_DESIGN_AND_IMPLEMENTATION_PLAN.md`
- `WorkstreamG_TestingAndRegression_DESIGN_AND_IMPLEMENTATION_PROGRESS.md`

Those files will hold the active verification-buildout state, pack implementation progress, evidence summaries, and remaining environment-dependent testing gaps once coding begins.

**Stable plan anchor:** `PLAN:WorkstreamG.WorkingDocumentPair`

---

## 13. Definition of Done

Workstream G should be considered complete when all of the following are true:

1. the canonical verification document set exists,
2. major `TEST:` anchors and traceability are defined,
3. smoke, data-integrity, connector, graph, browser, and release packs are established,
4. test-data and environment-control conventions are real,
5. evidence-of-completion routines are operational,
6. explicit manual/deferred handling exists where automation is not yet practical,
7. and the required execution evidence for the test estate itself has been captured.

If these are not true, Glimmer still lacks a reliable long-term proof and regression substrate, even if many individual tests exist.

**Stable plan anchor:** `PLAN:WorkstreamG.DefinitionOfDone`

---

## 14. Final Note

Workstream G is what stops Glimmer from becoming fragile as it gets smarter.

If this workstream is done well, every other workstream becomes safer to extend, refactor, and trust.
If it is done badly, the product may look complete while quietly accumulating drift, regressions, and unproven assumptions.

The right outcome is a verification estate that is boringly dependable, because that is what lets the rest of the system move fast without losing integrity.

**Stable plan anchor:** `PLAN:WorkstreamG.Conclusion`

