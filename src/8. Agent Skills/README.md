# 8. Agent Skills

## Purpose

This folder contains **instructional skill documents** that teach coding agents *how to reason and work* within the Agentic Delivery Framework.

These are deeper than the short checklists in `src/9. Agent Tools/prompts/` (which say *what steps to follow*) and more practical than the framework document itself (which defines *what the methodology is*). Each skill document explains reasoning patterns, decision-making heuristics, and when/why to apply framework concepts.

Think of it as the **team onboarding guide** for any new agent session.

## Authority Model

Skill documents are **instructional guidance**, not authoritative control documents.

The active control set remains:

| Layer | Authority |
|-------|-----------|
| `1. Requirements/` | What must be true |
| `2. Architecture/` | How the system is shaped |
| `3. Build Plan/` | How delivery work is organized |
| `4. Verification/` | How completion is proven |

Skill documents teach the agent how to *apply* those control documents — they do not replace them.

If a skill document conflicts with a control document, the control document wins.

## Relationship to `9. Agent Tools/`

| Folder | Contains | Purpose |
|--------|----------|---------|
| `8. Agent Skills/` | Instructional markdown | Teach reasoning and decision-making |
| `9. Agent Tools/prompts/` | Operational checklists | Step-by-step task templates |
| `9. Agent Tools/indexing/` | Executable scripts | Retrieval and indexing |
| `9. Agent Tools/validation/` | Executable scripts | Freshness and integrity checks |

**Prompts** say "do these steps." **Skills** explain "here's how to think about it and why."

## Skill Index

| # | Skill | Covers | Related Prompts |
|---|-------|--------|-----------------|
| 00 | [Agent Commands](00_commands.md) | `^warm-up`, `^what-next`, `^cool-down`, and other operator shortcuts | — |
| 01 | [Retrieval and Context Gathering](01_retrieval_and_context_gathering.md) | Using retrieval tools, context-window management, interpreting results | — |
| 02 | [Delivery Chain Reasoning](02_delivery_chain_reasoning.md) | Tracing REQ→ARCH→PLAN→TEST, detecting orphans | `workstream_implementation.md` |
| 03 | [Session Lifecycle](03_session_lifecycle.md) | Session start, checkpoints, handoff | `session_handoff.md` |
| 04 | [Code Change Discipline](04_code_change_discipline.md) | Inspecting first, working in slices, human boundaries | `workstream_implementation.md` |
| 05 | [Documentation Maintenance](05_documentation_maintenance.md) | Updating working docs, staleness, change control | `session_handoff.md` |
| 06 | [Drift Detection and Remediation](06_drift_detection_and_remediation.md) | Spotting drift, classification, remediation workflow | `architecture_review.md` |
| 07 | [Working with Anchors](07_working_with_anchors.md) | Creating, using, citing, maintaining anchors | `verification_mapping.md` |

## Conventions

1. **Each skill document follows a consistent structure:** Purpose → When to Use → Core Concepts → Reasoning Patterns → Worked Examples → Common Mistakes → Related Skills.
2. **Reference, don't duplicate.** Point to framework sections and control documents rather than copying their content.
3. **Keep skills stable.** These should change infrequently — only when the framework methodology evolves.
4. **Do not define new anchors here.** Skill documents reference existing `REQ:`/`ARCH:`/`PLAN:`/`TEST:` anchors but should not establish new authoritative anchors.
5. **Tech-stack specifics belong in copilot-instructions.** Skill `04` may reference common framework patterns but defers to `.github/copilot-instructions.md` for detailed conventions.

