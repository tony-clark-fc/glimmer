# Skill 03 — Session Lifecycle

## Purpose

Teach the agent how to start, run, and end a work session so that progress is durable and the next session (human or agent) can resume without re-discovering what was already known.

## When to Use

- Every work session. This is not optional — it's the operating rhythm.

## Core Concepts

### The Session Problem

AI coding agents have **no memory between sessions**. When the conversation ends, everything is lost — unless it's written down in the repository.

Working documents (`src/5. Working/`) are the agent's persistent memory. The handoff block is the most critical artifact.

### Three Phases

| Phase | Goal | Key Actions |
|-------|------|-------------|
| **Start** | Orient to current state | Freshness check, read handoff, scope the session |
| **Mid** | Execute with checkpoints | Implement in slices, update progress, stop at boundaries |
| **End** | Preserve state for next session | Write handoff block, verification status, commit-ready state |

## Phase 1 — Session Start

### Step-by-Step

```text
1. Check index freshness:
   python3 "src/9. Agent Tools/validation/check_agent_index_freshness.py"

2. If stale, regenerate:
   python3 "src/9. Agent Tools/indexing/generate_agent_index.py"

3. Read the handoff block from the relevant progress file:
   src/5. Working/{workstream}_implementation_progress.md

4. Read the "Next exact step" — this is your starting point.

5. Read the "Blockers" — if blockers exist, address them first or ask the human.

6. Inspect the last-changed files listed in the handoff to confirm they match your expectations.

7. Scope the session: what can you realistically complete? Don't plan beyond 3–5 slices.
```

### Freshness Decision

```text
"Is the index fresh?"
├── Yes → Proceed with retrieval
├── Stale by < 1 day → Proceed with caution, note staleness
└── Stale by > 1 day → Regenerate before relying on retrieval
```

### If No Progress File Exists

This means you're starting a new workstream or the first session on a task:

1. Create both working documents (plan + progress) before writing code
2. Fill the plan with objective, scope, relevant anchors, phased approach
3. Initialize the progress file with an empty handoff block
4. Then proceed to implementation

## Phase 2 — Mid-Session

### Working Rhythm

```text
For each slice of work:
  1. Identify the bounded concern (one entity, one service method, one page)
  2. Trace the delivery chain (Skill 02) — know your PLAN: and ARCH: anchors
  3. Inspect existing code before making changes
  4. Implement the change
  5. Verify (run tests, check errors, manual inspection)
  6. Record what was done and what was found
```

### When to Checkpoint

Update the progress file mid-session when:

- You've completed a logical slice and are moving to the next
- You've found a mismatch or drift that needs recording
- You've hit a blocker that may terminate the session
- The session has been running for a while and you want to preserve state

### When to Stop

Stop and surface to the human when:

- A **human boundary** is reached (credentials, cloud resources, destructive operations, approval gates)
- A **design decision** is needed that isn't covered by existing `ARCH:` anchors
- **Architecture drift** is discovered that you can't classify as "acceptable current-state"
- A **blocker** prevents further progress and cannot be resolved within the session
- You've completed the planned scope — don't invent more work

## Phase 3 — Session End

### The Handoff Block

This is the single most important artifact of every session. Write it into the progress file:

```markdown
## Handoff Block
- **Current phase:** [where in the plan this work sits]
- **Last completed step:** [what was just finished — be specific]
- **Next exact step:** [the single most important thing to do next]
- **Blockers:** [anything preventing progress, or "none"]
- **Human input required:** [decisions, credentials, approvals, or "none"]
- **Files most recently changed:** [list of files touched this session]
- **Relevant `ARCH:` anchors:** [anchors consulted or affected]
- **Relevant `PLAN:` anchors:** [plan anchors this work maps to]
- **Relevant `TEST:` anchors:** [test anchors that should be verified]
```

### The Verification Status

Below the handoff, add or update:

```markdown
## Verification Status
- **Critical scenarios passing:** [list with evidence, or "none newly proven"]
- **Critical scenarios pending:** [list]
- **High-priority scenarios pending:** [list]
- **Manual-only scenarios:** [list]
- **Environment blockers:** [list or "none"]
```

### Quality Check

Before ending the session, confirm:

- [ ] Handoff block is written and specific
- [ ] "Next exact step" is clear enough for a cold start
- [ ] Files changed are listed
- [ ] Mismatches or drift found are recorded
- [ ] Verification status reflects what was actually proven (not just implemented)
- [ ] Blockers are explicitly surfaced

### The Gold Standard

> A new session — whether the same agent, a different agent, or the human — should be able to resume from the handoff block without reading anything else first. If it has to re-inspect the full document set, the handoff failed.

## Common Mistakes

| Mistake | Why It's Harmful | Better Approach |
|---------|------------------|-----------------|
| Skipping the freshness check | May work from stale context | Always check at session start |
| Not reading the handoff block | Re-discovers what was already known | Read it first — it's the starting point |
| "Next step: continue implementation" | Too vague — next session wastes time scoping | Be specific: "Implement CreateAsync in SensorDeploymentAppService" |
| Implementing without updating progress | Session crashes → progress lost | Checkpoint after each slice |
| Ending without a handoff block | Next session starts from zero | Always write the handoff, even for short sessions |
| Over-planning the session | Plans 10 slices, completes 2 | Scope to 3–5 realistic slices |

## Related Skills

- [01 — Retrieval and Context Gathering](01_retrieval_and_context_gathering.md) — context gathering at session start
- [05 — Documentation Maintenance](05_documentation_maintenance.md) — what to update and when

