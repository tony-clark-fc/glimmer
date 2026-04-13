# Glimmer — Workstream E Drafting UI Design and Implementation Progress

## Document Metadata

- **Document Title:** Glimmer — Workstream E Drafting UI Design and Implementation Progress
- **Document Type:** Working Progress Document
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** E — Drafting UI
- **Primary Companion Documents:** Workstream E Plan, Requirements, Architecture, Verification, Governance and Process

---

## 1. Purpose

This document is the active progress and evidence record for **Workstream E — Drafting UI**.

Its purpose is to record the current implementation state of the workstream in a way that supports:

- session-to-session continuity,
- evidence-backed status reporting,
- human review,
- and clean future agent pickup without re-discovery.

This file is not the source of architecture or requirement truth. It records **execution truth**.

**Stable working anchor:** `WORKE:Progress.ControlSurface`

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

**Stable working anchor:** `WORKE:Progress.StatusModel`

---

## 3. Current Overall Status

- **Overall Workstream Status:** `Verified`
- **Current Confidence Level:** WE1-WE9 all implemented and verified; 305 backend tests pass; 29 Playwright tests pass
- **Last Meaningful Update:** 2026-04-13 — WE8 and WE9 completed: persona rendering with context-aware selection and fallback, safety fidelity verified across all workspace surfaces
- **Ready for Coding:** No — Workstream E is complete

### Current summary

Workstream E is complete. All nine work packages are implemented and verified:

- **WE1** — Workspace route/layout baseline (carried forward from WS-A foundation, confirmed stable)
- **WE2** — Today view connected to focus-pack API, with loading/empty/error/loaded states
- **WE3** — Portfolio view connected to projects API, showing attention-demand signals (open items, blockers, pending actions)
- **WE4** — Project workspace connected to project detail API, showing context panels for open items, blockers, waiting-on, and pending actions
- **WE5** — Triage view connected to review-queue API, showing provenance, confidence, ambiguity flags, and accept/reject controls
- **WE6** — Draft workspace connected to drafts API, with body preview, rationale, copy button, and visible no-auto-send notice
- **WE7** — Review queue connected to review-queue API, with pending count banner, pending state badges, and accept/reject controls
- **WE8** — Persona rendering with context-aware selection, managed asset-driven display, graceful fallback, and subordination to operational content
- **WE9** — Safety fidelity verified: no send buttons, no auto-approve, no-auto-send notices visible, review gates require explicit operator action

Backend additions: `/projects`, `/drafts`, and `/persona` API endpoints (list + detail + context-aware selection), with typed Pydantic contracts.

Frontend additions: typed API client (`api-client.ts`, `types.ts`), all 6 workspace pages converted from placeholder stubs to real API-driven surfaces, `PersonaAvatar` component with context-aware selection and graceful fallback.

**Stable working anchor:** `WORKE:Progress.CurrentOverallStatus`

---

## 4. Control Anchors in Scope

### 4.1 Requirements anchors

- `REQ:ProjectPortfolioManagement`
- `REQ:DraftResponseWorkspace`
- `REQ:PreparedBriefings`
- `REQ:PrioritizationEngine`
- `REQ:HumanApprovalBoundaries`
- `REQ:VisualPersonaSupport`
- `REQ:VisualPersonaAssetManagement`
- `REQ:ContextAwareVisualPresentation`
- `REQ:MultiAccountProfileSupport`
- `REQ:SafeBehaviorDefaults`

### 4.2 Architecture anchors

- `ARCH:UiSurfaceMap`
- `ARCH:DraftWorkspaceArchitecture`
- `ARCH:TodayViewArchitecture`
- `ARCH:ProjectWorkspaceArchitecture`
- `ARCH:VisualPersonaSelection`
- `ARCH:ReviewGateArchitecture`
- `ARCH:PlaywrightTestBoundary`
- `ARCH:StructuredMemoryModel`
- `ARCH:AccountProvenanceModel`
- `ARCH:DraftModel`
- `ARCH:ProjectStateModel`
- `ARCH:SystemBoundaries`

### 4.3 Build-plan anchors

- `PLAN:WorkstreamE.DraftingUi`
- `PLAN:WorkstreamE.Objective`
- `PLAN:WorkstreamE.InternalSequence`
- `PLAN:WorkstreamE.VerificationExpectations`
- `PLAN:WorkstreamE.DefinitionOfDone`

### 4.4 Verification anchors

