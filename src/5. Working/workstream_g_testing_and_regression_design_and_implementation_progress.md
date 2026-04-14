# Glimmer — Workstream G Testing and Regression Design and Implementation Progress

## Document Metadata

- **Document Title:** Glimmer — Workstream G Testing and Regression Design and Implementation Progress
- **Document Type:** Working Progress Document
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** G — Testing and Regression
- **Primary Companion Documents:** Workstream G Plan, Requirements, Architecture, Verification, Governance and Process

---

## 1. Purpose

This document is the active progress and evidence record for **Workstream G — Testing and Regression**.

Its purpose is to record the current implementation state of the workstream in a way that supports:

- session-to-session continuity,
- evidence-backed status reporting,
- human review,
- and clean future agent pickup without re-discovery.

This file is not the source of architecture or requirement truth. It records **execution truth**.

**Stable working anchor:** `WORKG:Progress.ControlSurface`

---

## 2. Status Model

The following status vocabulary should be used consistently in this file.

- `Designed`
- `InProgress`
- `Implemented`
- `Verified`
- `Blocked`
- `HumanReviewRequired`
- `Deferred`

A work item should not be treated as complete merely because code exists. Verification status must be recorded explicitly.

**Stable working anchor:** `WORKG:Progress.StatusModel`

---

## 3. Current Overall Status

- **Overall Workstream Status:** `Verified`
- **Current Confidence Level:** All 8 work packages implemented and verified; 493 total backend tests pass (451 pre-H + 42 new Workstream H); all pack markers operational; evidence tooling functional
- **Last Meaningful Update:** 2026-04-14 — WG1-WG8 implementation complete; workstream_h marker added for H-series tests
- **Ready for Coding:** Complete — all work packages verified

### Current summary

Workstream G has been implemented. The verification estate is now operational:

- **WG1** — Core test harness baseline: pytest markers registered for all 11 pack types via `conftest.py` `pytest_configure` hook; programmatic marker application via `pytest_collection_modifyitems` maps 43 test files to their workstream/pack markers without modifying test source
- **WG2** — TEST: anchor traceability: `tests/tools/anchor_scanner.py` scans test files for TEST: anchor references and maps against the canonical test catalog; generates coverage report showing 40/59 catalog anchors covered, 19 missing (mostly Workstream H deep research and future UI anchors), 38 additional test-only anchors
- **WG3** — Smoke pack: `pytest -m smoke` runs 5 backend smoke tests; Playwright browser tests cover frontend starts and workspace navigation
- **WG4** — Workstream pack execution: all workstream packs (A–F) runnable via `pytest -m workstream_X`; data_integrity and release packs also runnable; all pack counts verified
- **WG5** — Data-integrity regression: 10 new cross-cutting tests in `test_data_integrity_pack.py` — source-layer distinctness, accepted-state promotion with origin trace, summary accumulation, multi-account provenance persistence, global auto_send_blocked enforcement
- **WG6** — Release pack: `pytest -m release` composes 139 representative tests from across all workstreams + data integrity + smoke; all pass
- **WG7** — Evidence collection: `tests/tools/evidence_report.py` runs any pack via pytest, captures JUnit XML, and generates Markdown evidence summaries in `tests/evidence/`
- **WG8** — ManualOnly/Deferred discipline: `tests/tools/manual_deferred.yaml` registry tracks 6 manual-only and deferred scenarios (frontend/browser, live OAuth, Telegram bot, real audio); evidence reports include these in output

**Stable working anchor:** `WORKG:Progress.CurrentOverallStatus`

---

## 4. Control Anchors in Scope

### 4.1 Requirements anchors

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

### 4.2 Architecture anchors

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

### 4.3 Build-plan anchors

- `PLAN:WorkstreamG.TestingAndRegression`
- `PLAN:WorkstreamG.Objective`
- `PLAN:WorkstreamG.InternalSequence`
- `PLAN:WorkstreamG.VerificationExpectations`
- `PLAN:WorkstreamG.DefinitionOfDone`

### 4.4 Verification anchors

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

**Stable working anchor:** `WORKG:Progress.ControlAnchors`

