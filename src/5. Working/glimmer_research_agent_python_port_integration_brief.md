# Glimmer — Detailed Implementation Brief for Research-Agent Integration

## Document Purpose

This brief is intended to be given directly to the AI coding agent working on **Glimmer**.

Its purpose is to introduce a new requirement and design direction into the project:

**Glimmer must gain the ability to use the operator’s browser-driven Gemini workflow, via a Python port of the existing C# / .NET research agent, so that Glimmer can perform deeper research and heavier reasoning through a bounded external research capability when the local model is insufficient for the task.**

This brief is not a vague suggestion. It is an instruction to:

1. update the canonical control documents,
2. embed the new capability into the requirements, architecture, build plan, and verification model,
3. define the implementation approach for porting the existing C# research agent into Python,
4. and stage the work in a controlled, reviewable, local-first way that fits Glimmer’s existing operating model.

---

## 1. Background and Design Intent

Glimmer is already up and running in the IDE and the first three workstreams have been implemented at a meaningful level:

- Workstream A — Foundation
- Workstream B — Domain and Memory
- Workstream C — Connectors

A document review and alignment pass has also just been completed, and this is therefore the correct time to introduce an important new capability in a disciplined way rather than bolting it on later.

The new capability is as follows:

- the operator already has an existing **research agent** built in **C# / .NET**,
- that agent uses **Playwright** and **Chrome running in debug mode**,
- it is able to drive the operator’s browser in a controlled way,
- and it is able to use that browser-based workflow as a practical route into **Gemini** for more difficult research and reasoning tasks.

The Glimmer codebase, however, is being built in **Python**, and the goal is not to keep a split-brain implementation where this advanced research capability lives forever in a disconnected .NET sidecar unless that becomes a deliberate architecture choice later.

The immediate direction is therefore:

- provide the existing research-agent codebase to the AI coding agent,
- instruct the agent to **port the research agent into Python**,
- and integrate it into Glimmer as a **bounded, optional, high-value research and deep-reasoning tool**.

This capability should be treated as:

- **local-first**,
- **operator-controlled**,
- **explicitly invoked or policy-invoked**,
- **non-default for routine work**,
- and **auditable / reviewable**.

It must not be implemented as an unconstrained browsing/autonomy feature.

---

## 2. Core Product Change

The agent must update the Glimmer control documents and implementation direction so that Glimmer can:

1. determine when a task exceeds the practical reasoning or research comfort zone of the local/default model,
2. route that task to a bounded **deep research capability**,
3. execute that capability through a Python-native version of the operator’s browser automation research agent,
4. use Playwright + Chrome debug-mode browser control to interact with Gemini through the operator’s browser path,
5. return structured research outputs back into Glimmer’s memory / triage / planning / drafting workflows,
6. and preserve review, provenance, and safety boundaries throughout.

This new capability should conceptually sit between:

- Glimmer’s orchestration layer,
- Glimmer’s external connector/tool layer,
- and Glimmer’s structured memory / artifact model.

It is **not** just “browser automation.”
It is a bounded **research and reasoning escalation path**.

---

## 3. Required Outcome From the Coding Agent

The coding agent must do the following.

### 3.1 Review and absorb the existing Glimmer control surface

Before making changes, the agent must read and align against the existing active canonical docs, especially:

- Requirements
- Architecture
- Build Plan
- Testing Strategy
- Test Catalog
- Relevant workstream docs

The agent must treat the current documents as the control surface and extend them coherently rather than adding disconnected notes.

### 3.2 Incorporate the new capability into the canonical documents

The agent must update the Glimmer documents so the new deep-research capability is reflected in:

- product requirements,
- architecture structure,
- build sequencing,
- workstream scope,
- and verification expectations.

### 3.3 Prepare for code porting work

The agent must assume that the operator will provide the existing C# / .NET research-agent codebase for analysis.

The agent should then:

- study that code,
- identify the conceptual modules and boundaries,
- design a Python-native equivalent,
- and propose the safest migration path into the current Glimmer repository.

### 3.4 Keep the capability bounded

The agent must preserve these design truths:

- this is not a generic autonomous web-browsing agent,
- this is not an unrestricted internet-control feature,
- this is not a silent background actor,
- and this capability must remain reviewable, tool-like, and policy-bounded.

---

## 4. New Requirement to Add

The requirements documentation must be updated to introduce a new requirement family covering **deep research and escalated reasoning**.

The updated requirements set should make room for the following truths.

### 4.1 Functional requirement intent

Glimmer shall support a bounded deep-research capability that can be invoked when:

