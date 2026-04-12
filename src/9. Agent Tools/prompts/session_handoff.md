# Prompt: Session Handoff

Use this template at the end of a work session to produce a durable handoff for the next session.

## Handoff Block

Update the relevant progress file (`src/5. Working/{workstream}_implementation_progress.md`) with:

```markdown
## Handoff Block
- **Current phase:** [where in the plan this work sits]
- **Last completed step:** [what was just finished]
- **Next exact step:** [the single most important thing to do next]
- **Blockers:** [anything preventing progress]
- **Human input required:** [decisions, credentials, approvals needed]
- **Files most recently changed:** [list of files touched this session]
- **Relevant `ARCH:` anchors:** [architecture anchors consulted or affected]
- **Relevant `PLAN:` anchors:** [plan anchors this work maps to]
- **Relevant `TEST:` anchors:** [test anchors that should be verified]
```

## Verification Status

```markdown
## Verification Status
- **Critical scenarios passing:** [list or "none newly proven"]
- **Critical scenarios pending:** [list]
- **High-priority scenarios pending:** [list]
- **Manual-only scenarios:** [list]
- **Environment blockers:** [list or "none"]
```

## Checklist

Before ending the session, confirm:

- [ ] Progress file is updated with current handoff block
- [ ] Files changed are listed
- [ ] Any mismatches or drift found are recorded
- [ ] Verification status reflects what was actually proven (not just implemented)
- [ ] Blockers and human decision gates are explicitly surfaced
- [ ] The "next exact step" is specific enough for a new session to resume without re-reading everything

## Key Principle

> The next session — whether human or agent — should be able to resume from this handoff block without needing to re-inspect the full document corpus. If the handoff is vague, the next session will waste context window rediscovering what was already known.

