# Glimmer — TEST: Anchor Traceability Report

**Catalog anchors defined:** 59
**Anchors referenced in tests:** 78
**Covered by tests:** 40
**Missing from tests:** 19
**In tests but not in catalog:** 38

## Covered Anchors

| Anchor | Test Files |
|---|---|
| `TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext` | integration/test_connector_gcal.py |
| `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount` | integration/test_connector_gmail.py |
| `TEST:Connector.ManualImport.LabelingAndRouting` | integration/test_connector_manual.py |
| `TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext` | integration/test_connector_mscal.py |
| `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread` | integration/test_connector_msmail.py |
| `TEST:Connector.SyncFailure.VisibleState` | integration/test_connector_sync.py |
| `TEST:Connector.Telegram.InboundBecomesBoundedSignal` | integration/test_connector_telegram.py |
| `TEST:Domain.Audit.MeaningfulStateMutation` | integration/test_domain_audit.py |
| `TEST:Domain.InterpretedVsAccepted.Separation` | integration/test_domain_interpretation.py, integration/test_data_integrity_pack.py |
| `TEST:Domain.MultiAccount.ProvenancePersistence` | integration/test_data_integrity_pack.py, integration/test_domain_source.py |
| `TEST:Domain.ProjectLifecycle.BasicPersistence` | integration/test_domain_portfolio.py |
| `TEST:Domain.StakeholderIdentity.MultiIdentityLinking` | integration/test_domain_stakeholder.py |
| `TEST:Domain.SummaryRefresh.Lineage` | integration/test_domain_summary.py |
| `TEST:Drafting.DraftGeneration.CreatesReviewableDraft` | integration/test_drafting_handoff.py |
| `TEST:Drafting.NoAutoSend.BoundaryPreserved` | integration/test_drafting_handoff.py, api/test_voice_api.py, api/test_projects_drafts.py |
| `TEST:Drafting.Variants.MultipleVariantsRemainLinked` | api/test_projects_drafts.py |
| `TEST:Planner.FocusPack.GeneratesExplainablePriorities` | integration/test_planner_focus.py |
| `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable` | integration/test_planner_refresh.py |
| `TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure` | integration/test_planner_nextsteps.py, api/test_triage_api.py |
| `TEST:Security.NoAutoSend.GlobalBoundaryPreserved` | integration/test_telegram_companion.py, integration/test_cross_surface_handoff.py, integration/test_drafting_handoff.py, integration/test_data_integrity_pack.py, api/test_voice_api.py, api/test_telegram_api.py |
| `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` | integration/test_cross_surface_handoff.py, api/test_triage_api.py |
| `TEST:Smoke.BackendStarts` | api/test_smoke.py |
| `TEST:Smoke.DatabaseConnectivity` | api/test_smoke.py |
| `TEST:Smoke.FrontendStarts` | browser/workspace-navigation.spec.ts |
| `TEST:Smoke.WorkspaceNavigationBasic` | browser/workspace-navigation.spec.ts |
| `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded` | integration/test_telegram_companion.py, integration/test_cross_surface_handoff.py, api/test_telegram_api.py |
| `TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary` | integration/test_telegram_companion.py, api/test_telegram_api.py |
| `TEST:Triage.ActionExtraction.ClearRequestBecomesCandidateAction` | integration/test_triage_extraction.py |
| `TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview` | integration/test_triage_extraction.py |
| `TEST:Triage.Intake.SourceRoutesCorrectly` | integration/test_triage_intake.py |
| `TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview` | integration/test_triage_classification.py |
| `TEST:Triage.ProjectClassification.SingleStrongMatch` | integration/test_triage_classification.py |
| `TEST:Triage.StakeholderInterpretation.UncertainIdentityRequiresReview` | integration/test_triage_classification.py |
| `TEST:UI.DraftWorkspace.ShowsContextAndVariants` | api/test_projects_drafts.py |
| `TEST:UI.Persona.FallbackAndContextSelectionWorks` | api/test_persona.py |
| `TEST:UI.PortfolioView.ComparesProjectAttentionDemand` | api/test_projects_drafts.py |
| `TEST:UI.ProjectWorkspace.ShowsSynthesisNotJustChronology` | api/test_projects_drafts.py |
| `TEST:Voice.Session.ContinuityPreservedWithinSession` | integration/test_voice_continuity.py |
| `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions` | integration/test_voice_routing.py |
| `TEST:Voice.Session.TranscriptBecomesStructuredSignal` | integration/test_voice_transcript_normalization.py, api/test_voice_api.py |

## Missing from Tests

These anchors are defined in the catalog but have no implementing test:

