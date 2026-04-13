# 4. Verification

## Purpose

This folder contains the **verification layer** for Glimmer — how completion is proven.

```
REQ: → ARCH: → PLAN: → TEST:
```

## Principles

- Code existence is not evidence of completion
- Verification depth should be proportionate to risk
- Every capability needs at least one `TEST:` anchor
- Verification is part of implementation, not cleanup

## Conventions

- Use `TEST:` anchors for stable references (e.g., `TEST:Domain.ProjectLifecycle.BasicPersistence`)
- Organize verification by capability and workstream
- Distinguish between automated and manual verification
- Track verification packs for release gates

## Document Set

| File | Purpose |
|---|---|
| `08_testing_strategy.md` | Testing and verification architecture (architecture-origin document — see also `2. Architecture/README.md`) |
| `test_catalog.md` | Complete catalog of test scenarios with `TEST:` anchors |
| `verification_pack_smoke.md` | Smoke-level baseline proof |
| `verification_pack_workstream_a.md` | Workstream A — Foundation verification pack |
| `verification_pack_workstream_b.md` | Workstream B — Domain and Memory verification pack |
| `verification_pack_workstream_c.md` | Workstream C — Connectors verification pack |
| `verification_pack_workstream_d.md` | Workstream D — Triage and Prioritization verification pack |
| `verification_pack_workstream_e.md` | Workstream E — Drafting UI verification pack |
| `verification_pack_workstream_f.md` | Workstream F — Voice verification pack |
| `verification_pack_data_integrity.md` | Cross-cutting data integrity verification pack |
| `verification_pack_release.md` | Release-gate verification pack |

### Note on `08_testing_strategy.md`

This document self-identifies as a Split Architecture Document and defines `ARCH:` anchors. It is housed here under Verification because this is the natural discovery path for testing and proof concerns. The Architecture README also references it as part of the architecture set.