- a task requires multi-step external research,
- a task requires heavier reasoning than the default/local model handles well,
- a task requires browser-mediated access to Gemini through the operator’s environment,
- or a task benefits from structured evidence gathering across pages/sources through a controlled research flow.

### 4.2 Invocation model

The requirement should support one or more of the following invocation paths:

- explicit operator request,
- workflow-level escalation from orchestration,
- or rule-based invocation where the task type clearly warrants deep research.

However, invocation must remain bounded and explainable.

### 4.3 Output expectations

The research capability should produce structured outputs such as:

- research summary,
- evidence points,
- source trail,
- extracted findings,
- reasoning notes or decision support,
- and a confidence / completion / exception signal.

### 4.4 Safety requirements

The requirement must make clear that the capability:

- does not silently send external messages,
- does not mutate project memory without passing through Glimmer’s existing review/memory rules,
- does not become a general unrestricted browsing shell,
- and does not bypass operator control.

### 4.5 Provenance requirements

The requirement should state that research runs must preserve provenance, including where practical:

- invocation origin,
- triggering task or workflow,
- run timestamp,
- tool/mode used,
- relevant browser session context,
- and sources or pages touched.

### 4.6 Suggested requirement anchor additions

The agent should introduce stable `REQ:` anchors such as:

- `REQ:DeepResearchCapability`
- `REQ:ResearchEscalationPath`
- `REQ:ResearchRunProvenance`
- `REQ:ResearchOutputArtifacts`
- `REQ:BoundedBrowserMediatedResearch`

The agent may refine the exact names, but the concept must be explicit and durable.

---

## 5. Architecture Changes Required

The architecture documents must be updated so the new capability is not treated as an afterthought.

### 5.1 System-overview changes

The system overview should explicitly recognize a **deep research / escalated reasoning capability** as part of the system boundary.

This should be framed as:

- an optional bounded capability,
- layered onto the orchestration and memory model,
- used when the core assistant requires richer external reasoning support,
- and implemented through a local-first research adapter/tool path.

### 5.2 Connector and ingestion architecture changes

The research-agent integration should be reflected in the connector/tool architecture.

The architecture should decide whether this belongs as:

- a specialized connector family,
- a tool adapter under the orchestration layer,
- or a dedicated research-service boundary.

The likely best framing is:

- **a bounded research tool/service boundary**
- sitting alongside other external boundaries,
- but distinguished from message/calendar connectors because it is an invoked capability rather than a passive source connector.

### 5.3 Orchestration changes

The LangGraph architecture must be extended to define:

- how Glimmer decides a task should escalate to deep research,
- how a research run is invoked,
- what graph state is persisted during the run,
- how interrupts / review gates apply,
- and how research results re-enter the main workflow.

This likely requires new architecture anchors for:

- research escalation policy,
- research-run lifecycle,
- research result ingestion,
- and research artifact persistence.

### 5.4 Domain and memory changes

The domain model should be extended to support explicit research artifacts.

The agent should add conceptual entities or artifact models such as:

- `ResearchRun`
- `ResearchFinding`
- `ResearchSourceReference`
- `ResearchSummaryArtifact`
- `ResearchInvocationContext`

The exact implementation can vary, but the architecture must make room for:

- durable research runs,
- structured findings,
- run status,
- provenance,
- and linkage back to projects/messages/drafts/focus packs where relevant.

### 5.5 Security and permission changes

The security architecture must explicitly cover:

- browser debug-mode usage,
- local Chrome attachment/control boundary,
- credential/session handling assumptions,
- limits on what research automation is allowed to do,
- whether only whitelisted flows/pages are allowed in MVP,
- and how operator consent / browser readiness is handled.

This is important because this capability uses the operator’s live browser context.

### 5.6 UI and UX architecture changes

The UI architecture should make room for:

- a visible research-run state where relevant,
- surfacing of research outputs,
- indication that a deeper reasoning tool was used,
- review of research summaries/findings,
- and possible manual operator invocation from the UI.

The UI does not need a huge dedicated research console in MVP unless the agent judges it necessary, but the architecture must not hide this capability.

### 5.7 Testing architecture changes

The testing architecture must define how to verify:

- research invocation logic,
- browser-bound adapter boundaries,
- result normalization and provenance,
- resilience to browser/session failures,
- and safe fallback behavior.

### 5.8 Suggested architecture anchors

The agent should introduce stable `ARCH:` anchors such as:

