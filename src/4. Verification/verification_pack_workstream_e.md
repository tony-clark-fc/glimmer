# Glimmer — Verification Pack: Workstream E Drafting UI

## Document Metadata

- **Document Title:** Glimmer — Verification Pack: Workstream E Drafting UI
- **Document Type:** Canonical Verification Pack
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Test Catalog, Requirements, Architecture, Build Plan, Testing Strategy, Workstream E Drafting UI, Workstream D Verification Pack

---

## 1. Purpose

This document defines the **Workstream E verification pack** for **Glimmer**.

Its purpose is to prove that the primary web workspace created by **Workstream E — Drafting UI** makes Glimmer’s assistant outputs visible, reviewable, navigable, and operationally useful.

Where Workstream D proves that Glimmer’s assistant core can classify, extract, prioritize, and prepare reviewable artifacts, this pack proves that those artifacts can be surfaced through the web workspace in a way the operator can actually trust and use.

**Stable verification anchor:** `TESTPACK:WorkstreamE.ControlSurface`

---

## 2. Role of the Workstream E Pack

This pack exists to verify the implementation outcomes expected from the Drafting UI workstream, including:

- Today view usefulness,
- Portfolio view comparison behavior,
- Project workspace synthesis,
- Triage view reviewability,
- Draft workspace clarity and variant handling,
- Review queue visibility and control,
- persona-aware but bounded presentation,
- and browser-testable operator workflows across the main Glimmer control room.

This pack is the first verification surface that proves Glimmer’s outputs are not trapped behind services and graphs. It protects the operator experience where real day-to-day use happens.

**Stable verification anchor:** `TESTPACK:WorkstreamE.Role`

---

## 3. Relationship to the Control Surface

This verification pack is derived from and aligned to:

- the **Agentic Delivery Framework**, especially its authority model, work-package operating model, verification model, evidence-of-completion posture, and traceability expectations,
- the **Testing Strategy Companion**, especially automation-first proof, Playwright-first browser verification, layered browser/API testing, and evidence-backed completion,
- the **Glimmer Agentic Delivery Document Set**, which explicitly defines `verification-pack-workstream-e.md` as part of the canonical verification family,
- the **Glimmer Requirements**, especially draft response workspace, communication tone support, project portfolio management, prepared briefings, visual persona support, context-aware visual presentation, and human approval boundaries,
- the latest **Architecture** state, especially the manually maintained canonical architecture index and its UI, draft-workspace, Today-view, project-workspace, persona, review-gate, and testing anchors,
- the **Build Plan**, **Build Strategy and Scope**, and **Workstream E — Drafting UI**, which define the workspace-first operating model and why the web workspace comes after the assistant core and before companion/voice expansion,
- the **Glimmer Testing Strategy** and **Workstream G — Testing and Regression**, which define browser workflow verification, Playwright scope, and regression-pack design,
- the **Governance and Process** document, which requires evidence-backed completion and surfaced drift for meaningful work,
- and the current **Test Catalog**, which already defines the core browser/workspace, review, drafting-boundary, and persona `TEST:` anchors this pack should organize and extend.

**Stable verification anchor:** `TESTPACK:WorkstreamE.ControlSurfaceAlignment`

---

## 4. Why This Pack Is Load-Bearing

The architecture and workstream plan are explicit that the web workspace is the **canonical control surface** for Glimmer. Telegram and voice are companion modes, not replacements. The workspace must therefore make Glimmer’s outputs visible in a way that supports judgment, review, and execution rather than vague AI theater.

Workstream E is where that becomes real through:

- route and layout maturation,
- Today view,
- Portfolio view,
- Project workspace,
- Triage view,
- Draft workspace,
- Review queue,
- persona-aware presentation,
- and browser-testable UI behavior.

If this pack is weak, Glimmer may still look polished while actually depending on:

- hidden provenance,
- blurred pending-vs-accepted state,
- unusable draft comparison,
- weak review visibility,
- or a chatbot-shaped UX that hides the actual control model.

That is exactly what this pack is meant to prevent.

**Stable verification anchor:** `TESTPACK:WorkstreamE.Rationale`

---

## 5. Workstream E Verification Scope

### 5.1 In scope