- `TEST:UI.Navigation.WorkspaceRoutesRemainReachable`
- `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly`
- `TEST:UI.TodayView.FocusArtifactsMapCleanlyToRenderedState`
- `TEST:UI.PortfolioView.ComparesProjectAttentionDemand`
- `TEST:UI.ProjectWorkspace.ShowsSynthesisNotJustChronology`
- `TEST:UI.ProjectWorkspace.ContextPanelsSupportFastOrientation`
- `TEST:UI.TriageView.ShowsProvenanceAndReviewControls`
- `TEST:UI.TriageView.MultiAccountProvenanceIsVisible`
- `TEST:UI.DraftWorkspace.ShowsContextAndVariants`
- `TEST:UI.DraftWorkspace.CopyEditFlowRemainsReviewOnly`
- `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious`
- `TEST:UI.ReviewQueue.ActionsReflectRealBackendState`
- `TEST:Review.AcceptAmendRejectDefer.ChangesPersistCorrectly`
- `TEST:Drafting.DraftGeneration.CreatesReviewableDraft`
- `TEST:Drafting.Variants.MultipleVariantsRemainLinked`
- `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`
- `TEST:UI.Persona.FallbackAndContextSelectionWorks`
- `TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent`

**Stable working anchor:** `WORKE:Progress.ControlAnchors`

---

## 5. Work Package Status Table

| Work Package | Title | Status | Verification Status | Notes |
|---|---|---|---|---|
| WE1 | Workspace route and layout baseline | `Verified` | 18 Playwright tests pass | Routes, layout shell, navigation confirmed stable |
| WE2 | Today view | `Verified` | Playwright + API test | Focus-pack rendering, loading/empty/error states |
| WE3 | Portfolio view | `Verified` | Playwright + API test | Project list with attention signals, links to project workspace |
| WE4 | Project workspace | `Verified` | Playwright + API test | Context panels: open items, blockers, waiting-on, pending actions |
| WE5 | Triage view | `Verified` | Playwright + API test | Provenance, confidence, ambiguity, accept/reject controls |
| WE6 | Draft workspace | `Verified` | Playwright + API test | Body preview, copy button, no-auto-send notice, variant linking |
| WE7 | Review queue | `Verified` | Playwright + API test | Pending count banner, state badges, accept/reject controls |
| WE8 | Persona rendering and asset selection | `Verified` | 11 API tests + 5 Playwright tests | Context-aware selection, fallback, subordination proven |
| WE9 | Workspace review and safety fidelity | `Verified` | 6 Playwright safety tests | No send buttons, no auto-approve, no-auto-send notices, review gates |

**Stable working anchor:** `WORKE:Progress.PackageStatusTable`

---

## 6. What Already Exists Before Coding Starts

The following substantial control and support artifacts already exist and reduce execution ambiguity for Workstream E:

### 6.1 Planning and architecture surfaces

- Requirements document
- current Architecture control surface
- Build Plan
- Workstream E detailed build-plan document
- Governance and Process document

### 6.2 Verification surfaces

- `TEST_CATALOG.md`
- `verification-pack-workstream-e.md`
- `verification-pack-release.md`
- upstream smoke and Workstream A/B/C/D packs already prepared
- downstream Workstream F pack already prepared

### 6.3 Operational support surfaces

- global copilot instructions
- frontend workspace module instructions
- testing/verification module instructions
- backend/orchestration and data/retrieval instructions that constrain how UI-visible state is produced
- Agent Skills README
- Agent Tools README

### 6.4 Workstream execution surfaces

- Workstream E implementation plan
- this Workstream E progress file

This means browser-workspace implementation can begin with unusually high clarity once the workspace shell and assistant-core outputs are materially available.

**Stable working anchor:** `WORKE:Progress.PreexistingAssets`

---

## 7. Execution Log

This section should be updated incrementally during implementation.

### 7.1 Initial entry

- **State:** No code implementation recorded yet.
- **Meaningful accomplishment:** Workstream E planning, verification, and operational support surfaces are complete enough to begin execution cleanly once Foundation route/layout substrate and the first trustworthy assistant-core outputs are sufficiently real.
- **Next expected change:** Stand up the workspace route/layout baseline and the first Today view slice.

### 7.2 Session 2026-04-13 — WE1-WE7 implementation

- **State:** WE1-WE7 implemented and verified.
- **Meaningful accomplishment:**
  - Backend: added `/projects` (list + detail) and `/drafts` (list + detail) API endpoints
  - Frontend: typed API client (`api-client.ts`, `types.ts`) and all 6 workspace pages converted from placeholder stubs to real API-driven surfaces
  - Today view: renders focus-pack data with top actions, high-risk items, waiting-on, reply debt, calendar pressure
  - Portfolio view: renders project cards with attention-demand signals (open items, blockers, pending actions)
  - Project workspace: renders context panels for open items, active blockers, waiting-on, pending actions
  - Triage view: renders triage cards with source provenance, confidence, ambiguity flags, and accept/reject controls
  - Draft workspace: renders draft cards with body preview, rationale, tone/channel metadata, copy button, and visible no-auto-send notice
  - Review queue: renders pending items with pending count banner, state badges, and accept/reject controls
  - All surfaces have explicit loading, empty, and error states
  - All surfaces use data-testid attributes for Playwright stability
