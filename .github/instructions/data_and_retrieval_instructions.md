---
applyTo: "apps/backend/**/models/**/*.py,apps/backend/**/domain/**/*.py,apps/backend/**/persistence/**/*.py,apps/backend/**/repositories/**/*.py,apps/backend/**/db/**/*.py,apps/backend/**/retrieval/**/*.py,apps/backend/**/summaries/**/*.py,apps/backend/**/search/**/*.py,apps/backend/**/migrations/**/*.py"
---

# Glimmer — Data, Persistence, and Retrieval Module Instructions

## Purpose

This instruction file defines the module-scoped rules for Glimmer data model, persistence, summaries, retrieval, and database-adjacent implementation.

It supplements the global `.github/copilot-instructions.md` file and applies specifically to:

- domain and persistence models,
- repository implementations,
- relational schema and migrations,
- summary and memory-refresh services,
- retrieval/search code,
- vector-support code,
- and data-integrity-related infrastructure.

These rules are stricter than generic data-layer guidance because this part of Glimmer is where the system’s operational truth lives.

The load-bearing concerns here are:

- structured relational truth,
- accepted-vs-interpreted separation,
- provenance retention,
- summary discipline,
- auditability,
- and keeping retrieval as a helper rather than a hidden replacement for real state.

Framework alignment: Agentic Delivery Framework and Testing Strategy Companion.

---

## 1. Authority and Scope Rule

When working in this module area, the agent must stay aligned to the following control surfaces in order:

1. Requirements
2. Architecture
3. Build Plan
4. Verification
5. Global Copilot instructions
6. This module instruction file
7. Workstream working documents
8. Code

Do not let convenience in schema, repository, or retrieval design silently override Glimmer’s documented memory model.

---

## 2. What This Module Must Preserve

Data and retrieval work must preserve these core Glimmer properties:

- **structured memory over loose history**,
- **relational truth first**,
- **accepted state separate from interpreted state**,
- **source provenance preserved throughout persistence**,
- **summary artifacts as derived artifacts, not magical truth rewrites**,
- **retrieval as bounded recall support rather than the primary state model**,
- and **auditability for meaningful state evolution**.

These are load-bearing architecture rules, not implementation preferences.

---

## 3. Primary Data-Model Rules

### 3.1 Model the domain explicitly

Persist meaningful operational concepts as explicit models rather than hiding them in free text blobs.

This includes, where relevant:

- operator context,
- projects,
- workstreams,
- milestones,
- stakeholders,
- stakeholder identities,
- connected accounts,
- account profiles,
- messages,
- threads,
- calendar events,
- imported signals,
- interpreted artifacts,
- accepted work items,
- drafts,
- briefing artifacts,
- focus packs,
- persona assets,
- channel sessions,
- summaries,
- and audit records.

### 3.2 Keep memory layers distinct

Preserve the documented memory layering:

1. source records
2. interpreted candidate artifacts
3. accepted operational state
4. synthesized artifacts and summaries

Do not collapse these layers into one “memory” table or one generic document unless the control documents explicitly require that shape.

### 3.3 Provenance is part of the data model

Source account, provider, profile, thread/event/source identity, timestamps, and import metadata are not optional decoration. They are part of the meaning of the record.

### 3.4 Relationships matter

Prefer explicit relationships over convenience denormalization when relationship semantics are part of the product behavior.

Examples include:

- stakeholder-to-project links,
- source artifact to connected-account linkage,
- interpreted artifact to source linkage,
- accepted work item to origin linkage,
- summary to refresh lineage,
- and audit record to the state mutation it explains.

---

## 4. Relational Persistence Rules

### 4.1 PostgreSQL is the operational source of truth

Use PostgreSQL-backed structured state as the primary operational store.

This means:

- important state should be queryable relationally,
- migrations matter,
- constraints matter,
- and entity relationships matter.

Do not treat the relational layer as a temporary cache for model prompts.

### 4.2 Preserve migration discipline

Schema evolution should happen through deliberate migrations or equivalent explicit change tracking.

Do not:

- silently rely on runtime schema creation in production-like paths,
- make ad hoc destructive changes without recording them,
- or introduce persistence changes without considering migration impact.

### 4.3 Model constraints explicitly

Where the domain implies rules such as uniqueness, requiredness, versioning, ownership, or lifecycle constraints, reflect those rules in persistence design where practical.

