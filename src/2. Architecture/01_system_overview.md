# Glimmer — System Overview

## Document Metadata

- **Document Title:** Glimmer — System Overview
- **Document Type:** Split Architecture Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `ARCHITECTURE.md`
- **Primary Companion Documents:** Requirements, Domain Model, LangGraph Orchestration, Connectors and Ingestion

---

## 1. Purpose

This document defines the high-level system shape for **Glimmer**.

It explains how the product is intended to operate from the perspective of:

- user-facing modes,
- deployment posture,
- major capability groupings,
- system boundaries,
- multi-account handling,
- and companion-channel interaction.

This file does not attempt to define all detailed data structures or orchestration flows. Those concerns are delegated to the domain model and orchestration documents. Instead, this document provides the top-level architecture narrative that connects the requirements posture to the split architecture set.

**Stable architecture anchor:** `ARCH:SystemOverview`
**Stable architecture anchor:** `ARCH:SystemIntent`

---

## 2. High-Level Narrative

Glimmer is a **local-first AI project chief-of-staff system** built for a single primary operator who is managing multiple live projects across multiple communication accounts and contexts.

At a high level, Glimmer works by:

1. ingesting project-relevant signals from connected communication and calendar accounts,
2. normalizing those signals into a structured internal model,
3. maintaining persistent project and stakeholder memory,
4. using orchestration flows to classify, prioritize, summarize, and draft,
5. presenting the resulting guidance through a dedicated web interface,
6. and extending a subset of interaction capability through Telegram as a mobile companion surface.

The core system is not a general autonomous agent. It is a **reviewable, structured, advisory operating system for project coordination**.

The product is therefore designed around the idea that:

- memory must be durable,
- prioritization must be explainable,
- communication support must be tactful,
- and externally impactful actions must remain under operator control.

**Stable architecture anchor:** `ARCH:SystemNarrative`

---

## 3. Operating Modes

Glimmer shall support distinct but connected operating modes.

### 3.1 Primary web workspace mode

The web workspace is the main operating surface for Glimmer.

This mode is intended for:

- portfolio review,
- project-specific planning,
- message triage,
- draft review,
- stakeholder context review,
- work breakdown refinement,
- and detailed interaction with Glimmer’s visual persona and execution views.

The web workspace is the canonical human-facing system of interaction.

**Stable architecture anchor:** `ARCH:OperatingMode.WebWorkspace`

### 3.2 Telegram companion mode

Telegram is the selected MVP companion channel for Glimmer.

This mode is intended for lightweight, mobile, or out-of-office interaction such as:

- asking what matters most today,
- checking project status,
- capturing notes or follow-ups,
- receiving a concise summary,
- and continuing conversational interaction away from the main UI.

Telegram is not intended to replace the web workspace. It is a companion surface with narrower scope, optimized for convenience and continuity.

**Stable architecture anchor:** `ARCH:OperatingMode.TelegramCompanion`

### 3.3 Voice interaction mode

Voice interaction is a mode of use rather than a completely separate product surface.

Voice may be exposed through the web workspace and, over time, may also interact with companion-channel workflows where technically and operationally appropriate.

Voice mode is intended for:

- spoken briefings,
- spoken project updates,
- capture of actions,
- and conversational planning.

Voice remains layered onto the same underlying memory and orchestration model as the rest of the product.

**Stable architecture anchor:** `ARCH:OperatingMode.Voice`

### 3.4 Background synchronization mode

Glimmer also includes non-interactive background operation for:

- polling or receiving messages from connected sources,
- ingesting calendar events,
- refreshing summaries,
- updating project memory,
- and preparing daily/weekly operating views.

This background mode exists to keep the system current between active user sessions.

**Stable architecture anchor:** `ARCH:OperatingMode.BackgroundSync`

### 3.5 Review and approval mode

Certain workflows enter an explicit review state, such as:

- draft approval,
- ambiguous classification confirmation,
- memory mutation review,
- and other non-trivial operator-facing decisions.

This review mode is a foundational behavioral characteristic of Glimmer rather than a special case.

**Stable architecture anchor:** `ARCH:OperatingMode.Review`

---

## 4. Capability Map

The system is composed of seven primary capability groups.

### 4.1 Portfolio coordination

This capability group covers:

- maintaining multiple projects,
- comparing them against each other,
- surfacing urgency and blockage,
- and helping the operator decide where time should go next.

