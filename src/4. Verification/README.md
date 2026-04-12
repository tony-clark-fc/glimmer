# 4. Verification

## Purpose

This folder contains the **verification layer** — how completion is proven.

```
REQ: → ARCH: → PLAN: → TEST:
```

## Principles

- Code existence is not evidence of completion
- Verification depth should be proportionate to risk
- Every capability needs at least one `TEST:` anchor

## Conventions

- Use `TEST:` anchors for stable references (e.g., `TEST:Capability.Auth.LoginHappyPath`)
- Organize tests by capability, not by code structure
- Distinguish between automated and manual verification
- Track regression packs for release gates

## Suggested Structure

- `*_verification_index.md` — entry point and verification strategy
- `*_test_catalog.md` — complete catalog of test scenarios with `TEST:` anchors
- `*_regression_pack.md` — scenarios that must pass before any release
- `*_manual_verification_checklist.md` — scenarios requiring human verification

