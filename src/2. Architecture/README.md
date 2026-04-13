# 2. Architecture

## Purpose

This folder contains the **split architecture documents** for Glimmer.

Architecture defines **how the system is shaped** — the structures, patterns, constraints, and decisions that govern implementation.

```
REQ: → ARCH: → PLAN: → TEST:
```

## Conventions

- Use `ARCH:` anchors for stable references (e.g., `ARCH:ProjectStateModel`, `ARCH:ConnectorIsolation`)
- Architecture documents describe intended design, not implementation status
- Each document focuses on one major architectural concern and cross-references its companions

## Document Set

| File | Purpose |
|---|---|
| `01_system_overview.md` | High-level system shape, operating modes, capability map, deployment posture |
| `02_domain_model.md` | Core domain entities, relationships, ownership boundaries, state layers |
| `03_langgraph_orchestration.md` | Graph topology, orchestration principles, interrupt/resume, review gates |
| `04_connectors_and_ingestion.md` | Connector architecture, normalization, provenance, multi-account handling |
| `05_memory_and_retrieval.md` | Memory layers, summary strategy, semantic retrieval, audit and trace |
| `06_ui_and_voice.md` | UI surfaces, interaction principles, voice architecture, Telegram companion UX |
| `07_security_and_permissions.md` | Security boundaries, OAuth model, no-auto-send policy, review gate enforcement |

### Related architecture-origin document

| File | Location | Purpose |
|---|---|---|
| `08_testing_strategy.md` | `4. Verification/` | Testing and verification architecture — housed under Verification for discovery convenience |
