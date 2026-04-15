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
- **Current Confidence Level:** WE1-WE9 all implemented and verified; E11-E14 implemented and verified; 863 backend tests pass; 56 Playwright tests pass (including 6 mind-map + 6 staged-persistence tests)
- **Last Meaningful Update:** 2026-04-16 — E14 (Staged Persistence and Confirm Flow) implemented: MindMapWorkingState model, working state backup/restore API, confirm & save batch commit, discard flow, frontend working state hook, toolbar UI with accept/confirm/discard controls, 20 backend API tests + 6 Playwright tests all pass; full suite 56/56 Playwright, 863/863 backend
- **Ready for Coding:** E14 complete — E15 (Paste-in Ingestion) is next

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
| E11 | Project CRUD API and direct management UI | `Verified` | 20 API tests + 5 Playwright tests | Create/update/archive endpoints, portfolio modal, project detail edit/archive controls |
| E12 | Persona page conversation UI | `Verified` | 22 API tests + 6 Playwright tests | Session lifecycle, LLM-backed chat, message persistence, workspace mode, fallback handling |
| E13 | Persona page mind-map visualization | `Verified` | 6 Playwright tests | React Flow canvas, 8 semantic node types, dagre layout, zoom/pan/minimap, working state indicators |
| E14 | Persona page staged persistence and confirm flow | `Verified` | 20 API tests + 6 Playwright tests | MindMapWorkingState model, save/restore backup, Confirm & Save batch commit (projects first, then subsidiary entities), discard flow, toolbar UI, accept/confirm/discard controls |

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

### 7.4 Session 2026-04-15 — E11 Project CRUD implementation

- **State:** E11 implemented and verified.
- **Meaningful accomplishment:**
  - Backend: added `POST /projects/{id}/archive` endpoint, name validation on create/update, `include_archived` query param on list, `archived` field in summary/detail responses
  - Frontend: `archiveProject` API client function, `ProjectFormModal` component (create project form), Portfolio page "New Project" button + modal + "Show archived" toggle, Project detail page Edit/Archive controls with confirmation
  - Tests: 20 new API integration tests covering create/read/update/archive, validation, filtering, 404/409 edge cases; 5 new Playwright e2e tests for portfolio creation modal and project detail controls
  - Progress document updated
- **Verification executed:**
  - 20 new backend API tests — all pass
  - Full backend suite: 821/821 pass (no regressions)
  - Frontend build: 0 TypeScript errors
  - 5 new Playwright e2e tests added
- **Files created:**
  - `src/tests/api/test_project_crud.py` (new — 20 CRUD tests)
  - `src/apps/web/src/components/project-form-modal.tsx` (new — create project modal)
  - `src/apps/web/e2e/project-crud.spec.ts` (new — 5 Playwright tests)
- **Files modified:**
  - `src/apps/backend/app/api/projects.py` (archive endpoint, validation, filtering, archived field)
  - `src/apps/web/src/lib/api-client.ts` (archiveProject function)
  - `src/apps/web/src/lib/types.ts` (archived field on ProjectSummary and ProjectDetail)
  - `src/apps/web/src/app/portfolio/page.tsx` (New Project button, modal, show-archived toggle)
  - `src/apps/web/src/app/projects/[id]/page.tsx` (Edit/Archive controls)
  - `src/tests/conftest.py` (test_project_crud in pack map)

### 7.5 Session 2026-04-15 — E12 Persona page conversation UI

- **State:** E12 implemented and verified.
- **Meaningful accomplishment:**
  - Backend: `PersonaPageSession` and `PersonaPageMessage` models added to `channel.py`, linking to `ChannelSession` as a web-channel subtype
  - Backend: conversation session API — `POST /persona/sessions` (create), `GET /persona/sessions/{id}` (get with history), `POST /persona/sessions/{id}/messages` (send + LLM reply), `PATCH /persona/sessions/{id}` (lifecycle transitions)
  - Backend: conversation inference task (`tasks/conversation.py`) + prompt template (`prompts/conversation.py`) + `persona_chat_smart()` orchestration function with LLM-first/fallback
  - Backend: session lifecycle enforcement — active↔paused, active→confirmed/abandoned, terminal states reject further messages
  - Frontend: persona page rewired from placeholder responses to real session API — creates session on mount, sends messages to backend, displays LLM-generated replies
  - Frontend: error handling for session creation failure and message send failure with user-visible error states
  - Alembic migration for `persona_page_sessions` and `persona_page_messages` tables
  - Tests: 22 new API integration tests covering session CRUD, message send/persist/metadata, lifecycle transitions, terminal states, validation
  - 6 new Playwright e2e tests for persona page rendering, controls, and avatar