This pack covers proof for the following Drafting UI concerns:

- route and layout integrity for the main workspace surfaces,
- Today view rendering of priorities and pressure,
- Portfolio view comparison behavior,
- Project workspace synthesis and context display,
- Triage view provenance and review controls,
- Draft workspace context, variant handling, and copy/edit posture,
- Review queue interaction and pending-vs-accepted distinction,
- persona rendering selection and fallback behavior,
- and browser-testable operator journeys across the main workspace.

### 5.2 Out of scope

This pack does **not** attempt to prove:

- low-level connector/provider normalization correctness,
- deep assistant-core classification quality in isolation,
- voice-session conversational quality,
- or Telegram companion usefulness beyond workspace handoff implications.

Those belong to other workstream packs and cross-cutting packs.

**Stable verification anchor:** `TESTPACK:WorkstreamE.Scope`

---

## 6. Source `TEST:` Anchors Included in This Pack

The Workstream E pack is built primarily from the web-workspace, drafting-and-review, and security scenario groups in the canonical Test Catalog, with a small number of workspace-specific extensions where needed.

### 6.1 Canonical web workspace anchors already defined in the Test Catalog

#### `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly`
- **Scenario name:** Today view presents priorities, pressure, and rationale clearly
- **Layers:** `browser`
- **Role in this pack:** Proves the daily operating view is materially useful.

#### `TEST:UI.PortfolioView.ComparesProjectAttentionDemand`
- **Scenario name:** Portfolio view supports comparison across project attention demand
- **Layers:** `browser`
- **Role in this pack:** Proves portfolio-level prioritization support is visible.

#### `TEST:UI.ProjectWorkspace.ShowsSynthesisNotJustChronology`
- **Scenario name:** Project workspace presents synthesized project context
- **Layers:** `browser`
- **Role in this pack:** Proves project pages are relevance-first rather than raw dumps.

#### `TEST:UI.TriageView.ShowsProvenanceAndReviewControls`
- **Scenario name:** Triage view shows provenance, ambiguity, and review controls
- **Layers:** `browser`
- **Role in this pack:** Proves source meaning and review behavior remain visible in the UI.

#### `TEST:UI.DraftWorkspace.ShowsContextAndVariants`
- **Scenario name:** Draft workspace shows linked context and draft variants clearly
- **Layers:** `browser`
- **Role in this pack:** Proves the draft workspace is a real operator tool.

#### `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious`
- **Scenario name:** Review queue makes pending vs accepted state obvious
- **Layers:** `browser`
- **Role in this pack:** Proves the UI preserves candidate-vs-accepted distinction.

#### `TEST:UI.Persona.FallbackAndContextSelectionWorks`
- **Scenario name:** Persona rendering supports context-aware selection and fallback
- **Layers:** `browser`, `unit`
- **Role in this pack:** Proves persona support is bounded and asset-driven.

### 6.2 Canonical drafting/review and security anchors already defined in the Test Catalog

#### `TEST:Review.AcceptAmendRejectDefer.ChangesPersistCorrectly`
- **Scenario name:** Review actions persist correctly across accept/amend/reject/defer flows
- **Layers:** `api`, `integration`, `browser`
- **Role in this pack:** Proves review is a real control path in the workspace.

#### `TEST:Drafting.DraftGeneration.CreatesReviewableDraft`
- **Scenario name:** Draft generation creates a reviewable draft artifact
- **Layers:** `graph`, `integration`, `api`
- **Role in this pack:** Proves the workspace is displaying real durable drafting artifacts rather than invented UI-only content.

#### `TEST:Drafting.Variants.MultipleVariantsRemainLinked`
- **Scenario name:** Multiple draft variants remain linked to one drafting episode
- **Layers:** `integration`, `api`
- **Role in this pack:** Proves variant comparison is grounded in real model state.

#### `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- **Scenario name:** Draft workflow does not create outbound send behavior
- **Layers:** `graph`, `api`, `integration`
- **Role in this pack:** Proves the workspace does not imply or trigger unsafe send behavior.

#### `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`
- **Scenario name:** Externally meaningful actions require structured approval
- **Layers:** `graph`, `api`, `browser`
- **Role in this pack:** Proves the browser-visible control surfaces actually preserve approval discipline.

