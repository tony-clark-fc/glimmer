# Glimmer — Workstream E: Drafting UI

## Document Metadata

- **Document Title:** Glimmer — Workstream E: Drafting UI
- **Document Type:** Detailed Build Plan Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `BUILD_PLAN.md`
- **Primary Companion Documents:** Requirements, Architecture, Build Strategy and Scope, Testing Strategy, Workstream D Triage and Prioritization

---

## 1. Purpose

This document defines the implementation strategy for **Workstream E — Drafting UI**.

Its purpose is to implement the main user-facing web control surfaces that expose Glimmer’s assistant outputs, with particular emphasis on the drafting workspace and the core operator views that make triage, prioritization, and review-first behavior operational.

This workstream is where Glimmer’s backend intelligence starts to become a practical day-to-day operating experience.

**Stable plan anchor:** `PLAN:WorkstreamE.DraftingUi`

---

## 2. Workstream Objective

Workstream E exists to implement Glimmer’s main reviewable web workspace layer, including:

- Today view,
- Portfolio view,
- Project workspace view,
- Triage view,
- Draft workspace view,
- review queue behavior,
- persona-aware presentation support,
- and the UI-side workflows for accepting, amending, deferring, and using assistant-generated outputs.

At the end of this workstream, Glimmer should have a coherent primary operating surface through which the operator can consume and act on the outputs of the memory, connector, triage, and planner layers.

**Stable plan anchor:** `PLAN:WorkstreamE.Objective`

---

## 3. Why This Workstream Comes After Triage and Prioritization

The build strategy explicitly puts the core web workspace after the triage/prioritization layer and before companion/voice expansion. That order is deliberate: the main UI should expose real assistant behavior, not placeholder theatrics.

This workstream depends on:

- structured domain and memory state,
- normalized source records,
- reviewable interpretation artifacts,
- planner outputs such as focus packs,
- and application/API surfaces for triage and prioritization.

Without those, the UI would either be static scaffolding or a thin shell around mocked assistant behavior. This workstream is therefore about operationalizing real outputs, not inventing a frontend in isolation.

**Stable plan anchor:** `PLAN:WorkstreamE.Rationale`

---

## 4. Related Requirements Anchors

This workstream directly supports the following requirements:

- `REQ:DraftResponseWorkspace`
- `REQ:CommunicationToneSupport`
- `REQ:ProjectPortfolioManagement`
- `REQ:ProjectCRUD`
- `REQ:ProjectMemory`
- `REQ:StakeholderMemory`
- `REQ:PrioritizationEngine`
- `REQ:PreparedBriefings`
- `REQ:VisualPersonaSupport`
- `REQ:ContextAwareVisualPresentation`
- `REQ:HumanApprovalBoundaries`
- `REQ:GlimmerPersonaPage`
- `REQ:PersonaPageStagedPersistence`
- `REQ:PersonaPagePasteInIngestion`
- `REQ:ContextualAskGlimmer`

These requirements define the user-facing side of Glimmer's value: the operator must be able to see what matters, review what the system inferred, inspect context, use generated drafts without losing control, create and manage projects, and interact conversationally with Glimmer through the persona page.

**Stable plan anchor:** `PLAN:WorkstreamE.RequirementsAlignment`

---

## 5. Related Architecture Anchors

This workstream is primarily implementing the architecture described by:

- `ARCH:UiSurfaceMap`
- `ARCH:TodayViewArchitecture`
- `ARCH:PortfolioViewArchitecture`
- `ARCH:ProjectWorkspaceArchitecture`
- `ARCH:TriageViewArchitecture`
- `ARCH:DraftWorkspaceArchitecture`
- `ARCH:ReviewQueueArchitecture`
- `ARCH:VisualPersonaSelection`
- `ARCH:ReviewGateArchitecture`
- `ARCH:PlaywrightTestBoundary`
- `ARCH:UxSurface.PersonaPage`
- `ARCH:PersonaPage.ConversationModel`
- `ARCH:PersonaPage.MindMapArchitecture`
- `ARCH:PersonaPage.StagedPersistence`
- `ARCH:PersonaPage.PasteInPipeline`
- `ARCH:PersonaPage.OrchestrationRelationship`
- `ARCH:PersonaPageSessionModel`
- `ARCH:MindMapWorkingStateModel`
- `ARCH:PasteInSourceArtifactModel`
- `ARCH:ContextualAskGlimmerInteraction`