---

## 5. Work Package Status Table

| Work Package | Title | Status | Verification Status | Notes |
|---|---|---|---|---|
| WG1 | Core test harness baseline | `Verified` | 11 markers registered, 43 files mapped, 451 tests collect cleanly | Programmatic via conftest.py |
| WG2 | `TEST:` anchor traceability support | `Verified` | 40/59 catalog anchors covered, report generates correctly | `tests/tools/anchor_scanner.py` |
| WG3 | Smoke and foundational pack execution routines | `Verified` | 5 smoke tests pass via `pytest -m smoke`; Playwright smoke exists | `run_pack.sh smoke` works |
| WG4 | Workstream pack execution hardening | `Verified` | All 9 pack markers (A–F + data_integrity + release + smoke) execute correctly | Pack counts match expectations |
| WG5 | Data-integrity regression surface | `Verified` | 10 new tests pass — source distinctness, promotion trace, summary accumulation, provenance, auto_send | `test_data_integrity_pack.py` |
| WG6 | Release-pack execution routine | `Verified` | 139 release-pack tests pass (representative cross-system) | `pytest -m release` |
| WG7 | Evidence collection and reporting support | `Verified` | Evidence reports generate for smoke and release packs | `tests/tools/evidence_report.py` |
| WG8 | `ManualOnly` and `Deferred` discipline | `Verified` | 6 scenarios registered in manual_deferred.yaml; included in evidence output | `tests/tools/manual_deferred.yaml` |

**Stable working anchor:** `WORKG:Progress.PackageStatusTable`

---

## 6. What Already Exists Before Coding Starts

The following substantial control and support artifacts already exist and reduce execution ambiguity for Workstream G:

### 6.1 Planning and architecture surfaces

- Requirements document
- current Architecture control surface
- Build Plan
- Governance and Process document
- Workstream G implementation plan

### 6.2 Verification surfaces

- `TEST_CATALOG.md`
- `verification-pack-smoke.md`
- `verification-pack-workstream-a.md`
- `verification-pack-workstream-b.md`
- `verification-pack-workstream-c.md`
- `verification-pack-workstream-d.md`
- `verification-pack-workstream-e.md`
- `verification-pack-workstream-f.md`
- `verification-pack-data-integrity.md`
- `verification-pack-release.md`

### 6.3 Operational support surfaces

- global copilot instructions
- testing/verification module instructions
- backend/orchestration instructions
- frontend workspace instructions
- data/retrieval instructions
- connectors instructions
- voice/companion instructions
- Agent Skills README
- Agent Tools README

### 6.4 Workstream execution surfaces

- this Workstream G progress file
- Workstream A–F plan/progress pairs already prepared

This means Testing and Regression can begin with unusually high clarity once enough real implementation exists to prove.

**Stable working anchor:** `WORKG:Progress.PreexistingAssets`

---

## 7. Execution Log

This section should be updated incrementally during implementation.

### 7.1 Initial entry

- **State:** No code implementation recorded yet.
- **Meaningful accomplishment:** Workstream G planning, verification design, and operational support surfaces are complete enough to begin execution cleanly once the first real product slices exist.
- **Next expected change:** Stand up the core test harness baseline and make the smoke pack executable.

### 7.2 Session 2026-04-14 — WG1-WG8 implementation