### 4.4 Soft state transitions deserve explicit modeling

When state changes matter operationally, represent that state explicitly rather than burying it in a note field.

Examples include:

- review status,
- accepted vs pending,
- sync status,
- active vs superseded summary,
- and blocked vs ready work state.

---

## 5. Accepted vs Interpreted State Rules

### 5.1 Never treat model inference as immediate truth

Interpreted artifacts such as:

- project classifications,
- extracted actions,
- extracted deadlines,
- decisions,
- blockers,
- or stakeholder resolution guesses

must remain reviewable candidate state until explicitly accepted or otherwise promoted under the documented rules.

### 5.2 Accepted state must be durable and queryable

Accepted work items, decisions, risks, blockers, waiting-on records, and related operational artifacts must exist as their own durable layer.

### 5.3 Promotion paths should be traceable

Where interpreted artifacts become accepted operational state, the persistence model should support traceability across that transition.

### 5.4 Do not blur layers for query convenience

If a query is awkward, fix the query or add a projection. Do not solve it by collapsing candidate and accepted state together.

---

## 6. Provenance and Multi-Account Rules

### 6.1 Never flatten account identity

One operator may have multiple Google and Microsoft accounts and profiles. Data-layer code must preserve that distinction.

At minimum, records should preserve or reliably resolve:

- connected account identity,
- provider type,
- account profile where relevant,
- remote object identity,
- channel/source type,
- and import timestamps.

### 6.2 Provenance survives transformation

Normalization, summarization, classification, planning, and drafting may all derive new artifacts, but the persistence layer must still support origin tracing back to the relevant source artifacts.

### 6.3 Query with account awareness where it matters

Do not write data access logic that quietly assumes one default inbox, one default tenant, or one generic source stream when the use case is actually account-sensitive.

---

## 7. Summary and Memory-Refresh Rules

### 7.1 Summaries are derived artifacts

Project summaries, briefing artifacts, focus packs, and related synthesized memory artifacts are derived outputs.

They are important, but they are not permission to discard the lower-level source and accepted state they were derived from.

### 7.2 Summary refresh must be explicit

Summary refresh should happen through:

- explicit triggers,
- explicit services,
- explicit metadata,
- and traceable lineage.

Do not create hidden background summary rewriting that leaves no audit trail.

### 7.3 Preserve summary metadata

Persist metadata that allows the system to understand:

- what was summarized,
- when,
- by which process or policy,
- under what threshold or trigger,
- and whether the summary is current or superseded.

### 7.4 Do not let summaries become shadow truth

Summaries can support fast orientation and retrieval, but they must not become the only place where important facts exist.

---

## 8. Retrieval and Search Rules

### 8.1 Retrieval supports memory; it does not replace it

Semantic retrieval, embeddings, vector search, or hybrid search may help Glimmer recall relevant context efficiently.

However:

- retrieval is secondary to structured state,
- retrieved similarity is not accepted truth,
- and retrieval results must be interpreted in the context of the domain model.

### 8.2 Bound retrieval scope

Prefer bounded retrieval strategies such as:

- project-scoped recall,
- stakeholder-scoped recall,
- recent-source recall,
- or summary-linked recall

instead of broad unbounded search over everything for every task.

### 8.3 Preserve retrieval provenance

If retrieval influences a visible artifact, the system should be able to explain what sources or summaries informed the output.

### 8.4 Do not use vector stores as the system of record

Vector support is an augmentation layer, not the canonical persistence model.

### 8.5 Retrieval freshness matters

Where freshness or staleness changes meaning, retrieval logic should prefer current or active artifacts rather than blindly ranking old content highly.

---

## 9. Repository and Query Rules

### 9.1 Repositories should express domain meaning

Repository and query methods should reflect real domain use cases.

Prefer names and query shapes such as:

- get active focus pack for project,
- list pending review artifacts for operator,
- load source records for connected account,
- retrieve current project summary,
- list accepted work items by project and state

rather than generic “get all entities” patterns everywhere.

### 9.2 Separate read models where useful

If the domain model becomes awkward for UI or workflow-specific reads, add explicit projections or query services.

Do not damage the domain model just to make one UI query convenient.

### 9.3 Keep query behavior inspectable

Complex retrieval and summary-selection logic should be testable and explainable, not hidden inside opaque repository magic.

---

## 10. Audit and Traceability Rules