These anchors define the web workspace as the canonical control surface, require visible reviewable artifacts, and establish the drafting workspace, Today view, Triage view, persona-aware interaction model, and persona page conversational workspace that this workstream must make real.

**Stable plan anchor:** `PLAN:WorkstreamE.ArchitectureAlignment`

---

## 6. Workstream Scope

### 6.1 In scope

This workstream includes:

- implementation of the primary web workspace views,
- route/page structure for Today, Portfolio, Project, Triage, Drafts, and Review surfaces,
- display and interaction patterns for assistant-generated artifacts,
- draft-variant comparison and editing support,
- visible provenance/context rendering,
- persona-aware presentation support in relevant surfaces,
- project CRUD API and direct project management UI,
- persona page conversational chat interface with Glimmer avatar,
- persona page dynamic mind-map visualization using React Flow,
- persona page staged persistence model and confirm/save flow,
- persona page paste-in ingestion pipeline,
- and the browser-visible workflows needed for review-first assistant interaction.

**Stable plan anchor:** `PLAN:WorkstreamE.InScope`

### 6.2 Out of scope

This workstream does **not** include:

- Telegram UX implementation as a primary focus,
- final voice console behavior,
- connector internals,
- deep graph/orchestration implementation,
- or autonomous send/commit flows.

This workstream focuses on the main web control surface. Telegram and voice remain later companion layers, not replacements for the workspace.

**Stable plan anchor:** `PLAN:WorkstreamE.OutOfScope`

---

## 7. Implementation Outcome Expected from This Workstream

By the end of Workstream E, Glimmer should be able to do the following in a structurally real way:

- present the operator with a Today view showing current priorities and pressure points,
- show a portfolio comparison view across active projects,
- show a project workspace with synthesized context and linked operational records,
- show triage items with provenance, classification, extracted actions, and review controls,
- show generated drafts in a dedicated drafting workspace with variants and context,
- present review-required artifacts through explicit review surfaces,
- preserve visible distinction between suggestions and accepted state,
- and use approved persona assets in a bounded, context-aware way on relevant UI surfaces.

At that point, Glimmer’s core web control surface becomes operational rather than conceptual.

**Stable plan anchor:** `PLAN:WorkstreamE.ExpectedOutcome`

---

## 8. UI Implementation Packages

## 8.1 Work Package E1 — Primary web app route and layout maturation

**Objective:** Turn the frontend shell into a real multi-surface workspace.

### In scope
- routing/page structure for primary surfaces
- shared layout/navigation refinement
- state/query patterns for loading assistant data
- page-level loading/error/empty-state handling

### Expected outputs
- mature route structure for Today / Portfolio / Project / Triage / Drafts / Review
- shared layout conventions
- testable navigation flows

### Related anchors
- `ARCH:UiSurfaceMap`
- `ARCH:UiPrinciple.WorkspaceFirst`
- `ARCH:UiAccessibilityAndClarity`