**Stable architecture anchor:** `ARCH:Capability.PortfolioCoordination`

### 4.2 Project memory and retrieval

This capability group covers:

- durable project memory,
- stakeholder memory,
- retrieval of recent decisions and activity,
- and structured recall that supports drafting and prioritization.

**Stable architecture anchor:** `ARCH:Capability.ProjectMemory`

### 4.3 Message and signal triage

This capability group covers:

- ingestion from multiple connected accounts,
- message normalization,
- source attribution,
- project classification,
- action/deadline extraction,
- and triage queue generation.

**Stable architecture anchor:** `ARCH:Capability.SignalTriage`

### 4.4 Planning and prioritization

This capability group covers:

- work breakdown support,
- next-step generation,
- daily focus generation,
- weekly review support,
- and explainable priority ranking.

**Stable architecture anchor:** `ARCH:Capability.PlanningAndPrioritization`

### 4.5 Drafting and communication support

This capability group covers:

- reply draft generation,
- tone shaping,
- stakeholder-aware wording,
- and a separate reviewable drafting workspace.

**Stable architecture anchor:** `ARCH:Capability.DraftingSupport`

### 4.6 Companion interaction

This capability group covers:

- Telegram conversation handling,
- lightweight mobile access,
- continuity of interaction beyond the main UI,
- and concise summaries and capture flows.

**Stable architecture anchor:** `ARCH:Capability.CompanionInteraction`

### 4.7 Persona and experience support

This capability group covers:

- visual persona rendering,
- mood/context-driven persona image selection,
- briefing-style output,
- and maintenance of Glimmer’s product voice.

**Stable architecture anchor:** `ARCH:Capability.PersonaExperience`

**Stable architecture anchor:** `ARCH:CapabilityMap`

---

## 5. Multi-Account Operator Model

Glimmer is explicitly designed for a single primary operator who may have multiple connected communication identities.

This includes support for more than one:

- Google account,
- Google Workspace account,
- Microsoft 365 / Office 365 account,
- mail profile,
- calendar profile,
- and potentially distinct organizational tenant context.

The architecture shall treat this as a first-class operating reality.

The purpose of multi-account support is not merely account aggregation. It is to preserve operational meaning. A message’s source account may influence:

- its likely project associations,
- its stakeholder interpretation,
- its urgency,
- its draft tone,
- and how the operator chooses to act on it.

Therefore, Glimmer must preserve source provenance all the way through ingestion, triage, memory linking, and UI presentation.

**Stable architecture anchor:** `ARCH:OperatingMode.MultiAccountContext`

---

## 6. Deployment Posture

### 6.1 Local-first deployment

The default deployment posture for Glimmer is local-first.

This means the baseline architecture should assume that the operator’s most sensitive working context — including project memory, message content, draft content, and local task state — is primarily stored and managed under local control.

The local-first posture does not prohibit selective cloud-assisted capabilities. However, such capabilities must be explicit, reviewable, and policy-driven.

**Stable architecture anchor:** `ARCH:DeploymentPosture`

### 6.2 Layered local runtime model

A typical Glimmer deployment is expected to include:

- a local backend service runtime,
- a local or locally managed primary database,
- local or locally controlled artifact storage,
- a browser-based UI served by the local application stack,
- local model inference for reasoning, voice, and assistant tasks,
- and configured access to remote APIs such as Google and Microsoft for source ingestion.

This allows Glimmer to preserve a strong local operational center while still interacting with external services through explicit connectors.

**Stable architecture anchor:** `ARCH:DeploymentModel.LocalRuntime`
**Stable architecture anchor:** `ARCH:TechnologyBaseline`

### 6.2A Target hardware profile and local inference baseline

The target deployment environment for Glimmer MVP is an **Apple Silicon workstation** with high unified memory — specifically, an **Apple M5 Max with 128 GB unified memory** or equivalent.

This hardware profile is significant because it enables:

- local inference of large language models (up to 31B parameters at FP16/Q8 precision) with sufficient throughput for interactive use,
- concurrent execution of multiple model sizes for different task classes,
- native audio model inference for voice interaction without mandatory cloud dependencies,
- and sufficient memory bandwidth for conversational-speed token generation.

