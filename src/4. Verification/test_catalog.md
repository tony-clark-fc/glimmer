# Glimmer — Test Catalog

## Document Metadata

- **Document Title:** Glimmer — Test Catalog
- **Document Type:** Canonical Verification Document
- **Status:** Draft
- **Project:** Glimmer
- **Parent Document:** `4. Verification/`
- **Primary Companion Documents:** Requirements, Architecture, Build Plan, Testing Strategy, Verification Packs

---

## 1. Purpose

This document defines the canonical `TEST:` anchor catalog for **Glimmer**.

Its purpose is to provide a stable scenario vocabulary that ties together:

- requirements,
- architecture,
- build-plan workstreams,
- automated tests,
- verification packs,
- and workstream progress evidence.

This document is not the full regression pack set and it is not the test implementation itself.

It is the stable reference surface for **what must be proven**.

**Stable verification anchor:** `TESTCATALOG:ControlSurface`

---

## 2. Role of the Test Catalog

The test catalog exists so that Glimmer does not end up with:

- drifting scenario names,
- duplicated proof definitions,
- vague references like “tested the planner stuff,”
- or workstream progress notes that cannot be traced back to a stable proof target.

Each important scenario should therefore have:

- a stable `TEST:` anchor,
- a concise scenario name,
- a defined verification layer,
- a mapped requirement or architecture rationale,
- and eventual pack membership.

**Stable verification anchor:** `TESTCATALOG:Role`

---

## 3. Traceability Model

The intended Glimmer traceability chain is:

`REQ:` → `ARCH:` → `PLAN:` → `TEST:`

This means:

- requirements define what must be true,
- architecture defines how the system is shaped,
- build-plan workstreams define how delivery is sequenced,
- and `TEST:` anchors define how important behavior is proven.

Tests, verification packs, progress files, and release summaries should reference the `TEST:` anchors directly where meaningful.

**Stable verification anchor:** `TESTCATALOG:TraceabilityModel`

---

## 4. Verification Layer Vocabulary

Every `TEST:` anchor should map to one or more verification layers.

The standard Glimmer verification layers are:

- `unit`
- `integration`
- `api`
- `graph`
- `browser`
- `contract`
- `manual_only`
- `deferred`

These layers align to the Glimmer testing strategy and Workstream G expectations.

**Stable verification anchor:** `TESTCATALOG:VerificationLayers`

---

## 5. Test Status Vocabulary

The following status vocabulary should be used when summarizing `TEST:` anchors in packs or progress files.

- `Planned`
- `Implemented`
- `ExecutedPassing`
- `ExecutedFailing`
- `ManualOnly`
- `Deferred`

This catalog does not attempt to store day-to-day status itself for every scenario, but all downstream reporting should use a consistent vocabulary.

**Stable verification anchor:** `TESTCATALOG:StatusVocabulary`

---

## 6. Scenario Group Map

The Glimmer test catalog is organized into the following scenario groups:

1. Foundation and startup
2. Domain and memory integrity
3. Connector and provenance behavior
4. Triage and interpretation behavior
5. Planning and prioritization behavior
6. Drafting and review behavior
7. Web workspace behavior
8. Voice and companion behavior
9. Security and approval boundaries
10. Cross-cutting regression and release confidence

**Stable verification anchor:** `TESTCATALOG:ScenarioGroups`

---

## 7. Catalog Entries

## 7.1 Foundation and startup scenarios

### `TEST:Smoke.BackendStarts`
- **Scenario name:** Backend starts and exposes basic health/status behavior
- **Primary layers:** `integration`, `api`
- **Primary requirement/architecture drivers:** `REQ:ProductPurpose`, `ARCH:SystemBoundaries`, `ARCH:TechnologyBaseline`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove the backend application can boot in a minimal local configuration and expose a stable status surface.

### `TEST:Smoke.FrontendStarts`
- **Scenario name:** Frontend workspace shell starts and renders
- **Primary layers:** `integration`, `browser`
- **Primary requirement/architecture drivers:** `REQ:ProductPurpose`, `ARCH:UiSurfaceMap`, `ARCH:TechnologyBaseline`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove the web application starts cleanly and presents the base workspace shell.