### Definition of done
- the frontend is no longer just a placeholder shell; the main control surfaces exist as navigable application routes

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE1.WebWorkspaceShell`

---

## 8.2 Work Package E2 — Today view implementation

**Objective:** Implement the daily chief-of-staff operating surface.

### In scope
- rendering of current focus outputs and top priorities
- display of deadline pressure, reply debt, waiting-on items, and calendar pressure
- rationale snippets for why suggested actions matter
- view composition from planner/focus-pack data

### Expected outputs
- Today page implementation
- API/UI wiring for focus-pack and current-priority retrieval
- tests for major rendering and interaction states

### Related anchors
- `ARCH:TodayViewArchitecture`
- `ARCH:TodayViewDesign`
- `ARCH:Capability.PlanningAndPrioritization`

### Definition of done
- the operator can open a real Today view and understand what matters now, why, and what is blocked or pressing

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE2.TodayView`

---

## 8.3 Work Package E3 — Portfolio view implementation

**Objective:** Implement the comparative multi-project operating surface.

### In scope
- list/grid view of active projects
- urgency, blockage, and attention-demand indicators
- links into project workspaces
- account- and source-aware signals where relevant

### Expected outputs
- Portfolio page implementation
- data contracts for portfolio summaries
- tests for sorting/grouping/display behavior where meaningful

### Related anchors
- `ARCH:PortfolioViewArchitecture`
- `ARCH:Capability.PortfolioCoordination`
- `ARCH:OperatingMode.WebWorkspace`

### Definition of done
- the operator can compare active projects through a dedicated portfolio surface rather than navigating projects one by one blindly

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE3.PortfolioView`

---

## 8.4 Work Package E4 — Project workspace implementation

**Objective:** Implement the primary deep-dive operational surface for one project.

### In scope
- project summary rendering
- workstream/milestone rendering
- decisions, risks, blockers, and next actions presentation
- linked stakeholders, recent signals, drafts, and briefing artifacts
- synthesized, relevance-first project page composition

### Expected outputs
- Project workspace page implementation
- data retrieval/wiring for project-level context
- tests for project navigation and key content presence

### Related anchors
- `ARCH:ProjectWorkspaceArchitecture`
- `ARCH:ProjectWorkspaceDesign`
- `ARCH:ProjectMemoryModel`

### Definition of done
- the operator can open a project and quickly orient using synthesized context instead of raw chronological dumps

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE4.ProjectWorkspace`

---

## 8.5 Work Package E5 — Triage view implementation

**Objective:** Make Glimmer’s message understanding visible and actionable.

### In scope
- rendering of triage items from interpreted artifacts
- display of source provenance, participants, project classification, confidence, extracted actions/deadlines, and next-step suggestions
- actions for accept, amend, reassign, defer, informational-only, and draft request
- filtering by source account/profile where useful

### Expected outputs
- Triage page implementation
- UI controls for triage review actions
- tests for triage review interactions and provenance visibility

### Related anchors
- `ARCH:TriageViewArchitecture`
- `ARCH:TriageViewDesign`
- `ARCH:UiPrinciple.ReviewableOutputs`
- `ARCH:MultiAccountUxProvenance`

### Definition of done
- triage items are no longer hidden in backend state; the operator can inspect and act on them through a real review surface

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE5.TriageView`

---

## 8.6 Work Package E6 — Draft workspace implementation

**Objective:** Implement the dedicated draft-response review surface.

### In scope
- rendering of drafts and draft variants
- linked source-message/project/stakeholder context
- tone posture visibility
- operator editing and reformulation support
- copy/mark-used actions
- bounded no-auto-send posture in UI behavior

### Expected outputs
- Draft workspace page implementation
- draft variant controls and editor behavior
- tests for variant selection, editing, and copy-ready presentation

### Related anchors
- `ARCH:DraftWorkspaceArchitecture`
- `ARCH:DraftWorkspaceDesign`
- `ARCH:DraftingGraph`
- `ARCH:NoAutoSendPolicy`

### Definition of done
- Glimmer drafts are reviewable and usable in a dedicated workspace rather than appearing as opaque AI output blocks

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE6.DraftWorkspace`

---

## 8.7 Work Package E7 — Review queue and approval UX

**Objective:** Implement the generalized review surface for pending assistant decisions.

