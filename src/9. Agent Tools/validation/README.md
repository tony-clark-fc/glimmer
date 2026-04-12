# Validation Tools

## Purpose

This folder contains lightweight checks for local agent-support artifacts.

The first validation helper is:

- `check_agent_index_freshness.py` — verifies that `AGENT_INDEX.json` exists and is not older than the markdown files it indexes

## Usage

```bash
python3 "src/9. Agent Tools/validation/check_agent_index_freshness.py"
python3 "src/9. Agent Tools/validation/check_agent_index_freshness.py" --json
```

