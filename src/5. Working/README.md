# 5. Working

## Purpose

This folder contains **active working documents** for in-flight workstreams.

These are the session-continuity layer — not the long-term truth. They record:

- exact files inspected
- current findings
- mismatches between docs and code
- remediation items
- verification status
- blockers and human decision gates
- next-session handoff state

## Conventions

- Each active workstream should have a paired set:
  - `{workstream}_implementation_plan.md`
  - `{workstream}_implementation_progress.md`
- Keep the **Handoff Block** current at all times
- The progress file is the first thing the next session reads

## Template — Working Index

Create `00_working_index.md` to list all active working sets:

```markdown
# Working Documents Index

## Active Working Sets

### Workstream A — [Name]
- `workstream_a_{name}_implementation_plan.md`
- `workstream_a_{name}_implementation_progress.md`
```