### `TEST:Smoke.DatabaseConnectivity`
- **Scenario name:** Primary relational store is reachable through the application
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:LocalFirstOperatingModel`, `ARCH:MemoryStorageStrategy`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove the application can connect to PostgreSQL under the intended local-first baseline.

### `TEST:Smoke.WorkspaceNavigationBasic`
- **Scenario name:** Core workspace routes are reachable
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `REQ:ProjectPortfolioManagement`, `ARCH:UiSurfaceMap`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`, `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the main route structure is navigable at a basic level.

### `TEST:Foundation.Config.LocalFirstDefaultsResolve`
- **Scenario name:** Local-first configuration defaults resolve correctly
- **Primary layers:** `unit`, `api`
- **Primary requirement/architecture drivers:** `REQ:LocalFirstOperatingModel`, `ARCH:DeploymentPosture`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove Pydantic Settings load local-first defaults without external dependencies.

### `TEST:Foundation.Persistence.MigrationBaselineExists`
- **Scenario name:** Alembic migration baseline exists and is recorded
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `ARCH:MemoryStorageStrategy`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove the migration chain is initialized and tracked.

### `TEST:Foundation.Backend.StructureRespectsBoundaryShape`
- **Scenario name:** Backend package structure respects the expected boundary shape
- **Primary layers:** `unit`
- **Primary requirement/architecture drivers:** `ARCH:SystemBoundaries`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove the backend app structure follows the planned separation.

### `TEST:Foundation.Frontend.WorkspaceShellExists`
- **Scenario name:** Frontend workspace shell exists with expected route structure
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `ARCH:UiSurfaceMap`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove the workspace shell renders with all primary navigation routes.

### `TEST:Foundation.AgentSupport.CoreSurfacesPresent`
- **Scenario name:** Agent support surfaces — control docs, instructions, skills, tools — are present
- **Primary layers:** `unit`
- **Primary requirement/architecture drivers:** `ARCH:SystemBoundaries`
- **Primary workstream linkage:** `PLAN:WorkstreamA.Foundation`
- **Intent:** Prove operational support files required for agent-assisted delivery exist.

**Stable verification anchor:** `TESTCATALOG:FoundationAndStartup`

---

## 7.2 Domain and memory integrity scenarios

### `TEST:Domain.ProjectLifecycle.BasicPersistence`
- **Scenario name:** Project records persist and reload correctly
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:ProjectPortfolioManagement`, `ARCH:ProjectStateModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove project state is durable and queryable.

### `TEST:Domain.StakeholderIdentity.MultiIdentityLinking`
- **Scenario name:** One stakeholder can hold multiple identities without losing distinction
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:StakeholderMemory`, `ARCH:StakeholderModel`, `ARCH:StakeholderIdentityModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove identity plurality without forced merging.

### `TEST:Domain.MultiAccount.ProvenancePersistence`
- **Scenario name:** Source provenance survives persistence round trips
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:MultiAccountProfileSupport`, `ARCH:ConnectedAccountModel`, `ARCH:AccountProvenanceModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove account, profile, provider, and remote identity are durable.

### `TEST:Domain.InterpretedVsAccepted.Separation`
- **Scenario name:** Interpreted artifacts remain distinct from accepted operational state
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:Explainability`, `REQ:TraceabilityAndAuditability`, `ARCH:StateOwnershipBoundaries`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove low-confidence or candidate state does not silently become accepted truth.

### `TEST:Domain.SummaryRefresh.Lineage`
- **Scenario name:** Summary refresh preserves lineage and metadata
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:ProjectMemory`, `ARCH:ProjectMemoryRefresh`, `ARCH:AuditAndTraceLayer`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`, `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove summary artifacts remain traceable and refreshes are explicit.

### `TEST:Domain.Audit.MeaningfulStateMutation`
- **Scenario name:** Meaningful state mutations generate durable audit records
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:TraceabilityAndAuditability`, `ARCH:AuditAndTraceLayer`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove the system records meaningful memory evolution.

### `TEST:Domain.ProjectPortfolio.WorkstreamsAndMilestonesPersist`
- **Scenario name:** Project workstreams and milestones persist with correct relationships
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:ProjectPortfolioManagement`, `ARCH:ProjectStateModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove workstream and milestone entities belong to projects and persist correctly.

### `TEST:Domain.SourceRecords.MessagesThreadsEventsPersistSeparately`
- **Scenario name:** Messages, threads, events, and signals persist as separate source records
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:MessageIngestion`, `ARCH:MessageModel`, `ARCH:ConnectedAccountModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove source-layer records remain distinct and provenance-bearing.

### `TEST:Domain.Interpretation.ReviewStateLifecyclePersists`
- **Scenario name:** Interpretation review state lifecycle persists through all valid transitions
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:ReviewGateArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove review states (pending_review, accepted, rejected, amended, superseded) are durable.

### `TEST:Domain.Execution.AcceptedArtifactsPersistSeparately`
- **Scenario name:** Accepted operational artifacts persist separately from interpreted candidates
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:Explainability`, `ARCH:StateOwnershipBoundaries`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove work items, decisions, risks, blockers, and waiting-on records are durable.

### `TEST:Domain.Drafting.DraftsAndVariantsPersistWithIntent`
- **Scenario name:** Drafts and variants persist with intent context
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:DraftResponseWorkspace`, `ARCH:DraftModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove draft and variant entities preserve drafting intent and linkage.

### `TEST:Domain.Briefings.FocusAndBriefingArtifactsPersist`
- **Scenario name:** Focus packs and briefing artifacts persist with scope metadata
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:PreparedBriefings`, `ARCH:TodayViewArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove briefing and focus artifacts are durable and scoped.

### `TEST:Domain.Persona.AssetsAndClassificationPersist`
- **Scenario name:** Persona assets and classification records persist
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:VisualPersonaSupport`, `ARCH:PersonaAssetModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove persona asset management entities are durable.

### `TEST:Domain.ChannelSessions.TelegramAndVoiceStatePersist`
- **Scenario name:** Channel sessions with Telegram and voice state persist
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:StateContinuity`, `ARCH:ChannelSessionModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove session continuity records for companion channels are durable.

### `TEST:Domain.Operator.PersistsWithPreferences`
- **Scenario name:** Primary operator persists with all preference fields
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:ProductPurpose`, `ARCH:PrimaryOperatorModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove operator context (timezone, language, tone, channel preferences) persists.

### `TEST:Domain.Operator.OwnsProjectsAccountsSessions`
- **Scenario name:** Operator owns projects, connected accounts, and channel sessions
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `ARCH:PrimaryOperatorModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove the operator ownership chain across major entities.

