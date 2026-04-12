# Glimmer — Workstream E Drafting UI Design and Implementation Plan

## Document Metadata

- **Document Title:** Glimmer — Workstream E Drafting UI Design and Implementation Plan
- **Document Type:** Working Implementation Plan
- **Status:** Draft
- **Project:** Glimmer
- **Workstream:** E — Drafting UI
- **Primary Companion Documents:** Requirements, Architecture, Build Plan, Verification, Governance and Process, Global Copilot Instructions, Module Instructions, Workstream E Verification Pack

---

## 1. Purpose

This document is the active working implementation plan for **Workstream E — Drafting UI**.

Its purpose is to translate the canonical Workstream E build-plan document into an execution-ready plan that a coding agent can use during real implementation sessions.

This file should remain practical and anchored. It is not the source of architecture truth. It is the working plan for how Glimmer’s main browser workspace should be implemented, verified, and advanced slice by slice.

**Stable working anchor:** `WORKE:Plan.ControlSurface`

---

## 2. Workstream Objective

The objective of Workstream E is to implement the primary web workspace where the operator can actually use Glimmer’s outputs to make decisions, review ambiguity, compare drafts, and navigate active projects.

At the end of Workstream E, the repository should have real browser-visible support for:

- route and layout structure for the main workspace,
- Today view,
- Portfolio view,
- Project workspace,
- Triage view,
- Draft workspace,
- Review queue,
- managed persona-aware rendering,
- and the browser-visible control flows needed to keep pending, accepted, provenance-aware, and review-required states legible.

This workstream is where Glimmer starts becoming a usable operational control room instead of just a capable backend.

**Stable working anchor:** `WORKE:Plan.Objective`

---

## 3. Control Anchors in Scope

### 3.1 Requirements anchors

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

### 3.2 Architecture anchors

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

### 3.3 Build-plan anchors

- `PLAN:WorkstreamE.DraftingUi`
- `PLAN:WorkstreamE.Objective`
- `PLAN:WorkstreamE.InternalSequence`
- `PLAN:WorkstreamE.VerificationExpectations`
- `PLAN:WorkstreamE.DefinitionOfDone`

### 3.4 Verification anchors

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

**Stable working anchor:** `WORKE:Plan.ControlAnchors`

---

## 4. Execution Principles for This Workstream

### 4.1 Workspace-first, not chatbot-first

The main browser experience must be structured as a control room with distinct operating surfaces, not a generic assistant chat page.

### 4.2 Reviewability must stay visible

Pending, accepted, ambiguous, and review-required states must remain legible in the UI. Do not flatten them into one visually neat but operationally misleading surface.

### 4.3 Provenance must survive rendering

The workspace should make source/account/provenance context visible where it materially affects operator judgment. Clean UI is not an excuse to erase meaning.

### 4.4 Drafting remains review-only

The Draft workspace may support viewing, editing, comparing, and copying drafts, but it must not drift into silent or implied outbound sending.

### 4.5 Persona remains supportive, not dominant

Persona rendering should improve continuity and tone without obscuring operational content or turning the workspace into assistant theater.

### 4.6 Browser proof matters from the start

This workstream should be driven by browser-visible proof, not by assuming that correctly wired components automatically create a usable control room.

**Stable working anchor:** `WORKE:Plan.ExecutionPrinciples`

---

## 5. Workspace Shape Target for Workstream E

By the end of this workstream, the implementation should materially support the following browser workspace categories or directly equivalent concrete shapes:

- global route/layout shell
- Today surface
- Portfolio surface
- Project surface
- Triage surface
- Draft surface
- Review surface
- persona-aware rendering surfaces
- browser-visible navigation and handoff paths between these surfaces

These layers must remain legible, provenance-aware, review-safe, and Playwright-testable.

**Stable working anchor:** `WORKE:Plan.WorkspaceShapeTarget`

---

## 6. Work Packages to Execute

## 6.1 WE1 — Workspace route and layout baseline

### Objective
Implement the base route structure, layout shell, and stable navigation model for the main Glimmer control room.

### Expected touch points
- frontend route files
- layout shell
- navigation components
- browser tests

### Verification expectation
- `TEST:UI.Navigation.WorkspaceRoutesRemainReachable`

### Notes
Start with route clarity and stable page structure, not decorative polish.

**Stable working anchor:** `WORKE:Plan.PackageWE1`

---

## 6.2 WE2 — Today view

### Objective
Implement the Today surface that renders priorities, pressure signals, waiting-on items, and rationale in a way that is useful for day-to-day operation.