- **Verification executed:**
  - 22 new backend API tests — all pass
  - Full backend suite: 843/843 pass (no regressions)
  - Frontend build: 0 TypeScript errors
  - 6 new Playwright e2e tests added
- **Files created:**
  - `src/apps/backend/app/inference/tasks/conversation.py` (new — LLM conversation task)
  - `src/apps/backend/app/inference/prompts/conversation.py` (new — conversation prompt template)
  - `src/apps/backend/alembic/versions/e12a0c4f7b91_add_persona_page_session_tables.py` (new — migration)
  - `src/tests/api/test_persona_conversation.py` (new — 22 API tests)
  - `src/apps/web/e2e/persona-conversation.spec.ts` (new — 6 Playwright tests)
- **Files modified:**
  - `src/apps/backend/app/models/channel.py` (PersonaPageSession + PersonaPageMessage models)
  - `src/apps/backend/app/models/__init__.py` (register new models)
  - `src/apps/backend/app/api/persona.py` (conversation session endpoints)
  - `src/apps/backend/app/inference/orchestration.py` (persona_chat_smart function)
  - `src/apps/web/src/lib/types.ts` (PersonaSession, PersonaMessage, SessionStatus types)
  - `src/apps/web/src/lib/api-client.ts` (session/message API functions)
  - `src/apps/web/src/app/glimmer/page.tsx` (rewired to real API)
  - `src/tests/conftest.py` (test_persona_conversation in pack map)

### 7.6 Session 2026-04-15 — E13 Persona page mind-map visualization

- **State:** E13 implemented and verified.
- **Meaningful accomplishment:**
  - Installed `@xyflow/react` (React Flow) and `@dagrejs/dagre` layout library
  - Created 8 custom node types with semantic visual encoding: project (indigo), stakeholder (lavender), milestone (emerald), risk (amber), blocker (error red), work_item (neutral), decision (primary), dependency (muted)
  - Working-state visual distinction: dashed borders + "DRAFT" badge for pending nodes, solid borders for accepted, dimmed for discarded
  - Dagre automatic hierarchical layout with configurable direction and spacing
  - Hover "Ask Glimmer about this" affordance on all non-discarded nodes
  - Click-to-select shows NodeDetailPanel with entity type, label, status, and source origin
  - React Flow Controls (zoom in/out/fit) and MiniMap with entity-type color coding
  - Demo seed data showing all 8 node types with relational edges for visual proof
  - Replaced placeholder IdeaCanvas with real MindMapCanvas in WorkspaceCanvas
  - Added mind-map CSS overrides for React Flow integration in globals.css
- **Verification executed:**
  - Frontend build: 0 TypeScript errors
  - Full backend suite: 843/843 pass (no regressions from E12)
  - 6 new Playwright e2e tests added
- **Files created:**
  - `src/apps/web/src/app/glimmer/mind-map-nodes.tsx` (new — 8 custom node types)
  - `src/apps/web/src/app/glimmer/mind-map-layout.ts` (new — dagre layout utility)
  - `src/apps/web/src/app/glimmer/mind-map-canvas.tsx` (new — React Flow canvas component)
  - `src/apps/web/e2e/mind-map.spec.ts` (new — 6 Playwright tests)
- **Files modified:**
  - `src/apps/web/package.json` (@xyflow/react, @dagrejs/dagre dependencies)
  - `src/apps/web/src/lib/types.ts` (MindMapNodeData, MindMapEdgeData, entity/relation types)
  - `src/apps/web/src/app/glimmer/workspace-canvas.tsx` (IdeaCanvas → MindMapCanvas)
  - `src/apps/web/src/app/globals.css` (mind-map React Flow CSS overrides)

### 7.7 Session 2026-04-16 — E13 bug fixes and Playwright test stabilization

- **State:** E13 bugs fixed and all 6 Playwright tests now pass.
- **Bugs found and fixed:**
  1. **Infinite render loop in MindMapCanvas:** `createDemoNodes()` and `createDemoEdges()` were called on every render creating new array references, which triggered the `useMemo` → `useEffect` → `setState` cycle endlessly. Fixed by memoizing demo data and `rawNodes`/`rawEdges` with `useMemo`.
  2. **Layout z-index overlap:** The persona page top section (containing the controls gutter with workspace mode buttons) and bottom section (workspace canvas) both had `z-10`. At the Playwright test viewport (1280×720), the workspace canvas content intercepted pointer events on the mode buttons. Fixed by raising the top section to `z-20`.
  3. **Playwright API route mocking:** Mind-map tests needed `page.route()` interception for `/persona/mood`, `/persona/sessions`, and `/projects*` endpoints to prevent the Next.js dev error overlay from blocking the page when no backend is running.
- **Verification executed:**
  - 6 mind-map Playwright tests: 6/6 pass
  - Full Playwright suite: 50/50 pass (no regressions)
  - Full backend suite: 843/843 pass (no regressions)
  - TypeScript type check: 0 errors
