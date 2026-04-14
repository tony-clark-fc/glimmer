# Glimmer — Verification Evidence: smoke

**Pack:** `smoke`
**Executed:** 2026-04-13 22:26 UTC
**Environment:** Local development (macOS)

## Summary

| Metric | Count |
|---|---|
| Total | 5 |
| Passed | 5 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| **Verdict** | **✅ PASS** |

## Test Results

| Status | Class | Test | Time |
|---|---|---|---|
| ✅ PASSED | `tests.api.test_smoke` | `test_backend_starts` | 0.073s |
| ✅ PASSED | `tests.api.test_smoke` | `test_database_connectivity` | 0.009s |
| ✅ PASSED | `tests.api.test_smoke` | `test_database_session_works` | 0.019s |
| ✅ PASSED | `tests.api.test_smoke` | `test_local_first_defaults_resolve` | 0.000s |
| ✅ PASSED | `tests.api.test_smoke` | `test_backend_package_structure_exists` | 0.000s |

## Manual / Deferred Scenarios

| Anchor | Status | Reason |
|---|---|---|
| `TEST:Smoke.FrontendStarts` | ManualOnly | Requires running Next.js dev server + Playwright; not included in pytest suite |
| `TEST:Smoke.WorkspaceNavigationBasic` | ManualOnly | Requires running Next.js dev server + Playwright; separate npx playwright test execution |
| `TEST:Connector.GoogleMail.LiveOAuth` | Deferred | Requires real Google OAuth credentials and app registration |
| `TEST:Connector.MicrosoftMail.LiveOAuth` | Deferred | Requires real Microsoft app registration and Graph API credentials |
| `TEST:Telegram.LiveBotInteraction` | Deferred | Requires provisioned Telegram bot token and webhook setup |
| `TEST:Voice.RealAudioPipeline` | Deferred | Requires MLX runtime, Gemma 4 models, and real audio hardware on M5 Max |
