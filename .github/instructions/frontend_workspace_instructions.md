---
applyTo: "apps/web/**/*.{ts,tsx,js,jsx},apps/web/**/app/**/*.{ts,tsx,js,jsx},apps/web/**/components/**/*.{ts,tsx,js,jsx},apps/web/**/lib/**/*.{ts,tsx,js,jsx}"
---

# Glimmer — Frontend Workspace Module Instructions

## Purpose

This instruction file defines the module-scoped rules for Glimmer frontend workspace and UI implementation.

It supplements the global `.github/copilot-instructions.md` file and applies specifically to:

- React / Next.js frontend code,
- route and page structure,
- workspace views,
- triage and review components,
- draft workspace components,
- persona rendering components,
- and frontend state/query patterns.

These rules are stricter than generic frontend guidance because this part of Glimmer is where the operator experiences:

- review-first behavior,
- provenance visibility,
- accepted-vs-pending distinction,
- bounded persona expression,
- and the workspace-first operating model.

Framework alignment: Agentic Delivery Framework and Testing Strategy Companion.

---

## 1. Authority and Scope Rule

When working in this module area, the agent must stay aligned to the following control surfaces in order:

1. Requirements
2. Architecture
3. Build Plan
4. Verification
5. Global Copilot instructions
6. This module instruction file
7. Workstream working documents
8. Code

Do not let existing UI code or component habits silently override the documented Glimmer interaction model.

---

## 2. What This Module Must Preserve

Frontend workspace work must preserve these core Glimmer properties:

- **workspace-first interaction** rather than chat-first interaction,
- **reviewable visible artifacts** rather than hidden assistant state,
- **context before action** for important operator decisions,
- **clear accepted-vs-pending distinction**,
- **visible provenance and multi-account awareness** where it matters,
- **draft-only communication posture**,
- and **bounded persona rendering** that supports clarity rather than clutter.

These are load-bearing UX rules, not optional styling preferences.

---

## 3. Primary UI Posture Rules

### 3.1 Workspace-first, not chatbot-first

Do not build Glimmer as a single, unbounded assistant chat page.

The main operating model must remain a structured workspace with dedicated surfaces such as:

- Today
- Portfolio
- Project
- Triage
- Drafts
- Review

Conversation may appear inside these surfaces where useful, but it must not replace them.

### 3.2 Reviewable artifacts must be visible

Important outputs must appear as visible UI artifacts, such as:

- triage items,
- extracted actions,
- focus packs,
- drafts,
- review requests,
- and project summaries.

Do not bury important assistant output inside a transient toast, expandable afterthought, or isolated chat bubble.

### 3.3 Context before action

When the operator is asked to accept, amend, reject, defer, copy, or act, the UI should present enough surrounding context to support fast judgment.

Avoid interfaces that demand blind confirmation.

### 3.4 Pending vs accepted must be obvious

The UI must clearly distinguish between:

- candidate classifications vs accepted project assignment,
- extracted actions vs accepted work items,
- draft suggestions vs used text,
- and pending review vs settled state.

Do not visually flatten those states into one undifferentiated list.

---

## 4. Route and Page Structure Rules

### 4.1 Route by operating surface

Prefer route/page structure aligned to Glimmer’s operating surfaces.

Typical route families should map to capabilities such as:

- `/today`
- `/portfolio`
- `/projects/[id]`
- `/triage`
- `/drafts`
- `/review`
- `/briefings`
- `/voice` or embedded workspace voice surface

Do not create one vague catch-all assistant route as the primary UX.

### 4.2 Page purpose must be legible

Each major page should have a clear operational purpose. The operator should be able to understand, from the layout alone, what the page is for and what decisions it supports.

### 4.3 Preserve deep-linkability

Meaningful work items, projects, triage entries, and drafts should be reachable through stable routes or query-state patterns where appropriate.

This helps session continuity and review handoff.

---

## 5. Layout and Composition Rules

### 5.1 Favor control room composition

Page layouts should feel like an operating workspace, not a marketing site and not a toy chat shell.

Favor compositions that help the operator:

- orient quickly,
- inspect context,
- compare alternatives,
- and act deliberately.

### 5.2 Prioritize the important state first

Page composition should surface:

- what matters now,
- what needs review,
- what is blocked,
- and what has the strongest time pressure,

before low-value decorative elements.

### 5.3 Empty states should still guide work

