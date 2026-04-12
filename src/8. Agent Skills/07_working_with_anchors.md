# Skill 07 — Working with Anchors

## Purpose

Teach the agent how to create, use, cite, and maintain the stable anchor system (`REQ:`, `ARCH:`, `PLAN:`, `TEST:`) that holds the framework together.

## When to Use

- When you need to reference a design decision, requirement, or test scenario
- When you find a material section that doesn't have an anchor
- When writing progress notes, code comments, or ADR entries
- When proposing new verification scenarios

## Core Concepts

### What Anchors Are

Anchors are **stable, semantic, human-readable labels** that survive document refactoring. Section numbers change. Headings get renamed. Anchors persist.

They are the **stable reference points** that connect requirements to architecture to build plan to verification.

### The Four Anchor Families

| Prefix | Lives In | Purpose | Example |
|--------|----------|---------|---------|
| `REQ:` | Requirements | What must be true | `REQ:FieldDataCollection.SensorTracking` |
| `ARCH:` | Architecture | How the system is shaped | `ARCH:SurveyDataModel.SensorDeployments` |
| `PLAN:` | Build Plan | How delivery is organized | `PLAN:WorkstreamA.SensorDeployment` |
| `TEST:` | Verification | How completion is proven | `TEST:SensorDeployment.RecordDeployment.HappyPath` |

### Anchor Naming Convention

Anchors use **dot-separated hierarchical names** that read naturally:

```text
PREFIX:Domain.Concept.Detail

Examples:
  REQ:UserManagement.RoleAssignment
  ARCH:DataModel.SurveyPlan.Navigation
  PLAN:WorkstreamB.SchemaDesign.Phase2
  TEST:SurveyPlan.Create.DuplicateNameRejected
```

Rules:
- PascalCase for each segment
- Dots separate hierarchy levels (broad → specific)
- Keep names short but meaningful
- Names should make sense without reading the surrounding text

## How to Define an Anchor

In the source document, place the anchor as a comment or text near the section heading:

```markdown
### 4.3 Sensor Deployment Data Model

<!-- ARCH:SurveyDataModel.SensorDeployments -->

Sensor deployments record the placement and retrieval...
```

Or as visible text:

```markdown
### 4.3 Sensor Deployment Data Model

**Stable architecture anchor:** `ARCH:SurveyDataModel.SensorDeployments`
```

Both work. The retrieval index extracts both formats.

## How to Use Anchors

### In Working Documents (Progress Files)

```markdown
Implemented sensor deployment recording per `ARCH:SurveyDataModel.SensorDeployments`.
Verified with `TEST:SensorDeployment.RecordDeployment.HappyPath`.
```

### In Code Comments

```csharp
// Per ARCH:SurveyDataModel.SensorDeployments — deployments link to SurveyPlan + SurveySite
public Guid SurveyPlanId { get; set; }
public Guid SurveySiteId { get; set; }
```

### In ADR Entries

```markdown
**Related anchors:** `ARCH:SurveyDataModel.SensorDeployments`, `REQ:FieldDataCollection.SensorTracking`
```

### In Build Plan Workstreams

```markdown
## Workstream A — Sensor Deployment Implementation

Related architecture anchors:
- `ARCH:SurveyDataModel.SensorDeployments`
- `ARCH:MobileAPI.ActionBasedRouting`

Related requirement anchors:
- `REQ:FieldDataCollection.SensorTracking`
```

## Reasoning Patterns

### Pattern 1 — "Should I create a new anchor?"

```text
"I found a section without an anchor."
│
├── "Is this section a major decision, entity, or design rule?"
│   ├── Yes → Create an anchor
│   └── No → "Is it a subsection of something that has an anchor?"
│       ├── Yes → The parent anchor may be sufficient
│       └── No → "Will this section be referenced from elsewhere?"
│           ├── Yes → Create an anchor
│           └── No → Probably doesn't need one
```

**Rule of thumb:** If you'd reference it from a different document, it needs an anchor.

### Pattern 2 — "I want to reference something but can't find the anchor"

```text
1. Search with retrieval: agent_retrieve.py "ARCH:LikelyName" --json
2. Search broader: agent_retrieve.py "topic keywords" --json
3. Read the relevant index file for the document set
4. If no anchor exists:
   ├── Is the section material enough to warrant one?
   │   ├── Yes → Propose the anchor (in progress file, for human to add)
   │   └── No → Reference by file path and heading instead
```

### Pattern 3 — "I'm proposing a new TEST: scenario"

```text
1. Name it using the hierarchical convention:
   TEST:Entity.Operation.Scenario

   Examples:
   TEST:SurveyPlan.Create.HappyPath
   TEST:SurveyPlan.Create.MissingRequiredFieldsRejected
   TEST:SurveyPlan.Delete.CascadeToSites

2. Place it in the verification catalog with:
   - Scenario description
   - Preconditions
   - Expected outcome
   - Evidence type (automated test, manual check, log inspection)

3. Reference the related ARCH: and REQ: anchors
```

## Anchor Maintenance

### When Anchors Move

If a section is reorganized, the anchor moves with it. That's the entire point — the name stays stable even when the section number changes.

### When Anchors Become Obsolete

If the concept an anchor represents is removed from the architecture:
1. Don't delete the anchor immediately — search for references first
2. Check: is anything still pointing at it? (working docs, code comments, build plan)
3. If referenced: update all references before removing
4. If not referenced: remove it

### Orphan Anchors

An anchor that exists but is never referenced from another document is potentially orphaned. This isn't always a problem — some anchors exist for future reference. But if an `ARCH:` anchor has no `PLAN:` reference, it may indicate unplanned work.

## Common Mistakes

| Mistake | Why It's Harmful | Better Approach |
|---------|------------------|-----------------|
| Creating anchors for trivial details | Anchor system becomes noisy | Only anchor material decisions and reference points |
| Inconsistent naming | Hard to guess and search for | Use PascalCase, dot-separated hierarchy |
| Referencing anchors that don't exist | Broken traceability chain | Search first, propose if missing |
| Duplicating anchor names | Ambiguous references | Each anchor name must be unique |
| Not citing anchors in code comments | Design decisions hidden from code readers | Add anchor citations for non-obvious implementations |
| Defining new control anchors in working docs | Working docs are session state, not authority | Define anchors in control docs (1–4), cite them in working docs (5) |

## Related Skills

- [02 — Delivery Chain Reasoning](02_delivery_chain_reasoning.md) — how anchors form the delivery chain
- [01 — Retrieval and Context Gathering](01_retrieval_and_context_gathering.md) — how to find existing anchors
- [06 — Drift Detection and Remediation](06_drift_detection_and_remediation.md) — anchors as drift detection reference points

