# 2. Architecture

## Purpose

This folder contains the **architecture documents** for the project.

Architecture defines **how the system is shaped** — the structures, patterns, constraints, and decisions that govern implementation.

```
REQ: → ARCH: → PLAN: → TEST:
```

## Conventions

- Use `ARCH:` anchors for stable references (e.g., `ARCH:DataModel.UserEntity`)
- Architecture documents describe intended design, not implementation status
- Record material decisions in an **ADR Register** (Architecture Decision Register)
- Use appendices for as-built documentation that captures current-state truth

## Suggested Structure

- `*_architecture_index.md` — entry point and table of contents
- `*_solution_overview.md` — high-level system shape
- `*_application_architecture.md` — application layer design
- `*_data_architecture.md` — data models and storage
- `*_security_and_access.md` — authentication, authorization, permissions
- `*_adr_register.md` — architecture decision register
- `appendices/` — as-built documentation for stabilized patterns

