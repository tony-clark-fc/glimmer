# Skill 04 — Code Change Discipline

## Purpose

Teach the agent how to make code changes that are aligned with the framework, architecturally sound, and verifiable — while knowing when to stop and ask.

## When to Use

- Every time you are about to write or modify code
- When evaluating whether a code change requires architectural review

## Core Concepts

### Inspect Before Writing

Never modify code you haven't read. The codebase is the strongest evidence of current-state truth (see framework principles). Before changing a file:

1. Read the file (or at least the relevant section)
2. Understand what it currently does
3. Identify the governing `ARCH:` anchor
4. Know what `TEST:` scenarios cover this area

### Work in Small Slices

One bounded concern per slice:
- One entity and its supporting layers
- One app service method
- One page or UI component
- One configuration change

Complete each slice fully (implement → verify → record) before starting the next.

### The "Should I Proceed?" Decision Tree

```text
"I'm about to make a change."
│
├── "Is there an ARCH: anchor governing this area?"
│   ├── Yes → "Does my change align with it?"
│   │   ├── Yes → Proceed
│   │   ├── Extends it → Propose ADR, note in progress, proceed carefully
│   │   └── Contradicts it → STOP. Record as drift. See Skill 06.
│   └── No → "Is this a trivial implementation detail?"
│       ├── Yes → Proceed
│       └── No → Surface the gap — this may need an ARCH: anchor
│
├── "Am I at a human boundary?"
│   Secrets, cloud resources, destructive DB operations,
│   approval gates, production deployments
│   └── Yes → STOP. Document what's needed and why.
│
├── "Am I inventing something?"
│   New endpoints, new entities, new patterns, new abstractions
│   └── "Was this asked for?"
│       ├── Yes (in PLAN: or by user) → Proceed
│       └── No → STOP. Surface the suggestion, don't implement silently.
│
└── "Is this a risky change?"
    Data model changes, auth changes, cross-cutting concerns
    └── Yes → Extra caution: trace the full chain, verify thoroughly
```

## Implementation Patterns

### Pattern 1 — Adding a New Entity

Follow the Entity Generation Pattern from copilot-instructions:

1. Domain.Shared  → Constants class, enums
1. Shared Layer     → Constants class, enums
2. Domain           → Entity with proper constructors, repository interface (if custom)
3. Contracts        → DTOs, service interface
4. Application      → App service with authorization, mapping profile
5. Persistence      → DbSet, entity configuration, migration
6. Web              → Pages (if applicable)
7. Localization     → Keys in resource files
8. Permissions      → Defined and registered
9. Tests            → Integration tests

At each layer, check: does this align with the governing `ARCH:` anchor?

### Pattern 2 — Modifying an Existing Service

```text
1. Read the existing service implementation
2. Read the related DTOs and interfaces
3. Identify the ARCH: and PLAN: anchors
4. Make the smallest change that satisfies the requirement
5. Update tests to cover the change
6. Update localization if UI-visible text changed
7. Record in progress file
```

### Pattern 3 — Fixing a Bug or Mismatch

```text
1. Read the code exhibiting the bug
2. Is this a case where code contradicts ARCH:?
   ├── Yes → Classify as drift (Skill 06), fix toward the architecture
   └── No → Fix the implementation bug
3. Verify the fix against relevant TEST: scenarios
4. Check for similar patterns elsewhere — the bug may be systemic
5. Record the finding and fix in progress file
```

## Tech-Stack Alignment

For ABP-specific conventions (entity patterns, DI patterns, async handling, anti-patterns), defer to the detailed guidance in `.github/copilot-instructions.md`. Key reminders:
For project-specific conventions (entity patterns, DI patterns, async handling, anti-patterns), defer to the detailed guidance in `.github/copilot-instructions.md`. Key reminders:
- Use `IRepository<T>`, never `DbContext` directly in app services
- Use repository abstractions, not raw database contexts in services
- Use framework-provided ID generators where available
- Use framework-provided time abstractions where available
- Async all the way — never block on async code
- Business logic in application services, never in controllers

## Verification After Changes

Every code change should be verified proportionate to its risk:

| Risk Level | Verification Required |
|------------|----------------------|
| **Low** (localization, cosmetic) | Compile check, visual inspection |
| **Medium** (service logic, DTOs) | Compile + run existing tests + check errors |
| **High** (data model, auth, cross-cutting) | Full test run + manual verification + regression check |

After making changes:
1. Check for compile/lint errors in changed files
2. Run relevant tests
3. Map to `TEST:` anchors — which scenarios are now proven?
4. Update verification status in the progress file

## Common Mistakes

| Mistake | Why It's Harmful | Better Approach |
|---------|------------------|-----------------|
| Modifying code you haven't read | May break existing behavior | Always inspect first |
| Making multiple unrelated changes at once | Hard to verify, hard to revert | One slice at a time |
| Silently adding architecture | Agent invents patterns nobody asked for | Surface extensions, don't implement silently |
| Ignoring test failures | "It compiles" ≠ "it works" | Fix or explain every failure |
| Using ABP anti-patterns | Creates tech debt and diverges from framework | Follow copilot-instructions conventions |
| Using framework anti-patterns | Creates tech debt and diverges from framework | Follow copilot-instructions conventions |

## Related Skills

- [02 — Delivery Chain Reasoning](02_delivery_chain_reasoning.md) — tracing the chain before coding
- [06 — Drift Detection and Remediation](06_drift_detection_and_remediation.md) — what to do when code contradicts architecture
- [07 — Working with Anchors](07_working_with_anchors.md) — citing anchors in code comments

