# Prompt: Workstream Implementation Slice

Use this template when starting implementation on a workstream delivery slice.

## Pre-flight

1. **Identify the workstream anchor** — e.g., `PLAN:WorkstreamB.SurveyPlanLifecycle`
2. **Run retrieval** to gather context:
   ```bash
   python3 "src/9. Agent Tools/indexing/agent_retrieve.py" "PLAN:WorkstreamX.SliceName" --json
   ```
3. **Locate the delivery chain** for this slice:
   - `REQ:` — what requirement(s) does this satisfy?
   - `ARCH:` — what architectural constraints apply?
   - `PLAN:` — what is the defined scope and phasing?
   - `TEST:` — what scenarios must be proven?

## Inspection

4. **Read the workstream build-plan section** — understand scope, dependencies, human decision gates
5. **Read the working documents** (if they exist):
   - `src/5. Working/{workstream}_implementation_plan.md`
   - `src/5. Working/{workstream}_implementation_progress.md`
6. **Inspect current codebase state** — identify what's already built vs. what's missing
7. **Record findings** — note mismatches, drift, or incomplete implementation

## Implementation

8. **Work in small slices** — one bounded concern at a time
9. **Follow project conventions** — entities, services, permissions, localization
10. **Do not silently change architecture** — if the implementation requires deviation from `ARCH:` anchors, surface it
11. **Stop at human boundaries** — secrets, cloud resources, destructive operations, approval gates

## Verification

12. **Map to `TEST:` anchors** — which scenarios does this slice prove?
13. **Run relevant tests** — unit, integration, or manual as appropriate
14. **Record evidence** — test names, pass/fail, logs, screenshots

## Handoff

15. **Update the progress file** with:
    - files changed
    - findings
    - mismatches found
    - verification status
    - blockers / human decision gates
    - next-session handoff state

