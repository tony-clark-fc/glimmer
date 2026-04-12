# Prompt Templates

Reusable task templates for common agent workflows, anchored to the Agentic Delivery Framework's `REQ:`/`ARCH:`/`PLAN:`/`TEST:` chain.

## Available Templates

| Template | Purpose | When to Use |
|---|---|---|
| `workstream_implementation.md` | Step-by-step checklist for starting a workstream slice | Beginning implementation on any delivery slice |
| `architecture_review.md` | Review a proposed change against architecture + ADR register | Evaluating new features, drift, or design extensions |
| `verification_mapping.md` | Map implementation to `TEST:` anchors and find evidence gaps | Assessing verification coverage before claiming completion |
| `session_handoff.md` | Produce a durable handoff for the next session | End of any significant work session |

## Conventions

- Keep templates short and operational.
- Anchor back to the active control docs where relevant.
- Do not embed hidden policy that should instead live in `src/0. Framework/`, `src/3. Build Plan/`, or `.github/copilot-instructions.md`.
- Templates are guidance, not rigid scripts — adapt to the specific task.

## Deeper Reasoning — Agent Skills

For the reasoning and decision-making behind these templates, see the instructional skill documents in `src/8. Agent Skills/`:

| Template | Deepened By |
|----------|-------------|
| `workstream_implementation.md` | Skills 02 (Delivery Chain Reasoning), 04 (Code Change Discipline) |
| `architecture_review.md` | Skill 06 (Drift Detection and Remediation) |
| `verification_mapping.md` | Skills 02 (Delivery Chain Reasoning), 07 (Working with Anchors) |
| `session_handoff.md` | Skills 03 (Session Lifecycle), 05 (Documentation Maintenance) |

