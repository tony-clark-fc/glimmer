# 3. Build Plan

## Purpose

This folder contains the **build plan** — how delivery work is organized into workstreams, phases, and slices.

```
REQ: → ARCH: → PLAN: → TEST:
```

## Conventions

- Use `PLAN:` anchors for stable references (e.g., `PLAN:WorkstreamA.PlatformFoundations`)
- Each workstream should have a dedicated build-plan section
- Include decision gates where human input is required before proceeding
- Reference `REQ:` and `ARCH:` anchors to maintain traceability

## Suggested Structure

- `*_build_plan_index.md` — entry point and workstream summary
- `*_build_plan_strategy_and_scope.md` — overall delivery strategy
- `*_workstream_[name].md` — one per workstream with phases, steps, and dependencies
- `*_build_plan_governance_and_phasing.md` — governance rules and release phases

