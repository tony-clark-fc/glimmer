# Skill 05 — Documentation Maintenance

## Purpose

Teach the agent when, what, and how to update documentation so that the repository's control surface stays current without overstepping authority boundaries.

## When to Use

- After completing any implementation slice
- When findings reveal mismatches between docs and code
- At the end of every session (handoff block)
- When the human asks for documentation updates

## Core Concepts

### What the Agent May Update Autonomously

| Document Type | Agent May Update? | Notes |
|---------------|-------------------|-------|
| **Progress files** (`src/5. Working/*_progress.md`) | ✅ Yes — this is expected | Handoff blocks, verification status, progress logs |
| **Plan files** (`src/5. Working/*_plan.md`) | ⚠️ Cautiously | Record findings, update status. Don't change scope or objectives. |
| **Verification status** | ✅ Yes | Update what's proven, pending, blocked |
| **Localization files** (`en.json`) | ✅ Yes | Add keys for new features |
| **Code comments** | ✅ Yes | Add anchor citations, clarify intent |

### What the Agent Must Propose (Not Unilaterally Change)

| Document Type | Agent Action |
|---------------|--------------|
| **Requirements** (`src/1. Requirements/`) | Propose new or changed `REQ:` — record in progress file for human review |
| **Architecture** (`src/2. Architecture/`) | Propose updates — record as candidate ADR or remediation item |
| **Build Plan** (`src/3. Build Plan/`) | Propose scope changes — record in progress file |
| **Verification catalog** (`src/4. Verification/`) | Propose new `TEST:` scenarios — can draft, but human approves |
| **ADR register** | Propose new ADRs — draft the entry, flag for human approval |
| **Framework docs** (`src/0. Framework/`) | Never change without explicit instruction |
| **Copilot instructions** (`.github/`) | Never change without explicit instruction |

### The Key Principle

> The agent maintains the working surface (progress, status, findings). The human owns the control surface (requirements, architecture, plan, verification).

## Reasoning Patterns

### Pattern 1 — "I just completed a slice. What do I update?"

```text
1. Progress file:
   - Add a timestamped entry to the progress log
   - List files changed
   - Note findings or mismatches
   - Update verification status

2. Plan file (if needed):
   - Mark the completed slice as done
   - Note any scope adjustments discovered during implementation

3. Localization (if UI strings added):
   - Add keys to en.json

4. Code comments (if applicable):
   - Add ARCH: anchor citations to non-obvious implementations
```

### Pattern 2 — "I found a mismatch between docs and code. What do I do?"

```text
1. Do NOT silently rewrite the docs to fit the code.
2. Classify the difference:
   ├── Acceptable current-state implementation
   │   → Note it in progress file, no further action
   ├── Transitional implementation
   │   → Note it with the target state and when it should be resolved
   ├── Architecture drift requiring remediation
   │   → Record as remediation item, see Skill 06
   └── Candidate ADR
       → Draft an ADR entry, flag for human review
3. Record the classification in the progress file.
```

### Pattern 3 — "The handoff block is stale. How do I update it?"

The handoff block should be **replaced**, not appended to. It represents the current state, not a history:

```text
1. Read the existing handoff block
2. Replace all fields with current values
3. "Last completed step" → what you just finished
4. "Next exact step" → the single most important next action
5. "Blockers" → current blockers (clear resolved ones)
6. "Files most recently changed" → THIS session's files
7. Update the verification status block below it
```

## Staleness Signals

Watch for these signs that documentation is becoming stale:

| Signal | Action |
|--------|--------|
| Progress file "Next step" doesn't match current state | Update the handoff block |
| Architecture doc describes entities that don't exist in code | Record as potential drift |
| Build plan references completed work as "pending" | Propose plan update |
| Verification status says "passing" but tests don't exist | Correct the verification status |
| Working doc references deleted or renamed files | Update the references |

## What "Current" Means

- **Progress files**: Updated at the end of every session (minimum)
- **Plan files**: Updated when scope or understanding changes
- **Verification status**: Updated whenever evidence changes
- **Handoff block**: Always reflects the state at session end, not session start
- **Architecture docs**: Updated only with human approval

## Common Mistakes

| Mistake | Why It's Harmful | Better Approach |
|---------|------------------|-----------------|
| Rewriting architecture to match code | Silently legitimizes drift | Classify and record the difference |
| Not updating progress files | Next session loses context | Update after every slice |
| Appending to handoff block instead of replacing | Block becomes a log, not state | Replace with current values |
| Changing build plan scope without human approval | Agent deciding what to build | Propose scope changes, don't enact them |
| Over-documenting trivial changes | Noise in working docs | Record meaningful findings, not every line changed |
| Leaving verification status as "passing" when untested | False confidence | Be honest — "likely but unproven" is better |

## Related Skills

- [03 — Session Lifecycle](03_session_lifecycle.md) — when documentation updates happen in the session flow
- [06 — Drift Detection and Remediation](06_drift_detection_and_remediation.md) — handling doc-code mismatches