- `ARCH:DeepResearchCapability`
- `ARCH:ResearchToolBoundary`
- `ARCH:GeminiBrowserMediatedAdapter`
- `ARCH:ResearchEscalationPolicy`
- `ARCH:ResearchRunLifecycle`
- `ARCH:ResearchArtifactModel`
- `ARCH:ResearchVerificationStrategy`

The exact labels can vary, but the concepts must exist.

---

## 6. Build Plan Changes Required

The build plan must be updated to reflect that this is a meaningful capability addition, not a throwaway implementation detail.

### 6.1 Update overall strategy and scope

The strategy and scope document should state that Glimmer includes a bounded deep-research and escalated-reasoning path for harder tasks, using a Python-native browser-mediated Gemini integration.

### 6.2 Workstream placement

The agent must determine the right workstream placement for this capability.

The most likely options are:

1. **Extend Workstream C — Connectors**
   - if treated primarily as an external tool boundary and adapter capability.

2. **Extend Workstream D — Triage and Prioritization**
   - if treated primarily as an orchestration escalation path.

3. **Create a new dedicated workstream**
   - if the capability is large enough to warrant standalone treatment.

The most disciplined answer is probably:

- add the research-tool boundary and basic Python porting groundwork into **Workstream C**,
- add orchestration escalation logic into **Workstream D**,
- and add verification hardening into **Workstream G**.

If the amount of work is substantial, the agent may propose a dedicated workstream such as:

- **Workstream H — Deep Research and External Reasoning**

That would be acceptable if justified cleanly.

### 6.3 Required build-plan content

The build plan updates should cover:

- Python porting of the existing C# research agent,
- abstraction boundary for the research tool,
- browser attachment/bootstrap strategy,
- Gemini interaction flow,
- structured research-run outputs,
- orchestration integration,
- failure and degraded-mode handling,
- operator invocation or review triggers,
- and verification expectations.

### 6.4 Working-document expectations

Once the build-plan position is chosen, the agent should create or update the appropriate workstream-level design/progress documents for this new body of work.

---

## 7. Verification and Testing Changes Required

The verification model must expand to cover this capability properly.

### 7.1 Test-catalog additions

The canonical test catalog should gain new `TEST:` anchors around:

- research escalation decision logic,
- research-run invocation,
- browser-attachment failure handling,
- Gemini-adapter result capture,
- research provenance persistence,
- safe fallback when browser/Gemini is unavailable,
- no-auto-send / bounded-behavior protection,
- and ingestion of research outputs back into Glimmer.

Suggested `TEST:` anchors include:

- `TEST:Research.Escalation.RoutesWhenTaskRequiresDeepResearch`
- `TEST:Research.Invocation.StartsBoundedResearchRun`
- `TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult`
- `TEST:Research.Provenance.RunAndSourceTrailPersisted`
- `TEST:Research.Failure.BrowserUnavailableHandledSafely`
- `TEST:Research.Failure.GeminiInteractionFailureVisible`
- `TEST:Research.Security.NoUnboundedActionTaking`
- `TEST:Research.Output.ResultsReenterWorkflowSafely`

### 7.2 Test-layer expectations

The testing strategy should cover proof across:

- **unit** for escalation rules and mapping logic,
- **integration** for research-run persistence and artifact linkage,
- **graph** for orchestration invocation/resume behavior,
- **contract** for browser/Gemini adapter boundaries,
- **manual_only** where live browser/Gemini verification cannot be fully automated,
- and possibly **browser** tests if Glimmer exposes research-run state in the UI.

### 7.3 Verification pack changes

The smoke pack probably does not need deep-research proof initially.

However, at minimum the workstream or release packs should eventually include:

- research capability happy path,
- degraded-mode path,
- provenance proof,
- and bounded-behavior proof.

### 7.4 Evidence expectations

The agent should define what counts as acceptable implementation evidence for this capability, especially where full automation may be difficult due to live browser/session constraints.

The evidence model should likely include a mixture of:

- automated unit/integration/graph tests,
- contract-level tests with mocks/fakes,
- controlled manual validation using the operator’s local browser session,
- and recorded progress/evidence notes.

---

## 8. Porting Direction: Existing C# Research Agent to Python

The coding agent must prepare for a real migration exercise from the existing .NET codebase into Python.

### 8.1 The agent must not do a blind line-by-line translation

The task is not to mechanically rewrite C# syntax into Python.

The task is to:

- inspect the existing agent,
- identify the true architectural components,
- port the behavior into idiomatic Python,
- and align the result to Glimmer’s architecture and coding conventions.

### 8.2 Expected conceptual modules to identify

