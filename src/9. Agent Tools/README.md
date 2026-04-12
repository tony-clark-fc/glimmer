# 9. Agent Tools

## Purpose

This folder is the standard home for **repository-local agent skills, helper tools, and support artifacts**.

It exists so operators and coding agents have one predictable place for:

- local retrieval/indexing helpers
- validation and freshness checks
- small support scripts used during agentic delivery
- generated tool-side artifacts that should not be confused with the authoritative Markdown control docs

## Authority Rule

Files in `src/9. Agent Tools/` are **support artifacts**, not the source of truth.

The active control set remains:

- `src/0. Framework/`
- `src/1. Requirements/`
- `src/2. Architecture/`
- `src/3. Build Plan/`
- `src/4. Verification/`

If a tool output conflicts with an active control document, treat the tool output as suspect until reconciled.

## Relationship to `8. Agent Skills/`

| Folder | Contains | Purpose |
|--------|----------|---------|
| `8. Agent Skills/` | Instructional markdown documents | Teach the agent *how to reason* about framework workflows |
| `9. Agent Tools/prompts/` | Operational checklists | Step-by-step task templates ("do these steps") |
| `9. Agent Tools/indexing/` | Executable Python scripts | Retrieval and index generation |
| `9. Agent Tools/validation/` | Executable Python scripts | Freshness and integrity checks |

**Skills** explain the "why" and "how to think about it." **Prompts** list the "what to do." **Scripts** provide the tools.

For deeper reasoning behind each prompt template, see the cross-referenced skill documents in `src/8. Agent Skills/README.md`.

## Suggested Structure

```text
src/9. Agent Tools/
├── README.md
├── indexing/        # retrieval/index generation helpers and outputs
├── validation/      # freshness/integrity checks
├── prompts/         # optional reusable agent task templates
└── scratch/         # optional temporary local artifacts not intended as authority
```

## Conventions

1. Prefer small, single-purpose scripts.
2. Keep generated artifacts clearly named and reproducible.
3. Do not place authoritative requirements, architecture, plan, or verification content here.
4. If a tool becomes material to delivery control, reference it from the relevant `PLAN:` and `TEST:` anchors.
5. If a tool embodies a significant architectural decision, record or propose the relevant ADR rather than letting the tool define policy implicitly.

## Initial Intended Uses

- local documentation retrieval helpers for the active markdown corpus
- retrieval-map generation such as `AGENT_INDEX.json`
- stale-index/freshness validation
- reusable prompt templates for common agent workflows
- small supporting utilities for future agent workflows

## Current Contents

- `indexing/generate_agent_index.py` — builds `src/9. Agent Tools/indexing/AGENT_INDEX.json` with keywords, frontmatter parsing, and cross-document relationships
- `indexing/agent_retrieve.py` — resolves likely documents and bounded snippets from the generated index (scores against anchors, keywords, headings, and more)
- `indexing/AGENT_INDEX.json` — generated retrieval artifact (not hand-maintained)
- `validation/check_agent_index_freshness.py` — checks whether the generated index is missing or stale
- `prompts/workstream_implementation.md` — checklist for starting a workstream delivery slice
- `prompts/architecture_review.md` — template for reviewing changes against architecture and ADR register
- `prompts/verification_mapping.md` — template for mapping implementation to `TEST:` anchors
- `prompts/session_handoff.md` — template for producing durable end-of-session handoffs

## CI / Git Hooks

A pre-commit hook is available at `.githooks/pre-commit` that warns when `AGENT_INDEX.json` is stale.

To enable:
```bash
git config core.hooksPath .githooks
```