- `TEST:Planner.Fix2`
- `TEST:Release.Browser.CoreOperatorJourneysPass`
- `TEST:Release.DataIntegrity.MemoryAndProvenanceRemainConsistent`
- `TEST:Release.Graph.CoreAssistantFlowsPass`
- `TEST:Release.Smoke.CoreSystemBoots`
- `TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult`
- `TEST:Research.Escalation.RoutesWhenTaskRequiresDeepResearch`
- `TEST:Research.Failure.BrowserUnavailableHandledSafely`
- `TEST:Research.Failure.GeminiInteractionFailureVisible`
- `TEST:Research.Invocation.StartsBoundedResearchRun`
- `TEST:Research.Output.ResultsReenterWorkflowSafely`
- `TEST:Research.Provenance.RunAndSourceTrailPersisted`
- `TEST:Research.Security.NoUnboundedActionTaking`
- `TEST:Review.AcceptAmendRejectDefer.ChangesPersistCorrectly`
- `TEST:Security.LeastPrivilege.ScopeExpansionMustBeExplicit`
- `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious`
- `TEST:UI.Stuff`
- `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly`
- `TEST:UI.TriageView.ShowsProvenanceAndReviewControls`

## In Tests but Not in Catalog

These anchors appear in tests but are not in the canonical catalog:

- `TEST:API.Operator.CreateReadUpdate` → api/test_operator.py
- `TEST:API.Operator.SingleOperatorConstraint` → api/test_operator.py
- `TEST:ApplicationSurface.TriageAndPriorityEndpointsSupportReviewActions` → api/test_triage_api.py
- `TEST:ChannelSession.SummariesPersistWithTraceableOrigin` → integration/test_voice_continuity.py, api/test_voice_api.py
- `TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile` → integration/test_connector_context.py
- `TEST:Connector.Framework.ProviderBoundaryIsolation` → integration/test_connector_framework.py
- `TEST:Connector.IntakeHandoff.BoundedReferenceFlow` → integration/test_connector_intake.py
- `TEST:Connector.Normalization.PersistBeforeInterpretation` → integration/test_connector_intake.py
- `TEST:Connector.Security.ReadFirstNoAutoSendPreserved` → integration/test_connector_framework.py
- `TEST:Domain.Briefings.FocusAndBriefingArtifactsPersist` → integration/test_domain_drafting.py
- `TEST:Domain.ChannelSessions.TelegramAndVoiceStatePersist` → integration/test_domain_channel.py
- `TEST:Domain.Drafting.DraftsAndVariantsPersistWithIntent` → integration/test_domain_drafting.py
- `TEST:Domain.Execution.AcceptedArtifactsPersistSeparately` → integration/test_domain_execution.py
- `TEST:Domain.Interpretation.ReviewStateLifecyclePersists` → integration/test_domain_interpretation.py
- `TEST:Domain.Operator.OwnsProjectsAccountsSessions` → integration/test_domain_operator.py
- `TEST:Domain.Operator.PersistsWithPreferences` → integration/test_domain_operator.py
- `TEST:Domain.Persona.AssetsAndClassificationPersist` → integration/test_domain_persona.py
- `TEST:Domain.ProjectPortfolio.WorkstreamsAndMilestonesPersist` → integration/test_domain_portfolio.py
- `TEST:Domain.SourceRecords.MessagesThreadsEventsPersistSeparately` → integration/test_domain_source.py
- `TEST:Foundation.AgentSupport.CoreSurfacesPresent` → api/test_operational_support.py
- `TEST:Foundation.Backend.StructureRespectsBoundaryShape` → api/test_smoke.py
- `TEST:Foundation.Config.LocalFirstDefaultsResolve` → api/test_smoke.py
- `TEST:Foundation.Frontend.WorkspaceShellExists` → browser/workspace-navigation.spec.ts
- `TEST:Foundation.Persistence.MigrationBaselineExists` → integration/test_persistence_baseline.py
- `TEST:Integrity.AcceptedState.PromotionRetainsOriginTrace` → integration/test_data_integrity_pack.py
- `TEST:Integrity.SourceLayer.MessagesThreadsEventsSignalsRemainDistinct` → integration/test_data_integrity_pack.py
- `TEST:Integrity.Summaries.SupersessionDoesNotEraseHistory` → integration/test_data_integrity_pack.py
- `TEST:Planner.FocusPack.PersistsTopActionsAndPressureSignals` → integration/test_planner_focus.py
- `TEST:Planner.PriorityRationale.VisibleInApplicationSurface` → api/test_triage_api.py
- `TEST:Something.Something` → tools/anchor_scanner.py
- `TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace` → integration/test_cross_surface_handoff.py, api/test_telegram_api.py
- `TEST:Triage.Extraction.DecisionAndDeadlineSignalsPersist` → integration/test_triage_extraction.py
- `TEST:Triage.ReviewInterrupt.ResumeContinuesSafely` → integration/test_triage_extraction.py
- `TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent` → api/test_persona.py
- `TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession` → integration/test_voice_session_bootstrap.py, api/test_voice_api.py
- `TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation` → integration/test_cross_surface_handoff.py, api/test_voice_api.py
- `TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant` → integration/test_voice_spoken_briefing.py, api/test_voice_api.py
- `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved` → integration/test_telegram_companion.py, integration/test_cross_surface_handoff.py, integration/test_voice_routing.py
