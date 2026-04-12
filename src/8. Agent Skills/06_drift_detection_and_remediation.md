# Skill 06 — Drift Detection and Remediation

## Purpose

Teach the agent how to spot architecture drift, classify it correctly, and take appropriate action — without silently legitimizing or silently breaking things.

## When to Use

- When code doesn't match what `ARCH:` anchors describe
- When you find undocumented design decisions in the codebase
- When an implementation contradicts an existing ADR
- When you're reviewing code for alignment before extending it

## Core Concepts

### What Is Drift?

**Architecture drift** occurs when the as-built codebase diverges from the documented architectural intent. Not all divergence is bad — some is intentional and transitional. The agent's job is to **detect and classify**, not to judge.

### The Classification Taxonomy

| Classification | Meaning | Agent Action |
|---------------|---------|--------------|
| **Acceptable current-state** | Code implements a reasonable approach that doesn't contradict architecture — architecture just hasn't described this specific detail | Note in progress file. No remediation needed. |
| **Transitional implementation** | Code is intentionally interim — a stepping stone toward the architectural target | Note the transitional nature AND the target state. Track in working docs. |
| **Drift requiring remediation** | Code contradicts an approved `ARCH:` anchor or ADR | Record as remediation item. Do not extend the drift. Propose a fix path. |
| **Candidate ADR** | Code embodies a material architectural decision not yet captured in the ADR register | Draft an ADR entry. Flag for human review. |

### Why Classification Matters

Without classification, drift is invisible. It accumulates until:
- New work builds on drifted foundations, compounding the problem
- A refactoring becomes necessary that nobody planned for
- The documentation becomes unreliable because it doesn't match the code

## Reasoning Patterns

### Pattern 1 — "This code doesn't match the architecture doc"

```text
1. Read the relevant ARCH: section carefully
2. Read the code carefully
3. Ask: "Is the architecture wrong, or is the code wrong?"
4. Check the ADR register for related decisions
5. Classify:
   ├── Architecture is aspirational, code is what's built
   │   → Acceptable current-state or transitional
   ├── Architecture was approved, code deviates without reason
   │   → Drift requiring remediation
   ├── Code implements something better than what's documented
   │   → Candidate ADR (capture what the code decided)
   └── Unclear
       → Record the finding, flag for human judgment
```

### Pattern 2 — "I found an undocumented design decision"

```text
1. Is this decision trivial (naming convention, minor refactoring)?
   → Note it, no ADR needed

2. Is this decision material (new pattern, new integration, changed data model)?
   → Draft a candidate ADR:
     - Title: what was decided
     - Context: why it was needed
     - Decision: what the code does
     - Consequences: what this affects
     - Status: "Observed in code — proposed for ADR register"

3. Record the finding in the progress file
4. Flag for human review
```

### Pattern 3 — "I'm about to extend drifted code"

```text
STOP. Do not extend drift.

1. Record the drift in the progress file
2. Classify it using the taxonomy above
3. Options:
   a. Fix the drift first, then extend (if small and safe)
   b. Note the drift and ask the human for direction
   c. Implement the extension in a way that doesn't deepen the drift
      (e.g., implement new code correctly, note that old code needs remediation)
4. Never pretend the drift doesn't exist
```

## Detection Signals

### Strong Drift Signals

| Signal | Likely Classification |
|--------|----------------------|
| Entity has properties not in architecture data model | Candidate ADR or drift |
| Service uses a pattern explicitly prohibited in `ARCH:` | Drift requiring remediation |
| Code references external service not in integration architecture | Candidate ADR |
| Permission structure differs from `ARCH:` permission model | Drift requiring remediation |
| Code uses `DateTime.Now` when framework time abstraction is mandated | Drift (framework anti-pattern) |

### Weak Drift Signals (Inspect Before Classifying)

| Signal | May Be |
|--------|--------|
| Extra helper methods not in architecture | Acceptable implementation detail |
| Different DTO shape than architecture sketch | Acceptable if semantically equivalent |
| Code has TODO comments referencing future architecture | Transitional implementation |
| Tests cover scenarios not in verification catalog | Good initiative (but catalog should be updated) |

## Remediation Workflow

When drift is confirmed:

```text
1. RECORD — Add a remediation item to the progress file:
   - What: describe the drift
   - Where: file(s) and line(s)
   - Classification: drift / transitional / candidate ADR
   - Impact: what's affected if this isn't fixed
   - Proposed action: fix path or ADR proposal

2. CLASSIFY — Use the taxonomy. Be precise.

3. PROPOSE — Draft the fix or ADR entry.
   - For small fixes: implement if within scope
   - For large fixes: propose as a work package
   - For ADR candidates: draft the ADR entry

4. DO NOT implement large remediations without human approval.

5. UPDATE working docs — ensure the drift is tracked until resolved.
```

## Common Mistakes

| Mistake | Why It's Harmful | Better Approach |
|---------|------------------|-----------------|
| Silently fixing drift without recording it | Future sessions don't know it happened | Record the finding AND the fix |
| Silently rewriting docs to match drifted code | Legitimizes unreviewed drift | Classify and propose — let the human decide |
| Extending drifted code without noting the drift | Deepens the problem | STOP, record, classify, then decide how to proceed |
| Calling everything "drift" | Noise — trivial differences aren't drift | Use the classification taxonomy |
| Creating ADRs for trivial decisions | ADR register becomes noisy | ADRs are for material architectural decisions only |

## Related Skills

- [02 — Delivery Chain Reasoning](02_delivery_chain_reasoning.md) — tracing anchors to spot misalignment
- [04 — Code Change Discipline](04_code_change_discipline.md) — the "should I proceed?" decision tree
- [07 — Working with Anchors](07_working_with_anchors.md) — anchors as drift detection reference points