**Stable verification anchor:** `TESTCATALOG:DomainAndMemory`

---

## 7.3 Connector and provenance scenarios

### `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount`
- **Scenario name:** Google mail normalization preserves thread and account meaning
- **Primary layers:** `integration`, `contract`
- **Primary requirement/architecture drivers:** `REQ:MessageIngestion`, `REQ:MultiAccountProfileSupport`, `ARCH:GmailConnector`, `ARCH:NormalizationPipeline`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove Gmail normalization retains operationally meaningful metadata.

### `TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext`
- **Scenario name:** Google Calendar normalization preserves profile and calendar context
- **Primary layers:** `integration`, `contract`
- **Primary requirement/architecture drivers:** `REQ:MessageIngestion`, `ARCH:GoogleCalendarConnector`, `ARCH:NormalizationPipeline`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove event meaning is preserved, not flattened into generic text.

### `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread`
- **Scenario name:** Microsoft mail normalization preserves mailbox and conversation context
- **Primary layers:** `integration`, `contract`
- **Primary requirement/architecture drivers:** `REQ:MessageIngestion`, `REQ:MultiAccountProfileSupport`, `ARCH:MicrosoftGraphConnector`, `ARCH:NormalizationPipeline`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove Graph mail semantics remain intact.

### `TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext`
- **Scenario name:** Microsoft calendar normalization preserves account and event context
- **Primary layers:** `integration`, `contract`
- **Primary requirement/architecture drivers:** `REQ:MessageIngestion`, `ARCH:MicrosoftGraphConnector`, `ARCH:NormalizationPipeline`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove Microsoft calendar event context survives normalization.

### `TEST:Connector.ManualImport.LabelingAndRouting`
- **Scenario name:** Manual imports are explicitly labeled and routed safely
- **Primary layers:** `integration`, `api`
- **Primary requirement/architecture drivers:** `REQ:MessageIngestion`, `ARCH:ManualImportBoundary`, `ARCH:NormalizationPipeline`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove unsupported-channel input stays explicit and auditable.

### `TEST:Connector.Telegram.InboundBecomesBoundedSignal`
- **Scenario name:** Telegram inbound interaction becomes bounded internal signal/session state
- **Primary layers:** `integration`, `contract`, `graph`
- **Primary requirement/architecture drivers:** `REQ:TelegramMobilePresence`, `ARCH:TelegramConnector`, `ARCH:ChannelSessionModel`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`, `PLAN:WorkstreamF.Voice`
- **Intent:** Prove Telegram does not bypass the core intake model.

### `TEST:Connector.SyncFailure.VisibleState`
- **Scenario name:** Connector sync failure is visible and does not silently disappear
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:TraceabilityAndAuditability`, `ARCH:ConnectorIsolation`, `ARCH:AccountProvenanceModel`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove sync and authorization failures are observable.

### `TEST:Connector.Framework.ProviderBoundaryIsolation`
- **Scenario name:** Connector framework enforces provider boundary isolation
- **Primary layers:** `unit`, `contract`
- **Primary requirement/architecture drivers:** `ARCH:ConnectorIsolation`, `ARCH:ApiFirstIntegration`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove connector ABC, provider types, and module structure enforce bounded contracts.

### `TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile`
- **Scenario name:** Connector execution resolves and uses the correct account profile
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:MultiAccountProfileSupport`, `ARCH:ConnectedAccountModel`, `ARCH:AccountProvenanceModel`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove multi-account support is operational, not just modeled.

### `TEST:Connector.IntakeHandoff.BoundedReferenceFlow`
- **Scenario name:** Connector-to-intake handoff produces bounded references
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:MessageIngestion`, `ARCH:NormalizationPipeline`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove handoff uses record IDs, not raw payloads.

### `TEST:Connector.Normalization.PersistBeforeInterpretation`
- **Scenario name:** Normalized records persist before any interpretation begins
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:TraceabilityAndAuditability`, `ARCH:NormalizationPipeline`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove source records exist in the database before triage or classification.

### `TEST:Connector.Security.ReadFirstNoAutoSendPreserved`
- **Scenario name:** Connector layer remains read-first with no auto-send capability
- **Primary layers:** `unit`, `contract`
- **Primary requirement/architecture drivers:** `REQ:SafeBehaviorDefaults`, `ARCH:NoAutoSendPolicy`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove no outbound side effects exist at the connector layer.

**Stable verification anchor:** `TESTCATALOG:ConnectorsAndProvenance`

---

## 7.4 Triage and interpretation scenarios

### `TEST:Triage.Intake.SourceRoutesCorrectly`
- **Scenario name:** Normalized source records route into the correct intake path
- **Primary layers:** `graph`
- **Primary requirement/architecture drivers:** `REQ:ContextualMessageClassification`, `ARCH:IntakeGraph`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove intake routing is source-aware and bounded.

### `TEST:Triage.ProjectClassification.SingleStrongMatch`
- **Scenario name:** Strong project match is classified correctly
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:ContextualMessageClassification`, `ARCH:TriageGraph`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove classification can use memory and provenance to find a clear project match.

### `TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview`
- **Scenario name:** Ambiguous project classification creates structured review state
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:TriageGraphReviewGate`, `ARCH:ReviewGateArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove ambiguity does not silently harden into accepted truth.