### 10.1 Meaningful memory evolution must be auditable

The persistence layer should support traceability for meaningful changes such as:

- interpreted artifact creation,
- review decisions,
- accepted-state promotion,
- summary refresh,
- draft generation where tracked,
- and connector sync/failure updates where they affect user-visible behavior.

### 10.2 Audit records should explain, not just log

Where possible, audit-linked records should help answer:

- what changed,
- why,
- from what source,
- under what review state,
- and whether the operator overrode the assistant.

### 10.3 Do not rely on application logs alone

Logs are useful operationally, but they are not a substitute for durable traceable records in the domain where the architecture calls for them.

---

## 11. Migration and Schema-Change Rules

### 11.1 Schema changes are design changes

Changes to core entities, relationships, or constraints are not trivial edits. Treat them as design-affecting work.

### 11.2 Surface material schema tradeoffs

If a schema decision affects:

- provenance,
- review-state separation,
- summary lineage,
- multi-account semantics,
- or auditability,

surface the tradeoff instead of silently simplifying it.

### 11.3 Respect backward evolution where relevant

Where the project has already started to accumulate real data, think about how the migration path preserves correctness, not just how to make the ORM happy.

---

## 12. Security and Data-Handling Rules

### 12.1 Secrets do not belong in normal operational tables unless designed so

Do not casually persist provider secrets, raw tokens, or credentials in domain tables.

### 12.2 Sensitive context should remain bounded

When deciding what to persist, keep the local-first and least-privilege posture in mind. Persist what the system needs, not everything that happens to be available.

### 12.3 Retrieval must respect privacy boundaries

Do not create broad retrieval behavior that can accidentally surface unrelated sensitive project context into the wrong workflow without bounded justification.

---

## 13. Testing Expectations for This Module

When editing data/persistence/retrieval code, the default proof target should include as appropriate:

- **unit tests** for deterministic normalization, selection, or ranking helpers,
- **integration tests** for mappings, repositories, migrations, state transitions, and summary refresh behavior,
- **data-integrity tests** for accepted-vs-interpreted separation, provenance retention, and audit record creation,
- **API or service-level tests** where data-layer behavior is surfaced through application boundaries,
- and **retrieval-behavior tests** where bounded recall logic influences visible outputs.

### 13.1 Data-specific proof rules

- Domain-model changes must prove relationship correctness.
- Migration changes must prove schema compatibility and expected constraints.
- Summary changes must prove refresh triggers, metadata, and lineage.
- Provenance-related changes must prove account/profile/source identity survives persistence round trips.
- Retrieval changes must prove boundedness and must not implicitly replace structured truth.

### 13.2 Do not mark data-layer work complete without executed proof

If a meaningful persistence or retrieval change has no executed verification, the work is not done.

---

## 14. Preferred Data-Layer Session Workflow

When working in this module area, the default session sequence should be:

1. identify relevant `REQ:` anchors,
2. identify relevant `ARCH:` anchors,
3. identify relevant `PLAN:` anchors,
4. inspect current models, mappings, queries, and migrations,
5. implement one bounded persistence/retrieval slice,
6. run the relevant proof,
7. update the workstream progress file,
8. report assumptions, blockers, and evidence clearly.

---

## 15. What to Do When the Docs Are Incomplete

If a persistence or retrieval change needs a data rule that does not yet have a stable anchor:

1. do not invent the data model silently,
2. propose the missing anchor,
3. make only the smallest safe implementation move,
4. and record the gap in the relevant working document.

Typical examples include:

- a new summary artifact type,
- a new provenance field requirement,
- a new accepted-state promotion pattern,
- or a new retrieval-boundedness rule.

---

## 16. Anti-Patterns to Avoid in This Module

Do not:

- replace explicit domain entities with generic JSON blobs for convenience,
- collapse interpreted and accepted state into one model,
- treat vector search as the main truth source,
- discard provenance during normalization or summary generation,
- let summaries rewrite history without lineage,
- rely on logs instead of audit records where auditability is required,
- make schema changes without migration discipline,
- or optimize data shape purely for one temporary UI convenience.

---

## 17. Final Rule

When in doubt, make the data layer more:

- explicit,
- provenance-preserving,
- relationally grounded,
- audit-friendly,
- and testable.

Do not optimize for magical retrieval or temporary convenience.
Optimize for a durable operational memory system that the rest of Glimmer can trust.