### In scope
- review queue listing
- rendering of review-needed classifications, extracted actions, and other gated artifacts
- accept/amend/reject/defer controls
- clear distinction between pending proposals and accepted state

### Expected outputs
- Review queue page or integrated review surface
- reusable approval/review components
- tests for review-state rendering and interaction behavior

### Related anchors
- `ARCH:ReviewQueueArchitecture`
- `ARCH:ReviewGateUx`
- `ARCH:ReviewArtifactPresentation`
- `ARCH:ReviewGateArchitecture`

### Definition of done
- review-gated assistant outputs are visible and actionable through a coherent UI pattern rather than being implied by backend state only

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE7.ReviewQueueUx`

---

## 8.8 Work Package E8 — Persona-aware presentation layer

**Objective:** Implement bounded, useful persona rendering tied to approved assets and interaction context.

### In scope
- loading/rendering of approved persona assets
- fallback/default persona behavior
- mapping from interaction context to persona asset selection support
- persona display in suitable surfaces such as Today, briefing, draft, or assistant panels

### Expected outputs
- persona rendering component(s)
- integration with persona asset metadata
- tests for fallback behavior and context-aware rendering rules where meaningful

### Related anchors
- `ARCH:VisualPersonaArchitecture`
- `ARCH:VisualPersonaSelection`
- `ARCH:VisualPersonaRenderingRules`

### Definition of done
- Glimmer’s persona support is real, bounded, and asset-driven rather than improvised or purely decorative

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE8.PersonaPresentationLayer`

---

## 8.9 Work Package E9 — Stakeholder and briefing support surfaces

**Objective:** Expose the supporting surfaces that deepen context without cluttering the main views.

### In scope
- stakeholder context panel/page behavior
- briefing-oriented presentation surface(s)
- quick access from project, triage, or Today flows into these supporting views

### Expected outputs
- stakeholder context surface
- briefing surface implementation or major component set
- tests for navigation and content visibility

### Related anchors
- `ARCH:StakeholderSurfaceArchitecture`
- `ARCH:BriefingSurfaceArchitecture`
- `ARCH:ContextBeforeAction`

### Definition of done
- the operator can inspect supporting human and situational context without losing the main task flow

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE9.SupportingContextSurfaces`

---

## 8.10 Work Package E10 — Browser-verification-ready UX patterns

**Objective:** Ensure the UI is implemented in a way that supports durable Playwright proof rather than brittle manual clicking.

### In scope
- stable selectors/test IDs where needed
- deterministic loading patterns
- reduction of flaky timing assumptions
- page/component conventions that improve browser automation reliability

### Expected outputs
- browser-test-friendly UI conventions in the implemented surfaces
- Playwright-oriented support hooks where appropriate
- tests proving the major UI flows can be automated reliably

### Related anchors
- `ARCH:PlaywrightTestBoundary`
- `ARCH:BrowserWorkflowVerification`
- `ARCH:TestingPrinciple.LayeredProof`

### Definition of done
- the UI is not only functional, but structured in a way that supports durable browser automation rather than fragile manual regression dependence

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE10.BrowserTestableUxPatterns`

---

## 8.11 Work Package E11 — Project CRUD API and direct project management UI

**Objective:** Provide a direct, form-based path for project creation and management independent of the persona page conversation.

### In scope
- backend project CRUD API endpoints (list, get, create, update/archive)
- thin Pydantic request/response contracts with attention-demand signals
- portfolio-integrated project creation form or modal
- project field editing in the project workspace
- archive/reactivate controls

### Expected outputs
- `/api/projects` endpoint set with full CRUD behavior
- frontend project creation and editing UI components
- tests for API CRUD operations and UI creation flow

### Related anchors
- `REQ:ProjectCRUD`
- `REQ:ProjectPortfolioManagement`
- `ARCH:ProjectStateModel`
- `ARCH:PortfolioViewArchitecture`