Empty, loading, and error states should be explicit and useful.

Do not leave blank whitespace where the operator cannot tell whether:

- the system is loading,
- there is no data,
- or something broke.

### 5.4 Do not hide critical meaning in hover-only UI

Important review context, provenance, confidence, or status should not depend solely on hover interactions that are weak on touch devices and easy to miss.

---

## 6. Triage and Review UX Rules

### 6.1 Triage cards must show provenance

Triage items should visibly preserve, where relevant:

- source account,
- channel/provider,
- participants,
- thread context,
- project candidate,
- and ambiguity or confidence state.

Do not strip source meaning just because the UI is trying to feel clean.

### 6.2 Review actions must be explicit

Where review is required, the UI should provide clear actions such as:

- accept,
- amend,
- reassign,
- reject,
- defer,
- or mark informational.

Do not hide these behind vague menus if they are the main purpose of the surface.

### 6.3 Ambiguity must be visible, not softened away

If the backend marks something as ambiguous or review-needed, the UI must preserve that truth visibly.

Do not style uncertain outcomes to look final just because it looks cleaner.

### 6.4 Review queue is a real operating surface

If a review queue exists, treat it as a core control surface, not an overflow bucket.

The operator should be able to understand:

- what decision is needed,
- why it is needed,
- what the likely options are,
- and what happens next.

---

## 7. Draft Workspace Rules

### 7.1 Draft workspace is dedicated, not incidental

Draft generation should appear in a dedicated draft workspace or clearly bounded draft surface.

Do not render important reply drafts as stray assistant paragraphs on unrelated pages.

### 7.2 Drafts must carry context

The draft UI should show enough linked context, such as:

- source message or signal,
- project,
- stakeholder,
- tone posture,
- and relevant rationale,

for the operator to decide whether the draft is appropriate.

### 7.3 Draft variants should be comparable

If multiple variants exist, the UI should make them inspectable and comparable without forcing the operator through clumsy tab-hopping or hidden dropdown-only discovery.

### 7.4 No-auto-send posture must remain visible

UI actions around drafts should reinforce that the system drafts for review and copy/paste use.

Do not imply automatic sending or blur the distinction between generating and sending.

---

## 8. Today, Portfolio, and Project Rules

### 8.1 Today view is a chief-of-staff brief

The Today view should emphasize:

- top priorities,
- why they matter,
- reply pressure,
- deadline pressure,
- waiting-on items,
- and notable blockers.

Do not let it collapse into a generic backlog list.

### 8.2 Portfolio view is comparative

Portfolio UI should help the operator compare active projects across urgency, health, blockage, and attention demand.

Avoid designs that make the operator click into every project to discover which one matters most.

### 8.3 Project workspace should be relevance-first

Project pages should favor synthesis over chronology.

The operator should be able to orient quickly around:

- objective,
- phase,
- current pressure,
- milestones,
- next actions,
- decisions,
- risks,
- blockers,
- stakeholders,
- and recent meaningful signal.

Do not default to raw message feeds as the primary project experience.

---

## 9. Persona and Presentation Rules

### 9.1 Persona is supportive, not dominant

Glimmer’s visual persona should reinforce tone, continuity, and engagement without becoming the main event.

The operator is here to run work, not admire an assistant mascot.

### 9.2 Use only managed persona assets

Frontend persona rendering should use approved asset metadata and context-linked selection logic.

Do not invent arbitrary persona variants in code.

### 9.3 Always support graceful fallback

If a context-specific persona asset is unavailable, the UI must fall back cleanly to a default approved Glimmer asset.

### 9.4 Persona must not obscure control information

Do not let large persona presentation blocks push critical triage, draft, or priority information below the fold without reason.

---

## 10. Voice and Companion Surface Rules in Frontend

### 10.1 Web remains the canonical review surface

Even where voice and Telegram are supported, the frontend must preserve the web workspace as the authoritative review and control center.

### 10.2 Voice UI should feel integrated, not bolted on

Voice console or related voice controls should be part of the main workspace model, not a disconnected experimental widget.

### 10.3 Companion handoff should be obvious

When an interaction needs richer review than Telegram or voice can safely support, the UI should provide a clean handoff into the relevant workspace surface.

Do not pretend that companion channels can safely do everything.

---

## 11. Frontend Data and State Rules

### 11.1 Keep data loading explicit

