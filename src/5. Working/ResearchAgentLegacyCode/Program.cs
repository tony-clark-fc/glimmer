using Microsoft.Extensions.Options;
using ResearchAgent.Models;
using ResearchAgent.Services;

var builder = WebApplication.CreateBuilder(args);

// ── Kestrel on port 5060 (separate from QuestResearch on :5050) ──
builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenLocalhost(5060);
});

// ── Strongly-typed options ──
builder.Services.Configure<ResearchAgentOptions>(
    builder.Configuration.GetSection(ResearchAgentOptions.SectionName));
builder.Services.Configure<ChromeOptions>(
    builder.Configuration.GetSection(ChromeOptions.SectionName));

// ── Services ──
builder.Services.AddSingleton<ChromeBrowserProvider>();
builder.Services.AddSingleton<GeminiAutomationService>();
builder.Services.AddSingleton<ResearchJobTracker>();
builder.Services.AddHostedService<ResearchJobWorker>();

var app = builder.Build();

// ═══════════════════════════════════════════════════════════════════════
// Endpoints
// ═══════════════════════════════════════════════════════════════════════

// POST /api/research — Fire-and-forget: submit a research job.
// Returns 202 Accepted with a job ID. Consumer monitors Google Drive
// for the completed document (named per the request).
app.MapPost("/api/research", (ResearchRequest request, ResearchJobTracker tracker) =>
{
    if (string.IsNullOrWhiteSpace(request.Prompt))
        return Results.BadRequest(new { Error = "Prompt is required" });

    if (string.IsNullOrWhiteSpace(request.DocumentName))
        return Results.BadRequest(new { Error = "DocumentName is required" });

    var job = tracker.Enqueue(request);

    return Results.Accepted($"/api/research/{job.Id}", new ResearchResponse
    {
        JobId = job.Id,
        Status = job.Status,
        Message = "Research job queued",
        QueuedAt = job.QueuedAt
    });
});

// GET /api/research/{id} — Poll job status (diagnostic, not primary delivery).
// The consumer's primary mechanism is monitoring Google Drive.
app.MapGet("/api/research/{id:guid}", (Guid id, ResearchJobTracker tracker) =>
{
    var job = tracker.GetJob(id);
    if (job is null)
        return Results.NotFound(new { Error = "Job not found" });

    return Results.Ok(new ResearchResponse
    {
        JobId = job.Id,
        Status = job.Status,
        Message = job.ErrorMessage,
        DocumentUrl = job.DocumentUrl,
        QueuedAt = job.QueuedAt,
        StartedAt = job.StartedAt,
        CompletedAt = job.CompletedAt
    });
});

// GET /api/status — Operational status: Busy/Idle, queue depth, rate limit.
// Primary endpoint for QuestResearch's ResearchBacklogWorker to determine
// when the agent is ready to accept a new request. ARCH:ResearchAgentStatusAPI
app.MapGet("/api/status", (
    GeminiAutomationService gemini,
    ResearchJobTracker tracker,
    IOptions<ResearchAgentOptions> options) =>
{
    var opts = options.Value;
    var currentJob = tracker.CurrentJob;

    return Results.Ok(new StatusResponse
    {
        Status = gemini.IsBusy ? "Busy" : "Idle",
        QueueDepth = tracker.QueueDepth,
        TodayCompletions = tracker.TodayCompletions,
        DailyRateLimit = opts.DailyRateLimit,
        IsRateLimited = tracker.IsRateLimited(opts.DailyRateLimit),
        CurrentJobId = currentJob?.Id,
        CurrentDocumentName = currentJob?.DocumentName
    });
});

// GET /health — Health check: Chrome connectivity + queue status.
app.MapGet("/health", (ChromeBrowserProvider chrome, ResearchJobTracker tracker) =>
{
    return Results.Ok(new
    {
        Status = "Healthy",
        Chrome = new
        {
            PortOpen = chrome.IsChromePortOpen,
            Connected = chrome.IsAvailable
        },
        Queue = new
        {
            Depth = tracker.QueueDepth,
            TodayCompletions = tracker.TodayCompletions
        }
    });
});

// POST /api/chat — Synchronous: send a prompt to Gemini and return the response.
// Blocks until Gemini finishes responding (seconds to minutes depending on mode).
// Only one Gemini operation at a time — returns 409 if another op is in progress.
app.MapPost("/api/chat", async (
    ChatRequest request,
    GeminiAutomationService gemini,
    CancellationToken ct) =>
{
    if (string.IsNullOrWhiteSpace(request.Prompt))
        return Results.BadRequest(new { Error = "Prompt is required" });

    if (!ResearchAgentOptions.ValidModes.Contains(
            request.Mode, StringComparer.OrdinalIgnoreCase))
    {
        return Results.BadRequest(new
        {
            Error = $"Invalid mode '{request.Mode}'. " +
                    $"Valid modes: {string.Join(", ", ResearchAgentOptions.ValidModes)}"
        });
    }

    try
    {
        var result = await gemini.ExecuteChatAsync(request, ct);
        return Results.Ok(result);
    }
    catch (InvalidOperationException ex) when (
        ex.Message.Contains("Another Gemini operation"))
    {
        return Results.Conflict(new
        {
            Error = ex.Message
        });
    }
    catch (TimeoutException)
    {
        return Results.StatusCode(504); // Gateway Timeout
    }
});

app.Run();