### Definition of done
- the operator can create, update, and archive projects through a direct interface without needing a conversational interaction

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE11.ProjectCrudApi`

---

## 8.12 Work Package E12 — Persona page conversation UI

**Objective:** Implement the conversational chat interface and Glimmer persona display on the dedicated Persona page.

### In scope
- persona page route and layout
- prominent Glimmer avatar display with mood-aware selection
- real-time chat interface with operator input and Glimmer responses
- conversation session lifecycle management (active, paused, confirmed, abandoned)
- suggested conversation starters
- voice input support within the chat interface (deferred to Workstream F integration if needed)
- routing conversation messages through the orchestration core

### Expected outputs
- `/glimmer` persona page implementation
- chat message rendering and input components
- session state management
- API contract for conversation session create/message/complete
- tests for conversation rendering, session lifecycle, and persona avatar display

### Related anchors
- `REQ:GlimmerPersonaPage`
- `ARCH:UxSurface.PersonaPage`
- `ARCH:PersonaPage.ConversationModel`
- `ARCH:PersonaPage.OrchestrationRelationship`
- `ARCH:PersonaPageSessionModel`
- `ARCH:VisualPersonaSelection`

### Definition of done
- the operator can have a conversational interaction with Glimmer on the persona page, with a visible persona avatar and session management

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE12.PersonaPageConversationUi`

---

## 8.13 Work Package E13 — Persona page mind-map visualization

**Objective:** Implement the dynamic, interactive mind-map that grows as the persona-page conversation progresses.

### In scope
- React Flow integration for node/edge rendering
- custom node types for projects, stakeholders, milestones, risks, blockers, work items, decisions, dependencies
- edge types for relational links
- radial or hierarchical layout with automatic positioning
- zoom, pan, and minimap controls
- animated node entry and progressive disclosure
- visual distinction between working (unconfirmed) and persisted nodes
- node click-to-inspect and hover "Ask Glimmer" affordance
- optional operator node rearrangement

### Expected outputs
- React Flow canvas component with custom node/edge types
- layout algorithm integration (dagre or elkjs)
- mind-map state management synchronized with conversation flow
- tests for node rendering, visual state indicators, and canvas interaction

### Related anchors
- `REQ:GlimmerPersonaPage`
- `ARCH:PersonaPage.MindMapArchitecture`
- `ARCH:MindMapWorkingStateModel`
- `ARCH:MindMapCandidateNodeModel`
- `ARCH:MindMapCandidateEdgeModel`

### Definition of done
- the mind-map renders dynamically during conversation with semantically meaningful node types, visual state indicators, and interactive canvas controls

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE13.PersonaPageMindMap`

---

## 8.14 Work Package E14 — Persona page staged persistence and confirm flow

**Objective:** Implement the staged persistence model that holds candidate entities in working state until the operator explicitly confirms.

### In scope
- client-side working state management for candidate nodes and edges
- visual "draft" indicators for unconfirmed entities
- "Confirm & Save" action that commits accepted working state to the database
- backend staged-persistence endpoint for coordinated batch commit
- discard/abandon handling with preservation-or-warning flow
- session backup for pause/resume across navigation

### Expected outputs
- working state store (React state or lightweight client store)
- confirm & save API endpoint and handler
- batch persistence service that creates all accepted entities in one transaction
- tests for staged persistence lifecycle, confirm/discard flows, and working-vs-persisted visual distinction

### Related anchors
- `REQ:PersonaPageStagedPersistence`
- `ARCH:PersonaPage.StagedPersistence`
- `ARCH:StateOwnershipBoundaries`
- `ARCH:MindMapWorkingStateModel`

### Definition of done
- candidate entities remain in working state until explicit confirmation; "Confirm & Save" persists all accepted entities in one coordinated commit; the visual distinction between working and persisted state is clear

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE14.PersonaPageStagedPersistence`

---

## 8.15 Work Package E15 — Persona page paste-in ingestion