### `TEST:Triage.StakeholderInterpretation.UncertainIdentityRequiresReview`
- **Scenario name:** Uncertain stakeholder interpretation does not silently merge identities
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:StakeholderMemory`, `REQ:HumanApprovalBoundaries`, `ARCH:StakeholderIdentityModel`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove stakeholder uncertainty is review-safe.

### `TEST:Triage.ActionExtraction.ClearRequestBecomesCandidateAction`
- **Scenario name:** Clear follow-up request becomes persisted candidate action
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:ActionDeadlineDecisionExtraction`, `ARCH:ExtractedActionModel`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove clear operational meaning becomes reviewable structured output.

### `TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview`
- **Scenario name:** Uncertain extracted action remains reviewable candidate state
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:InterpretationReviewState`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove uncertain extraction does not become accepted work automatically.

### `TEST:Triage.Extraction.DecisionAndDeadlineSignalsPersist`
- **Scenario name:** Extracted decision and deadline signals persist as reviewable artifacts
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:ActionDeadlineDecisionExtraction`, `ARCH:TriageGraph`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove decision and deadline extraction creates durable interpreted artifacts.

### `TEST:Triage.ReviewInterrupt.ResumeContinuesSafely`
- **Scenario name:** Review interrupt and resume continues workflow safely
- **Primary layers:** `integration`, `graph`
- **Primary requirement/architecture drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:InterruptAndResumeModel`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove the review state lifecycle supports safe transitions.

**Stable verification anchor:** `TESTCATALOG:TriageAndInterpretation`

---

## 7.5 Planning and prioritization scenarios

### `TEST:Planner.FocusPack.GeneratesExplainablePriorities`
- **Scenario name:** Focus pack generation produces explainable priorities
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:PrioritizationEngine`, `ARCH:PlannerGraph`, `ARCH:TodayViewArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove planner output is not opaque urgency theater.

### `TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure`
- **Scenario name:** Work-breakdown assistance proposes next steps without silent structural mutation
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:WorkBreakdownSupport`, `REQ:HumanApprovalBoundaries`, `ARCH:PlannerGraphReviewGate`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove planning help remains advisory and review-safe.

### `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable`
- **Scenario name:** Project-memory refresh trigger is explicit and traceable
- **Primary layers:** `integration`, `graph`
- **Primary requirement/architecture drivers:** `REQ:ProjectMemory`, `ARCH:ProjectMemoryRefresh`, `ARCH:AuditAndTraceLayer`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove memory evolution caused by planner/triage is visible and durable.

### `TEST:Planner.FocusPack.PersistsTopActionsAndPressureSignals`
- **Scenario name:** Focus pack persists top actions, risks, waiting-on, and pressure signals
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:PrioritizationEngine`, `ARCH:PlannerGraph`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove focus-pack artifacts include prioritized items and pressure indicators.

### `TEST:Planner.PriorityRationale.VisibleInApplicationSurface`
- **Scenario name:** Priority rationale is visible through application/API surfaces
- **Primary layers:** `api`
- **Primary requirement/architecture drivers:** `REQ:Explainability`, `ARCH:TodayViewArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove the operator can see why items are prioritized.

**Stable verification anchor:** `TESTCATALOG:PlanningAndPrioritization`

---

## 7.6 Drafting and review scenarios

### `TEST:Drafting.DraftGeneration.CreatesReviewableDraft`
- **Scenario name:** Draft generation creates a reviewable draft artifact
- **Primary layers:** `graph`, `integration`, `api`
- **Primary requirement/architecture drivers:** `REQ:DraftResponseWorkspace`, `ARCH:DraftingGraph`, `ARCH:DraftModel`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`, `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove draft generation results in a durable reviewable output.

### `TEST:Drafting.Variants.MultipleVariantsRemainLinked`
- **Scenario name:** Multiple draft variants remain linked to one drafting episode
- **Primary layers:** `integration`, `api`
- **Primary requirement/architecture drivers:** `REQ:DraftResponseWorkspace`, `ARCH:DraftVariantModel`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove variants are comparable without fragmenting intent.

### `TEST:Drafting.NoAutoSend.BoundaryPreserved`
- **Scenario name:** Draft workflow does not create outbound send behavior
- **Primary layers:** `graph`, `api`, `integration`
- **Primary requirement/architecture drivers:** `REQ:SafeBehaviorDefaults`, `ARCH:NoAutoSendPolicy`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`, `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove drafting remains review-only and copy/paste oriented in MVP.

### `TEST:Review.AcceptAmendRejectDefer.ChangesPersistCorrectly`
- **Scenario name:** Review actions persist correctly across accept/amend/reject/defer flows
- **Primary layers:** `api`, `integration`, `browser`
- **Primary requirement/architecture drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:ReviewGateArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove review is a real control path, not UI theater.

### `TEST:ApplicationSurface.TriageAndPriorityEndpointsSupportReviewActions`
- **Scenario name:** Triage and priority API endpoints support review actions
- **Primary layers:** `api`
- **Primary requirement/architecture drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:ReviewGateArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`
- **Intent:** Prove triage/priority API surfaces expose review queue and action endpoints.

### `TEST:API.Operator.CreateReadUpdate`
- **Scenario name:** Operator API supports create, read, and update operations
- **Primary layers:** `api`
- **Primary requirement/architecture drivers:** `REQ:ProductPurpose`, `ARCH:PrimaryOperatorModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove the operator entity has a functioning thin API surface.