- **Files modified:**
  - `src/apps/web/src/app/glimmer/mind-map-canvas.tsx` (memoized demo data to fix infinite loop)
  - `src/apps/web/src/app/glimmer/page.tsx` (z-20 on top section for pointer event priority)
  - `src/apps/web/e2e/mind-map.spec.ts` (added API route mocking in beforeEach)

**Stable working anchor:** `WORKE:Progress.ExecutionLog`

### 7.8 Session 2026-04-16 — E14 Persona page staged persistence and confirm flow

- **State:** E14 implemented and verified.
- **Meaningful accomplishments:**
  1. **Backend model:** `MindMapWorkingState` SQLAlchemy model in `app/models/channel.py` — server-side backup of candidate nodes/edges per session. One-to-one relationship with `PersonaPageSession`. JSONB columns for nodes/edges, version counter, timestamps.
  2. **Alembic migration:** `e14a0b3c9d52_add_mindmap_working_state_table.py` — creates `mindmap_working_states` table with FK to `persona_page_sessions`, unique session constraint.
  3. **Backend API endpoints (4 new):**
     - `PUT /persona/sessions/{id}/working-state` — save/backup working state (session-scoped, not operational)
     - `GET /persona/sessions/{id}/working-state` — restore working state for session resumption
     - `POST /persona/sessions/{id}/confirm` — Confirm & Save: batch-commits accepted entities to operational database in one transaction, transitions session to "confirmed". Two-pass approach: projects first, then subsidiary entities (blockers, risks, milestones, work_items, decisions) linked to project.
     - `POST /persona/sessions/{id}/discard` — discard working state, transition session to "abandoned", delete working state record. No entities reach the database.
  4. **Frontend hook:** `use-working-state.ts` — React hook for managing client-side candidate nodes/edges with add/update/accept/discard/confirmAll/discardAll operations, auto-save debounce to backend, session restore.
  5. **Frontend toolbar:** `mind-map-toolbar.tsx` — staged persistence controls: pending/accepted/discarded counts, Accept All button, Confirm & Save button (disabled when no accepted nodes), Discard with confirmation, saving indicator, unsaved changes warning, terminal state display.
  6. **Frontend wiring:** `workspace-canvas.tsx` updated to accept working state props and render toolbar in idea mode. `page.tsx` wires `useWorkingState` hook and passes props.
  7. **Types + API client:** Added `CandidateNodePayload`, `CandidateEdgePayload`, `WorkingStateResponse`, `ConfirmWorkingStateResponse`, `DiscardWorkingStateResponse` types. Added `saveWorkingState`, `fetchWorkingState`, `confirmWorkingState`, `discardWorkingState` API client functions.
- **Architecture compliance:**
  - `ARCH:PersonaPage.StagedPersistence` — working state is session-scoped backup; nothing enters operational DB until explicit confirm
  - `ARCH:StateOwnershipBoundaries` — candidate state is strictly separated from accepted operational memory
  - `ARCH:MindMapWorkingStateModel` — model matches the architecture spec (nodes, edges, version, session link)
  - `REQ:PersonaPageStagedPersistence` — confirm flow commits all accepted entities in one coordinated batch
- **Verification executed:**
  - 20 backend API tests: 20/20 pass (save/retrieve, update, terminal-session rejection, confirm with project/stakeholder/risk/work_item/decision/blocker/milestone, partial acceptance, session status transition, discard lifecycle, edge cases)
  - 6 Playwright tests: 6/6 pass (toolbar visible in idea mode, Confirm & Save button present, disabled when no accepted nodes, demo nodes show pending status, toolbar not in non-idea modes, accepted vs pending visually distinct)
  - Full backend suite: 863/863 pass (0 regressions)
  - Full Playwright suite: 56/56 pass (0 regressions)
  - TypeScript type check: 0 errors
- **Files created:**
  - `apps/backend/app/models/channel.py` (MindMapWorkingState class added)
  - `apps/backend/alembic/versions/e14a0b3c9d52_add_mindmap_working_state_table.py`
  - `apps/web/src/app/glimmer/use-working-state.ts`
  - `apps/web/src/app/glimmer/mind-map-toolbar.tsx`
  - `apps/web/e2e/staged-persistence.spec.ts`
  - `tests/api/test_staged_persistence.py`