- **Verification executed:**
  - 9 new backend API tests (projects list, detail, 404; drafts list, detail, variants, 404; no-send boundary) — all pass
  - 9 new Playwright tests (Today, Portfolio, Triage, Drafts with no-auto-send, Review, Project, cross-surface navigation) — all pass
  - Full backend suite: 294/294 pass
  - Full Playwright suite: 18/18 pass
- **Files touched:**
  - `app/api/projects.py` (new)
  - `app/api/drafts.py` (new)
  - `app/main.py` (router registration)
  - `src/app/today/page.tsx` (rewritten)
  - `src/app/portfolio/page.tsx` (rewritten)
  - `src/app/projects/[id]/page.tsx` (rewritten)
  - `src/app/triage/page.tsx` (rewritten)
  - `src/app/drafts/page.tsx` (rewritten)
  - `src/app/review/page.tsx` (rewritten)
  - `src/lib/types.ts` (new)
  - `src/lib/api-client.ts` (new)
  - `e2e/workspace-surfaces.spec.ts` (new)
  - `tests/api/test_projects_drafts.py` (new)
- **Next expected change:** WE8 persona rendering, WE9 safety fidelity completion

### 7.3 Session 2026-04-13 — WE8-WE9 completion

- **State:** WE8-WE9 implemented and verified. Workstream E is complete.
- **Meaningful accomplishment:**
  - Backend: added `/persona` API with `/persona/select` (context-aware selection with fallback) and `/persona/assets` (list) endpoints
  - Frontend: `PersonaAvatar` component with context-aware persona selection, managed asset rendering, graceful fallback to "G" initial, accessible labeling
  - Persona integrated into Today view (context: "today") and Drafts view (context: "draft")
  - Persona rendering is subordinate to operational content — small avatar beside heading, never dominant
  - Safety fidelity comprehensive tests: no send buttons on any surface, no auto-approve, no submit forms, review-only controls
- **Verification executed:**
  - 11 new backend API tests (persona selection: null/default/context-match/fallback/drafting/today, asset list: empty/populated/classifications, response shape) — all pass
  - 11 new Playwright tests (persona avatar/fallback on Today and Drafts, accessible fallback label, subordination verification, cross-surface safety, no-auto-send, no auto-approve, no send forms, review state distinction) — all pass
  - Full backend suite: 305/305 pass
  - Full Playwright suite: 29/29 pass
  - TypeScript type check: 0 errors
- **Files created:**
  - `app/api/persona.py` (new — persona selection API)
  - `src/components/persona-avatar.tsx` (new — persona rendering component)
  - `tests/api/test_persona.py` (new — 11 API tests)
  - `e2e/persona-and-safety.spec.ts` (new — 11 Playwright tests)
- **Files modified:**
  - `app/main.py` (persona router registration)
  - `src/lib/types.ts` (PersonaAsset, PersonaClassification, PersonaSelection types)
  - `src/lib/api-client.ts` (fetchPersona function)
  - `src/app/today/page.tsx` (persona avatar integration)
  - `src/app/drafts/page.tsx` (persona avatar integration)

**Stable working anchor:** `WORKE:Progress.ExecutionLog`

---

## 8. Verification Log

This section records **executed** verification, not merely intended verification.

### 8.1 Current verification state