**Objective:** Implement operator-initiated paste-in of unstructured content with entity extraction and mind-map integration.

### In scope
- paste-in capture in the chat interface or dedicated paste area
- raw artifact preservation (PasteInSourceArtifact) before interpretation
- entity extraction through the orchestration core
- integration of extracted entities as candidate nodes in the working mind-map
- conversational explanation of what was extracted and why
- operator review of individual extracted entities (accept, edit, discard)
- provenance linkage from extracted nodes back to paste-in artifact

### Expected outputs
- paste-in UI component
- backend paste-in artifact persistence endpoint
- entity extraction service integration
- mind-map node creation from extraction results
- tests for paste-in capture, artifact persistence, extraction integration, and provenance linkage

### Related anchors
- `REQ:PersonaPagePasteInIngestion`
- `ARCH:PersonaPage.PasteInPipeline`
- `ARCH:PasteInSourceArtifactModel`

### Definition of done
- the operator can paste unstructured content; Glimmer extracts entities; extracted entities appear as candidate nodes on the mind-map; paste-in provenance is preserved

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE15.PersonaPagePasteIn`

---

## 8.16 Work Package E16 — Cross-surface "Ask Glimmer" contextual interaction

**Objective:** Implement the shared contextual interaction affordance that lets the operator invoke Glimmer's intelligence on any visible data element across all workspace pages.

### In scope
- hover-triggered or click-triggered affordance (sparkle ✦ icon) on significant data elements
- compact popover or panel anchored to the element with Glimmer avatar and text input
- contextual routing of operator request to the orchestration core with element data as input
- consistent component behavior across Today, Portfolio, Project, Triage, Draft, Review, and supporting surfaces
- review-gate compliance for any responses implying externally meaningful actions

### Expected outputs
- shared `AskGlimmerPopover` (or equivalent) React component
- element-type context metadata contract for orchestration routing
- integration on at least the primary workspace surfaces
- tests for affordance visibility, popover interaction, and review-gate compliance

### Related anchors
- `REQ:ContextualAskGlimmer`
- `ARCH:ContextualAskGlimmerInteraction`
- `ARCH:ReviewGateArchitecture`

### Definition of done
- every significant data element across the main workspace surfaces has a consistent, functional "Ask Glimmer" interaction affordance that routes through the orchestration core and respects review-gate discipline

**Stable plan anchor:** `PLAN:WorkstreamE.PackageE16.ContextualAskGlimmer`

---

## 9. Sequencing Inside the Workstream

The recommended internal order for Workstream E is:

1. E1 — Primary web app route and layout maturation
2. E2 — Today view implementation
3. E3 — Portfolio view implementation
4. E4 — Project workspace implementation
5. E5 — Triage view implementation
6. E7 — Review queue and approval UX
7. E6 — Draft workspace implementation
8. E8 — Persona-aware presentation layer
9. E9 — Stakeholder and briefing support surfaces
10. E10 — Browser-verification-ready UX patterns
11. E11 — Project CRUD API and direct project management UI
12. E12 — Persona page conversation UI
13. E13 — Persona page mind-map visualization
14. E14 — Persona page staged persistence and confirm flow
15. E15 — Persona page paste-in ingestion
16. E16 — Cross-surface "Ask Glimmer" contextual interaction

E11 may be implemented earlier (after E3/E4) since it provides basic project creation that other surfaces depend on. E12–E15 form a natural vertical progression for the full persona page feature. E16 can be implemented at any point after the primary surfaces (E1–E7) exist, but is listed last because it is a cross-cutting enhancement that benefits from all surfaces being in place first.

This order keeps the workspace hierarchy coherent: the operator gets the main control surfaces first, then review-heavy workflows, then drafting refinement, then persona/context support, then the full conversational persona page, then the cross-cutting interaction layer, with browser-testability treated as an explicit implementation concern throughout.

**Stable plan anchor:** `PLAN:WorkstreamE.InternalSequence`

---

## 10. Human Dependencies

This workstream is largely agent-executable once the prior workstreams are in place.

Expected human involvement is primarily around:

- approval of any major UX tradeoffs where multiple valid workspace patterns exist,
- confirmation of how assertive or prominent the persona layer should be,
- and approval of any meaningful compromise between visual polish and review clarity.

The operator may also provide or refine labeled persona assets over time, but the coding agent should be able to implement the data-driven rendering pattern before the full final asset set is complete.

**Stable plan anchor:** `PLAN:WorkstreamE.HumanDependencies`

---

## 11. Verification Expectations

Workstream E is complete only when the web control surfaces are not just implemented, but proven to support the intended user workflows.

### Verification layers expected
- browser workflow verification with Playwright
- API verification for the application surfaces that feed the UI
- integration verification for persisted draft/review/focus data where relevant
- light unit verification for rendering/selection helpers where useful

### Minimum proof expectations
- the Today view renders current priorities and focus artifacts correctly
- portfolio and project views render synthesized context correctly
- triage items display provenance, classification, and review controls clearly
- draft workspace shows linked context, variants, and bounded copy/edit flows
- review-required artifacts can be accepted/amended/deferred through a clear UI flow
- the UI visibly distinguishes pending proposals from accepted state
- persona rendering obeys fallback rules and does not break core workflows
- main user journeys are automatable through Playwright without fragile, timing-heavy hacks

This aligns directly to Glimmer’s testing strategy, which treats browser workflows, review-gate visibility, provenance presentation, and draft workspace behavior as load-bearing proof targets.

**Stable plan anchor:** `PLAN:WorkstreamE.VerificationExpectations`

---

## 12. Suggested Future Working Documents for This Workstream

This workstream should eventually be paired with:

- `WorkstreamE_DraftingUi_DESIGN_AND_IMPLEMENTATION_PLAN.md`
- `WorkstreamE_DraftingUi_DESIGN_AND_IMPLEMENTATION_PROGRESS.md`

Those files will hold the active UI implementation state, design tradeoffs, verification evidence, and remaining UX questions once coding begins.

**Stable plan anchor:** `PLAN:WorkstreamE.WorkingDocumentPair`

---

## 13. Definition of Done

Workstream E should be considered complete when all of the following are true:

1. the main web workspace routes and shared layout are real,
2. Today, Portfolio, Project, Triage, Draft, and Review surfaces are implemented,
3. assistant-generated outputs are visible as reviewable artifacts rather than hidden state,
4. the draft workspace supports variants, context visibility, and copy/edit flows,
5. review-required workflows are actionable through the UI,
6. provenance and multi-account context are visible where materially relevant,
7. persona-aware presentation is implemented in a bounded, asset-driven way,
8. the project CRUD API and direct project management UI are operational,
9. the persona page conversational chat, mind-map visualization, staged persistence, and paste-in ingestion are implemented,
10. the persona page respects staged persistence — candidate entities do not enter the database without explicit confirmation,
11. the cross-surface "Ask Glimmer" contextual interaction affordance is implemented consistently across all primary workspace surfaces,
12. and the required browser/API verification evidence has been executed and recorded.

If these are not true, Glimmer still lacks the primary operator control surface needed to turn backend intelligence into usable daily execution support.

**Stable plan anchor:** `PLAN:WorkstreamE.DefinitionOfDone`

---

## 14. Final Note

Workstream E is where Glimmer becomes something the operator can actually live inside.

If this workstream is done well, the product will feel like a disciplined control room: focused, reviewable, tactful, and ready for real use.
If it is done badly, the system will either feel like a generic admin UI or a flashy AI shell that hides too much of the real work.

The correct outcome is a workspace that surfaces the right context, the right decisions, and the right drafts at the right time — without taking away control.

**Stable plan anchor:** `PLAN:WorkstreamE.Conclusion`
