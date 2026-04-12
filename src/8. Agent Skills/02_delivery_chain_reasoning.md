# Skill 02 — Delivery Chain Reasoning

## Purpose

Teach the agent how to trace and validate the `REQ:` → `ARCH:` → `PLAN:` → `TEST:` delivery chain before implementing any meaningful change.

## When to Use

- Before starting implementation on any workstream slice
- When evaluating whether a proposed change is aligned with the architecture
- When classifying a finding as drift, extension, or aligned implementation
- When assessing verification coverage

## Core Concepts

### The Four-Link Chain

Every meaningful piece of work should be traceable through four layers:

| Link | Question | Document Home |
|------|----------|---------------|
| `REQ:` | What must be true? | `src/1. Requirements/` |
| `ARCH:` | How is the system shaped to make it true? | `src/2. Architecture/` |
| `PLAN:` | How is the work organized to build it? | `src/3. Build Plan/` |
| `TEST:` | How do we prove it's done? | `src/4. Verification/` |

### Why the Chain Matters

Without the chain:
- You might implement something nobody asked for (`REQ:` missing)
- You might implement it in a way that contradicts the design (`ARCH:` missing)
- You might implement it out of order or skip dependencies (`PLAN:` missing)
- You might claim it's done without proving it (`TEST:` missing)

The chain prevents silent bad decisions.

## Reasoning Patterns

### Pattern 1 — "I'm about to write code. What chain do I need?"

```text
1. What am I implementing?
2. Which PLAN: anchor covers this work?
   → agent_retrieve.py "PLAN:WorkstreamX.SliceName" --json
3. What ARCH: anchors does the plan reference?
   → Read the "Related architecture anchors" in the plan section
4. What REQ: anchors feed the architecture?
   → Check the architecture section for requirement references
5. What TEST: anchors must be proven?
   → Check the plan section or the verification catalog
6. Now I know the full chain. I can implement with confidence.
```

### Pattern 2 — "I found something in the code. Is it aligned?"

```text
1. What does this code do?
2. Is there an ARCH: anchor that governs this pattern?
   → agent_retrieve.py "ARCH:<likely anchor>" --json
3. Does the code match the architecture?
   ├── Yes → Proceed, cite the anchor in progress notes
   ├── Partially → Classify as transitional, note the gap
   └── No → Stop. Classify as drift. See Skill 06.
```

### Pattern 3 — "I need to add a new capability. Where does it fit?"

```text
1. Is there an existing REQ: for this?
   ├── Yes → Follow the existing chain
   └── No → Is this a new requirement? Surface it — don't invent requirements silently
2. Is there an ARCH: section covering this area?
   ├── Yes → Does my change align, extend, or contradict it?
   └── No → This may need a new ARCH: section or ADR
3. Is there a PLAN: workstream for this?
   ├── Yes → Follow the planned sequence
   └── No → Propose adding it to the plan
4. Are there TEST: scenarios defined?
   ├── Yes → Implement toward them
   └── No → Propose verification scenarios before claiming completion
```

### Detecting Chain Orphans

An **orphan** is a link that exists without its neighbors:

| Orphan Type | Signal | Risk |
|-------------|--------|------|
| `REQ:` without `ARCH:` | Requirement approved but no design | Will be implemented ad-hoc |
| `ARCH:` without `PLAN:` | Design exists but not scheduled | May never get built, or built out of order |
| `PLAN:` without `TEST:` | Work scheduled but no success criteria | "Done" is undefined |
| `TEST:` without `PLAN:` | Test defined but work not planned | Test may be premature or testing the wrong thing |
| Code without any anchor | Implementation exists with no chain | Drift candidate — inspect and classify |

When you find an orphan, record it in the working document. Don't silently fill in the missing links — surface the gap for human review.

## Worked Example

> Task: "Implement sensor deployment recording for the survey app"

```text
1. Search: agent_retrieve.py "sensor deployment" --json
2. Find: PLAN:WorkstreamA.SensorDeployment referenced in build plan
3. Read the plan section — it references:
   - ARCH:SurveyDataModel.SensorDeployments
   - REQ:FieldDataCollection.SensorTracking
   - TEST:SensorDeployment.RecordDeployment.HappyPath
4. Read the architecture section — sensor deployments are:
   - Recorded via app service method, not REST
   - Linked to SurveyPlan and SurveySite
   - Include GPS coordinates and deployment timestamp
5. Read the verification scenario — happy path expects:
   - Deployment recorded with all required fields
   - Linked correctly to plan and site
   - Queryable by survey plan
6. Now implement, knowing the full chain.
```

## Common Mistakes

| Mistake | Why It's Harmful | Better Approach |
|---------|------------------|-----------------|
| Starting code without finding the chain | Implementation may be misaligned | Always trace at least PLAN: and ARCH: before coding |
| Inventing a requirement to justify a change | Scope creep via agent initiative | Surface the need, don't fill the gap yourself |
| Treating "no TEST: anchor" as "no testing needed" | Untested work is unproven work | Propose verification scenarios |
| Filling in orphans silently | Hides gaps that the human should know about | Record orphans explicitly |

## Related Skills

- [01 — Retrieval and Context Gathering](01_retrieval_and_context_gathering.md) — how to find the chain
- [04 — Code Change Discipline](04_code_change_discipline.md) — how to implement once the chain is traced
- [07 — Working with Anchors](07_working_with_anchors.md) — how to create and cite anchors correctly