### `TEST:API.Operator.SingleOperatorConstraint`
- **Scenario name:** Operator API enforces the single-operator constraint
- **Primary layers:** `api`
- **Primary requirement/architecture drivers:** `ARCH:PrimaryOperatorModel`
- **Primary workstream linkage:** `PLAN:WorkstreamB.DomainAndMemory`
- **Intent:** Prove only one operator can exist (409 on duplicate creation).

**Stable verification anchor:** `TESTCATALOG:DraftingAndReview`

---

## 7.7 Web workspace scenarios

### `TEST:UI.Navigation.WorkspaceRoutesRemainReachable`
- **Scenario name:** All workspace routes remain reachable after changes
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `ARCH:UiSurfaceMap`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the workspace route structure is stable across development.

### `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly`
- **Scenario name:** Today view presents priorities, pressure, and rationale clearly
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `REQ:PrioritizationEngine`, `ARCH:TodayViewArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the main daily operating view is materially useful.

### `TEST:UI.PortfolioView.ComparesProjectAttentionDemand`
- **Scenario name:** Portfolio view supports comparison across project attention demand
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `REQ:ProjectPortfolioManagement`, `ARCH:UiSurfaceMap`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove portfolio navigation supports prioritization across projects.

### `TEST:UI.ProjectWorkspace.ShowsSynthesisNotJustChronology`
- **Scenario name:** Project workspace presents synthesized project context
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `REQ:ProjectMemory`, `ARCH:ProjectWorkspaceArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove project pages are relevance-first rather than raw message dumps.

### `TEST:UI.TriageView.ShowsProvenanceAndReviewControls`
- **Scenario name:** Triage view shows provenance, ambiguity, and review controls
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `REQ:ContextualMessageClassification`, `ARCH:TriageViewArchitecture`, `ARCH:ReviewGateArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove source meaning and review behavior remain visible in the UI.

### `TEST:UI.DraftWorkspace.ShowsContextAndVariants`
- **Scenario name:** Draft workspace shows linked context and draft variants clearly
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `REQ:DraftResponseWorkspace`, `ARCH:DraftWorkspaceArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the draft workspace is a real operator tool, not a text dump.

### `TEST:UI.DraftWorkspace.CopyEditFlowRemainsReviewOnly`
- **Scenario name:** Draft workspace copy/edit flow remains review-only with no send capability
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `REQ:SafeBehaviorDefaults`, `ARCH:NoAutoSendPolicy`, `ARCH:DraftWorkspaceArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove copy button exists but no send button, maintaining review-only posture.

### `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious`
- **Scenario name:** Review queue makes pending vs accepted state obvious
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:ReviewQueueArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove the UI preserves candidate-vs-accepted distinction.

### `TEST:UI.Persona.FallbackAndContextSelectionWorks`
- **Scenario name:** Persona rendering supports context-aware selection and fallback
- **Primary layers:** `browser`, `unit`
- **Primary requirement/architecture drivers:** `REQ:VisualPersonaSupport`, `ARCH:VisualPersonaSelection`, `ARCH:PersonaAssetModel`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove persona support is bounded and asset-driven.

### `TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent`
- **Scenario name:** Persona rendering remains subordinate to operational content
- **Primary layers:** `browser`, `api`
- **Primary requirement/architecture drivers:** `REQ:VisualPersonaSupport`, `ARCH:VisualPersonaSelection`
- **Primary workstream linkage:** `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove persona assets enhance but do not dominate the workspace.

**Stable verification anchor:** `TESTCATALOG:WebWorkspace`

---

## 7.8 Voice and companion scenarios

### `TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary`
- **Scenario name:** Telegram “what matters now” flow returns bounded companion summary
- **Primary layers:** `graph`, `contract`, `integration`
- **Primary requirement/architecture drivers:** `REQ:TelegramMobilePresence`, `ARCH:TelegramCompanionChannel`, `ARCH:TelegramCompanionUx`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove Telegram provides useful mobile support without becoming a hidden control room.

### `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded`
- **Scenario name:** Telegram interaction hands off to workspace when richer review is required
- **Primary layers:** `graph`, `browser`, `contract`
- **Primary requirement/architecture drivers:** `REQ:TelegramMobilePresence`, `REQ:HumanApprovalBoundaries`, `ARCH:ChannelHandoffUx`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove Telegram does not overreach beyond its safe scope.

### `TEST:Voice.Session.TranscriptBecomesStructuredSignal`
- **Scenario name:** Voice transcript becomes structured internal artifact
- **Primary layers:** `integration`, `graph`
- **Primary requirement/architecture drivers:** `REQ:VoiceInteraction`, `ARCH:VoiceToStructuredOutputPath`, `ARCH:VoiceSessionGraph`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove spoken input enters the core model rather than remaining ephemeral.

### `TEST:Voice.Session.ContinuityPreservedWithinSession`
- **Scenario name:** Voice session preserves short-horizon continuity
- **Primary layers:** `integration`, `graph`
- **Primary requirement/architecture drivers:** `REQ:StateContinuity`, `ARCH:VoiceSessionContinuity`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove voice interaction is not a sequence of stateless one-shots.

### `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions`
- **Scenario name:** Voice-derived meaningful actions still require review where appropriate
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:ReviewGateArchitecture`, `ARCH:VoiceInteractionArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove voice does not bypass approval discipline.