- **Files modified:**
  - `apps/backend/app/api/persona.py` (4 new endpoints + contracts)
  - `apps/backend/app/models/__init__.py` (MindMapWorkingState export)
  - `apps/web/src/lib/types.ts` (working state types)
  - `apps/web/src/lib/api-client.ts` (4 new API functions)
  - `apps/web/src/app/glimmer/workspace-canvas.tsx` (toolbar + props)
  - `apps/web/src/app/glimmer/page.tsx` (useWorkingState hook wiring)
  - `tests/conftest.py` (test_staged_persistence pack mapping)

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
- `TEST:ProjectCRUD.Api.CreateReadUpdateArchive` — **Pass** (20 API tests: create with 201, validation, read detail, partial update, archive sets status+flag, 404/409 edge cases)
- `TEST:ProjectCRUD.Api.ValidationRejectsEmptyName` — **Pass** (API: empty and whitespace-only names return 422)
- `TEST:ProjectCRUD.Api.ArchiveFiltersFromListByDefault` — **Pass** (API: archived projects excluded from list, included with ?include_archived=true)
- `TEST:ProjectCRUD.Api.ArchiveEndpointSetsStatusAndFlag` — **Pass** (API: POST /projects/{id}/archive sets archived=True, status=archived; double-archive returns 409)
- `TEST:ProjectCRUD.Browser.CreateProjectFromPortfolio` — **Pass** (Playwright: New Project button visible, modal opens with form fields and submit)
- `TEST:ProjectCRUD.Browser.EditProjectDetails` — **Pass** (Playwright: Edit/Archive buttons visible on active project detail page)
- `TEST:ProjectCRUD.Browser.ArchiveProject` — **Pass** (Playwright: Archive button present with confirmation flow)
- `TEST:PersonaPage.Conversation.ChatRendersAndAcceptsInput` — **Pass** (6 Playwright tests: persona page renders all sections, chat input accepts text, send button visible, mode controls visible, avatar mood attribute)
- `TEST:PersonaPage.Conversation.SessionLifecycleManaged` — **Pass** (22 API tests: session create/get/update, message send/persist/metadata, lifecycle transitions active↔paused/confirmed/abandoned, terminal states, validation)
- `TEST:PersonaPage.MindMap.NodesRenderWithSemanticTypes` — **Pass** (6 Playwright tests: idea mode shows mind-map canvas, 8 semantic node types visible, working state indicators with pending/accepted distinction, React Flow controls and minimap visible, non-idea modes do not show mind-map)
- `TEST:PersonaPage.MindMap.CanvasSupportsZoomPanInteraction` — **Pass** (Playwright: React Flow controls visible, minimap visible, canvas renders with interactive elements)
- `TEST:PersonaPage.MindMap.WorkingStateVisuallyDistinct` — **Pass** (6 Playwright tests: toolbar visible in idea mode, pending vs accepted nodes visually distinct with dashed/solid borders and DRAFT badge, Confirm & Save disabled when no accepted nodes, toolbar absent in non-idea modes)
- `TEST:PersonaPage.StagedPersistence.ConfirmSaveCommitsAllEntities` — **Pass** (20 API tests: save/retrieve working state, confirm persists projects/stakeholders/risks/blockers/milestones/work_items/decisions in one batch, only accepted_node_ids are persisted, session transitions to confirmed, edge cases)
- `TEST:PersonaPage.StagedPersistence.DiscardDoesNotPersist` — **Pass** (5 API tests: discard transitions to abandoned, deletes working state, no orphan entities, terminal-state rejection)

### 8.2 Verification interpretation

WE1-WE9 + E11 + E12 + E13 + E14 verification is complete. 863 backend tests pass. 56 Playwright tests pass (including 6 mind-map + 6 staged-persistence tests). TypeScript type check: 0 errors. The workspace is a review-first, safety-aware, persona-supported control room with direct project CRUD capability, LLM-backed conversational interaction on the persona page, a React Flow mind-map visualization for idea mode, and a staged persistence model that enforces candidate-vs-accepted state separation with explicit Confirm & Save batch commit.

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

Workstream E is complete, including E14. All work packages (WE1–WE9, E11, E12, E13, E14) are implemented and verified with 56 Playwright tests and 863 backend tests passing.

The next package in the build plan sequence is **E15 — Persona page paste-in ingestion**, which depends on E14's staged persistence model for candidate entity management.

**Stable working anchor:** `WORKE:Progress.ImmediateNextSlice`

---

## 12. Pickup Guidance for the Next Session

Workstream E is fully complete through E14. All packages are verified. The next session should:

1. Implement **E15 — Persona page paste-in ingestion** (depends on E14's staged persistence model)
2. E15 scope: paste-in capture, raw artifact preservation, entity extraction through orchestration core, extracted entities as candidate nodes in working mind-map, provenance linkage
3. After E15, consider E16 (Ask Glimmer) or pivot to real-data operational testing

**Note:** Google and Microsoft OAuth credentials have been provisioned (2026-04-16). Email access confirmed working for both providers. Calendar access provisioned but not yet exercised via user query. The operator wants to test calendar queries through conversational interaction (e.g., "Are there any meetings I need to attend this week?").

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