- **State:** WG1-WG8 implemented and verified.
- **Meaningful accomplishment:**
  - **WG1 — Core test harness baseline**: Registered 11 verification-pack markers (`smoke`, `workstream_a` through `workstream_f`, `data_integrity`, `release`, `manual_only`, `deferred`) in both `pyproject.toml` and via `pytest_configure` hook in `conftest.py`. Added `pytest_collection_modifyitems` that programmatically assigns markers to all 43 test files based on a file-to-pack mapping — no test files need modification.
  - **WG2 — TEST: anchor traceability**: Created `tests/tools/anchor_scanner.py` that scans all test files for `TEST:` anchor references and cross-references against the canonical test catalog. Produces a Markdown coverage report. Current coverage: 40/59 catalog anchors covered by implementing tests.
  - **WG3 — Smoke pack**: Smoke tests are now runnable via `pytest -m smoke` (5 backend tests). Browser smoke exists in Playwright. Created `tests/tools/run_pack.sh` convenience runner.
  - **WG4 — Workstream pack execution**: All workstream packs runnable via `pytest -m workstream_X`. Pack sizes: A=7, B=88, C=93, D=73, E=44, F=136, data_integrity=41, release=139, smoke=5.
  - **WG5 — Data-integrity regression**: Created `tests/integration/test_data_integrity_pack.py` with 10 cross-cutting tests: source-layer distinctness (message/thread/event/signal separation), accepted-state promotion retaining origin trace, summary supersession preserving history, multi-account provenance persistence, and global auto_send_blocked enforcement.
  - **WG6 — Release-pack execution**: Release pack composed from representative tests across all workstreams + data integrity + smoke. 139 tests pass via `pytest -m release`.
  - **WG7 — Evidence collection**: Created `tests/tools/evidence_report.py` that runs any pack, captures JUnit XML, and generates human-readable Markdown evidence (date, pack name, pass/fail/skip counts, per-test table, manual/deferred scenarios).
  - **WG8 — ManualOnly/Deferred discipline**: Created `tests/tools/manual_deferred.yaml` tracking 6 scenarios that cannot yet be automated (frontend Playwright, live Google/Microsoft OAuth, Telegram bot, real audio pipeline). Evidence reports incorporate these for honest visibility.
- **Verification executed:**
  - Full backend suite: 451/451 pass (441 existing + 10 new data-integrity)
  - Smoke pack: 5/5 pass via `pytest -m smoke`
  - All workstream packs: verified individually
  - Data-integrity pack: 10/10 pass via `pytest -m data_integrity`
  - Release pack: 139/139 pass via `pytest -m release`
  - Anchor scanner: 40/59 catalog anchors covered
  - Evidence report: generates correctly for smoke and release packs
- **Files created:**
  - `tests/conftest.py` (major enhancement — marker registration and file-to-pack mapping)
  - `tests/integration/test_data_integrity_pack.py` (new — 10 cross-cutting integrity tests)
  - `tests/tools/__init__.py` (new — tools package)
  - `tests/tools/anchor_scanner.py` (new — TEST: anchor traceability scanner)
  - `tests/tools/evidence_report.py` (new — evidence collection and reporting)
  - `tests/tools/manual_deferred.yaml` (new — ManualOnly/Deferred registry)
  - `tests/tools/run_pack.sh` (new — pack runner convenience script)
  - `tests/evidence/` (new directory — evidence report output)
- **Files modified:**
  - `apps/backend/pyproject.toml` (marker registration in pytest config)
  - `tests/api/test_voice_api.py` (re-added WF7/WF8 handoff API tests)
  - `tests/api/test_telegram_api.py` (re-added WF7/WF8 handoff + pending API tests)
- **Next expected change:** Workstream G is complete. Remaining work is Workstream H (Deep Research), which is blocked on C# source code provision.

**Stable working anchor:** `WORKG:Progress.ExecutionLog`

---

## 8. Verification Log

This section records **executed** verification, not merely intended verification.

### 8.1 Current verification state

- `TESTCATALOG:ControlSurface` — **Operational** (40/59 anchors covered by implementing tests; scanner generates live report)
- `TESTPACK:Smoke.ControlSurface` — **Pass** (5 backend tests via `pytest -m smoke`; Playwright browser tests separate)
- `TESTPACK:WorkstreamA.ControlSurface` — **Pass** (7 tests via `pytest -m workstream_a`)
- `TESTPACK:WorkstreamB.ControlSurface` — **Pass** (88 tests via `pytest -m workstream_b`)
- `TESTPACK:WorkstreamC.ControlSurface` — **Pass** (93 tests via `pytest -m workstream_c`)
- `TESTPACK:WorkstreamD.ControlSurface` — **Pass** (73 tests via `pytest -m workstream_d`)
- `TESTPACK:WorkstreamE.ControlSurface` — **Pass** (44 tests via `pytest -m workstream_e`)
- `TESTPACK:WorkstreamF.ControlSurface` — **Pass** (136 tests via `pytest -m workstream_f`)
- `TESTPACK:DataIntegrity.ControlSurface` — **Pass** (41 tests via `pytest -m data_integrity` — 10 new + 31 cross-tagged)
- `TESTPACK:Release.ControlSurface` — **Pass** (139 representative tests via `pytest -m release`)