### `TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession`
- **Scenario name:** Voice session bootstrap binds the correct operator and creates session state
- **Primary layers:** `integration`, `api`
- **Primary requirement/architecture drivers:** `REQ:VoiceInteraction`, `ARCH:VoiceSessionGraph`, `ARCH:ChannelSessionModel`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove voice sessions are operator-bound and channel-identified.

### `TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant`
- **Scenario name:** Spoken briefing is bounded in length and grounded in focus-pack data
- **Primary layers:** `integration`, `api`
- **Primary requirement/architecture drivers:** `REQ:PreparedBriefings`, `REQ:VoiceInteraction`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove spoken output is concise, numbered, and relevant — not bloated or vague.

### `TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation`
- **Scenario name:** Voice session handoff creates workspace-visible continuation record
- **Primary layers:** `integration`, `api`
- **Primary requirement/architecture drivers:** `REQ:StateContinuity`, `ARCH:ChannelHandoffUx`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove voice handoff creates BriefingArtifact(channel_handoff) for the main workspace.

### `TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace`
- **Scenario name:** Telegram review-needed state surfaces in the main workspace
- **Primary layers:** `integration`, `api`
- **Primary requirement/architecture drivers:** `REQ:TelegramMobilePresence`, `REQ:HumanApprovalBoundaries`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove Telegram handoffs create pending workspace records retrievable by the operator.

### `TEST:ChannelSession.SummariesPersistWithTraceableOrigin`
- **Scenario name:** Channel session summaries persist with traceable origin
- **Primary layers:** `integration`, `api`
- **Primary requirement/architecture drivers:** `REQ:StateContinuity`, `ARCH:ChannelSessionModel`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove session completion creates summaries linked to the originating session.

### `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved`
- **Scenario name:** Voice and Telegram both use the shared core flow with safety parity
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:SafeBehaviorDefaults`, `ARCH:LangGraphTopology`, `ARCH:NoAutoSendPolicy`
- **Primary workstream linkage:** `PLAN:WorkstreamF.Voice`
- **Intent:** Prove both companion channels route through the same IntakeGraph with auto_send_blocked.

**Stable verification anchor:** `TESTCATALOG:VoiceAndCompanion`

---

## 7.8A Deep research and escalated reasoning scenarios

### `TEST:Research.Escalation.RoutesWhenTaskRequiresDeepResearch`
- **Scenario name:** Research escalation routes tasks to deep research when criteria are met
- **Primary layers:** `graph`, `unit`
- **Primary requirement/architecture drivers:** `REQ:ResearchEscalationPath`, `ARCH:ResearchEscalationPolicy`, `ARCH:ResearchEscalationGraph`
- **Primary workstream linkage:** `PLAN:WorkstreamH.DeepResearch`
- **Intent:** Prove escalation logic correctly identifies tasks that warrant deep research.

### `TEST:Research.Invocation.StartsBoundedResearchRun`
- **Scenario name:** Research invocation starts a bounded research run with proper context
- **Primary layers:** `integration`, `graph`
- **Primary requirement/architecture drivers:** `REQ:DeepResearchCapability`, `ARCH:ResearchRunLifecycle`, `ARCH:ResearchRunModel`
- **Primary workstream linkage:** `PLAN:WorkstreamH.DeepResearch`
- **Intent:** Prove research runs start with proper context, provenance, and bounded scope.

### `TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult`
- **Scenario name:** Research adapter returns structured results from Gemini browser path
- **Primary layers:** `contract`, `manual_only`
- **Primary requirement/architecture drivers:** `REQ:ResearchOutputArtifacts`, `ARCH:GeminiBrowserMediatedAdapter`
- **Primary workstream linkage:** `PLAN:WorkstreamH.DeepResearch`
- **Intent:** Prove the adapter produces structured research artifacts from browser interaction.

### `TEST:Research.Provenance.RunAndSourceTrailPersisted`
- **Scenario name:** Research run and source trail are persisted with full provenance
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:ResearchRunProvenance`, `ARCH:ResearchRunModel`, `ARCH:ResearchSourceReferenceModel`
- **Primary workstream linkage:** `PLAN:WorkstreamH.DeepResearch`
- **Intent:** Prove research provenance survives persistence and is queryable.

### `TEST:Research.Failure.BrowserUnavailableHandledSafely`
- **Scenario name:** Browser unavailability is handled with visible failure state
- **Primary layers:** `contract`, `integration`
- **Primary requirement/architecture drivers:** `REQ:BoundedBrowserMediatedResearch`, `ARCH:BrowserResearchSecurityBoundary`
- **Primary workstream linkage:** `PLAN:WorkstreamH.DeepResearch`
- **Intent:** Prove the system degrades gracefully when the browser is not available.

### `TEST:Research.Failure.GeminiInteractionFailureVisible`
- **Scenario name:** Gemini interaction failure produces visible error state
- **Primary layers:** `contract`, `integration`
- **Primary requirement/architecture drivers:** `REQ:BoundedBrowserMediatedResearch`, `ARCH:ResearchAdapterSafetyBoundary`
- **Primary workstream linkage:** `PLAN:WorkstreamH.DeepResearch`
- **Intent:** Prove Gemini-specific failures are surfaced visibly rather than silently swallowed.

