# Glimmer — TEST: Anchor Traceability Report

**Catalog anchors defined:** 102
**Anchors referenced in tests:** 102
**Covered by tests:** 102
**Missing from tests:** 0
**In tests but not in catalog:** 0

## Covered Anchors

| Anchor | Test Files |
|---|---|
| `TEST:API.Operator.CreateReadUpdate` | tests/api/test_operator.py |
| `TEST:API.Operator.SingleOperatorConstraint` | tests/api/test_operator.py |
| `TEST:ApplicationSurface.TriageAndPriorityEndpointsSupportReviewActions` | tests/api/test_triage_api.py |
| `TEST:ChannelSession.SummariesPersistWithTraceableOrigin` | tests/integration/test_voice_continuity.py, tests/api/test_voice_api.py |
| `TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile` | tests/integration/test_connector_context.py |
| `TEST:Connector.Framework.ProviderBoundaryIsolation` | tests/integration/test_connector_framework.py |
| `TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext` | tests/integration/test_connector_gcal.py |
| `TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount` | tests/integration/test_connector_gmail.py |
| `TEST:Connector.IntakeHandoff.BoundedReferenceFlow` | tests/integration/test_connector_intake.py |
| `TEST:Connector.ManualImport.LabelingAndRouting` | tests/integration/test_connector_manual.py |
| `TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext` | tests/integration/test_connector_mscal.py |
| `TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread` | tests/integration/test_connector_msmail.py |
| `TEST:Connector.Normalization.PersistBeforeInterpretation` | tests/integration/test_connector_intake.py |
| `TEST:Connector.Security.ReadFirstNoAutoSendPreserved` | tests/integration/test_connector_framework.py |
| `TEST:Connector.SyncFailure.VisibleState` | tests/integration/test_connector_sync.py |
| `TEST:Connector.Telegram.InboundBecomesBoundedSignal` | tests/integration/test_connector_telegram.py |
| `TEST:Domain.Audit.MeaningfulStateMutation` | tests/integration/test_domain_audit.py |
| `TEST:Domain.Briefings.FocusAndBriefingArtifactsPersist` | tests/integration/test_domain_drafting.py |
| `TEST:Domain.ChannelSessions.TelegramAndVoiceStatePersist` | tests/integration/test_domain_channel.py |
| `TEST:Domain.Drafting.DraftsAndVariantsPersistWithIntent` | tests/integration/test_domain_drafting.py |
| `TEST:Domain.Execution.AcceptedArtifactsPersistSeparately` | tests/integration/test_domain_execution.py |
| `TEST:Domain.Interpretation.ReviewStateLifecyclePersists` | tests/integration/test_domain_interpretation.py |
| `TEST:Domain.InterpretedVsAccepted.Separation` | tests/integration/test_domain_interpretation.py, tests/integration/test_data_integrity_pack.py |
| `TEST:Domain.MultiAccount.ProvenancePersistence` | tests/integration/test_data_integrity_pack.py, tests/integration/test_domain_source.py |
| `TEST:Domain.Operator.OwnsProjectsAccountsSessions` | tests/integration/test_domain_operator.py |
| `TEST:Domain.Operator.PersistsWithPreferences` | tests/integration/test_domain_operator.py |
| `TEST:Domain.Persona.AssetsAndClassificationPersist` | tests/integration/test_domain_persona.py |
| `TEST:Domain.ProjectLifecycle.BasicPersistence` | tests/integration/test_domain_portfolio.py |
| `TEST:Domain.ProjectPortfolio.WorkstreamsAndMilestonesPersist` | tests/integration/test_domain_portfolio.py |
| `TEST:Domain.SourceRecords.MessagesThreadsEventsPersistSeparately` | tests/integration/test_domain_source.py |
| `TEST:Domain.StakeholderIdentity.MultiIdentityLinking` | tests/integration/test_domain_stakeholder.py |
| `TEST:Domain.SummaryRefresh.Lineage` | tests/integration/test_domain_summary.py |
| `TEST:Drafting.DraftGeneration.CreatesReviewableDraft` | tests/integration/test_drafting_handoff.py |
| `TEST:Drafting.NoAutoSend.BoundaryPreserved` | tests/integration/test_drafting_handoff.py, tests/api/test_voice_api.py, tests/api/test_projects_drafts.py, apps/web/e2e/workspace-surfaces.spec.ts, apps/web/e2e/persona-and-safety.spec.ts |
| `TEST:Drafting.Variants.MultipleVariantsRemainLinked` | tests/api/test_projects_drafts.py |
| `TEST:ExpertAdvice.Failure.GeminiUnavailableHandledSafely` | tests/integration/test_research_adapter.py, tests/integration/test_research_models.py |
| `TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse` | tests/integration/test_research_adapter.py |
| `TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected` | tests/integration/test_research_adapter.py, tests/integration/test_research_models.py |
| `TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate` | tests/integration/test_research_escalation.py, tests/integration/test_research_models.py, tests/api/test_research_api.py |
| `TEST:ExpertAdvice.Provenance.ExchangeRecordPersisted` | tests/integration/test_research_models.py |
| `TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice` | tests/integration/test_research_escalation.py, tests/api/test_research_api.py |
| `TEST:Foundation.AgentSupport.CoreSurfacesPresent` | tests/api/test_operational_support.py |
| `TEST:Foundation.Backend.StructureRespectsBoundaryShape` | tests/api/test_smoke.py |
| `TEST:Foundation.Config.LocalFirstDefaultsResolve` | tests/api/test_smoke.py |
| `TEST:Foundation.Frontend.WorkspaceShellExists` | tests/browser/workspace-navigation.spec.ts, apps/web/e2e/workspace-navigation.spec.ts |
| `TEST:Foundation.Persistence.MigrationBaselineExists` | tests/integration/test_persistence_baseline.py |
| `TEST:Integrity.AcceptedState.PromotionRetainsOriginTrace` | tests/integration/test_data_integrity_pack.py |
| `TEST:Integrity.SourceLayer.MessagesThreadsEventsSignalsRemainDistinct` | tests/integration/test_data_integrity_pack.py |
| `TEST:Integrity.Summaries.SupersessionDoesNotEraseHistory` | tests/integration/test_data_integrity_pack.py |
| `TEST:Planner.FocusPack.GeneratesExplainablePriorities` | tests/integration/test_planner_focus.py |
| `TEST:Planner.FocusPack.PersistsTopActionsAndPressureSignals` | tests/integration/test_planner_focus.py |
| `TEST:Planner.PriorityRationale.VisibleInApplicationSurface` | tests/api/test_triage_api.py |
| `TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable` | tests/integration/test_planner_refresh.py |
| `TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure` | tests/integration/test_planner_nextsteps.py, tests/api/test_triage_api.py |
| `TEST:Release.Browser.CoreOperatorJourneysPass` | apps/web/e2e/workspace-surfaces.spec.ts |
| `TEST:Release.DataIntegrity.MemoryAndProvenanceRemainConsistent` | tests/integration/test_data_integrity_pack.py |
| `TEST:Release.Graph.CoreAssistantFlowsPass` | tests/integration/test_triage_intake.py |
| `TEST:Release.Smoke.CoreSystemBoots` | tests/api/test_smoke.py |
| `TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult` | tests/integration/test_research_adapter.py |
| `TEST:Research.Escalation.RoutesWhenTaskRequiresDeepResearch` | tests/integration/test_research_escalation.py |
| `TEST:Research.Failure.BrowserUnavailableHandledSafely` | tests/integration/test_chrome_lifecycle.py, tests/integration/test_research_adapter.py |
| `TEST:Research.Failure.GeminiInteractionFailureVisible` | tests/integration/test_research_adapter.py |
| `TEST:Research.Invocation.StartsBoundedResearchRun` | tests/integration/test_research_models.py |
| `TEST:Research.Output.ResultsReenterWorkflowSafely` | tests/integration/test_research_escalation.py, tests/integration/test_research_models.py, tests/api/test_research_api.py |
| `TEST:Research.Provenance.RunAndSourceTrailPersisted` | tests/integration/test_research_models.py |
| `TEST:Research.Security.NoUnboundedActionTaking` | tests/integration/test_research_adapter.py |
| `TEST:Review.AcceptAmendRejectDefer.ChangesPersistCorrectly` | tests/api/test_projects_drafts.py |
| `TEST:Security.LeastPrivilege.ScopeExpansionMustBeExplicit` | tests/integration/test_connector_framework.py |
| `TEST:Security.NoAutoSend.GlobalBoundaryPreserved` | tests/integration/test_telegram_companion.py, tests/integration/test_cross_surface_handoff.py, tests/integration/test_drafting_handoff.py, tests/integration/test_data_integrity_pack.py, tests/api/test_voice_api.py, tests/api/test_telegram_api.py |
| `TEST:Security.ReviewGate.ExternalImpactRequiresApproval` | tests/integration/test_cross_surface_handoff.py, tests/api/test_triage_api.py, apps/web/e2e/persona-and-safety.spec.ts |
| `TEST:Smoke.BackendStarts` | tests/api/test_smoke.py |
| `TEST:Smoke.DatabaseConnectivity` | tests/api/test_smoke.py |
| `TEST:Smoke.FrontendStarts` | tests/browser/workspace-navigation.spec.ts, apps/web/e2e/workspace-navigation.spec.ts |
| `TEST:Smoke.WorkspaceNavigationBasic` | tests/browser/workspace-navigation.spec.ts, apps/web/e2e/workspace-navigation.spec.ts |
| `TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded` | tests/integration/test_telegram_companion.py, tests/integration/test_cross_surface_handoff.py, tests/api/test_telegram_api.py |
| `TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace` | tests/integration/test_cross_surface_handoff.py, tests/api/test_telegram_api.py |
| `TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary` | tests/integration/test_telegram_companion.py, tests/api/test_telegram_api.py |
| `TEST:Triage.ActionExtraction.ClearRequestBecomesCandidateAction` | tests/integration/test_triage_extraction.py |
| `TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview` | tests/integration/test_triage_extraction.py |
| `TEST:Triage.Extraction.DecisionAndDeadlineSignalsPersist` | tests/integration/test_triage_extraction.py |
| `TEST:Triage.Intake.SourceRoutesCorrectly` | tests/integration/test_triage_intake.py |
| `TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview` | tests/integration/test_triage_classification.py |
| `TEST:Triage.ProjectClassification.SingleStrongMatch` | tests/integration/test_triage_classification.py |
| `TEST:Triage.ReviewInterrupt.ResumeContinuesSafely` | tests/integration/test_triage_extraction.py |
| `TEST:Triage.StakeholderInterpretation.UncertainIdentityRequiresReview` | tests/integration/test_triage_classification.py |
| `TEST:UI.DraftWorkspace.CopyEditFlowRemainsReviewOnly` | apps/web/e2e/workspace-surfaces.spec.ts |
| `TEST:UI.DraftWorkspace.ShowsContextAndVariants` | tests/api/test_projects_drafts.py, apps/web/e2e/workspace-surfaces.spec.ts |
| `TEST:UI.Navigation.WorkspaceRoutesRemainReachable` | apps/web/e2e/workspace-surfaces.spec.ts |
| `TEST:UI.Persona.FallbackAndContextSelectionWorks` | tests/api/test_persona.py, apps/web/e2e/persona-and-safety.spec.ts |
| `TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent` | tests/api/test_persona.py, apps/web/e2e/persona-and-safety.spec.ts |
| `TEST:UI.PortfolioView.ComparesProjectAttentionDemand` | tests/api/test_projects_drafts.py, apps/web/e2e/workspace-surfaces.spec.ts |
| `TEST:UI.ProjectWorkspace.ShowsSynthesisNotJustChronology` | tests/api/test_projects_drafts.py |
| `TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious` | apps/web/e2e/workspace-surfaces.spec.ts, apps/web/e2e/persona-and-safety.spec.ts |
| `TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly` | apps/web/e2e/workspace-surfaces.spec.ts |
| `TEST:UI.TriageView.ShowsProvenanceAndReviewControls` | apps/web/e2e/workspace-surfaces.spec.ts |
| `TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession` | tests/integration/test_voice_session_bootstrap.py, tests/api/test_voice_api.py |
| `TEST:Voice.Session.ContinuityPreservedWithinSession` | tests/integration/test_voice_continuity.py |
| `TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation` | tests/integration/test_cross_surface_handoff.py, tests/api/test_voice_api.py |
| `TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions` | tests/integration/test_voice_routing.py |
| `TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant` | tests/integration/test_voice_spoken_briefing.py, tests/api/test_voice_api.py |
| `TEST:Voice.Session.TranscriptBecomesStructuredSignal` | tests/integration/test_voice_transcript_normalization.py, tests/api/test_voice_api.py |
| `TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved` | tests/integration/test_telegram_companion.py, tests/integration/test_cross_surface_handoff.py, tests/integration/test_voice_routing.py |