### Expected touch points
- Today page/component(s)
- focus-pack rendering logic
- supporting API integration
- browser/API tests

### Verification expectation
- `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly`
- `TEST:UI.TodayView.FocusArtifactsMapCleanlyToRenderedState`

### Notes
This view should feel like a chief-of-staff brief, not a generic list.

**Stable working anchor:** `WORKE:Plan.PackageWE2`

---

## 6.3 WE3 — Portfolio view

### Objective
Implement the Portfolio surface that lets the operator compare project attention demand and decide where to focus.

### Expected touch points
- Portfolio page/component(s)
- project summary rendering
- browser tests

### Verification expectation
- `TEST:UI.PortfolioView.ComparesProjectAttentionDemand`

### Notes
The operator should not need to click into every project just to discover which one matters.

**Stable working anchor:** `WORKE:Plan.PackageWE3`

---

## 6.4 WE4 — Project workspace

### Objective
Implement the Project surface so it presents synthesized context, current pressure, and relevant artifacts rather than a raw chronology dump.

### Expected touch points
- Project page/component(s)
- context panels
- summary/artifact rendering
- browser tests

### Verification expectation
- `TEST:UI.ProjectWorkspace.ShowsSynthesisNotJustChronology`
- `TEST:UI.ProjectWorkspace.ContextPanelsSupportFastOrientation`

### Notes
This surface should help the operator orient quickly around the project’s current reality.

**Stable working anchor:** `WORKE:Plan.PackageWE4`

---

## 6.5 WE5 — Triage view

### Objective
Implement the Triage surface so source provenance, ambiguity, and review controls remain visible and actionable.

### Expected touch points
- Triage page/component(s)
- triage-card rendering
- provenance display
- review controls
- browser tests

### Verification expectation
- `TEST:UI.TriageView.ShowsProvenanceAndReviewControls`
- `TEST:UI.TriageView.MultiAccountProvenanceIsVisible`

### Notes
This view is where clean design can most easily hide something important. Do not let it.

**Stable working anchor:** `WORKE:Plan.PackageWE5`

---

## 6.6 WE6 — Draft workspace

### Objective
Implement the Draft workspace for viewing, comparing, editing, and copying reviewable draft variants with sufficient context.

### Expected touch points
- Draft workspace page/component(s)
- draft comparison/selection UI
- copy/edit controls
- supporting API integration
- browser/API tests

### Verification expectation
- `TEST:UI.DraftWorkspace.ShowsContextAndVariants`
- `TEST:UI.DraftWorkspace.CopyEditFlowRemainsReviewOnly`
- `TEST:Drafting.Variants.MultipleVariantsRemainLinked`

### Notes
The workspace must make it obvious that drafts are artifacts for review, not actions already taken.

**Stable working anchor:** `WORKE:Plan.PackageWE6`

---

## 6.7 WE7 — Review queue

### Objective
Implement the Review surface where pending, accepted, rejected, amended, and deferred states can be inspected and controlled clearly.

### Expected touch points
- Review page/component(s)
- review action controls
- backend-state integration
- browser/API/integration tests

### Verification expectation
- `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious`
- `TEST:UI.ReviewQueue.ActionsReflectRealBackendState`
- `TEST:Review.AcceptAmendRejectDefer.ChangesPersistCorrectly`

### Notes
This is a real control surface, not a UI afterthought.

**Stable working anchor:** `WORKE:Plan.PackageWE7`

---

## 6.8 WE8 — Persona rendering and asset selection

### Objective
Implement bounded persona selection, rendering, and fallback behavior using managed persona assets and context mapping.

### Expected touch points
- persona rendering components
- selection helpers
- fallback behavior
- browser/unit/manual checks

### Verification expectation
- `TEST:UI.Persona.FallbackAndContextSelectionWorks`
- `TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent`

### Notes
Persona should support continuity and tone without competing with the actual task surface.

**Stable working anchor:** `WORKE:Plan.PackageWE8`

---

## 6.9 WE9 — Workspace review and safety fidelity

### Objective
Ensure the browser-visible workspace preserves no-auto-send, approval discipline, and backend-state fidelity across review and draft flows.

### Expected touch points
- workspace controls
- API integration
- browser/API/integration tests

### Verification expectation
- `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`
- `TEST:Drafting.DraftGeneration.CreatesReviewableDraft`

### Notes
This package is where the visible workspace must stay aligned to the assistant-core safety model.

**Stable working anchor:** `WORKE:Plan.PackageWE9`

---

## 7. Recommended Execution Order

The recommended execution order inside this working plan is:

1. WE1 — Workspace route and layout baseline
2. WE2 — Today view
3. WE3 — Portfolio view
4. WE4 — Project workspace
5. WE5 — Triage view
6. WE6 — Draft workspace
7. WE7 — Review queue
8. WE8 — Persona rendering and asset selection
9. WE9 — Workspace review and safety fidelity

This sequence keeps the main operating surfaces coherent while allowing browser proof to build progressively.

**Stable working anchor:** `WORKE:Plan.ExecutionOrder`

---

## 8. Expected Files and Layers Likely to Change

The initial Workstream E implementation is likely to touch files or file groups such as:

- frontend route/layout files
- workspace pages and components
- rendering helpers/selectors
- browser/Playwright tests
- supporting API integration surfaces
- persona asset rendering helpers
- Workstream E working documents

This list should be refined as implementation begins.

**Stable working anchor:** `WORKE:Plan.LikelyTouchPoints`

---

## 9. Verification Plan for Workstream E

### 9.1 Minimum required proof

At minimum, Workstream E implementation should produce executable proof for:

- workspace route/navigation reachability
- Today/Portfolio/Project rendering usefulness
- triage provenance and review visibility
- draft context and variant handling
- review queue state clarity and action fidelity
- persona selection/fallback behavior
- persona subordination to operational content
- no-auto-send and approval-discipline fidelity in the visible workspace

### 9.2 Primary verification surfaces

The main verification references for this workstream are:

- `verification-pack-workstream-e.md`
- `verification-pack-release.md` for representative release-level checks later

### 9.3 Evidence expectation

Meaningful implementation slices in this workstream should update the Workstream E progress file with:

- what was implemented
- what proof was executed
- what passed
- what failed
- what remains blocked or deferred

**Stable working anchor:** `WORKE:Plan.VerificationPlan`

---

## 10. Human Dependencies and Likely Decisions

This workstream is mostly agent-executable, but a few human decisions may still be needed.

Likely human-dependent areas include:

- confirming specific workspace layout preferences if multiple good patterns exist
- confirming how prominent persona rendering should be in edge cases
- reviewing any UI tradeoff where clarity and visual polish conflict

The coding agent should complete all safe browser and UI work before surfacing human dependencies as blockers.

**Stable working anchor:** `WORKE:Plan.HumanDependencies`

---

## 11. Known Risks in This Workstream

### 11.1 Risk — UI drifts into chatbot shape

This is the most common shortcut and would undermine the whole workspace-first product posture.

### 11.2 Risk — Pending and accepted states get flattened visually

If the operator cannot see what is settled vs unsettled, trust will degrade quickly.

### 11.3 Risk — Provenance gets hidden for visual neatness

If account/source identity is erased, decision quality will suffer even if the backend kept the data.

### 11.4 Risk — Draft UI implies action execution

If copy/edit flows blur into sending, the visible safety posture will be weakened.

### 11.5 Risk — Persona becomes theater

If persona rendering dominates the workspace or pushes critical information below the fold, the UI will drift away from its actual job.

### 11.6 Risk — Browser proof is treated as optional

This workstream is about visible operator behavior. If it is not browser-proven, it is not truly done.

**Stable working anchor:** `WORKE:Plan.Risks`

---

## 12. Immediate Next Session Recommendations

When actual coding for Workstream E begins, the first sensible execution slice is:

1. implement the workspace route/layout baseline,
2. stand up the Today view,
3. connect it to seeded or test data,
4. add the first browser proof for route reachability and Today rendering,
5. then expand into Portfolio and Project surfaces.

That slice gives the project a real browser-visible control room quickly without trying to solve every UI surface at once.

**Stable working anchor:** `WORKE:Plan.ImmediateNextSlice`

---

## 13. Definition of Ready for Workstream E Completion

Workstream E should only be considered ready for completion when all of the following are materially true:

- workspace route/layout shell is real
- Today/Portfolio/Project surfaces are real
- Triage surface is real
- Draft surface is real
- Review surface is real
- persona selection/fallback is real
- visible no-auto-send and approval fidelity is real
- and the corresponding browser/API proof paths have been executed and recorded

If these are not true, Workstream E is not done, even if the UI looks impressive.

**Stable working anchor:** `WORKE:Plan.DefinitionOfReadyForCompletion`

---

## 14. Final Note

This workstream is where Glimmer either becomes a real operator control room or stays a promising backend with a thin shell.

That is the standard here.

The goal is not to make the UI merely attractive. The goal is to make the browser workspace:

- legible,
- provenance-aware,
- review-safe,
- and operationally useful enough that it becomes the real center of daily use.

**Stable working anchor:** `WORKE:Plan.Conclusion`

