# 1. Requirements

## Purpose

This folder contains the **requirements baseline** for the project.

Requirements define **what must be true** about the system. They are the first link in the delivery chain:

```
REQ: → ARCH: → PLAN: → TEST:
```

## Conventions

- Use `REQ:` anchors for stable references (e.g., `REQ:UserManagement.Authentication`)
- Requirements should be testable — if you can't verify it, it's not a requirement
- Keep requirements at the right level of abstraction — not too detailed (that's architecture), not too vague (that's a goal)
- Version requirements documents when making material changes

## Getting Started

Create your first requirements document:

```markdown
# {{PROJECT_NAME}} — Requirements Baseline

## Document Status
- **Status:** Draft v1
- **Purpose:** Define the requirements baseline for {{PROJECT_NAME}}

---

## 1. Functional Requirements

### 1.1 [Area Name]

**Stable requirement anchor:** `REQ:AreaName.CapabilityName`

[Describe what must be true]
```