The target local inference runtime is **MLX** (Apple's framework for machine learning on Apple Silicon), which supports efficient model execution using the unified memory architecture.

The current reference model family is **Gemma 4**, with three tiers mapped to different task profiles:

| Model | Parameters | Role | Precision target |
|---|---|---|---|
| Gemma 4 31B IT (Thinking) | 31B | Deep reasoning — triage, prioritization, drafting, planning | FP16 / Q8 |
| Gemma 4 26B A4B IT (Thinking) | 26B (MoE, 3.8B active) | Low-latency conversational assistant — daily chat, fast responses | Q6_K / Q8 |
| Gemma 4 E4B IT (Thinking) | 4.5B | Native audio voice interaction — direct speech-to-speech with prosody awareness | FP16 |

This multi-model local strategy aligns with the model-routing policy defined in the security and permissions architecture (`ARCH:RemoteModelBoundary`). The key difference from the original posture is that **all three tiers can run locally** on the target hardware, making cloud model providers optional rather than structurally required.

The specific model family and versions may evolve. The architecture should treat the model layer as a bounded dependency behind an inference abstraction, not as a hardwired coupling to a single model checkpoint.

**Stable architecture anchor:** `ARCH:TargetHardwareProfile`
**Stable architecture anchor:** `ARCH:LocalInferenceBaseline`

### 6.3 External dependency posture

External services are used where they are the official and stable source of truth for connected systems, such as:

- Gmail,
- Google Calendar,
- Microsoft Graph mail,
- Microsoft Graph calendar,
- and Telegram messaging infrastructure.

Voice infrastructure is expected to run locally using on-device model inference rather than requiring an external voice service dependency.

These dependencies must remain bounded through connectors and explicit integration contracts.

**Stable architecture anchor:** `ARCH:DeploymentModel.ExternalDependencies`

---

## 7. System Boundary and Responsibilities

**Stable architecture anchor:** `ARCH:SystemBoundaries`

### 7.1 What Glimmer is responsible for

Glimmer is responsible for:

- maintaining structured project and stakeholder context,
- understanding and organizing project-relevant communications,
- identifying likely next steps and priorities,
- preparing contextual briefings,
- drafting responses for operator review,
- escalating tasks that exceed local model capability to a bounded deep-research path,
- and supporting multi-surface interaction across web, voice, and Telegram.

**Stable architecture anchor:** `ARCH:SystemResponsibility.InScope`

### 7.2 What Glimmer is not responsible for

Glimmer is not responsible for, in MVP:

- autonomous outward communication,
- unbounded desktop control or general web automation,
- covert background decision-making,
- unsupported personal-message platform integration,
- or replacing the operator's judgment on sensitive stakeholder matters.

**Stable architecture anchor:** `ARCH:SystemResponsibility.OutOfScope`

### 7.3 Deep research and escalated reasoning boundary

Glimmer shall support a bounded deep-research capability for tasks that exceed the local model's practical reasoning or research capability.

This capability:

- uses a Python-native browser-mediated adapter to interact with Gemini through the operator's own browser session,
- is invoked explicitly by the operator, by orchestration policy, or by escalation logic within workflows,
- produces structured research artifacts that re-enter Glimmer's memory, triage, and planning flows,
- and remains bounded, auditable, and operator-controlled.

This is not a general autonomous web-browsing feature. It is a **bounded research and reasoning escalation tool** that sits between the orchestration layer, the external tool boundary, and the structured memory model.

**Stable architecture anchor:** `ARCH:DeepResearchCapability`
**Stable architecture anchor:** `ARCH:ResearchToolBoundary`

### 7.5 Expert advice (synchronous external consultation)

Glimmer shall support a synchronous expert-advice capability that uses the same browser-mediated Gemini adapter to consult a more powerful external LLM for specific questions, decisions, or reasoning tasks.

Expert advice is distinct from deep research in that:

- it is **synchronous** — a single prompt is sent and a text response is returned (seconds to minutes),
- it does not produce multi-step research documents or Google Docs artifacts,
- it supports mode selection (Fast for quick lookups, Thinking for reasoning-heavy tasks, Pro for general expert consultation),
- and it records each exchange as a lightweight provenance-preserving consultation record.

Expert-advice responses enter Glimmer's workflow as **interpreted candidates**, not accepted truth. They are subject to the same review-gate discipline as any other interpreted artifact.

The expert-advice path shares the same browser-mediated adapter boundary and Chrome debug-mode attachment as deep research. Only one Gemini operation may execute at a time (deep research or expert advice), enforced by the adapter's internal operation lock.

**Stable architecture anchor:** `ARCH:ExpertAdviceCapability`

### 7.4 Review-first operating posture

The system is deliberately designed so that important outputs are surfaced for human review rather than silently committed into the outside world.

This includes:

- reply drafts,
- ambiguous classifications,
- memory merges or non-trivial updates,
- and other operator-significant interpretations.

This is central to trust and usability.

**Stable architecture anchor:** `ARCH:SystemResponsibility.ReviewFirst`

---

## 8. User Experience Surfaces

### 8.1 Portfolio surface

A portfolio-level surface shall present:

- current projects,
- priority ranking,
- stale or blocked items,
- upcoming obligations,
- and recommended focus.

**Stable architecture anchor:** `ARCH:UxSurface.Portfolio`

### 8.2 Project workspace surface

A project-level surface shall present:

- goals,
- workstreams,
- milestones,
- risks,
- decisions,
- stakeholders,
- recent messages,
- and next actions.

**Stable architecture anchor:** `ARCH:UxSurface.ProjectWorkspace`

### 8.3 Triage surface

A triage surface shall present:

- newly ingested messages,
- classification results,
- ambiguous items,
- extracted tasks or deadlines,
- and draft suggestions.

**Stable architecture anchor:** `ARCH:UxSurface.Triage`

### 8.4 Draft workspace surface

A drafting surface shall present:

- response drafts,
- variants,
- associated project context,
- stakeholder context,
- and copy-ready output.

**Stable architecture anchor:** `ARCH:UxSurface.DraftWorkspace`

### 8.5 Telegram companion surface

The Telegram companion surface shall provide:

- concise interaction,
- summary retrieval,
- mobile note capture,
- and direct conversational access to Glimmer’s assistant layer.

This surface is intentionally narrower than the web workspace.

**Stable architecture anchor:** `ARCH:UxSurface.Telegram`

### 8.6 Persona presentation surface

Persona presentation is not confined to one page. It may appear across relevant UI surfaces where Glimmer is represented as an active assistant presence.

Persona image selection shall be context-aware and driven by approved labeled assets.

**Stable architecture anchor:** `ARCH:UxSurface.PersonaPresentation`

---

## 9. Cross-Cutting Quality Attributes

### 9.1 Continuity

The system must preserve continuity between sessions, channels, and operating modes.

**Stable architecture anchor:** `ARCH:Quality.Continuity`

### 9.2 Explainability

The system must give the operator enough visible rationale to trust classification, prioritization, and draft suggestions.

**Stable architecture anchor:** `ARCH:Quality.Explainability`

### 9.3 Proactivity without overreach

The system should be proactive in surfacing priorities, risks, and draft suggestions, but must not cross into silent action-taking.

**Stable architecture anchor:** `ARCH:Quality.ProactiveButReviewable`

### 9.4 Source provenance

The system must preserve the provenance of source accounts, channels, and ingested items so that meaning is not flattened during normalization.

**Stable architecture anchor:** `ARCH:Quality.SourceProvenance`

### 9.5 Tactful communication support

The system must support tact and contextual sensitivity in outward-facing draft generation.

**Stable architecture anchor:** `ARCH:Quality.TactfulDrafting`

---

## 10. Relationship to the Rest of the Architecture Set

This document intentionally stops short of detailed specification for:

- entity schemas,
- graph node contracts,
- connector implementation rules,
- persistence structures,
- security/token handling details,
- and testing-layer specifics.

Those concerns are handled in the following companion documents:

- `02_domain_model.md`
- `03_langgraph_orchestration.md`
- `04_connectors_and_ingestion.md`
- `05_memory_and_retrieval.md`
- `06_ui_and_voice.md`
- `07_security_and_permissions.md`
- `08_testing_strategy.md` (housed under `4. Verification/`)

This file should remain readable as the top-level system narrative even as those deeper documents evolve.

**Stable architecture anchor:** `ARCH:SystemOverviewDocumentBoundary`
**Stable architecture anchor:** `ARCH:ArchitectureControlSurface`

---

## 11. Final Note

Glimmer is architected as a local-first, multi-account, multi-surface chief-of-staff system whose primary operating qualities are:

- structured memory,
- explainable prioritization,
- tactful drafting,
- controlled companion interaction,
- and strong human review boundaries.

The purpose of this architecture is not to produce an impressive but ungoverned assistant. The purpose is to create a durable operational partner that helps the operator stay focused, prepared, and in control.

**Stable architecture anchor:** `ARCH:SystemOverviewConclusion`

