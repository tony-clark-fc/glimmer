# Live Browser Tests

These tests require a **real Chrome instance** with an authenticated Gemini session.
They are classified as `ManualOnly` per the verification framework and are **never**
run as part of the automated test suite.

## Prerequisites

1. A Chrome user-data directory with an authenticated Google account that has Gemini access.
   The operator's profile is at: `/Users/tony/PlaywrightProfiles/Gemini`

2. Playwright installed: `pip install playwright && playwright install`

## Running

From the backend directory (`src/apps/backend`):

```bash
# Run all live browser tests (launches Chrome automatically):
pytest ../../tests/live/ -v -s

# Run only the connection/health smoke tests (no Gemini interaction):
pytest ../../tests/live/test_live_browser_connection.py -v -s

# Run the expert advice (chat) live test:
pytest ../../tests/live/test_live_expert_advice.py -v -s
```

The `-s` flag is important — it shows real-time logging from the adapter so you
can watch the browser interaction as it happens.

## What these tests prove

| Test file | TEST: anchor | What it proves |
|---|---|---|
| `test_live_browser_connection.py` | `TEST:Research.Failure.BrowserUnavailableHandledSafely` | Chrome launches, CDP connects, Gemini loads, user is signed in |
| `test_live_expert_advice.py` | `TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult`, `TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse` | Full expert advice round-trip through real Gemini |

## Notes

- These tests use the **real adapter** (not mocks) with a real Chrome instance.
- The expert advice test sends a trivial prompt to minimize cost/time.
- Deep Research is NOT tested here (5–60 minutes, consumes credits).
- Chrome is auto-launched if not already running on the CDP port.
- The tab is closed after each test; Chrome remains running.

