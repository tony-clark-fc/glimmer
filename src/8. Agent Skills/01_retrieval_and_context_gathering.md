# Skill 01 — Retrieval and Context Gathering

## Purpose

Teach the agent how to efficiently gather the right context before reasoning or coding, without flooding the context window with irrelevant material.

## When to Use

- At the start of every significant task (before writing code or docs)
- When the task topic is unfamiliar or spans multiple documents
- When you need to find the controlling anchors for a piece of work

## Core Concepts

### The Retrieval Tool Chain

The repository provides three scripts in `src/9. Agent Tools/`:

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `check_agent_index_freshness.py` | Detect stale index | Start of session |
| `generate_agent_index.py` | Rebuild the index | When stale |
| `agent_retrieve.py` | Find relevant docs and snippets | Before reasoning over any topic |

### The Retrieval Hierarchy

Results are ranked. Prefer them in this order:

1. **Active canonical control docs** (`status: active`, `canonical: true`) — requirements, architecture, build plan, verification
2. **Active non-canonical docs** — supporting architecture docs, decision registers
3. **Working documents** — implementation plans and progress files
4. **Legacy/source-evidence docs** — older documents preserved for context

### Anchors vs. Keywords

The retrieval tool scores **formal anchors** (`REQ:`, `ARCH:`, `PLAN:`, `TEST:`) higher than keyword matches. This is intentional — anchors are precise control points.

- If you know the anchor name, search for it directly: `"ARCH:SurveyDataModel"`
- If you don't know the anchor, search by topic: `"survey data model"` — and look for anchor names in the results

## Reasoning Patterns

### Pattern 1 — Starting a New Task

```text
1. What is the topic?
2. Is the index fresh?        → check_agent_index_freshness.py
3. Search for the topic       → agent_retrieve.py "<topic>" --json
4. Read the top-ranked snippet
5. Is there a formal anchor?  → Note it for delivery chain tracing
6. Is the snippet sufficient? → If yes, proceed. If no, open the full document.
```

### Pattern 2 — Following a Known Anchor

```text
1. Search for the anchor directly → agent_retrieve.py "PLAN:WorkstreamA.Slice3" --json
2. Read the returned snippet — it will show the defining section
3. Check `referenced_by` in the index — find where else this anchor is used
4. This gives you the full delivery chain for the anchor
```

### Pattern 3 — Broadening When Results Are Insufficient

```text
1. First search returned poor results
2. Try a broader keyword query
3. Try searching for the parent anchor (e.g., "PLAN:WorkstreamA" instead of a specific slice)
4. If still insufficient, read the relevant index file directly:
   - Architecture index: src/2. Architecture/1_*_index_*.md
   - Build plan index: src/3. Build Plan/01_*_index_*.md
5. Only as a last resort, scan directory listings for relevant files
```

## Context Window Budget

The context window is finite. Manage it deliberately:

- **Don't dump entire documents** when a snippet will do
- **Don't read all architecture files** — read the one relevant section
- **Don't re-read files you've already read** in this session
- **Do read multiple small files** rather than one massive concatenation
- **Do note anchor names** so you can return to a section later without re-reading

### Budget Decision Tree

```text
"Do I need this context?"
├── "I know the exact anchor/section" → Read just that section
├── "I know the file but not the section" → Read headings first, then the section
├── "I know the topic but not the file" → Use retrieval, read the snippet
└── "I'm exploring" → Use retrieval broadly, scan results, then narrow
```

## Common Mistakes

| Mistake | Why It's Harmful | Better Approach |
|---------|------------------|-----------------|
| Reading every architecture file at session start | Fills context window before real work begins | Use retrieval to find the 1–2 relevant sections |
| Ignoring the index freshness check | Stale index → wrong documents ranked high | Always check freshness at session start |
| Searching only by keyword | Misses the authoritative control points | Search for formal anchors when possible |
| Re-reading files already in context | Wastes context budget | Track what you've already read |
| Opening the full framework doc | 1900+ lines consumed unnecessarily | Retrieve the relevant section only |

## Related Skills

- [02 — Delivery Chain Reasoning](02_delivery_chain_reasoning.md) — what to do once you've gathered context
- [03 — Session Lifecycle](03_session_lifecycle.md) — when retrieval fits in the session flow