### 8.2 Verification interpretation

WG1-WG8 verification is complete. The test estate is now operational with marker-driven pack execution, anchor traceability, data-integrity regression, release-pack composition, evidence reporting, and honest ManualOnly/Deferred tracking. Full backend suite: 451/451 pass.

**Stable working anchor:** `WORKG:Progress.VerificationLog`

---

## 9. Known Risks and Watchpoints

### 9.1 Risk — Verification remains on paper only

This is the biggest risk in the workstream. A beautifully authored pack set that is not executable creates false confidence.

### 9.2 Risk — Coverage theater replaces scenario truth

If the workstream chases counts instead of meaningful confidence, the estate will look stronger than it is.

### 9.3 Risk — Pack execution becomes too heavy to run routinely

If smoke, workstream, data-integrity, or release routines are too bloated, they will be neglected.

### 9.4 Risk — Evidence capture is too vague

If outputs are hard to interpret, human decision-makers will still be forced to reconstruct confidence manually.

### 9.5 Risk — `ManualOnly` and `Deferred` discipline becomes dishonest

If these categories are hidden or blurred, release confidence will become unreliable.

**Stable working anchor:** `WORKG:Progress.Risks`

---

## 10. Human Dependencies

At this point, no hard blocker exists. All automated verification infrastructure is operational.

Remaining human-dependent items:

- Playwright browser tests require manual execution (Next.js dev server must be running)
- Live OAuth tests require Google/Microsoft app registration and credentials
- Telegram bot tests require bot provisioning
- Real audio pipeline tests require MLX + Gemma 4 on target hardware
- Evidence report format may need human review for preferred styling

**Stable working anchor:** `WORKG:Progress.HumanDependencies`

---

## 11. Immediate Next Slice

Workstream G is complete. All 8 work packages are implemented and verified.

Remaining work:
1. **Workstream H (Deep Research)** is the last remaining workstream — blocked on C# source code provision
2. Future enhancements:
   - CI/CD integration (GitHub Actions wiring for pack execution)
   - More data-integrity scenarios as the system evolves
   - Release evidence report formatting refinements

**Stable working anchor:** `WORKG:Progress.ImmediateNextSlice`

---

## 12. Pickup Guidance for the Next Session

When the next session begins:

1. **Note that WG1-WG8 are complete and verified** (451/451 tests pass).
2. Run `pytest tests/ -q` to confirm baseline.
3. Run `python tests/tools/anchor_scanner.py` to check traceability.
4. Use `python tests/tools/evidence_report.py <pack>` to generate evidence.
5. If adding new tests, update the `_FILE_PACK_MAP` in `conftest.py`.
6. If adding new TEST: anchors, update the test catalog and re-run the scanner.

**Stable working anchor:** `WORKG:Progress.PickupGuidance`

---

## 13. Definition of Real Progress for This File

This file should only be updated when one or more of the following has genuinely changed:

- code or harness logic was implemented,
- a work package status changed,
- executable verification was run,
- a blocker emerged or was cleared,
- or pickup guidance materially changed.

This avoids turning the file into vague narration.

**Stable working anchor:** `WORKG:Progress.DefinitionOfRealProgress`

---

## 14. Final Note

Workstream G is complete. The verification estate is operational:

- 11 markers registered, 43 test files mapped to packs
- 451 backend tests pass
- 9 pack-based execution commands work (smoke, workstream_a–f, data_integrity, release)
- Anchor traceability: 40/59 catalog anchors covered
- Evidence reporting generates structured Markdown summaries
- ManualOnly/Deferred scenarios are tracked honestly

The test estate is executable, traceable, honest, and strong enough that real release decisions can be made from it.

**Stable working anchor:** `WORKG:Progress.Conclusion`

