# Indexing Tools

## Purpose

This folder contains local documentation retrieval helpers for the repository.

The toolset is intentionally small and dependency-free (Python standard library only):

- `generate_agent_index.py` builds a machine-readable index from the markdown control surface
- `agent_retrieve.py` resolves likely documents, anchors, and bounded snippets from that index
- `AGENT_INDEX.json` is the generated retrieval artifact when the index is built locally

## Index Features

The generated index includes per document:

- **keywords** — automatically extracted from headings, path segments, anchor names, and body text (max 15 per doc)
- **anchors** — regex-extracted formal anchors (`REQ:`, `ARCH:`, `PLAN:`, `TEST:`, etc.) split into `defined_anchors` and `mentioned_anchors`
- **frontmatter** — YAML frontmatter is parsed when present (supports `status`, `canonical`, `last_updated`)
- **relationships** — cross-document links detected via shared anchors (`references` and `referenced_by`)
- **headings**, **domains**, **description**, **authority_rank**, **source_modified_utc**

## Usage

From the repository root:

```bash
# Generate/regenerate the index
python3 "src/9. Agent Tools/indexing/generate_agent_index.py"

# Retrieve by anchor
python3 "src/9. Agent Tools/indexing/agent_retrieve.py" "PLAN:WorkstreamA.DocumentRetrievalLayer"

# Retrieve by free text
python3 "src/9. Agent Tools/indexing/agent_retrieve.py" "documentation retrieval layer" --top 3

# JSON output for agent consumption
python3 "src/9. Agent Tools/indexing/agent_retrieve.py" "authentication model" --json
```

## Notes

- The index is generated from markdown documents; it is not authoritative itself.
- The retrieval workflow is designed to prefer active/canonical docs over working or legacy evidence.
- Keywords are auto-extracted and capped — no manual curation needed.
- Frontmatter overrides (status, canonical) take effect only when present; path-based classification is the default.
- Refresh the index after documentation changes.

