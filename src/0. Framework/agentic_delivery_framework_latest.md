# Agentic Delivery Framework

**A methodology for building software with AI coding agents as implementation partners.**

**Version:** 1.4\
**Date:** 2026-03-27\
**Status:** Reference — verification and retrieval model integrated\
**Intended Audience:** Small-to-medium engineering efforts with a strong human lead and one or more AI coding agents. Solo founder + agent, small delivery teams, and platform teams will get the most value. Larger organisations can adopt the methodology selectively.\
**Tooling Assumption:** The framework is technology-agnostic (see Section 26). Examples use JetBrains Rider, GitHub Copilot (Agent mode), Azure DevOps, and Claude Opus 4.x.

---

## Table of Contents

1. [What This Framework Is](#1-what-this-framework-is)
2. [Why This Works](#2-why-this-works)
3. [Prerequisites and Tooling Setup](#3-prerequisites-and-tooling-setup)
4. [Framework Overview](#4-framework-overview)
5. [Phase 0 — Foundations Before Code](#5-phase-0--foundations-before-code)
6. [The Document Hierarchy](#6-the-document-hierarchy)
7. [Anchor System — Stable References That Survive Refactoring](#7-anchor-system--stable-references-that-survive-refactoring)
8. [Copilot Instructions — Programming the Agent](#8-copilot-instructions--programming-the-agent)
9. [Module-Scoped Instructions](#9-module-scoped-instructions--context-aware-guidance)
10. [Build Plan and Workstreams](#10-build-plan-and-workstreams)
11. [Working Documents — Session Continuity](#11-working-documents--session-continuity)
12. [Work Package Design](#12-work-package-design)
13. [Human–Agent Responsibility Model](#13-humanagent-responsibility-model)
14. [Agent Guardrails and Safety Rules](#14-agent-guardrails-and-safety-rules)
15. [Session Management and Handoffs](#15-session-management-and-handoffs)
16. [Governance and Change Control](#16-governance-and-change-control)
17. [Verification Model](#17-verification-model)
18. [Evidence of Completion](#18-evidence-of-completion)
19. [Requirements and Verification Traceability](#19-requirements-and-verification-traceability)
20. [State Models and Decision Tables](#20-state-models-and-decision-tables)
21. [Document Quality and Staleness](#21-document-quality-and-staleness)
22. [Azure DevOps Integration](#22-azure-devops-integration)
23. [Scaling to Complex Architectures](#23-scaling-to-complex-architectures)
24. [Quick-Start Checklist](#24-quick-start-checklist)
25. [Templates](#25-templates)
26. [Framework-Generic vs. Project-Specific Guidance](#26-framework-generic-vs-project-specific-guidance)
27. [Worked Example — End-to-End Flow](#27-worked-example--end-to-end-flow)
28. [Operator Quick-Reference Card](#28-operator-quick-reference-card)
29. [`9. Agent Tools/` — Repository-Local Agent Skills and Support Tooling](#29-9-agent-tools--repository-local-agent-skills-and-support-tooling)
30. [`8. Agent Skills/` — Instructional Skill Documents](#30-8-agent-skills--instructional-skill-documents)

---

## 1. What This Framework Is

This is a practical methodology for using AI coding agents — specifically GitHub Copilot in Agent mode with a premium model like Claude Opus 4.x — as genuine implementation partners in software delivery.

It is not about using autocomplete. It is not about asking an LLM to explain code. It is about establishing a structured operating model where:

- a human architect/operator defines **what** and **why**,
- AI agents execute **how** under explicit constraints,
- working documents provide **continuity** across sessions,
- stable anchors prevent **drift** as documents evolve,
- and clear boundaries prevent **silent bad decisions**.

This framework was developed and refined on a real production project — a monolithic ASP.NET Core application with a multi-agent AI pipeline, dual databases, and a phased rebuild of \~15 workstreams. It scaled effectively with a single human operator and a premium coding agent working in tight collaboration.

It is strongest for **small-to-medium engineering efforts** where a capable human lead works with one or more AI coding agents. This includes solo founders building a product, small delivery teams augmenting capacity with AI, and platform teams using agents for implementation-heavy workstreams. The methodology scales up, but it was forged in and optimised for the tight-feedback-loop environment where one person owns the design and the agent owns the keyboard.

The principles apply to any technology stack and any project where significant implementation work can be delegated to an AI agent.

---

## 2. Why This Works

Traditional AI coding assistance fails at scale because:

1. **Context is lost between sessions.** Chat history is ephemeral. The agent forgets everything.
2. **Scope creeps silently.** Without boundaries, agents invent architecture, add unnecessary abstractions, and wander.
3. **Design truth is implicit.** If the architecture lives only in a human's head, the agent will invent its own.
4. **Human-only work is invisible.** The agent tries to do things it cannot (create cloud resources, invent credentials) or stops too early.
5. **There is no handoff protocol.** When a session ends, the next session starts from scratch.

This framework solves these problems by treating the AI agent as a junior-to-mid developer with excellent technical skills but no institutional memory, no access to infrastructure, and no authority to make design decisions.

The key insight: **the quality of AI-generated code is directly proportional to the quality of the instructions and context you give it.**

---

## 3. Prerequisites and Tooling Setup

### 3.1 Required Tools

| Tool                      | Purpose                                 | Notes                                                                    |
| ------------------------- | --------------------------------------- | ------------------------------------------------------------------------ |
| **JetBrains Rider**       | IDE                                     | Any JetBrains IDE works; Rider is used for .NET examples                 |
| **GitHub Copilot plugin** | AI agent interface                      | Must support Agent mode (Copilot Chat with tool use)                     |
| **Premium model**         | Claude Opus 4.x, GPT-4.1, or equivalent | Agent mode requires a model that can use tools, read files, run commands |
| **Azure DevOps**          | Repository + work tracking              | Git repo; Boards for backlog if desired                                  |
| **Git**                   | Version control                         | Standard Git workflow; the agent commits nothing automatically           |

### 3.2 Rider Configuration

1. **Install GitHub Copilot plugin** — Settings → Plugins → Marketplace → "GitHub Copilot"
2. **Enable Agent mode** — Copilot Chat panel → select Agent mode (not Chat mode)
3. **Select premium model** — In the Copilot Chat model selector, choose Claude Opus 4.x or equivalent
4. **Configure file watchers** — Rider will index the repo; ensure `.github/` is not excluded from indexing

### 3.3 Repository Setup in Azure DevOps

1. Create a Git repository in your Azure DevOps project
2. Clone locally; open in Rider
3. Create the document hierarchy (see [Section 6](#6-the-document-hierarchy)) before writing code
4. Push the initial document structure as the first commit — this becomes the agent's operating context

### 3.4 Copilot Instructions Location

GitHub Copilot reads agent instructions from specific file paths. These are the files that "program" the agent's behavior:

```text
.github/
├── copilot-instructions.md          ← Global instructions (always loaded)
└── instructions/
    ├── module-a.instructions.md     ← Scoped instructions (loaded per file pattern)
    ├── module-b.instructions.md
    └── ...

src/9. Agent Tools/
├── README.md                        ← Operator/agent tooling conventions
├── indexing/                        ← Local retrieval/indexing scripts and outputs
├── validation/                      ← Freshness and integrity checks
└── ...
```

The global `copilot-instructions.md` is loaded into every Copilot Agent session automatically. Module-scoped files are loaded when the agent works on files matching their `applyTo` glob pattern.

The `9. Agent Tools/` folder within the numbered document hierarchy is the recommended home for repository-local agent skills, retrieval helpers, validation scripts, and generated tool-side artifacts. It is a support surface for delivery, not a replacement for the active control documents.

---

## 4. Framework Overview

The framework has six layers that work together:

```text
┌─────────────────────────────────────────────────────────────┐
│  1. DESIGN TRUTH DOCUMENTS                                  │
│     Requirements (REQ:) · Architecture (ARCH:) · Decisions  │
│     (Human-authored, agent-referenced, anchor-indexed)      │
├─────────────────────────────────────────────────────────────┤
│  2. DELIVERY PLAN                                           │
│     Build Plan (PLAN:) · Workstreams · Phase Plan           │
│     (Human-authored, agent-executable, traceable to REQ:)   │
├─────────────────────────────────────────────────────────────┤
│  3. VERIFICATION MODEL                                      │
│     Test Catalog (TEST:) · Verification Packs · Regression  │
│     (Human-defined, agent-implemented, evidence-backed)     │
├─────────────────────────────────────────────────────────────┤
│  4. AGENT INSTRUCTIONS                                      │
│     copilot-instructions.md · Module instructions           │
│     (Human-authored, agent-consumed, controls behavior)     │
├─────────────────────────────────────────────────────────────┤
│  5. WORKING DOCUMENTS                                       │
│     Plan files · Progress files · Handoff blocks            │
│     (Agent-maintained, human-reviewed, session continuity)  │
├─────────────────────────────────────────────────────────────┤
│  6. CODE + EVIDENCE                                         │
│     Source · Tests · Migrations · Config · Logs             │
│     (Agent-generated, human-reviewed, evidence-verified)    │
└─────────────────────────────────────────────────────────────┘
```

Each layer depends on the one above it. The agent never invents architecture. The architecture never describes implementation sequence. Verification defines how success is proven. Working documents bridge the gap between sessions. Code is the output, not the plan.

---

## 5. Phase 0 — Foundations Before Code

**The single most important rule in this framework: do the thinking before writing any code.**

Phase 0 is the investment that makes everything else work. Skip it and you will spend more time correcting the agent than it saves you.

### 5.1 What Phase 0 Delivers

Before a single line of application code is written, you must have:

1. **A requirements document** — what the system must do, in plain language
2. **An architecture document** — structural decisions, component design, data model, integration points
3. **A build plan** — workstreams, phase plan, human vs. agent responsibility split
4. **Copilot instructions** — global behavior rules, project conventions, coding standards
5. **Module instructions** — per-concern coding rules scoped to file patterns
6. **An anchor index** — stable reference labels across all documents

### 5.2 How Long Phase 0 Takes

For a small-to-medium project (single web app): **1–3 days of focused human work**, potentially with AI assistance for drafting.

For a large distributed system: **3–7 days**, because the architecture document needs to cover more ground and the workstream decomposition is more complex.

This is not wasted time. It is the highest-leverage work in the entire project.

### 5.3 Can the Agent Help With Phase 0?

Yes — significantly. You can use Agent mode to:

- Draft requirements from verbal descriptions or existing notes
- Structure an architecture document from your design decisions
- Decompose a build plan into workstreams
- Generate copilot instruction files from your conventions

But **you** must review, refine, and approve the output. The agent is a drafter, not an architect. The documents become the control surface for all future work — they must be accurate.

---

## 6. The Document Hierarchy

### 6.1 Recommended Folder Structure

```text
YourProject/
├── .github/
│   ├── copilot-instructions.md              ← Global agent instructions
│   └── instructions/
│       ├── backend-services.instructions.md ← Module-scoped instructions
│       ├── data-layer.instructions.md
│       ├── frontend.instructions.md
│       └── infrastructure.instructions.md
├── _Agent_Skills/ or 8. Agent Skills/
│   ├── README.md                            ← Skill index, authority model, conventions
│   ├── 01_retrieval_and_context_gathering.md
│   ├── 02_delivery_chain_reasoning.md
│   ├── ...                                  ← Instructional skill documents
├── _Agent_Tools/ or 9. Agent Tools/
│   ├── README.md                            ← Agent-tooling conventions and inventory
│   ├── indexing/                            ← Retrieval/index generation helpers
│   ├── validation/                          ← Freshness/integrity checks
│   └── ...
├── 1. Requirements/
│   └── requirements.md                      ← What the system must do
├── 2. Architecture/
│   ├── ARCHITECTURE.md                      ← Index with anchor map
│   ├── 01-overview.md                       ← Split by concern
│   ├── 02-system-design.md
│   ├── 03-data-model.md
│   └── ...
├── 3. Build Plan/
│   ├── BUILD_PLAN.md                        ← Index with workstream map
│   ├── 00-strategy-and-scope.md
│   ├── workstream-a-foundation.md
│   ├── workstream-b-data.md
│   └── ...
├── 4. Verification/
│   ├── TEST_CATALOG.md
│   ├── verification-pack-smoke.md
│   ├── verification-pack-release.md
│   ├── verification-pack-workstream-a.md
│   └── ...
├── src/                                     ← Application code
├── tests/                                   ← Test projects
└── WorkstreamA_Foundation_DESIGN_AND_IMPLEMENTATION_PLAN.md     ← Working docs
    WorkstreamA_Foundation_DESIGN_AND_IMPLEMENTATION_PROGRESS.md
    WorkstreamB_Data_DESIGN_AND_IMPLEMENTATION_PLAN.md
    WorkstreamB_Data_DESIGN_AND_IMPLEMENTATION_PROGRESS.md
    ...
```

For a very small project, the verification artifacts can live inside the Build Plan folder instead. Once the project has multiple workstreams or meaningful regression risk, a dedicated verification area keeps scenario definitions, packs, and regression targets visible and durable.

### 6.2 Why Numbered Folders?

The `1. Requirements/`, `2. Architecture/`, `3. Build Plan/` naming convention:

- Makes the reading order obvious to humans and agents
- Sorts correctly in file explorers
- Signals that these are reference documents, not code
- Prevents them from being mixed into source directories

The agent-tools folder (whether `_Agent_Tools/` at project root or `9. Agent Tools/` within the numbered hierarchy) keeps agent-operational helpers visible and standardized without implying that the tools themselves are the authoritative design or verification surface.

### 6.3 Why Split Large Documents?

Architecture and build plan documents should be split by concern (one file per major section) when they exceed \~300 lines. This:

- Reduces token usage when the agent reads specific sections
- Makes anchor lookups faster
- Allows independent editing without merge conflicts
- Keeps each file focused and reviewable

Always maintain an **index file** (`ARCHITECTURE.md`, `BUILD_PLAN.md`) that maps files to concerns and anchors to files.

### 6.4 Machine-Readable Retrieval Layer for Large Documentation Sets

When a repository accumulates a large active control surface, the framework should include a **machine-readable retrieval layer** in addition to the human-readable index files.

The recommended pattern is:

- Markdown documents remain the **source of truth**
- human-readable index files remain the primary operator map
- a generated `AGENT_INDEX.json` acts as a compact retrieval map for local scripts and coding agents
- repository-local retrieval scripts and validation helpers live under the agent-tools folder (e.g., `src/9. Agent Tools/`)

The retrieval map should be **generated**, not hand-maintained.

At minimum it should capture, per document:

- relative path
- title
- short description
- authority posture such as `status` and `canonical`
- extracted formal anchors
- extracted headings
- domains or routing tags
- freshness metadata such as declared update date and/or repository modification date

The retrieval map is an acceleration layer, not a new authority layer.
It must never replace the Markdown file as the controlling document.

When a repository adopts an agent-tools folder, place retrieval scripts, freshness checks, and related helper utilities there so operators and agents know where local skills live.

For repositories with active, working, and legacy documentation layers, retrieval logic should prefer:

1. active canonical control docs
2. active but non-canonical supporting docs
3. working docs
4. legacy/source-evidence docs

Large excerpts should not be embedded in the retrieval map. Keep it lightweight enough that a local tool can rank likely documents and then extract only the relevant bounded snippet from the source file.

Where this layer exists, add a lightweight validation step so stale indexes are detected before they mislead the agent.

---

## 7. Anchor System — Stable References That Survive Refactoring

### 7.1 The Problem Anchors Solve

AI agents work with documents that change over time. Section numbers shift. Headings are renamed. Content is reorganized.

If the agent was told to "implement the rules in section 4.3.2" and that section becomes 5.1.1 after a reorganization, the reference breaks silently.

Anchors provide **stable, semantic, human-readable labels** that survive document refactoring.

### 7.2 Anchor Naming Convention

Use a prefix that identifies the document family:

| Prefix  | Document     | Example                                                                            |
| ------- | ------------ | ---------------------------------------------------------------------------------- |
| `ARCH:` | Architecture | `ARCH:DataModel`, `ARCH:AuthStrategy`, `ARCH:ServiceBoundaries`                    |
| `PLAN:` | Build Plan   | `PLAN:WorkstreamB.SchemaDesign`, `PLAN:Phase3.Integration`                         |
| `REQ:`  | Requirements | `REQ:BenchmarkExtraction`, `REQ:ApprovalWorkflow`, `REQ:AuditTrail`                |
| `TEST:` | Verification | `TEST:BenchmarkApproval.HappyPath`, `TEST:UserRegistration.DuplicateEmailRejected` |

All four anchor types participate in the traceability chain (see Section 19).

### 7.3 How to Define an Anchor

In the source document, place the anchor as a line immediately after or within the section heading:

```markdown
### 4.3 Authentication Strategy

**Stable architecture anchor:** `ARCH:AuthStrategy`

The system uses OAuth 2.0 with PKCE for browser clients and...
```

### 7.4 How to Use Anchors

**In architecture documents** — define anchors on every major decision, component, or design rule.

**In build plan workstreams** — reference the architecture anchors the workstream implements:

```markdown
## Workstream D — Authentication Implementation

Related architecture anchors:
- `ARCH:AuthStrategy`
- `ARCH:TokenLifecycle`
- `ARCH:RoleModel`
```

**In verification artifacts** — define stable scenarios that prove important success and failure behavior:

```markdown
<!-- TEST:BenchmarkApproval.HappyPath -->
## Benchmark approval — happy path
```

**In copilot instructions** — cite anchors so the agent knows which design rules govern which code:

```markdown
## Authentication Rules
> Architecture references: `ARCH:AuthStrategy`, `ARCH:TokenLifecycle`

- Use PKCE flow for all browser-initiated auth
- Access tokens expire after 15 minutes
- Refresh tokens are rotated on every use
```

**In working documents** — the agent cites anchors when reporting progress:

```markdown
Implemented token rotation per `ARCH:TokenLifecycle`.
Verified login refresh path with `TEST:Authentication.TokenRefresh.HappyPath`.
```

**In code comments** — when a design decision drives implementation:

```csharp
// Per ARCH:TokenLifecycle — rotate refresh token on every use
await _tokenStore.RotateRefreshTokenAsync(userId, newToken);
```

### 7.5 Maintaining the Anchor Index

The architecture index file should contain a table mapping every anchor to its file:

```markdown
| Anchor | File |
|---|---|
| `ARCH:AuthStrategy` | [03-authentication.md](03-authentication.md) |
| `ARCH:TokenLifecycle` | [03-authentication.md](03-authentication.md) |
| `ARCH:DataModel` | [04-data-model.md](04-data-model.md) |
```

The verification catalog should do the same for important `TEST:` anchors.

### 7.6 Anchor Rules

1. **Anchors are stable** — once assigned, the label does not change unless the concept is deliberately replaced.
2. **Headings can change** — the visible heading may be renamed for clarity without affecting the anchor.
3. **If no anchor exists, propose one** — the agent should never reference "the architecture kind of suggests..." Instead: "No stable anchor was found for the retry policy. Proposed new anchor: `ARCH:RetryPolicy`."
4. **Cross-reference freely** — anchors are meant to be used across documents, instructions, code, tests, and working files.

---

## 8. Copilot Instructions — Programming the Agent

The `.github/copilot-instructions.md` file is the most important single file in this framework. It is loaded into every Agent mode session and defines how the agent behaves.

### 8.1 What Goes in Global Instructions

The global instructions file should contain, in this order:

#### Section 1: Project Overview

- What the project is (one paragraph)
- Tech stack (framework, language, database, key libraries)
- Solution structure (folder tree with one-line descriptions)

#### Section 2: Coding Conventions

- Language-specific rules (C# features, TypeScript strictness, Python type hints, etc.)
- Framework patterns (DI, middleware, state management, etc.)
- Naming conventions
- Error handling patterns
- Logging patterns
- Configuration patterns

#### Section 3: Architecture Summary

- Key architectural principles (3–5 bullets)
- Module/component descriptions
- Data model overview
- Integration patterns

#### Section 4: Verification Expectations

- How the agent should interpret linked `TEST:` anchors
- Expected verification behavior per work package
- Progress-file verification reporting rules
- Completion-state rules when proof is missing

#### Section 5: Module Index

A pointer to the module-scoped instruction files.

#### Section 6: Work Package Operating Model

This is the section that transforms the agent from a code generator into an implementation partner. It should define:

- **How to interpret work package references** (anchor-based navigation)
- **Working document conventions** (plan files, progress files, naming)
- **Delivery slice rules** (prefer small, testable slices)
- **Status labels** (Designed, Implemented, Verified, Blocked, Human review required)
- **Progress reporting format** (anchors, files changed, assumptions, blockers)
- **Session continuity behavior** (working docs as memory)
- **Default operating sequence** (review → scope → inspect → plan → implement → verify → report)

#### Section 7: Assumption and Uncertainty Handling

- When to make assumptions vs. ask
- How to record assumptions
- What categories require human confirmation (schema, security, infrastructure, prompts)

#### Section 8: Human Assistance Protocol

- Structured request format
- When the agent must stop
- What the agent should complete before stopping

#### Section 9: Safety Guardrails

- What the agent must never do (invent credentials, change schema silently, etc.)
- Preferred coding style
- Legacy code reuse rules (if applicable)

### 8.2 Size Guidance

A well-written global instructions file is typically **300–500 lines**. This seems long, but:

- Premium models handle this context efficiently
- The instructions are loaded once per session, not per request
- Comprehensive instructions dramatically reduce correction cycles
- Every line you omit is a behavior you leave to chance

### 8.3 Iteration

The instructions file is a living document. After every 3–5 agent sessions, review what went wrong and add or refine rules. Common additions:

- "Do not use `ViewBag` — use strongly-typed page models"
- "Always check for null before accessing `.Value`"
- "Run `get_errors` after every file edit"
- "Do not create abstract base classes unless there are at least two implementations"

### 8.4 Verification Expectations

Global instructions should also make the verification model operational. Add guidance covering the following points:

- Treat linked `TEST:` anchors as part of implementation scope, not optional follow-up work.
- Before implementing a high-value or stateful work package, identify the relevant `TEST:` scenarios.
- If no suitable `TEST:` anchors exist for risky work, propose them before continuing or record the gap explicitly.
- Prefer tests that prove scenario behavior, not just method coverage.
- For each completed slice, update the progress file with verification status.
- Do not mark a work package complete if critical linked scenarios remain unverified, unless they are explicitly classified as `ManualOnly` or `Deferred` with a stated reason.
- When blocked by missing infrastructure or environment setup, complete all code-safe verification work first and then issue a structured human assistance request.

### 8.5 Local Documentation Retrieval Rule

If a repository implements a local documentation retrieval layer, global instructions should require the agent to use it **before** broadly searching large Markdown corpora.

The operating rule should be:

1. refresh or validate the generated retrieval map when documentation may have changed
2. resolve the most relevant active/canonical document locally
3. use the returned anchor or bounded snippet as the primary context
4. only open the full document when the snippet is insufficient

Retrieval priority should be:

1. exact formal anchor match
2. matching heading section
3. bounded query-based fallback

Global instructions should also state the following guardrails:

- prefer `canonical: true` and `status: active` documents when multiple candidates match
- treat the Markdown document, not the retrieval map, as the source of truth
- report conflicts between candidate documents explicitly rather than guessing
- do not dump large document sets into the model context when local retrieval can narrow the search first

---

## 9. Module-Scoped Instructions — Context-Aware Guidance

### 9.1 What Module Instructions Are

Module-scoped instruction files provide detailed coding rules that only apply when the agent is working on specific files. They reduce noise by loading context only when relevant.

### 9.2 File Format

Each module instruction file has a YAML frontmatter header with an `applyTo` glob pattern:

```markdown
---
applyTo: "**/Services/**/*.cs,**/Repositories/**/*.cs,**/*Service*.cs"
---

# Backend Services: Patterns and Rules

> Architecture references: `ARCH:ServiceLayer`, `ARCH:RepositoryPattern`

## Service Layer
- Services live in `Services/` — business logic belongs here, not in controllers
- Register services as Scoped in DI
- All methods are async
- Use ILogger<T> for structured logging
...
```

### 9.3 Recommended Module Split

For a typical web application:

| File                               | Applies To                                             | Covers                                  |
| ---------------------------------- | ------------------------------------------------------ | --------------------------------------- |
| `backend-services.instructions.md` | `**/Services/**`, `**/Models/**`                       | Business logic, DTOs, error handling    |
| `data-layer.instructions.md`       | `**/Data/**`, `**/Repositories/**`, `**/Migrations/**` | EF Core, entities, repositories, schema |
| `frontend.instructions.md`         | `**/*.cshtml`, `**/*.tsx`, `**/Pages/**`               | UI components, styling, state           |
| `infrastructure.instructions.md`   | `**/Infrastructure/**`, `**/*Provider*`                | External integrations, clients, auth    |

For a distributed system, add:

| File                            | Applies To                                         | Covers                           |
| ------------------------------- | -------------------------------------------------- | -------------------------------- |
| `api-contracts.instructions.md` | `**/Contracts/**`, `**/*Request*`, `**/*Response*` | API versioning, schema evolution |
| `messaging.instructions.md`     | `**/Events/**`, `**/Handlers/**`                   | Message bus, event sourcing      |
| `deployment.instructions.md`    | `**/*.bicep`, `**/*.tf`, `**/infra/**`             | IaC, deployment pipelines        |

### 9.4 What Makes Good Module Instructions

- **Specific code patterns** — show the interface, the registration pattern, the error handling convention
- **Architecture references** — cite the `ARCH:` anchors that govern this module
- **Verification references** — cite the `TEST:` anchors or pack expectations that matter for this module when the behavior is high-risk
- **Do and don't lists** — explicit rules the agent must follow
- **Entity schemas** — list the properties, constraints, and relationships for data entities
- **Integration patterns** — how external services are called, what errors are expected

---

## 10. Build Plan and Workstreams

### 10.1 Purpose of the Build Plan

The build plan translates architecture into executable work. It answers:

- **What** gets built in what order?
- **Who** does each part — agent or human?
- **When** does the human need to intervene?
- **What evidence** proves each phase is done?

### 10.2 Build Plan Structure

```text
3. Build Plan/
├── BUILD_PLAN.md                    ← Index: workstream map + anchor index
├── 00-strategy-and-scope.md         ← Delivery principles, scope, assumptions
├── workstream-a-foundation.md       ← One file per workstream
├── workstream-b-data-layer.md
├── workstream-c-auth.md
├── workstream-d-api.md
├── workstream-e-frontend.md
├── workstream-f-testing.md
└── 99-governance-and-process.md     ← Phase plan, human checklist, agent model
```

### 10.3 Workstream Design

Each workstream file should contain:

1. **Stable anchor** — `PLAN:WorkstreamB.DataLayerImplementation`
2. **Objective** — what this workstream delivers
3. **Related architecture anchors** — which `ARCH:` sections it implements
4. **Related requirement anchors** — which `REQ:` requirements it satisfies
5. **Related verification anchors** — which `TEST:` scenarios it is expected to satisfy where appropriate
6. **Numbered work packages** — bounded units of work
7. **Dependencies** — what must be done first

### 10.4 Phase Plan

The phase plan groups workstreams into sequential phases with:

- **Phase objective** — what capability this phase delivers
- **Dominant workstreams** — which workstreams are active
- **Key outputs** — concrete deliverables
- **Verification pack coverage** — which `TEST:` scenarios or regression packs must pass before phase exit
- **Human intervention points** — where the human must act
- **Exit criteria** — what must be true before moving on
- **Test gate** — specific test evidence required

### 10.5 Workstream Sizing

A good workstream produces **3–10 working sessions** of agent work. If a workstream would take more than 10 sessions, split it.

Each work package within a workstream should be completable in **1–2 sessions**.

---

## 11. Working Documents — Session Continuity

### 11.1 The Session Problem

AI coding agents have no memory between sessions. When you close a chat and open a new one, the agent starts fresh. It does not remember what was built, what was decided, or what failed.

Working documents solve this by giving the agent a **persistent, structured memory** that lives in the repository alongside the code.

### 11.2 Document Pair Convention

Every workstream gets two files:

```text
Workstream{Letter}_{ShortName}_DESIGN_AND_IMPLEMENTATION_PLAN.md
Workstream{Letter}_{ShortName}_DESIGN_AND_IMPLEMENTATION_PROGRESS.md
```

### 11.3 The Plan File

The plan file captures **intent** — what will be built and how. It contains:

- Objective
- Relevant `ARCH:` and `PLAN:` anchors
- Relevant `TEST:` anchors for high-value scenarios
- Scope and non-goals
- Assumptions (confirmed and unconfirmed)
- Human dependencies
- Phased implementation plan
- Completion criteria

The agent creates this file **before writing code** and updates it as understanding improves.

### 11.4 The Progress File

The progress file captures **state** — what has been done and what comes next. It is the session continuity artifact.

#### The Handoff Block

At the top of every progress file, maintain a structured handoff block:

```markdown
## Handoff Block
- **Current phase:** Phase 2 — Service implementation
- **Last completed step:** Created UserService with CRUD operations
- **Next exact step:** Implement password reset flow in UserService
- **Blockers:** SMTP configuration needed for email sending
- **Human input required:** SMTP credentials and sender address
- **Files most recently changed:** Services/UserService.cs, Models/UserDto.cs
- **Relevant `ARCH:` anchors:** ARCH:UserManagement, ARCH:AuthStrategy
- **Relevant `PLAN:` anchors:** PLAN:WorkstreamC.UserService
- **Relevant `TEST:` anchors:** TEST:UserManagement.PasswordReset.HappyPath, TEST:UserManagement.PasswordReset.InvalidTokenRejected
```

Below the handoff block, add a compact verification summary so the next session can see not just what changed, but what has actually been proven:

```markdown
## Verification Status
- Critical scenarios passing:
- Critical scenarios pending:
- Manual-only scenarios:
- Environment blockers:
```

#### Progress Log

Below the handoff block and verification block, maintain a timestamped log of completed work.

### 11.5 Rules for Working Documents

1. **One workstream per file pair** — do not mix workstreams
2. **Create both files before writing code** — the plan precedes the implementation
3. **Keep the handoff block current** — update it at the end of every session
4. **Keep the verification status current** — do not let it drift from reality
5. **Cross-workstream work gets its own files** — if implementing one workstream requires a change to another, update both progress files
6. **The progress file is the source of truth for implementation state** — not chat history
7. **Keep it concise** — the progress file should be short enough that an agent can read it in a few seconds

---

## 12. Work Package Design

### 12.1 Slice Size

The most important delivery discipline: **prefer small, reviewable, testable slices.**

Do not ask the agent to "build the authentication system." Instead, break it into:

1. Contract/design slice — interfaces, DTOs, configuration model
2. Service slice — core business logic implementation
3. Repository slice — data access for the feature
4. API slice — endpoint wiring
5. UI slice — frontend components
6. Verification slice — unit, integration, or end-to-end proof as appropriate

Each slice should be:

- Completable in one agent session (30–90 minutes of real interaction)
- Independently reviewable
- Independently testable where possible

### 12.2 Work Package Structure

Every work package given to the agent should include:

```markdown
**Objective:** [What this slice delivers]

**Relevant anchors:**
- `REQ:SomeRequirement`
- `ARCH:SomeAnchor`
- `PLAN:SomeWorkstream.SomePackage`
- `TEST:SomeScenario`

**Scope:**
- In scope: [specific deliverables]
- Out of scope: [explicit exclusions]

**Inputs and assumptions:**
- [What already exists]
- [What the agent can assume]

**Expected outputs:**
- [Files to create/modify]
- [Tests to add]
- [Verification evidence to record]

**Constraints:**
- [Rules the agent must follow]
- [Things the agent must not change]

**Human dependencies:**
- [What requires human action]

**Definition of done:**
- [Testable completion criteria]
- [Required `TEST:` scenarios proven or explicitly deferred]
```

### 12.3 How to Frame Work for the Agent

Instead of a vague request, give the agent a bounded instruction.

A good prompt references the relevant work package and, where the behavior is risky or stateful, the verification scenario as well:

> Continue with `PLAN:WorkstreamC.UserRepository` and satisfy `TEST:UserRepository.EmailUniqueness`.

That is far stronger than asking the agent to "finish the feature."

---

## 13. Human–Agent Responsibility Model

### 13.1 The RACI Split

| Activity                                | Agent                | Human                 |
| --------------------------------------- | -------------------- | --------------------- |
| Write application code                  | **Responsible**      | Accountable (reviews) |
| Write tests and verification automation | **Responsible**      | Accountable (reviews) |
| Create DTOs and interfaces              | **Responsible**      | Informed              |
| Design architecture                     | Consulted (drafts)   | **Responsible**       |
| Create cloud resources                  | Blocked (cannot do)  | **Responsible**       |
| Manage secrets or credentials           | Blocked (cannot do)  | **Responsible**       |
| Schema design decisions                 | Consulted (proposes) | **Accountable**       |
| Prompt engineering                      | Consulted (drafts)   | **Accountable**       |
| Approve unknown mappings                | Blocked              | **Responsible**       |
| Run destructive operations              | Blocked              | **Responsible**       |
| Write working documents                 | **Responsible**      | Reviews               |
| Update architecture docs                | Consulted (proposes) | **Accountable**       |

### 13.2 Human-Only Boundaries

Certain activities are structurally beyond what an AI agent can or should do — creating cloud resources, managing secrets, approving governance decisions, running destructive operations. The agent must stop at these boundaries and issue a structured human assistance request.

### 13.3 The Human Assistance Protocol

When the agent reaches a boundary that requires human action, it must:

1. **Complete all code-safe work first** — do everything possible before stopping
2. **Issue a structured request** using this format:

```markdown
**What is blocked:** [Specific step that cannot proceed]
**Why the agent cannot proceed:** [Why this requires human action]
**What has been prepared:** [Code, config, and verification work already completed]
**Exact human action required:** [Precise, actionable instruction]
**Files or config affected:** [Specific files]
**Confirmation needed to resume:** [What the human should report back]
```

3. **Continue with any remaining non-blocked work** — do not stop entirely if only one part is blocked.

---

## 14. Agent Guardrails and Safety Rules

### 14.1 The Non-Negotiables

The agent must never:

- invent credentials, endpoints, or secret values,
- silently change architecture, schema semantics, or operational policy,
- mark risky work complete without visible proof,
- run destructive operations without explicit human instruction,
- or overfit the design to transient implementation detail.

### 14.2 What the Agent Should Do by Default

The agent should:

- inspect existing context before coding,
- work in small slices,
- keep working documents current,
- verify as it goes,
- and surface uncertainty instead of hiding it.

### 14.3 Verification-Related Guardrails

The agent must not treat verification as optional polish. It must not use a passing unit test as evidence that a workflow is proven if the actual workflow still lacks integration or end-to-end verification. It must not hide missing proof behind vague labels such as "done" or "looks good."

### 14.4 Legacy Code Reuse Rules

Legacy code can be inspected for ideas, patterns, or migration clues. It must not be copied forward blindly. Reuse must be deliberate and architecture-aligned.

---

## 15. Session Management and Handoffs

### 15.1 Why Session Discipline Matters

The quality of multi-session delivery depends on whether the next session can recover context accurately and quickly.

### 15.2 End-of-Session Ritual

At the end of each session:

1. update the working plan if understanding changed,
2. update the handoff block,
3. update verification status,
4. record what was actually proven,
5. note blockers and human dependencies,
6. commit working documents alongside code.

### 15.3 Start-of-Session Ritual

At the start of a new session:

1. open the relevant workstream progress file,
2. read the handoff block,
3. read the verification status,
4. inspect the last changed files,
5. continue from the next exact step.

---

## 16. Governance and Change Control

### 16.1 Why Governance Exists

The purpose of governance in this framework is not bureaucracy. It is to prevent silent drift, unmanaged risk, and confusion as multiple AI and human contributors work across a living architecture and build plan.

### 16.2 Decision Logging

Record material design changes explicitly. Update the architecture or build plan when the design truth changes.

### 16.3 Prompt and Schema Change Control

Prompt changes and schema changes are high-risk changes because they can materially change behavior even when little code appears to move.

### 16.4 Verification Change Control

Verification assets are also governed artifacts. Changes to `TEST:` anchors, verification packs, or release regression expectations should be visible, reviewable, and reflected in the relevant plan or progress files when they materially affect what counts as complete.

---

## 17. Verification Model

### 17.1 Why Verification Must Be a First-Class Delivery Concern

Most delivery failures with AI coding agents are not caused by bad syntax. They are caused by an incomplete definition of **what success looks like in behavior**.

If the agent is told only to "implement the feature" or "add tests," it will often produce one of two weak outcomes:

1. code that appears complete but has not been proven against real workflows, or
2. shallow tests that exercise methods but do not prove the system behaves correctly.

This framework therefore treats verification as a **first-class delivery system**, not a final clean-up activity.

The operating principle is:

> AI agents do not just implement code slices. They implement and satisfy verification slices.

This means each meaningful workstream or feature must define:

- the scenarios that prove success,
- the intended automation level for those scenarios,
- the environment and data assumptions required to execute them,
- and the evidence needed before the work can be considered complete.

### 17.2 Verification Layers

Verification in this framework operates across five layers:

1. **Unit verification** — business rules, pure logic, validators, mapping, calculations
2. **Integration verification** — repository behavior, database writes, service boundaries, message flow, state transitions
3. **End-to-end verification** — complete user or system workflows across multiple layers
4. **Manual verification** — limited checks where automation is impractical or premature
5. **Non-functional verification** — performance, resilience, security, migration safety, observability, operability

Not every feature needs heavy coverage in every layer. But every meaningful feature must declare which layers matter.

### 17.3 The Verification Scenario Catalog

For each major capability, feature, or work package, define the **behavioral scenarios that prove it works**.

These are not detailed manual test scripts. They are concise definitions of intended success and failure behavior.

A good scenario describes:

- the purpose,
- the starting state,
- the triggering action,
- the expected result,
- and any critical side effects or invariants.

Example:

```markdown
<!-- TEST:BenchmarkApproval.HappyPath -->
## Benchmark approval — happy path

**Purpose:** Verify that a pending benchmark claim can be approved and activated.

**Preconditions:**
- Research document exists
- Extracted claim exists in PendingApproval status
- Reviewer has access to the approval workflow

**Action:**
- Reviewer approves the claim

**Expected outcome:**
- Claim becomes active
- Audit record is written
- Prior active benchmark is superseded if uniqueness rules require it
- UI reflects the new active state
```

This level of definition is enough for an agent to derive:

- unit tests for supporting rules,
- integration tests for persistence and transitions,
- end-to-end tests for the workflow,
- and manual checks only where needed.

### 17.4 The `TEST:` Anchor Convention

The framework already uses `REQ:`, `ARCH:`, and `PLAN:` anchors to stabilise design and delivery references. Verification requires an equivalent stable reference mechanism.

Use the following convention:

- `REQ:` — what must be true
- `ARCH:` — how the system is designed
- `PLAN:` — how delivery is sequenced
- `TEST:` — how success is proven

Examples:

- `TEST:UserRegistration.HappyPath`
- `TEST:UserRegistration.DuplicateEmailRejected`
- `TEST:LedgerWrite.AuditTrail`
- `TEST:SurveySync.NetworkFailureRetry`

Rules:

1. `TEST:` anchors must be stable over time, even if headings move.
2. Each high-value scenario should have exactly one canonical `TEST:` anchor.
3. One scenario may support multiple `REQ:` anchors if appropriate.
4. `TEST:` anchors should be referenced from work packages, progress files, and evidence summaries.
5. Avoid naming that is overly technical or tied to temporary implementation classes.

### 17.5 Verification Packs

A **Verification Pack** is the delivery-facing testing contract for a feature, workstream, phase, or release.

It groups the scenarios, automation expectations, data assumptions, and evidence requirements needed to prove a slice of delivery is genuinely complete.

A Verification Pack should normally include:

- the pack scope,
- the linked `REQ:`, `ARCH:`, `PLAN:`, and `TEST:` anchors,
- the scenarios in scope,
- the intended automation level for each scenario,
- the required seed or fixture data,
- dependency assumptions,
- known deferrals,
- and the evidence required for sign-off.

Typical pack types:

- **Workstream Pack** — proves a single workstream
- **Feature Pack** — proves a vertical feature slice
- **Smoke Pack** — basic startup and critical-path health
- **Release Pack** — cross-feature regression for a deployable increment
- **Data Integrity Pack** — migration, uniqueness, idempotency, state transition, and audit correctness

### 17.6 Automation Classification

Every scenario in a Verification Pack should declare the intended verification mode.

Recommended values:

- **Unit**
- **Integration**
- **EndToEnd**
- **ManualOnly**
- **Deferred**

A scenario may map to more than one mode.

Example:

```markdown
**Automation target:**
- Unit: Yes
- Integration: Yes
- EndToEnd: Yes
- ManualOnly: No
```

This prevents a common failure mode where a workflow is declared "tested" because a helper method has unit coverage while the real workflow remains unproven.

### 17.7 Verification by Default

Unless explicitly justified otherwise, each meaningful feature should aim to provide:

- unit verification for core business rules,
- integration verification for state changes and persistence behavior,
- at least one end-to-end happy path,
- and at least one end-to-end or integration-level critical failure path.

Examples of critical failure paths include duplicate identity rejection, permission-denied behavior, concurrency conflict handling, external dependency failure and retry handling, and invalid state transition rejection.

### 17.8 Environment and Test Data Declarations

Automated verification becomes fragile when the environment and data model are implicit.

Each Verification Pack should declare:

- required seed data,
- whether dependencies are real, fake, stubbed, or emulated,
- environment assumptions,
- reset or cleanup approach,
- and any human-only setup steps.

Example:

```markdown
**Environment assumptions:**
- Uses local SQL instance
- SMTP is stubbed
- External ledger writes are disabled via local stub

**Test data:**
- Seeded user account with reviewer role
- One pending benchmark claim
- One pre-existing active benchmark for uniqueness test

**Reset strategy:**
- Database reset script runs before integration suite
```

Without this, tests degrade over time and become difficult for agents to trust or repair.

### 17.9 Regression Packs

Verification should also be grouped into reusable regression packs that can be run intentionally.

Recommended default packs:

- **Smoke Pack** — application starts, core pages or endpoints respond, critical infrastructure wiring is healthy
- **Workstream Regression Pack** — all critical scenarios for a workstream
- **Release Regression Pack** — end-to-end coverage of the increment being released
- **Data Integrity Pack** — migrations, uniqueness, soft deletes, supersession, audit trails, and recovery-sensitive behavior

This allows agents and humans to work with named verification targets instead of vague requests such as "please test everything."

### 17.10 Agent Verification Behavior

The agent must treat linked verification scenarios as part of implementation, not as optional polish.

When executing a work package, the expected behavior is:

1. identify the relevant `TEST:` anchors,
2. implement the code slice,
3. implement or update the required automated tests,
4. run the relevant verification where possible,
5. record results and gaps in the progress file,
6. and only then mark the slice complete.

If a critical scenario cannot yet be automated, the agent must:

- state why,
- identify what is missing,
- classify the scenario as `ManualOnly` or `Deferred`,
- and record the gap explicitly in the progress file.

### 17.11 Non-Functional Verification

The framework must not reduce verification to functional happy paths only.

Where relevant, define explicit scenarios or packs for:

- migration safety,
- idempotency,
- retry and backoff,
- concurrency handling,
- time-based processing,
- large payload handling,
- observability and diagnostic completeness,
- authorization boundaries,
- and destructive-operation protection.

These may be automated at integration level, validated through targeted scripts, or in some cases handled by controlled manual checks.

### 17.12 What This Framework Deliberately Avoids

This framework does **not** require heavyweight traditional QA bureaucracy.

Avoid:

- giant manual test-case catalogs with low signal,
- writing scenarios so vaguely they are just rewritten requirements,
- treating code coverage percentage as the primary measure of quality,
- letting agents invent critical behavioral truth without human review.

The goal is simple: make success explicit, automatable where sensible, and visible to the next human or agent session.

---

## 18. Evidence of Completion

### 18.1 Why "Implemented" Is Not Enough

A work package is not complete because the agent wrote code. It is complete when the intended behavior is implemented, the critical scenarios are proven, and the evidence is visible.

This matters because AI-assisted delivery creates a dangerous illusion of progress. Code appears quickly. Documentation sounds convincing. But if verification evidence is weak or invisible, the next session starts from a false belief that the slice is done.

### 18.2 Evidence Checklist

A meaningful slice should normally leave behind evidence in four categories:

1. **Code evidence** — the files that implement the behavior
2. **Verification evidence** — unit, integration, end-to-end, manual, or script-based proof
3. **Progress evidence** — working document updates, handoff status, blockers, deferrals
4. **Design evidence** — anchor references, decision-log updates, architecture or plan updates if the design changed

A work package should not be marked complete unless the expected evidence for that slice is present or the gap is explicitly recorded.

### 18.3 Verification Evidence in the Progress File

The progress file should contain a dedicated verification summary for each meaningful slice.

Recommended block:

```markdown
## Verification Status
- `TEST:...` — Passing
- `TEST:...` — Pending environment setup
- `TEST:...` — ManualOnly
- `TEST:...` — Deferred

## Evidence Summary
- Unit tests: [passing/failing/not run]
- Integration tests: [passing/failing/not run]
- End-to-end tests: [passing/failing/not run]
- Manual checks: [done/pending]
- Known gaps: [list]
```

This lets the next session see immediately which behaviors have actually been proven and which still rely on trust.

### 18.4 When Evidence Is Missing

If evidence is missing, the agent should not silently upgrade status to complete.

Instead it should use a more accurate label such as:

- **Implemented — verification pending**
- **Partially verified**
- **Blocked by environment**
- **Manual verification required**
- **Deferred by decision**

This keeps progress reporting honest and reduces rework.

### 18.5 Completion Labels — Refined

Use completion labels that reflect both implementation and proof.

Recommended meanings:

- **Designed** — approach and scope defined, not yet implemented
- **Implemented** — code written, verification incomplete
- **Verified** — linked critical scenarios proven with available evidence
- **Blocked** — cannot continue without human or environmental input
- **Deferred** — intentionally postponed with reason recorded
- **Complete ✅** — implementation done, critical verification satisfied, evidence visible, handoff updated

The key change is simple: **Complete** is an evidence-backed state, not just a coding state.

---

## 19. Requirements and Verification Traceability

### 19.1 The Traceability Gap

Requirements traceability is necessary but incomplete on its own.

A common failure mode is:

- a requirement exists,
- architecture addresses it,
- a workstream claims to implement it,
- but there is no stable reference for how success is actually proven.

That leaves a dangerous gap between design intent and operational confidence.

The traceability chain should therefore be:

`REQ:` → `ARCH:` → `PLAN:` → `TEST:` → evidence

This is the full path from business intent to proof.

### 19.2 Traceability Rules

1. Every meaningful `REQ:` should be implemented by at least one `ARCH:` concept and one `PLAN:` work package.
2. Every high-risk, stateful, or business-critical `REQ:` should also map to at least one canonical `TEST:` scenario.
3. High-value work packages should reference the `TEST:` anchors they are expected to satisfy.
4. Progress files should report verification status against those `TEST:` anchors.
5. Evidence summaries should make it clear whether each linked scenario is passing, blocked, manual-only, or deferred.

### 19.3 Traceability in Work Packages

A strong work package references the full chain where appropriate.

Example:

```markdown
**Relevant anchors:**
- `REQ:ApprovalWorkflow`
- `ARCH:HumanApprovalGate`
- `PLAN:WorkstreamF.ApprovalProcessing`
- `TEST:BenchmarkApproval.HappyPath`
- `TEST:BenchmarkApproval.RejectPath`
```

This gives the agent a stable route from requirement to design to delivery to proof.

### 19.4 Orphan Detection

During reviews, actively look for four classes of orphan:

- **Requirement orphan** — a `REQ:` with no implementing `ARCH:` or `PLAN:`
- **Design orphan** — an `ARCH:` concept with no delivery work attached
- **Delivery orphan** — a `PLAN:` work package with no clear requirement or architecture reason
- **Verification orphan** — a risky feature with no `TEST:` scenario or no evidence path

These are some of the highest-value review checks in AI-assisted delivery because they expose silent gaps early.

### 19.5 Traceability Review Moments

Do not wait until the end of the project to think about traceability.

Review it at these moments:

- when the initial requirements, architecture, and build plan are drafted,
- when a new workstream is introduced,
- when a high-risk design change is made,
- before phase exit,
- before a release or major merge,
- and when a feature is declared complete.

### 19.6 Copilot Instruction Expectations

Project instructions should explicitly teach the agent to navigate and report through the full traceability chain.

At minimum, the global instructions should make clear that the agent is expected to:

- look for linked `REQ:`, `ARCH:`, `PLAN:`, and `TEST:` anchors before implementing risky work,
- propose missing `TEST:` anchors when a critical scenario has no stable reference,
- update progress files with verification status,
- and avoid declaring completion when proof is absent.

---

## 20. State Models and Decision Tables

Where an entity or workflow has lifecycle complexity, do not rely on prose alone. Add a state model or decision table.

State models are especially valuable for:

- approvals,
- order or ledger processing,
- retries and failure handling,
- multi-step onboarding,
- async workflows,
- long-running document or pipeline states.

A state model reduces ambiguity for both humans and agents and improves verification because it makes valid and invalid transitions explicit.

---

## 21. Document Quality and Staleness

The framework depends on documents being trustworthy. A stale architecture or progress file is worse than no file because it creates confident confusion.

Review these document families regularly:

- requirements,
- architecture,
- build plan,
- verification catalog and packs,
- working plan files,
- progress files,
- decision log.

### 21.1 Freshness Checks

Run a quick freshness review when:

- a workstream is introduced or completed,
- the design changes materially,
- a release is approaching,
- or a new agent session repeatedly gets confused.

### 21.2 Staleness Signals

A document is probably stale if:

- it references files or services that no longer exist,
- it claims verification is passing when current evidence is missing,
- it omits recent design changes,
- it no longer matches the working code shape,
- or repeated handoff confusion appears across sessions.

---

## 22. Azure DevOps Integration

The framework works with any Git-based platform, but Azure DevOps is a good fit because it gives you repositories, pull requests, and Boards in one place.

Useful patterns include:

- link work items to workstream anchors,
- reference anchors in commits or PR descriptions,
- track workstream state in Boards,
- and use named regression packs for release readiness.

Do not let the tool replace the framework. Boards are not a substitute for working documents or verification evidence.

---

## 23. Scaling to Complex Architectures

As the system grows, the framework scales by increasing decomposition, not by relaxing discipline.

For larger systems:

- split architecture by bounded context,
- split build plan by major capability area,
- add module-scoped instructions by technical concern,
- create verification packs by service or workflow,
- and keep anchor indexes current.

The same principles still apply: explicit design truth, explicit delivery sequencing, explicit proof.

---

## 24. Quick-Start Checklist

Use this checklist to set up the framework for a new project.

### Phase 0 Setup (Before Any Code)

-

### First Implementation Session

-

### Ongoing Sessions

-

### Per-Phase Check

-

### 24.4 Minimal Verification Adoption Path

If you want the control benefits of the verification model without adding unnecessary process, adopt it in three steps:

1. **Introduce ********TEST:******** anchors immediately** — this gives you traceability with minimal disruption.
2. **Add Verification Status to all progress files** — this makes proof visible in current delivery.
3. **Use Verification Packs only for meaningful workstreams and releases** — do not force a pack for every tiny code change.

That is enough to close most of the framework gap without creating drag.

---

## 25. Templates

### 25.1 Architecture Document Template

```markdown
# [System Name] — Architecture Document

## Document Structure
- [List split files if used]

## Anchor Index
| Anchor | File |
|---|---|
| `ARCH:...` | ... |
```

### 25.2 Build Plan Template

```markdown
# [System Name] — Build Plan

## Strategy and Scope
- Purpose
- Scope
- Assumptions
- Delivery principles

## Workstream [X] — [Name]
**Stable work package anchor:** `PLAN:WorkstreamX.Name`

### Objective
[What this workstream delivers]

### Related Anchors
- `REQ:...`
- `ARCH:...`
- `TEST:...`
```

### 25.3 Global Copilot Instructions Template

```markdown
## Project Overview
[System summary]

## Tech Stack
- [Stack]

## Project Structure
- [Folders]

## Conventions
- [Coding conventions]

## Verification Expectations
- Treat linked `TEST:` anchors as part of implementation scope.
- Identify relevant scenarios before implementing risky or stateful work.
- Prefer tests that prove behavior, not just method coverage.
- Update the progress file with verification status.
- Do not mark work complete while critical linked scenarios remain unverified unless they are explicitly ManualOnly or Deferred.

## Required behavior
- [Agent operating model]

## Working document conventions
- [Plan and progress file rules]

## Delivery slice rule
- [Small slices]

## Human assistance request format
- [Format]

## Agent guardrails
- [Guardrails]

## Session continuity
- [How to resume from progress files]
```

### 25.4 Module Instruction Template

```markdown
---
applyTo: "**/[pattern]/**"
---

# [Concern]

> Relevant anchors: `ARCH:...`, `TEST:...`

## [Concern 1]
- [Rules]

## [Concern 2]
- [Rules]
```

### 25.5 Working Plan File Template

```markdown
# Workstream [X] — [Name]: Design and Implementation Plan

## Objective
[What this slice delivers]

## Relevant Anchors
- `REQ:...`
- `ARCH:...`
- `PLAN:...`

## Verification Anchors
- `TEST:...`
- `TEST:...`

## Scope
- [In scope]

## Non-Goals
- [Out of scope]

## Assumptions
- [Confirmed and unconfirmed]

## Human Dependencies
- [What requires human action]

## Phased Implementation
- [Steps]

## Completion Criteria
- [Implementation outcome]
- [Verification outcome]
- [Evidence outcome]
```

### 25.6 Working Progress File Template

```markdown
# Workstream [X] — [Name]: Progress

## Handoff Block
- **Current phase:**
- **Last completed step:**
- **Next exact step:**
- **Blockers:**
- **Human input required:**
- **Files most recently changed:**
- **Relevant `ARCH:` anchors:**
- **Relevant `PLAN:` anchors:**
- **Relevant `TEST:` anchors:**

## Verification Status
- `TEST:...` — [status]
- `TEST:...` — [status]

## Evidence Summary
- Unit tests: [passing/failing/not run]
- Integration tests: [passing/failing/not run]
- End-to-end tests: [passing/failing/not run]
- Manual checks: [done/pending]
- Known gaps: [list]

## Progress Log
### Session [N] — [Date]
#### Status: [Designed / Implemented / Verified / Blocked / Complete ✅]
- [What changed]
```

### 25.7 Verification Pack Template

```markdown
# Verification Pack — [Name]

**Purpose:** [What delivery slice this pack proves]
**Scope:** [Feature / workstream / release / smoke / data integrity]

## Linked Anchors
- `REQ:...`
- `ARCH:...`
- `PLAN:...`
- `TEST:...`

## Environment Assumptions
- [Database / services / stubs / toggles / feature flags]

## Seed Data / Fixtures
- [Required data setup]

## Scenarios

### `TEST:[AnchorName1]`
**Purpose:** [Behavior being proven]
**Preconditions:**
- [State]

**Action:**
- [Trigger]

**Expected outcome:**
- [Result]

**Automation target:**
- Unit: Yes/No
- Integration: Yes/No
- EndToEnd: Yes/No
- ManualOnly: Yes/No

**Evidence required:**
- [Named test, script, log, screenshot, or progress note]

### `TEST:[AnchorName2]`
[Repeat]

## Known Deferrals
- [Scenario] — [Reason] — [Decision owner if needed]

## Exit Criteria
- [What must pass for this pack to be considered satisfied]
```

### 25.8 Test Catalog Entry Template

```markdown
<!-- TEST:[AnchorName] -->
## [Scenario Title]

**Purpose:** [Why this scenario matters]

**Preconditions:**
- [Starting state]

**Action:**
- [Trigger]

**Expected outcome:**
- [Primary outcome]
- [Important side effects or invariants]

**Automation target:**
- Unit: Yes/No
- Integration: Yes/No
- EndToEnd: Yes/No
- ManualOnly: Yes/No

**Notes:**
- [Optional]
```

---

## 26. Framework-Generic vs. Project-Specific Guidance

The framework itself should stay generic. Project-specific technology choices, architecture constraints, domain semantics, and operating policies belong in project documents and instructions, not in the framework core.

That is the difference between:

- a reusable methodology, and
- a project control package built using that methodology.

---

## 27. Worked Example — End-to-End Flow

A typical flow using this framework looks like this:

1. human defines requirements and architecture,
2. human decomposes work into a build plan,
3. project gets global and module-scoped instructions,
4. workstream plan and progress files are created,
5. agent implements a bounded slice,
6. agent verifies the linked scenarios,
7. agent records evidence and updates handoff state,
8. human reviews and commits,
9. next session resumes from the progress file.

This is how the framework turns an AI agent from an impressive demo into a usable implementation partner.

---

## 28. Operator Quick-Reference Card

When using this framework day to day, remember the sequence:

1. **Define the design truth** — requirements, architecture, build plan.
2. **Anchor everything important** — `REQ:`, `ARCH:`, `PLAN:`, `TEST:`.
3. **Program the agent** — strong global and scoped instructions.
4. **Use working documents as memory** — plan + progress files.
5. **Work in small slices** — implementation and verification together.
6. **Stop at human boundaries** — secrets, cloud setup, approvals, destructive actions.
7. **Require evidence** — do not confuse code with proof.
8. **Keep documents fresh** — stale guidance poisons sessions.

### 28.4 Final Operating Principle

> A workstream is not complete when the code compiles. It is complete when the intended behavior is implemented, the critical scenarios are proven, and the evidence is visible to the next human or agent session.

---

## 29. `9. Agent Tools/` — Repository-Local Agent Skills and Support Tooling

<!-- Stable anchor: PLAN:Framework.AgentToolsConvention -->

### 29.1 Purpose

When a repository's documentation surface grows beyond a handful of files, coding agents waste significant context window and time searching broadly through markdown. The `9. Agent Tools/` folder provides one predictable home for repository-local agent skills, retrieval helpers, validation scripts, and generated support artifacts.

It is a **support surface for delivery**, not a replacement for the active control documents.

### 29.2 Authority Model

Files in the agent-tools folder are **generated or operational artifacts**, not sources of truth.

The active control set remains the numbered document hierarchy:

| Layer | Authority |
|-------|-----------|
| `1. Requirements/` | What must be true |
| `2. Architecture/` | How the system is shaped |
| `3. Build Plan/` | How delivery work is organized |
| `4. Verification/` | How completion is proven |

If a tool output conflicts with an active control document, treat the tool output as suspect until reconciled.

`9. Agent Tools/` sits within the numbered hierarchy but its contents are support tooling, not authoritative design or verification documents. It keeps agent-operational helpers visible and standardized.

### 29.3 Standard Folder Structure

```text
src/9. Agent Tools/
├── README.md           ← Conventions, inventory, authority rules
├── indexing/           ← Retrieval/index generation helpers and outputs
│   ├── generate_agent_index.py
│   ├── agent_retrieve.py
│   ├── AGENT_INDEX.json   (generated, not hand-maintained)
│   └── README.md
├── validation/         ← Freshness/integrity checks
│   ├── check_agent_index_freshness.py
│   └── README.md
├── prompts/            ← Reusable agent task templates
│   ├── README.md
│   ├── workstream_implementation.md
│   ├── architecture_review.md
│   ├── verification_mapping.md
│   └── session_handoff.md
└── scratch/            ← Optional temporary local artifacts (not authority)
```

### 29.4 Conventions

1. **Prefer small, single-purpose scripts.** Each tool should do one thing well.
2. **Keep generated artifacts clearly named and reproducible.** A script should be able to regenerate any artifact from the markdown source.
3. **Do not place authoritative requirements, architecture, plan, or verification content here.** Those belong in the numbered hierarchy.
4. **If a tool becomes material to delivery control**, reference it from the relevant `PLAN:` and `TEST:` anchors.
5. **If a tool embodies a significant architectural decision**, record or propose the relevant ADR rather than letting the tool define policy implicitly.
6. **Keep scripts dependency-free where possible.** Python standard library is preferred for portability.

### 29.5 The Documentation Retrieval Layer

The primary initial use of `9. Agent Tools/` is a machine-readable documentation retrieval layer. The pattern is:

1. **Markdown documents remain the source of truth.**
2. **A generated `AGENT_INDEX.json`** acts as a compact retrieval map — lightweight enough for local scripts to rank likely documents without loading the full corpus.
3. **A retrieval script** (`agent_retrieve.py`) resolves the best documents, anchor candidates, and bounded snippets for a given query.
4. **A freshness validator** (`check_agent_index_freshness.py`) detects when the index is older than the documents it covers.

The generated index captures per document:

- **keywords** — automatically extracted from headings, path segments, anchor names, and body text (capped to avoid noise)
- **anchors** — regex-extracted formal anchors, split into `defined_anchors` (where the anchor is established) and `mentioned_anchors` (where it is referenced)
- **frontmatter** — YAML frontmatter is parsed when present, allowing documents to declare `status`, `canonical`, and `last_updated` metadata that overrides path-based defaults
- **relationships** — cross-document links detected via shared anchors (`references` and `referenced_by`)
- **headings**, **domains**, **description**, **authority_rank**, **source_modified_utc**

The retrieval layer should:

- prefer active/canonical control documents over working or legacy evidence
- use formal anchors (`REQ:`, `ARCH:`, `PLAN:`, `TEST:`, etc.) as precise control points, ranked above keyword matches
- keep the index lightweight — no large text excerpts embedded in the map
- surface staleness explicitly rather than serving stale results silently

### 29.6 Retrieval Workflow

The intended workflow for an agent session:

```text
1. Refresh the index (if stale):
   python3 "src/9. Agent Tools/indexing/generate_agent_index.py"

2. Resolve context for a task:
   python3 "src/9. Agent Tools/indexing/agent_retrieve.py" "<query>" --json

3. Use the returned snippet as primary context.
   Only open full documents when the snippet is insufficient.
```

This avoids dumping entire document corpora into the agent's context window.

### 29.7 Mandatory Agent Retrieval Rule

When a repository adopts `9. Agent Tools/` with a working retrieval layer, the global agent instructions (`copilot-instructions.md`) should include a mandatory retrieval rule so the agent actually uses the tooling before broad document searches.

The short-form rule is:

> Before searching or reasoning over repo documentation, run:
> `python3 "src/9. Agent Tools/indexing/agent_retrieve.py" "<task topic>" --json`
>
> Use the returned `snippet` first. Prefer `canonical: true` and `status: active` docs. Prefer formal anchors over keyword matches. Do not dump whole markdown corpora into model context unless the local retrieval result is insufficient. The markdown docs are the source of truth. `AGENT_INDEX.json` is only a retrieval map. If documents conflict, report the conflict explicitly.

### 29.8 Freshness and Validation

The retrieval layer is only useful if it stays current. At minimum:

- Run the freshness check at the start of significant work sessions.
- Regenerate the index after documentation changes.
- Wire the freshness check into CI or pre-commit hooks. A `.githooks/pre-commit` hook is the recommended lightweight approach — enable it with `git config core.hooksPath .githooks`.
- The retrieval script itself should warn when it detects potential staleness.

### 29.9 Current and Future Extensions

The convention currently includes:

- **retrieval and indexing** — `generate_agent_index.py`, `agent_retrieve.py`, and `AGENT_INDEX.json` with keywords, frontmatter parsing, and cross-document relationships
- **freshness validation** — `check_agent_index_freshness.py` plus a `.githooks/pre-commit` hook
- **prompt templates** — reusable task templates for workstream implementation, architecture review, verification mapping, and session handoff

Future extensions may include:

- code-generation scaffolding helpers
- cross-repo retrieval federation
- automated regression of retrieval quality

Each addition should follow the same authority rule: tools support delivery; they do not replace the control documents.

---

## 30. `8. Agent Skills/` — Instructional Skill Documents

<!-- Stable anchor: PLAN:Framework.AgentSkillsConvention -->

### 30.1 Purpose

As agent workflows grow more sophisticated, the terse rules in `copilot-instructions.md` and the step-by-step checklists in `9. Agent Tools/prompts/` are not enough to teach an agent *how to reason* about the framework's methodology.

`8. Agent Skills/` provides **instructional skill documents** — deeper teaching material that explains reasoning patterns, decision-making heuristics, and when/why to apply framework concepts. Think of it as the team onboarding guide for any new agent session.

### 30.2 Relationship to Other Layers

| Layer | Contains | Purpose |
|-------|----------|---------|
| `0. Framework/` | Framework methodology | Defines the methodology |
| `.github/copilot-instructions.md` | Agent behavior rules | Programs the agent's constraints |
| `8. Agent Skills/` | Instructional documents | Teaches the agent *how to think* |
| `9. Agent Tools/prompts/` | Operational checklists | Tells the agent *what steps to follow* |
| `9. Agent Tools/indexing/` | Executable scripts | Retrieval and indexing tools |

**Skills explain the "why" and "how to reason."** Prompts list the "what to do." Tools provide the "with what."

### 30.3 Authority Model

Skill documents are **instructional guidance**, not authoritative control documents.

The active control set remains the numbered document hierarchy (`1. Requirements/` through `4. Verification/`). Skill documents teach the agent how to *apply* those control documents — they do not replace them.

If a skill document conflicts with a control document, the control document wins.

### 30.4 Standard Skill Set

A repository adopting the framework should include skills covering at minimum:

| Skill | Covers |
|-------|--------|
| **Retrieval and Context Gathering** | How to use retrieval tools, manage context window, interpret results |
| **Delivery Chain Reasoning** | How to trace REQ→ARCH→PLAN→TEST, detect orphans |
| **Session Lifecycle** | Session start, mid-session checkpoints, end-of-session handoff |
| **Code Change Discipline** | Inspect first, work in slices, human boundaries, tech-stack alignment |
| **Documentation Maintenance** | What the agent may update vs. propose, staleness signals |
| **Drift Detection and Remediation** | Classification taxonomy, remediation workflow |
| **Working with Anchors** | Creating, using, citing, maintaining stable references |

Additional skills may be added for project-specific workflows (e.g., deployment procedures, specific testing strategies, domain-specific reasoning).

### 30.5 Conventions

1. **Each skill follows a consistent structure:** Purpose → When to Use → Core Concepts → Reasoning Patterns → Worked Examples → Common Mistakes → Related Skills.
2. **Reference, don't duplicate.** Skills point to framework sections and control documents rather than copying content.
3. **Keep skills stable.** These should change infrequently — only when the methodology evolves.
4. **Do not define new anchors in skill documents.** Skills reference existing `REQ:`/`ARCH:`/`PLAN:`/`TEST:` anchors but do not establish new authoritative anchors.
5. **Tech-stack specifics belong in copilot-instructions.** Skills may reference tech patterns but defer to the copilot instructions for detailed conventions.
6. **Number skill files for reading order** (e.g., `01_`, `02_`), similar to how architecture docs are split by concern.

### 30.6 Cross-References

Prompt templates in `9. Agent Tools/prompts/` should cross-reference the deeper skill documents where applicable:

| Prompt Template | Deepened By |
|-----------------|-------------|
| `workstream_implementation.md` | Skills 02 (Delivery Chain), 04 (Code Change) |
| `architecture_review.md` | Skill 06 (Drift Detection) |
| `verification_mapping.md` | Skill 02 (Delivery Chain), 07 (Anchors) |
| `session_handoff.md` | Skills 03 (Session Lifecycle), 05 (Documentation Maintenance) |

---

## Appendix A: Frequently Asked Questions

### Why not just keep everything in chat?

Because chat is not a durable operating model. Working documents are.

### Why so much emphasis on anchors?

Because section numbers drift and headings change. Stable references keep humans and agents aligned.

### Why not trust the agent to decide what to test?

Because agents are strong at implementation but weak at implicit behavioral truth. Make success explicit.

### Why not use code coverage as the main quality measure?

Because coverage can be high while behavior is still unproven. Scenario proof is more valuable.

### Does this only work with Copilot and Rider?

No. The framework is tool-agnostic. Those are just the tools used in the examples.

## Appendix B: Origin Context

This framework was refined through real-world use on a complex but focused engineering effort involving a monolithic web app, multi-agent AI processing, dual databases, cloud dependencies, approval workflows, and phased rebuild work. It was shaped by the practical realities of getting durable value from AI coding agents without letting them invent the design as they went.

