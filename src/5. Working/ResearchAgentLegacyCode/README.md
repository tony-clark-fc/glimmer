# ResearchAgent

A lightweight ASP.NET Core Minimal API that drives **Google Gemini** via browser automation (Playwright over CDP).  
It exposes two HTTP endpoints — one for **synchronous chat** and one for **fire-and-forget deep research** — making Gemini accessible as a service to any consumer that can send an HTTP POST.

> **Port:** `http://localhost:5060`  
> **Runtime:** .NET 10 · Playwright · Chrome via CDP  
> **Chrome profile:** Shared with QuestResearch — see [`CHROME_PROFILE_SETUP_GUIDE.md`](../CHROME_PROFILE_SETUP_GUIDE.md)

---

## Table of Contents

- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [POST /api/chat](#post-apichat) — Synchronous chat
  - [POST /api/research](#post-apiresearch) — Fire-and-forget deep research
  - [GET /api/research/{id}](#get-apiresearchid) — Poll job status
  - [GET /health](#get-health) — Health check
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Concurrency & Rate Limiting](#concurrency--rate-limiting)
- [Human Pacing](#human-pacing)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Start Chrome with remote debugging

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
    --remote-debugging-port=9222 `
    --user-data-dir="C:\PlaywrightProfiles\Gemini" `
    --profile-directory=Default `
    --no-first-run --no-default-browser-check
```

> The Chrome profile must be signed into a Google account with **Gemini Pro** access.  
> See [`CHROME_PROFILE_SETUP_GUIDE.md`](../CHROME_PROFILE_SETUP_GUIDE.md) for first-time setup.

### 2. Run the API

```powershell
cd ResearchAgent
dotnet run
```

### 3. Send a request

```powershell
# Synchronous chat — returns the response text
$body = '{"Prompt":"What is the capital of France?","Mode":"Fast"}'
Invoke-RestMethod -Uri http://localhost:5060/api/chat `
    -Method Post -Body $body -ContentType "application/json"

# Deep research — fire-and-forget, document appears in Google Drive
$body = '{"Prompt":"Research soil carbon benchmarks...","DocumentName":"SOC-Research-20260324"}'
Invoke-RestMethod -Uri http://localhost:5060/api/research `
    -Method Post -Body $body -ContentType "application/json"
```

---

## API Reference

### POST /api/chat

**Synchronous Gemini chat.** Sends a prompt, waits for the response, and returns the text.

#### Request

```http
POST /api/chat
Content-Type: application/json
```

```json
{
  "Prompt": "What is the capital of Australia? Reply in one sentence.",
  "Mode": "Fast"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `Prompt` | string | ✅ | — | The prompt to send to Gemini |
| `Mode` | string | — | `"Pro"` | Gemini mode: `"Fast"`, `"Thinking"`, or `"Pro"` |

#### Response — `200 OK`

```json
{
  "responseText": "The capital of Australia is Canberra.",
  "mode": "Fast",
  "durationMs": 21604
}
```

| Field | Type | Description |
|-------|------|-------------|
| `responseText` | string | Full text of Gemini's response |
| `mode` | string | The Gemini mode that was used |
| `durationMs` | number | Wall-clock duration in milliseconds (includes human pacing delays) |

#### Error Responses

| Status | Condition |
|--------|-----------|
| `400 Bad Request` | Missing `Prompt` or invalid `Mode` |
| `409 Conflict` | Another Gemini operation is already in progress |
| `504 Gateway Timeout` | Gemini did not respond within `ChatResponseTimeoutSeconds` |
| `500 Internal Server Error` | Chrome not available, selector mismatch, or other automation failure |

#### How It Works

1. **Navigate** to `gemini.google.com/app`
2. **Expand sidebar** → click **New Chat** (ensures clean conversation)
3. **Select mode** from the mode picker dropdown (skips if already correct)
4. **Enter prompt** into the input textbox
5. **Send** the prompt
6. **Wait** for the copy button to appear (signals response is complete)
7. **Click "Copy response"** and read the clipboard text
8. **Return** the response to the caller
9. **Close** the browser tab

---

### POST /api/research

**Fire-and-forget Gemini Deep Research.** Queues a research job that drives Gemini's Deep Research mode to produce a comprehensive research document, exports it to Google Docs, and renames it. The consumer monitors Google Drive for the completed document.

#### Request

```http
POST /api/research
Content-Type: application/json
```

```json
{
  "Prompt": "Research and compile ecological benchmarks for soil organic carbon in Australian tropical grasslands under livestock grazing...",
  "DocumentName": "AUS-TGP-LVG-SOC-20260324"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Prompt` | string | ✅ | The full research brief to send to Gemini Deep Research |
| `DocumentName` | string | ✅ | Desired filename for the Google Doc (the API renames the exported doc) |

#### Response — `202 Accepted`

```json
{
  "jobId": "3a529b19-989c-45e9-9aae-fa8c7e8b7d4f",
  "status": "Queued",
  "message": "Research job queued",
  "documentUrl": null,
  "queuedAt": "2026-03-24T03:15:00Z",
  "startedAt": null,
  "completedAt": null
}
```

#### Error Responses

| Status | Condition |
|--------|-----------|
| `400 Bad Request` | Missing `Prompt` or `DocumentName` |

#### How It Works

1. Job is **queued** and a `202 Accepted` is returned immediately
2. The background worker picks up the job (FIFO, one at a time)
3. **Navigate** to Gemini → enter prompt → open **Tools** → click **Deep Research**
4. **Click "Start research"** when the plan appears
5. **Wait** for research to complete (5–60 minutes)
6. **Export** to Google Docs via "Export to Docs"
7. **Rename** the document to the requested `DocumentName`
8. Job status updated to `Completed` (or `CompletedWithWarning` if rename failed)

#### Delivery Model

The API does **not** return the document content. Instead:

- The document is saved to **Google Drive** under the operator's account
- The consumer **monitors Google Drive** for a file matching the `DocumentName`
- The `GET /api/research/{id}` endpoint is available for diagnostics but is not the primary delivery mechanism

---

### GET /api/research/{id}

**Poll job status** (diagnostic). Returns the current state of a research job.

#### Response — `200 OK`

```json
{
  "jobId": "3a529b19-989c-45e9-9aae-fa8c7e8b7d4f",
  "status": "Completed",
  "message": null,
  "documentUrl": "https://docs.google.com/document/d/1WJApHg58m9...",
  "queuedAt": "2026-03-24T03:15:00Z",
  "startedAt": "2026-03-24T03:15:05Z",
  "completedAt": "2026-03-24T03:35:42Z"
}
```

| Status Value | Meaning |
|---|---|
| `Queued` | Waiting in the queue |
| `Running` | Currently executing in Chrome |
| `Completed` | Finished — document exported and renamed |
| `CompletedWithWarning` | Document exported but rename failed |
| `Failed` | Automation error (see `message`) |
| `RateLimited` | Daily rate limit reached — resubmit tomorrow |

---

### GET /health

**Health check.** Returns Chrome connectivity and queue status.

```json
{
  "status": "Healthy",
  "chrome": {
    "portOpen": true,
    "connected": true
  },
  "queue": {
    "depth": 0,
    "todayCompletions": 3
  }
}
```

---

## Configuration

All settings in `appsettings.json`:

### Chrome Section

| Key | Default | Description |
|-----|---------|-------------|
| `ExePath` | `C:\Program Files\...\chrome.exe` | Path to Chrome executable |
| `UserDataDir` | `C:\PlaywrightProfiles\Gemini` | Chrome user data directory (isolated profile) |
| `ProfileName` | `Default` | Chrome profile directory name |
| `GoogleAccount` | — | Google account email (logging only) |
| `RemoteDebuggingPort` | `9222` | CDP remote debugging port |
| `ConnectionTimeoutSeconds` | `30` | Max seconds to connect to Chrome via CDP |

### ResearchAgent Section

| Key | Default | Description |
|-----|---------|-------------|
| `ResearchTimeoutMinutes` | `60` | Max minutes for Deep Research to complete |
| `PlanTimeoutSeconds` | `240` | Max seconds for the research plan to appear |
| `DailyRateLimit` | `19` | Max research jobs per calendar day (UTC). `0` = no limit |
| `ExportSettleSeconds` | `15` | Seconds to wait after "Export to Docs" for Drive to save |
| `InterJobDelaySeconds` | `5` | Seconds between completing one research job and starting the next |
| `ChatResponseTimeoutSeconds` | `300` | Max seconds for a chat response (Fast/Thinking/Pro) |

---

## Architecture

```
ResearchAgent/
├── Program.cs                          Minimal API: endpoints + DI wiring
├── Models/
│   ├── ChatRequest.cs                  POST /api/chat request body
│   ├── ChatResult.cs                   Chat response DTO
│   ├── ResearchRequest.cs              POST /api/research request body
│   ├── ResearchResponse.cs             Research status DTO
│   ├── ResearchJob.cs                  Internal job state + status constants
│   ├── ResearchResult.cs               Automation result DTO
│   ├── ResearchAgentOptions.cs         Strongly-typed options (timeouts, limits)
│   └── ChromeOptions.cs                Chrome/CDP configuration
├── Services/
│   ├── ChromeBrowserProvider.cs        Singleton: Chrome auto-launch + CDP connection
│   ├── GeminiAutomationService.cs      Core automation: chat + deep research flows
│   ├── ResearchJobTracker.cs           In-memory job registry + Channel queue
│   └── ResearchJobWorker.cs            BackgroundService: sequential job processor
└── appsettings.json                    Configuration
```

### Key Design Decisions

- **Single Chrome instance** — both endpoints share one `ChromeBrowserProvider` (singleton)
- **Operation lock** — a `SemaphoreSlim(1,1)` ensures only one Gemini interaction at a time (chat or research)
- **Chat is synchronous** — the caller blocks until the response is ready
- **Research is async** — fire-and-forget via an in-memory job queue; delivery is via Google Drive
- **No persistence** — job state lives in memory; lost on restart. Google Drive is the durable artifact
- **Multi-strategy selectors** — every UI interaction has 3–4 fallback strategies to survive Google's frequent DOM changes

---

## Concurrency & Rate Limiting

| Constraint | Mechanism |
|---|---|
| One Gemini op at a time | `_operationLock` semaphore on `GeminiAutomationService` |
| Chat during research | Returns `409 Conflict` (won't block for 60 minutes) |
| Research during chat | Waits on the semaphore (chat completes in seconds) |
| Daily research limit | `DailyRateLimit` in config (default 19/day, resets at midnight UTC) |
| Chat rate limiting | Not rate-limited (short-lived, no known Gemini limit for standard chat) |

---

## Human Pacing

All browser interactions include **randomised delays** to simulate a real user:

| Pause Point | Delay Range | Purpose |
|---|---|---|
| After page load | 1.5–2.5s | User orienting on the page |
| After New Chat | 1.0–2.0s | Looking at the fresh chat |
| After mode selection | 1.0–2.0s | Mode UI settling |
| After pasting prompt | 1.5–3.0s | Reviewing before sending |
| After response appears | 2.0–4.0s | Reading before copying |

Delays are jittered via `Random.Shared.Next()` so no two interactions have the same cadence.

---

## Troubleshooting

### Chrome not connecting

```
Chrome is not available — ensure Chrome is running with --remote-debugging-port
```

**Fix:** Start Chrome with CDP enabled:
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
    --remote-debugging-port=9222 `
    --user-data-dir="C:\PlaywrightProfiles\Gemini" `
    --profile-directory=Default
```

### Sign-in required

```
Chrome profile is not signed into Google
```

**Fix:** Open Chrome manually, sign into the Google account, navigate to `gemini.google.com` and confirm Gemini Pro access works. Then restart ResearchAgent.

### Mode picker not found

```
Mode picker button not found — proceeding with current default mode
```

**Fix:** Google may have changed the Gemini UI. Check the `data-test-id="bard-mode-menu-button"` selector still exists. The chat will still work — it just uses whatever mode is currently active.

### Copy button timeout

```
Gemini did not finish responding within 300 seconds
```

**Fix:** Increase `ChatResponseTimeoutSeconds` in `appsettings.json`. "Thinking" and "Pro" modes can take 60–90+ seconds for complex prompts.

### 409 Conflict

```json
{ "error": "Another Gemini operation is in progress" }
```

**Fix:** Wait for the current operation to finish. Only one Gemini interaction at a time is supported (same Google account session).

### Diagnostic screenshots

On failure, screenshots are automatically saved to:
```
ResearchAgent/bin/Debug/net10.0/chat-failure_<guid>.png
ResearchAgent/bin/Debug/net10.0/failure_<guid>.png
```

Check these to see the exact Gemini UI state when something went wrong.