### `TEST:Research.Security.NoUnboundedActionTaking`
- **Scenario name:** Research capability does not take unbounded external actions
- **Primary layers:** `unit`, `contract`
- **Primary requirement/architecture drivers:** `REQ:BoundedBrowserMediatedResearch`, `REQ:SafeBehaviorDefaults`, `ARCH:ResearchAdapterSafetyBoundary`
- **Primary workstream linkage:** `PLAN:WorkstreamH.DeepResearch`
- **Intent:** Prove the research adapter enforces destination whitelisting and action boundaries.

### `TEST:Research.Output.ResultsReenterWorkflowSafely`
- **Scenario name:** Research results re-enter orchestration workflow as reviewable candidates
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:ResearchOutputArtifacts`, `ARCH:ResearchVerificationStrategy`, `ARCH:ResearchEscalationGraph`
- **Primary workstream linkage:** `PLAN:WorkstreamH.DeepResearch`
- **Intent:** Prove research outputs pass through review gates before entering accepted memory.

**Stable verification anchor:** `TESTCATALOG:DeepResearch`

## 7.8B Expert advice scenarios

### `TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse`
- **Scenario name:** Expert advice sends a prompt to Gemini and returns the response text
- **Primary layers:** `contract`, `integration`
- **Primary requirement/architecture drivers:** `REQ:ExpertAdviceCapability`, `ARCH:GeminiChatAdapter`, `ARCH:ExpertAdviceCapability`
- **Primary workstream linkage:** `PLAN:WorkstreamH.PackageH7.ExpertAdviceAdapter`
- **Intent:** Prove the adapter can execute a synchronous Gemini chat and return the response.

### `TEST:ExpertAdvice.Provenance.ExchangeRecordPersisted`
- **Scenario name:** Expert advice exchange is persisted with full provenance
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:ExpertAdviceProvenance`, `ARCH:ExpertAdviceExchangeModel`
- **Primary workstream linkage:** `PLAN:WorkstreamH.PackageH7.ExpertAdviceAdapter`
- **Intent:** Prove expert-advice exchanges preserve prompt, response, mode, duration, and invocation origin.

### `TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected`
- **Scenario name:** Expert advice respects Gemini mode selection (Fast, Thinking, Pro)
- **Primary layers:** `contract`, `unit`
- **Primary requirement/architecture drivers:** `REQ:ExpertAdviceCapability`, `ARCH:GeminiChatAdapter`
- **Primary workstream linkage:** `PLAN:WorkstreamH.PackageH7.ExpertAdviceAdapter`
- **Intent:** Prove mode selection is passed through and recorded correctly.

### `TEST:ExpertAdvice.Failure.GeminiUnavailableHandledSafely`
- **Scenario name:** Expert advice handles Gemini unavailability gracefully
- **Primary layers:** `contract`, `integration`
- **Primary requirement/architecture drivers:** `REQ:BoundedBrowserMediatedResearch`, `ARCH:ExpertAdviceCapability`
- **Primary workstream linkage:** `PLAN:WorkstreamH.PackageH7.ExpertAdviceAdapter`
- **Intent:** Prove the system degrades gracefully when Gemini is unavailable for expert advice.

### `TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice`
- **Scenario name:** Escalation policy correctly routes to expert advice vs. deep research
- **Primary layers:** `unit`, `graph`
- **Primary requirement/architecture drivers:** `REQ:EscalationRouting`, `ARCH:ExpertAdviceEscalationPolicy`
- **Primary workstream linkage:** `PLAN:WorkstreamH.PackageH8.ExpertAdviceOrchestration`
- **Intent:** Prove the escalation router selects the correct mode based on task characteristics.

### `TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate`
- **Scenario name:** Expert advice response enters workflow as interpreted candidate, not accepted truth
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:ExpertAdviceCapability`, `ARCH:ExpertAdviceReviewBoundary`
- **Primary workstream linkage:** `PLAN:WorkstreamH.PackageH8.ExpertAdviceOrchestration`
- **Intent:** Prove expert-advice outputs pass through review gates before entering accepted memory.

**Stable verification anchor:** `TESTCATALOG:ExpertAdvice`

---

## 7.9 Security and approval-boundary scenarios

### `TEST:Security.NoAutoSend.GlobalBoundaryPreserved`
- **Scenario name:** No-auto-send boundary is preserved across all channels
- **Primary layers:** `integration`, `graph`, `api`
- **Primary requirement/architecture drivers:** `REQ:SafeBehaviorDefaults`, `ARCH:NoAutoSendPolicy`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`, `PLAN:WorkstreamD.TriageAndPrioritization`, `PLAN:WorkstreamF.Voice`
- **Intent:** Prove no surface silently externalizes operator impact.

### `TEST:Security.ReviewGate.ExternalImpactRequiresApproval`
- **Scenario name:** Externally meaningful actions require structured approval
- **Primary layers:** `graph`, `api`, `browser`
- **Primary requirement/architecture drivers:** `REQ:HumanApprovalBoundaries`, `ARCH:ReviewGateArchitecture`
- **Primary workstream linkage:** `PLAN:WorkstreamD.TriageAndPrioritization`, `PLAN:WorkstreamE.DraftingUi`
- **Intent:** Prove review gates are real and cross-surface.