The agent should inspect the existing research-agent code and identify modules such as:

- browser bootstrap / Chrome debug attachment,
- Playwright session management,
- Gemini interaction/navigation flow,
- prompt or task packaging,
- response capture / normalization,
- retry/failure handling,
- logging and evidence capture,
- and orchestration-facing invocation surfaces.

### 8.3 Python target posture

The Python port should be:

- idiomatic to the Glimmer backend,
- separated by clear service/tool boundaries,
- testable without always requiring a live browser,
- and designed for local-first execution.

### 8.4 Key design rule

The Python port should expose a stable internal interface such as a service boundary or adapter contract, not leak raw Playwright automation details throughout the codebase.

For example, Glimmer should be able to ask for something like:

- start research run,
- execute research task,
- collect result,
- record provenance,
- and return structured findings,

without the rest of the system depending on low-level browser mechanics.

---

## 9. Implementation Constraints and Guardrails

The coding agent must preserve the following constraints.

### 9.1 Local-first still wins

This capability must align with Glimmer’s local-first posture.

### 9.2 Browser-mediated Gemini use is bounded

The system may use the operator’s browser path into Gemini, but only within an explicit bounded research capability.

### 9.3 No silent autonomy creep

This must not turn into general autonomous web behavior or unrestricted action-taking.

### 9.4 Reviewable outputs

Research outputs must enter Glimmer as reviewable, attributable artifacts.

### 9.5 Failure must be visible

If browser attachment fails, Chrome is not available, Gemini interaction breaks, or a run cannot complete, Glimmer must surface a visible degraded/failure state rather than pretending nothing happened.

### 9.6 Prefer abstraction over entanglement

The research capability should be introduced through a clean boundary that the rest of Glimmer can depend on safely.

---

## 10. Concrete Tasks for the Coding Agent

The coding agent should execute this body of work in the following order.

### Task 1 — Review and align

Read the active Glimmer requirements, architecture, build plan, testing strategy, and test catalog.

### Task 2 — Propose document changes

Identify exactly which files and anchors need updating.

### Task 3 — Update canonical docs

Edit the requirements, architecture, build-plan, and verification docs to introduce the deep-research capability.

### Task 4 — Determine workstream placement

Choose whether to:

- extend existing workstreams,
- or create a new dedicated workstream.

Record the reasoning clearly.

### Task 5 — Prepare Python-port design

Define the target Python architecture for the research-agent port, including:

- service boundaries,
- module breakdown,
- orchestration invocation shape,
- persistence/artifact model,
- and failure handling.

### Task 6 — Update verification model

Add `TEST:` anchors, verification-pack impact, and evidence rules.

### Task 7 — Create or update working docs

Create/update the relevant workstream design-and-implementation plan and progress documents to carry this work forward properly.

### Task 8 — Await source-code input

Once the operator provides the existing C# research-agent codebase, analyze it and produce a Python-port implementation plan before major code generation begins.

---

## 11. Expected Deliverables From the Coding Agent

The coding agent should produce the following.

### Document deliverables

- updated requirements document
- updated architecture document set
- updated build-plan document set
- updated testing strategy and/or verification docs
- updated test catalog
- new or updated workstream design/progress docs

### Design deliverables

- Python port design for the existing C# research agent
- proposed internal interface / adapter boundary
- proposed domain artifacts for research runs and findings
- proposed orchestration integration pattern
- proposed failure and degraded-mode strategy

### Verification deliverables

- new `TEST:` anchors
- proposed automation layers
- manual-only/deferred classifications where necessary
- research-capability verification expectations

---

## 12. Definition of Success

This brief should be considered successfully executed when:

1. the Glimmer control documents clearly describe the new deep-research capability,
2. the capability is properly anchored in requirements, architecture, build plan, and verification,
3. the Python port of the existing C# research agent has a clear architectural destination,
4. the work is placed into the build sequence coherently,
5. the verification model is expanded to prove the capability safely,
6. and the coding agent is ready to receive the existing C# codebase and continue with implementation planning.

---

## 13. Final Instruction to the Coding Agent

Do not treat this as a side note or optional enhancement.

Treat it as a meaningful evolution of Glimmer’s capability model:

- a bounded deep-research and escalated-reasoning path,
- implemented through a Python-native port of the operator’s existing browser-mediated Gemini research agent,
- integrated cleanly into the current local-first, review-first, provenance-preserving architecture.

Update the control documents first.
Then prepare the implementation path.
Then await the provided C# research-agent codebase for the Python-port design and build work.

