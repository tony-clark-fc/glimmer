# Glimmer — Verification Evidence: release

**Pack:** `release`
**Executed:** 2026-04-13 22:25 UTC
**Environment:** Local development (macOS)

## Summary

| Metric | Count |
|---|---|
| Total | 139 |
| Passed | 139 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| **Verdict** | **✅ PASS** |

## Test Results

| Status | Class | Test | Time |
|---|---|---|---|
| ✅ PASSED | `tests.api.test_projects_drafts.TestProjectsList` | `test_list_projects_empty` | 0.093s |
| ✅ PASSED | `tests.api.test_projects_drafts.TestProjectsList` | `test_list_projects_with_data` | 0.064s |
| ✅ PASSED | `tests.api.test_projects_drafts.TestProjectDetail` | `test_get_project_detail` | 0.031s |
| ✅ PASSED | `tests.api.test_projects_drafts.TestProjectDetail` | `test_get_project_not_found` | 0.015s |
| ✅ PASSED | `tests.api.test_projects_drafts.TestDraftsList` | `test_list_drafts_empty` | 0.015s |
| ✅ PASSED | `tests.api.test_projects_drafts.TestDraftsList` | `test_list_drafts_with_data` | 0.017s |
| ✅ PASSED | `tests.api.test_projects_drafts.TestDraftDetail` | `test_get_draft_with_variants` | 0.021s |
| ✅ PASSED | `tests.api.test_projects_drafts.TestDraftDetail` | `test_get_draft_not_found` | 0.011s |
| ✅ PASSED | `tests.api.test_projects_drafts.TestNoAutoSendBoundary` | `test_no_send_endpoint_exists` | 0.014s |
| ✅ PASSED | `tests.api.test_smoke` | `test_backend_starts` | 0.008s |
| ✅ PASSED | `tests.api.test_smoke` | `test_database_connectivity` | 0.009s |
| ✅ PASSED | `tests.api.test_smoke` | `test_database_session_works` | 0.023s |
| ✅ PASSED | `tests.api.test_smoke` | `test_local_first_defaults_resolve` | 0.000s |
| ✅ PASSED | `tests.api.test_smoke` | `test_backend_package_structure_exists` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestProviderBoundaryIsolation` | `test_all_connectors_inherit_from_base` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestProviderBoundaryIsolation` | `test_connectors_expose_provider_type` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestProviderBoundaryIsolation` | `test_connectors_expose_connector_type` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestProviderBoundaryIsolation` | `test_connectors_expose_supported_profile_types` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestProviderBoundaryIsolation` | `test_provider_directories_are_separate` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestProviderBoundaryIsolation` | `test_contracts_are_framework_level_not_provider_specific` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestProviderBoundaryIsolation` | `test_base_connector_abc_has_required_interface` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestReadFirstNoAutoSend` | `test_base_connector_has_no_send_methods` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestReadFirstNoAutoSend` | `test_connectors_have_no_send_methods` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_framework.TestReadFirstNoAutoSend` | `test_fetch_result_is_read_only_shape` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_preserves_gmail_message_id` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_preserves_thread_id` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_source_type_is_gmail` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_preserves_subject` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_preserves_sender` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_preserves_recipients` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_extracts_body_text` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_preserves_account_label_in_metadata` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_preserves_gmail_labels` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_message_parses_received_at` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_thread_preserves_thread_id` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_thread_source_type_is_gmail` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_thread_derives_subject` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_thread_collects_participants` | 0.000s |
| ✅ PASSED | `tests.integration.test_connector_gmail.TestGmailNormalization` | `test_thread_has_last_activity` | 0.000s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestVoiceHandoff` | `test_handoff_creates_artifact` | 0.006s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestVoiceHandoff` | `test_handoff_preserves_context` | 0.001s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestVoiceHandoff` | `test_handoff_updates_channel_session` | 0.002s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestVoiceHandoff` | `test_handoff_to_dict_serializable` | 0.001s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestTelegramHandoff` | `test_telegram_handoff_creates_artifact` | 0.003s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestTelegramHandoff` | `test_telegram_handoff_preserves_context` | 0.001s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestTelegramHandoff` | `test_telegram_handoff_updates_channel_session` | 0.002s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestPendingHandoffs` | `test_pending_handoffs_empty` | 0.001s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestPendingHandoffs` | `test_pending_handoffs_returns_voice_handoff` | 0.002s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestPendingHandoffs` | `test_pending_handoffs_returns_telegram_handoff` | 0.002s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestPendingHandoffs` | `test_pending_handoffs_mixed_channels` | 0.002s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestSafetyParity` | `test_auto_send_blocked_verification_passes` | 0.000s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestSafetyParity` | `test_auto_send_blocked_verification_fails_when_missing` | 0.000s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestSafetyParity` | `test_auto_send_blocked_verification_fails_when_false` | 0.000s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestSafetyParity` | `test_review_gate_preserved_when_path_exists` | 0.000s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestSafetyParity` | `test_review_gate_fails_when_no_path` | 0.000s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestSafetyParity` | `test_review_gate_ok_when_no_review_needed` | 0.000s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestSafetyParity` | `test_voice_handoff_always_blocks_auto_send` | 0.001s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestSafetyParity` | `test_telegram_handoff_always_blocks_auto_send` | 0.001s |
| ✅ PASSED | `tests.integration.test_cross_surface_handoff.TestSafetyParity` | `test_all_handoff_records_block_auto_send` | 0.002s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestSourceLayerDistinctness` | `test_message_and_thread_remain_separate` | 0.004s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestSourceLayerDistinctness` | `test_event_is_distinct_from_message` | 0.002s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestSourceLayerDistinctness` | `test_signal_preserves_origin_channel` | 0.001s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestAcceptedStatePromotion` | `test_classification_retains_review_state` | 0.003s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestAcceptedStatePromotion` | `test_extracted_action_retains_source_message` | 0.002s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestSummarySupersession` | `test_briefing_artifacts_accumulate` | 0.002s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestSummarySupersession` | `test_focus_packs_accumulate` | 0.002s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestMultiAccountProvenance` | `test_messages_from_different_accounts_stay_distinct` | 0.002s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestGlobalAutoSendBoundary` | `test_handoff_artifacts_always_block_auto_send` | 0.001s |
| ✅ PASSED | `tests.integration.test_data_integrity_pack.TestGlobalAutoSendBoundary` | `test_channel_sessions_do_not_bypass_review` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_audit.TestAuditMeaningfulStateMutation` | `test_audit_record_persists` | 0.002s |
| ✅ PASSED | `tests.integration.test_domain_audit.TestAuditMeaningfulStateMutation` | `test_audit_records_state_change` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_audit.TestAuditMeaningfulStateMutation` | `test_audit_promotion_from_interpreted_to_accepted` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_audit.TestAuditMeaningfulStateMutation` | `test_audit_by_system_actor` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_audit.TestAuditMeaningfulStateMutation` | `test_multiple_audits_for_same_entity` | 0.002s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestProjectLifecycle` | `test_create_project_persists` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestProjectLifecycle` | `test_project_fields_persist` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestProjectLifecycle` | `test_project_update_changes_updated_at` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestProjectLifecycle` | `test_project_archive` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestProjectLifecycle` | `test_multiple_projects_persist` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestWorkstreamPersistence` | `test_workstream_belongs_to_project` | 0.002s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestWorkstreamPersistence` | `test_project_has_many_workstreams` | 0.003s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestWorkstreamPersistence` | `test_workstream_fields_persist` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestMilestonePersistence` | `test_milestone_belongs_to_project` | 0.002s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestMilestonePersistence` | `test_project_has_many_milestones` | 0.002s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestMilestonePersistence` | `test_milestone_completion` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_portfolio.TestMilestonePersistence` | `test_milestone_fields_persist` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestConnectedAccountProvenance` | `test_create_google_account` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestConnectedAccountProvenance` | `test_create_microsoft_account` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestConnectedAccountProvenance` | `test_multiple_accounts_coexist` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestConnectedAccountProvenance` | `test_account_profile_links_to_account` | 0.003s |
| ✅ PASSED | `tests.integration.test_domain_source.TestConnectedAccountProvenance` | `test_message_preserves_account_provenance` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestConnectedAccountProvenance` | `test_event_preserves_account_provenance` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestSourceRecordsSeparation` | `test_thread_persists_independently` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestSourceRecordsSeparation` | `test_message_links_to_thread` | 0.002s |
| ✅ PASSED | `tests.integration.test_domain_source.TestSourceRecordsSeparation` | `test_message_exists_without_thread` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestSourceRecordsSeparation` | `test_calendar_event_persists_separately` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestSourceRecordsSeparation` | `test_imported_signal_persists_separately` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestSourceRecordsSeparation` | `test_imported_signal_without_account` | 0.001s |
| ✅ PASSED | `tests.integration.test_domain_source.TestSourceRecordsSeparation` | `test_message_full_provenance_chain` | 0.002s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestFocusPackGeneration` | `test_empty_state_produces_empty_focus_pack` | 0.004s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestFocusPackGeneration` | `test_work_items_appear_in_focus_pack` | 0.002s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestFocusPackGeneration` | `test_overdue_item_scores_highest` | 0.002s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestFocusPackGeneration` | `test_priority_items_have_rationale` | 0.002s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestFocusPackGeneration` | `test_pending_actions_included` | 0.002s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestFocusPackPersistence` | `test_focus_pack_persists` | 0.002s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestFocusPackPersistence` | `test_risk_items_included` | 0.002s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestFocusPackPersistence` | `test_waiting_on_included` | 0.002s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestFocusPackPersistence` | `test_project_filter_works` | 0.003s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestPriorityScoring` | `test_score_work_item_baseline` | 0.001s |
| ✅ PASSED | `tests.integration.test_planner_focus.TestPriorityScoring` | `test_score_pending_action_with_urgency` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestProjectClassificationStrongMatch` | `test_strong_name_match` | 0.001s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestProjectClassificationStrongMatch` | `test_no_projects_returns_no_match` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestProjectClassificationStrongMatch` | `test_no_matching_content_needs_review` | 0.001s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestProjectClassificationStrongMatch` | `test_classification_persists` | 0.002s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestProjectClassificationAmbiguous` | `test_ambiguous_multiple_matches_needs_review` | 0.001s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestProjectClassificationAmbiguous` | `test_ambiguous_classification_persists_as_pending` | 0.001s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestStakeholderResolution` | `test_single_match_resolves_cleanly` | 0.002s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestStakeholderResolution` | `test_unknown_sender_returns_empty` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestStakeholderResolution` | `test_multiple_matches_needs_review` | 0.001s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestStakeholderResolution` | `test_named_email_resolves` | 0.001s |
| ✅ PASSED | `tests.integration.test_triage_classification.TestStakeholderResolution` | `test_no_sender_returns_empty` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_intake.TestIntakeRouting` | `test_gmail_message_routes_to_triage` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_intake.TestIntakeRouting` | `test_microsoft_message_routes_to_triage` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_intake.TestIntakeRouting` | `test_calendar_event_routes_to_triage` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_intake.TestIntakeRouting` | `test_imported_signal_routes_to_triage` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_intake.TestIntakeRouting` | `test_routing_assigns_workflow_id` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_intake.TestIntakeRouting` | `test_routing_assigns_timestamp` | 0.000s |
| ✅ PASSED | `tests.integration.test_triage_intake.TestIntakeRouting` | `test_compiled_graph_executes` | 0.002s |
| ✅ PASSED | `tests.integration.test_triage_intake.TestIntakeRouting` | `test_unknown_record_type_defaults_to_triage` | 0.000s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceSessionGraph` | `test_graph_compiles` | 0.001s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceSessionGraph` | `test_graph_executes_bootstrap_to_end` | 0.002s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceSessionGraph` | `test_bootstrap_sets_safety_invariants` | 0.000s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceSessionGraph` | `test_route_to_core_with_no_signals` | 0.000s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceSessionGraph` | `test_route_to_core_with_signals` | 0.000s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceSessionGraph` | `test_check_review_returns_complete_when_no_review` | 0.000s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceSessionGraph` | `test_check_review_returns_review_needed` | 0.000s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceSessionGraph` | `test_graph_with_review_interrupt` | 0.002s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceRouting` | `test_voice_routes_through_intake_graph` | 0.002s |
| ✅ PASSED | `tests.integration.test_voice_routing.TestVoiceRouting` | `test_voice_routing_always_blocks_auto_send` | 0.002s |

## Manual / Deferred Scenarios

| Anchor | Status | Reason |
|---|---|---|
| `TEST:Smoke.FrontendStarts` | ManualOnly | Requires running Next.js dev server + Playwright; not included in pytest suite |
| `TEST:Smoke.WorkspaceNavigationBasic` | ManualOnly | Requires running Next.js dev server + Playwright; separate npx playwright test execution |
| `TEST:Connector.GoogleMail.LiveOAuth` | Deferred | Requires real Google OAuth credentials and app registration |
| `TEST:Connector.MicrosoftMail.LiveOAuth` | Deferred | Requires real Microsoft app registration and Graph API credentials |
| `TEST:Telegram.LiveBotInteraction` | Deferred | Requires provisioned Telegram bot token and webhook setup |
| `TEST:Voice.RealAudioPipeline` | Deferred | Requires MLX runtime, Gemma 4 models, and real audio hardware on M5 Max |