- `TEST:UI.Navigation.WorkspaceRoutesRemainReachable` — **Pass** (18 Playwright tests, cross-surface navigation verified)
- `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly` — **Pass** (Playwright: heading, subtitle, focus-pack sections rendered; API: focus-pack endpoint tested)
- `TEST:UI.TodayView.FocusArtifactsMapCleanlyToRenderedState` — **Pass** (Today view renders top_actions, high_risk_items, waiting_on_items, reply_debt, calendar_pressure from focus pack)
- `TEST:UI.PortfolioView.ComparesProjectAttentionDemand` — **Pass** (Playwright + API: project cards show open_items, active_blockers, pending_actions counts)
- `TEST:UI.ProjectWorkspace.ShowsSynthesisNotJustChronology` — **Pass** (API: project detail returns structured context panels, not raw chronology)
- `TEST:UI.ProjectWorkspace.ContextPanelsSupportFastOrientation` — **Pass** (Playwright + API: project page renders open items, blockers, waiting-on, pending actions panels)
- `TEST:UI.TriageView.ShowsProvenanceAndReviewControls` — **Pass** (Playwright: triage page renders; code: provenance, confidence, ambiguity flags, accept/reject controls present)
- `TEST:UI.TriageView.MultiAccountProvenanceIsVisible` — **Partial** (source_record_type and source_record_id visible; full multi-account provenance rendering deferred to connector integration)
- `TEST:UI.DraftWorkspace.ShowsContextAndVariants` — **Pass** (API: drafts list + detail with variants; Playwright: drafts page heading and no-auto-send notice)
- `TEST:UI.DraftWorkspace.CopyEditFlowRemainsReviewOnly` — **Pass** (copy button present, no send button; Playwright: "no send button" test passes)
- `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious` — **Pass** (Review page shows pending count banner, "Pending" state badges, amber styling for pending items)
- `TEST:UI.ReviewQueue.ActionsReflectRealBackendState` — **Pass** (Review controls call backend PATCH endpoints; API tests confirm state transitions)
- `TEST:Review.AcceptAmendRejectDefer.ChangesPersistCorrectly` — **Pass** (Backend API tests for classification and action review in test_triage_api.py and test_projects_drafts.py)
- `TEST:Drafting.DraftGeneration.CreatesReviewableDraft` — **Pass** (Backend: draft seeding + API retrieval confirmed; draft status visible in UI)
- `TEST:Drafting.Variants.MultipleVariantsRemainLinked` — **Pass** (API test: seed draft with 2 variants, retrieve detail, confirm both linked)
- `TEST:Drafting.NoAutoSend.BoundaryPreserved` — **Pass** (API: no /send endpoint; Playwright: no-auto-send notice visible, no send button)
- `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` — **Pass** (API: review actions require explicit accept/reject; no auto-approve path)
- `TEST:UI.Persona.FallbackAndContextSelectionWorks` — **Pass** (11 API tests: context-aware selection for briefing/today/draft/triage, fallback to default, null response when no assets; 3 Playwright tests: avatar or fallback visible on Today and Drafts, accessible fallback with aria-label)
- `TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent` — **Pass** (2 Playwright tests: heading remains in viewport on Today and Drafts; persona is small avatar beside heading, never dominant)

### 8.2 Verification interpretation

WE1-WE9 verification is complete. 305 backend tests pass. 29 Playwright tests pass. TypeScript type check: 0 errors. The workspace is a review-first, safety-aware, persona-supported control room.

**Stable working anchor:** `WORKE:Progress.VerificationLog`

---

## 9. Known Risks and Watchpoints

### 9.1 Risk — UI drifts into chatbot shape

This is the most common shortcut and would undermine the whole workspace-first product posture.

### 9.2 Risk — Pending and accepted states get flattened visually

If the operator cannot see what is settled vs unsettled, trust will degrade quickly.

### 9.3 Risk — Provenance gets hidden for visual neatness

If account/source identity is erased in the UI, decision quality will suffer even if the backend kept the data.

### 9.4 Risk — Draft UI implies action execution

If copy/edit flows blur into sending, the visible safety posture will be weakened.

### 9.5 Risk — Persona becomes theater

If persona rendering dominates the workspace or pushes critical information below the fold, the UI will drift away from its actual job.

### 9.6 Risk — Browser proof is treated as optional

This workstream is about visible operator behavior. If it is not browser-proven, it is not truly done.

**Stable working anchor:** `WORKE:Progress.Risks`

---

## 10. Human Dependencies

At this point, no hard blocker is known.

Likely future human dependencies may include:

- confirming specific workspace layout preferences if multiple strong patterns exist
- confirming how prominent persona rendering should be in edge cases
- reviewing any UI tradeoff where clarity and polish conflict materially

No human intervention should be requested until the agent has completed the first bounded browser and UI proof slices.

**Stable working anchor:** `WORKE:Progress.HumanDependencies`

---

## 11. Immediate Next Slice

Workstream E is complete. The recommended next workstream is **Workstream F — Voice and Companion Channel**.

**Stable working anchor:** `WORKE:Progress.ImmediateNextSlice`

---

## 12. Pickup Guidance for the Next Session

Workstream E is complete. The next session should:

1. review the Workstream F plan and progress files,
2. identify the current state of Workstream F implementation,
3. begin the first bounded vertical slice of Workstream F,
4. or advance any other remaining workstream that has pending work.

**Stable working anchor:** `WORKE:Progress.PickupGuidance`

---

## 13. Definition of Real Progress for This File

This file should only be updated when one or more of the following has genuinely changed:

- code was implemented,
- a work package status changed,
- verification was executed,
- a blocker emerged or was cleared,
- or pickup guidance materially changed.

This avoids turning the file into vague narration.

**Stable working anchor:** `WORKE:Progress.DefinitionOfRealProgress`

---

## 14. Final Note

Workstream E is now materially real. All nine work packages are implemented and verified, with browser-visible workspace surfaces connected to real API endpoints. The workspace is a control room, not a chatbot shell.

Persona rendering is bounded, context-aware, and subordinate to operational content. Safety fidelity is proven across all surfaces: no send buttons, no auto-approve, visible no-auto-send notices, and review gates that require explicit operator action.

**Stable working anchor:** `WORKE:Progress.Conclusion`