### `TEST:Security.LeastPrivilege.ScopeExpansionMustBeExplicit`
- **Scenario name:** Scope-expanding integration behavior is explicit and not silent
- **Primary layers:** `contract`, `integration`, `manual_only`
- **Primary requirement/architecture drivers:** `REQ:PrivacyAndLeastPrivilege`, `ARCH:LeastPrivilegeModel`
- **Primary workstream linkage:** `PLAN:WorkstreamC.Connectors`
- **Intent:** Prove connector behavior remains within intended permissions.

**Stable verification anchor:** `TESTCATALOG:SecurityAndApproval`

---

## 7.10 Cross-cutting regression and release scenarios

### `TEST:Release.Smoke.CoreSystemBoots`
- **Scenario name:** Core system smoke path passes for release confidence
- **Primary layers:** `integration`, `browser`
- **Primary requirement/architecture drivers:** `ARCH:TestingArchitecture`, `ARCH:VerificationLayerModel`
- **Primary workstream linkage:** `PLAN:WorkstreamG.TestingAndRegression`
- **Intent:** Prove the minimum viable system still boots and renders.

### `TEST:Release.DataIntegrity.MemoryAndProvenanceRemainConsistent`
- **Scenario name:** Data-integrity regression proves memory and provenance remain consistent
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:ProjectMemory`, `REQ:MultiAccountProfileSupport`, `ARCH:DomainMemoryVerification`
- **Primary workstream linkage:** `PLAN:WorkstreamG.TestingAndRegression`
- **Intent:** Prove foundational truth has not drifted across releases.

### `TEST:Release.Browser.CoreOperatorJourneysPass`
- **Scenario name:** Core operator browser journeys pass in release pack
- **Primary layers:** `browser`
- **Primary requirement/architecture drivers:** `REQ:ProjectPortfolioManagement`, `REQ:DraftResponseWorkspace`, `ARCH:PlaywrightTestBoundary`
- **Primary workstream linkage:** `PLAN:WorkstreamG.TestingAndRegression`
- **Intent:** Prove key UI journeys remain intact before release confidence is claimed.

### `TEST:Release.Graph.CoreAssistantFlowsPass`
- **Scenario name:** Core graph-driven assistant flows pass in release pack
- **Primary layers:** `graph`, `integration`
- **Primary requirement/architecture drivers:** `REQ:ContextualMessageClassification`, `REQ:PrioritizationEngine`, `ARCH:GraphVerificationStrategy`
- **Primary workstream linkage:** `PLAN:WorkstreamG.TestingAndRegression`
- **Intent:** Prove the assistant core still behaves coherently as a system.

### `TEST:Integrity.SourceLayer.MessagesThreadsEventsSignalsRemainDistinct`
- **Scenario name:** Source-layer records — messages, threads, events, signals — remain distinct
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:MessageIngestion`, `REQ:TraceabilityAndAuditability`, `ARCH:StructuredMemoryModel`
- **Primary workstream linkage:** `PLAN:WorkstreamG.TestingAndRegression`
- **Intent:** Prove source-record types do not collapse into a single table or lose type identity.

### `TEST:Integrity.AcceptedState.PromotionRetainsOriginTrace`
- **Scenario name:** Accepted-state promotion retains origin trace from interpreted artifacts
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:Explainability`, `REQ:TraceabilityAndAuditability`
- **Primary workstream linkage:** `PLAN:WorkstreamG.TestingAndRegression`
- **Intent:** Prove accepted work items retain a provenance link to their source interpretation.

### `TEST:Integrity.Summaries.SupersessionDoesNotEraseHistory`
- **Scenario name:** Summary supersession does not erase historical summaries
- **Primary layers:** `integration`
- **Primary requirement/architecture drivers:** `REQ:ProjectMemory`, `ARCH:ProjectMemoryRefresh`
- **Primary workstream linkage:** `PLAN:WorkstreamG.TestingAndRegression`
- **Intent:** Prove memory refresh creates new summaries rather than overwriting old ones.

**Stable verification anchor:** `TESTCATALOG:ReleaseAndRegression`

---

## 8. Catalog Maintenance Rules

### 8.1 Add anchors when risk appears

If a meaningful behavior emerges that has no stable `TEST:` anchor, add one instead of relying on vague prose in a progress file.

### 8.2 Do not create throwaway scenario names

Scenario labels should remain stable and descriptive. Avoid temporary labels like `TEST:Planner.Fix2` or `TEST:UI.Stuff`.

### 8.3 Prefer meaningful granularity

`TEST:` anchors should be granular enough to be useful, but not so tiny that the catalog becomes noise.

### 8.4 Keep the catalog aligned to current architecture and build plan

If workstream boundaries or architecture anchors evolve materially, update the catalog deliberately rather than letting traceability rot.

**Stable verification anchor:** `TESTCATALOG:MaintenanceRules`

---

## 9. Relationship to Verification Packs

This catalog defines the stable scenario vocabulary.

The verification packs should then group these scenarios into practical execution sets such as:

- smoke,
- workstream-specific proof,
- browser regression,
- connector regression,
- data-integrity regression,
- and release confidence packs.

The same `TEST:` anchor may appear in more than one pack where appropriate.

**Stable verification anchor:** `TESTCATALOG:RelationshipToPacks`

---

## 10. Final Note

The Glimmer test catalog exists to keep proof stable as the system evolves.

If this document is maintained well, future workstreams, automated tests, progress files, and release reviews can all talk about the same behaviors without ambiguity.

That is the point: not more paperwork, but less drift.

**Stable verification anchor:** `TESTCATALOG:Conclusion`