Use explicit loading, empty, success, and error states.

Do not hide network or state uncertainty behind optimistic assumptions when the operator needs trustworthy situational awareness.

### 11.2 Favor typed contracts

Use typed frontend contracts aligned to API/application-service surfaces.

Do not casually consume loosely shaped JSON where strong typing would prevent UI drift.

### 11.3 Keep query/state boundaries inspectable

Prefer state patterns that keep:

- server data,
- local UI state,
- optimistic state,
- and transient editing state

clearly distinguishable.

### 11.4 Avoid frontend-only truth for operational state

Operationally meaningful truth should come from the backend/domain model.

The frontend may hold UI-local transient editing state, but it must not become a shadow system of record.

---

## 12. Accessibility and Clarity Rules

### 12.1 Clarity outranks visual cleverness

When a visual design choice competes with comprehensibility, choose comprehensibility.

### 12.2 Keyboard and focus behavior matter

Important review and draft workflows should be usable without fragile mouse-only behavior.

### 12.3 Status and state should not rely on color alone

Use labels, icons, headings, and textual cues where needed. Review state, ambiguity, acceptance status, and blocking status should not be color-only signals.

---

## 13. Browser-Testability Rules

### 13.1 Build for Playwright from the start

Major UI flows should be implemented in a way that supports reliable browser automation.

### 13.2 Stable selectors where needed

Use stable selectors, roles, labels, or explicit test IDs where browser automation would otherwise become brittle.

### 13.3 Reduce timing fragility

Avoid unnecessary animation dependence, hidden delayed rendering, or unstable DOM reshaping that makes browser proof fragile.

### 13.4 Test important journeys, not decorative motion

Frontend verification should prioritize operator workflows such as:

- opening Today view,
- reviewing a triage item,
- navigating a project,
- comparing or editing a draft,
- and resolving a review-required item.

---

## 14. Testing Expectations for This Module

When editing frontend/workspace code, the default proof target should include as appropriate:

- browser workflow tests for primary user journeys,
- API-contract-aware tests where UI depends on response shape,
- light component/unit tests for deterministic helpers,
- and integration checks for persisted review/draft/focus behavior where the frontend depends on those boundaries.

### 14.1 Frontend-specific proof rules

- Today/Portfolio/Project work must prove context visibility, not just rendering.
- Triage and Review work must prove reviewability and accepted-vs-pending distinction.
- Draft workspace work must prove context linkage, variant handling, and no-auto-send posture.
- Persona work must prove fallback behavior and bounded rendering.
- Voice/companion-related UI must prove handoff and continuity support rather than pretending to be standalone control centers.

### 14.2 Do not mark frontend work complete without browser-visible proof

If meaningful user workflow behavior changed and there is no executed browser proof or explicitly justified deferred/manual classification, the work is not done.

---

## 15. Preferred Frontend Session Workflow

When working in this module area, the default session sequence should be:

1. identify relevant `REQ:` anchors,
2. identify relevant `ARCH:` anchors,
3. identify relevant `PLAN:` anchors,
4. inspect current routes/components/state boundaries,
5. implement one bounded surface or interaction slice,
6. run the relevant browser/API proof,
7. update the workstream progress file,
8. report assumptions, blockers, and evidence clearly.

---

## 16. What to Do When the Docs Are Incomplete

If a frontend change needs a UI/interaction rule that does not yet have a stable anchor:

1. do not invent the UX architecture silently,
2. propose the missing anchor,
3. make only the smallest safe implementation move,
4. and record the gap in the relevant working document.

Typical examples include:

- a new review interaction pattern,
- a new persona presentation state,
- a new project workspace section behavior,
- or a new cross-surface handoff pattern.

---

## 17. Anti-Patterns to Avoid in This Module

Do not:

- reduce the product to a generic chat screen,
- hide review-required meaning behind decorative UI,
- flatten provenance out of triage views,
- make draft output look already approved,
- let persona rendering dominate operational content,
- create fragile route/state patterns that are hard to automate,
- invent frontend-only truth for operational state,
- or optimize for visual novelty over execution clarity.

---

## 18. Final Rule

When in doubt, make the frontend more:

- legible,
- reviewable,
- provenance-aware,
- bounded,
- and browser-testable.

Do not optimize for flashy assistant theater.
Optimize for a calm, high-signal control room that helps the operator make better decisions faster.