### 6.3 Additional Workstream E-specific anchors introduced by this pack

#### `TEST:UI.Navigation.WorkspaceRoutesRemainReachable`
- **Scenario name:** Main workspace routes remain reachable through stable navigation paths
- **Primary layers:** `browser`
- **Primary drivers:** `REQ:ProjectPortfolioManagement`, `ARCH:UiSurfaceMap`, `ARCH:PlaywrightTestBoundary`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the main control-room route structure is coherent and reachable.

#### `TEST:UI.TodayView.FocusArtifactsMapCleanlyToRenderedState`
- **Scenario name:** Today view maps focus artifacts and pressure signals cleanly into rendered state
- **Primary layers:** `browser`, `api`
- **Primary drivers:** `REQ:PrioritizationEngine`, `ARCH:TodayViewArchitecture`, `ARCH:FocusPackModel`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the Today view is a faithful rendering of planner outputs, not decorative interpretation.

#### `TEST:UI.ProjectWorkspace.ContextPanelsSupportFastOrientation`
- **Scenario name:** Project workspace context panels support fast operator orientation
- **Primary layers:** `browser`
- **Primary drivers:** `REQ:ProjectMemory`, `REQ:PreparedBriefings`, `ARCH:ProjectWorkspaceArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the project view helps the operator orient quickly around current context.

#### `TEST:UI.TriageView.MultiAccountProvenanceIsVisible`
- **Scenario name:** Triage view visibly preserves multi-account and source provenance where relevant
- **Primary layers:** `browser`
- **Primary drivers:** `REQ:MultiAccountProfileSupport`, `ARCH:AccountProvenanceModel`, `ARCH:UiSurfaceMap`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the UI does not flatten source identity just to look cleaner.

#### `TEST:UI.DraftWorkspace.CopyEditFlowRemainsReviewOnly`
- **Scenario name:** Draft workspace copy/edit flows remain explicitly review-only
- **Primary layers:** `browser`, `api`
- **Primary drivers:** `REQ:DraftResponseWorkspace`, `REQ:SafeBehaviorDefaults`, `ARCH:DraftWorkspaceArchitecture`, `ARCH:NoAutoSendPolicy`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove copy/edit flows do not blur into autonomous send behavior.

#### `TEST:UI.ReviewQueue.ActionsReflectRealBackendState`
- **Scenario name:** Review queue actions update visible state in line with persisted backend review outcomes
- **Primary layers:** `browser`, `api`, `integration`
- **Primary drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:ReviewGateArchitecture`, `ARCH:ReviewQueueArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the review queue is not just a facade over stale or disconnected state.

#### `TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent`
- **Scenario name:** Persona rendering remains supportive and does not obscure operational content
- **Primary layers:** `browser`, `manual_only`
- **Primary drivers:** `REQ:VisualPersonaSupport`, `REQ:ContextAwareVisualPresentation`, `ARCH:VisualPersonaSelection`, `ARCH:UiSurfaceMap`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove persona presentation supports the workspace without overpowering it.

**Stable verification anchor:** `TESTPACK:WorkstreamE.IncludedTests`

---

## 7. Workstream E Pack Entry Table

| TEST Anchor | Scenario | Layer | Automation Status | Pack Priority | Notes |
|---|---|---|---|---|---|
| `TEST:UI.Navigation.WorkspaceRoutesRemainReachable` | Main workspace routes remain reachable through stable navigation paths | `browser` | Planned | Critical | Workspace-shell baseline |
| `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly` | Today view presents priorities, pressure, and rationale clearly | `browser` | Planned | Critical | Daily control surface baseline |
| `TEST:UI.TodayView.FocusArtifactsMapCleanlyToRenderedState` | Today view maps focus artifacts and pressure signals cleanly into rendered state | `browser`, `api` | Planned | High | Planner-to-UI fidelity |
| `TEST:UI.PortfolioView.ComparesProjectAttentionDemand` | Portfolio view supports comparison across project attention demand | `browser` | Planned | High | Comparative decision support |
| `TEST:UI.ProjectWorkspace.ShowsSynthesisNotJustChronology` | Project workspace presents synthesized project context | `browser` | Planned | Critical | Relevance-first project view |
| `TEST:UI.ProjectWorkspace.ContextPanelsSupportFastOrientation` | Project workspace context panels support fast operator orientation | `browser` | Planned | High | Practical usability check |
| `TEST:UI.TriageView.ShowsProvenanceAndReviewControls` | Triage view shows provenance, ambiguity, and review controls | `browser` | Planned | Critical | Triage reviewability baseline |
| `TEST:UI.TriageView.MultiAccountProvenanceIsVisible` | Triage view visibly preserves multi-account and source provenance where relevant | `browser` | Planned | High | Protects source meaning |
| `TEST:UI.DraftWorkspace.ShowsContextAndVariants` | Draft workspace shows linked context and draft variants clearly | `browser` | Planned | Critical | Draft surface baseline |
| `TEST:UI.DraftWorkspace.CopyEditFlowRemainsReviewOnly` | Draft workspace copy/edit flows remain explicitly review-only | `browser`, `api` | Planned | Critical | No-auto-send UI protection |
| `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious` | Review queue makes pending vs accepted state obvious | `browser` | Planned | Critical | Candidate-vs-accepted clarity |
| `TEST:UI.ReviewQueue.ActionsReflectRealBackendState` | Review queue actions update visible state in line with persisted backend review outcomes | `browser`, `api`, `integration` | Planned | High | Review control fidelity |
| `TEST:Review.AcceptAmendRejectDefer.ChangesPersistCorrectly` | Review actions persist correctly across accept/amend/reject/defer flows | `api`, `integration`, `browser` | Planned | Critical | Review-system baseline |
| `TEST:Drafting.DraftGeneration.CreatesReviewableDraft` | Draft generation creates a reviewable draft artifact | `graph`, `integration`, `api` | Planned | High | UI depends on real drafting artifacts |
| `TEST:Drafting.Variants.MultipleVariantsRemainLinked` | Multiple draft variants remain linked to one drafting episode | `integration`, `api` | Planned | High | Variant integrity |
| `TEST:Drafting.NoAutoSend.BoundaryPreserved` | Draft workflow does not create outbound send behavior | `graph`, `api`, `integration` | Planned | Critical | Cross-layer safety boundary |
| `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` | Externally meaningful actions require structured approval | `graph`, `api`, `browser` | Planned | Critical | Approval discipline remains visible |
| `TEST:UI.Persona.FallbackAndContextSelectionWorks` | Persona rendering supports context-aware selection and fallback | `browser`, `unit` | Planned | Medium | Managed asset behavior |
| `TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent` | Persona rendering remains supportive and does not obscure operational content | `browser`, `manual_only` | Planned | Medium | Human-eyeball UX guardrail |

**Stable verification anchor:** `TESTPACK:WorkstreamE.EntryTable`

---

## 8. Expected Automation Shape

### 8.1 Browser proof by default

Most Workstream E proof should be implemented through browser workflow testing because this workstream is fundamentally about:

- route reachability,
- operator visibility,
- reviewability,
- workspace control surfaces,
- and whether the UI actually supports the intended decision flows.

### 8.2 API and integration proof where UI fidelity depends on backend state

Where the workspace depends on durable review state, draft artifacts, focus packs, or accepted-vs-pending distinctions, API and integration proof should confirm that the browser-visible behavior is grounded in real backend state rather than fragile frontend-only interpretation.

### 8.3 Limited unit proof

Unit tests may be useful for bounded deterministic behavior such as persona selection/fallback helpers or small rendering-state helpers, but they are not the primary proof vehicle for this pack.

### 8.4 Minimal `manual_only` use

This pack should be heavily automated through Playwright and API/integration checks.

A small `ManualOnly` slice may still be appropriate for human-judgment UX checks such as whether persona rendering remains supportive rather than intrusive.

**Stable verification anchor:** `TESTPACK:WorkstreamE.AutomationShape`

---

## 9. Environment Assumptions

The Workstream E pack assumes the foundation, memory, connector, and assistant-core substrate are already in place.

### 9.1 Required assumptions

Expected baseline assumptions include:

- backend runtime and persistence substrate already working,
- frontend workspace shell already present,
- executable Playwright/browser harness,
- controlled application/API test environment,
- and stable seeded or fixture-driven data that exercises Today, Portfolio, Project, Triage, Draft, and Review surfaces meaningfully.

### 9.2 No dependence on live provider environments for core proof

This pack should not require live Google, Microsoft, Telegram, or voice production environments for its core browser proof.

The workspace behavior should be provable against controlled backend/application state.

### 9.3 Earlier proof should already exist

This pack assumes Workstream D verification has already established that the assistant-core outputs are trustworthy enough that UI failures can be interpreted as surface/interaction problems rather than deeper workflow uncertainty.

**Stable verification anchor:** `TESTPACK:WorkstreamE.EnvironmentAssumptions`

---

## 10. Execution Guidance

### 10.1 When to run this pack

This pack should normally be run:

- after meaningful route/layout changes,
- after changes to Today/Portfolio/Project/Triage/Draft/Review surfaces,
- after changes to persona rendering behavior,
- after browser-visible review-flow changes,
- before declaring Workstream E substantially complete,
- and before claiming that Glimmer is materially usable as a day-to-day control room.

### 10.2 Failure handling

If this pack fails:

- the product may still have functioning backend intelligence, but operator confidence should be treated cautiously,
- the failure should usually be resolved before broader usability claims are made,
- and progress reporting should explicitly state whether the problem affects route reachability, visibility of provenance, reviewability, draft usability, pending-vs-accepted clarity, or workspace coherence.

### 10.3 Relationship to later packs

This Workstream E pack proves the main web control surface in the workstream context.

Later voice/companion and release packs should build on it rather than rediscovering workspace failures indirectly.

**Stable verification anchor:** `TESTPACK:WorkstreamE.ExecutionGuidance`

---

## 11. Evidence Expectations

When the Workstream E pack is executed, evidence reporting should capture at minimum:

- execution date/time,
- environment posture used,
- which included `TEST:` anchors were executed,
- pass/fail outcome,
- any `ManualOnly` checks performed,
- any `Deferred` entries and why,
- and a brief statement of whether the web workspace is considered trustworthy enough for daily operator use.

This should be summarized in the relevant Workstream E progress file and referenced in broader phase-exit or regression summaries where appropriate.

**Stable verification anchor:** `TESTPACK:WorkstreamE.EvidenceExpectations`

---

## 12. Operational Ready Definition for This Pack

The Workstream E verification pack should be considered operationally established when:

1. all included `TEST:` anchors are defined and mapped,
2. workspace route/navigation proof exists,
3. Today/Portfolio/Project surface proof exists,
4. triage/review visibility proof exists,
5. draft workspace context/variant/review-only proof exists,
6. pending-vs-accepted distinction proof exists,
7. persona selection/fallback proof exists,
8. and the pack can be run repeatably through browser and supporting API/integration harnesses.

At that point, Workstream E has a meaningful verification surface that later voice/companion and release work can trust.

**Stable verification anchor:** `TESTPACK:WorkstreamE.DefinitionOfOperationalReady`

---

## 13. Relationship to Later Packs

This pack establishes the proof surface for the main web workspace only.

Later packs should build on it as follows:

- **Workstream F** should prove voice and companion interactions hand off into and remain consistent with the workspace protected here,
- **Release** should compose representative browser-visible control-room proof into cross-workstream confidence,
- and later long-lived browser regression should treat the most critical operator journeys here as mandatory confidence checks.

This progression is consistent with the Glimmer build plan, workstream map, and Workstream G verification-estate design.

**Stable verification anchor:** `TESTPACK:WorkstreamE.RelationshipToLaterPacks`

---

## 14. Final Note

If Workstream E is implemented but not properly verified, Glimmer may still look attractive while failing at the one thing that matters most here: helping the operator make good decisions from clear, reviewable information.

That is the danger this pack is meant to prevent.

Its job is to prove that Glimmer’s main workspace is:

- reachable,
- legible,
- provenance-aware,
- review-safe,
- and operationally usable enough to become the real center of the product.

**Stable verification anchor:** `TESTPACK:WorkstreamE.Conclusion`
