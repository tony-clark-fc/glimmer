using Microsoft.Extensions.Options;
using ResearchAgent.Models;

namespace ResearchAgent.Services;

/// <summary>
/// Background service that processes research jobs sequentially from the
/// <see cref="ResearchJobTracker"/> queue.
///
/// Only one job runs at a time — Gemini Deep Research is single-session
/// per Google account. Jobs are consumed from a Channel in FIFO order.
///
/// Rate limiting is enforced per calendar day (UTC). When the limit is
/// reached, queued jobs are deferred (status = RateLimited) and checked
/// again the next day.
/// </summary>
public class ResearchJobWorker : BackgroundService
{
    private readonly ResearchJobTracker _tracker;
    private readonly GeminiAutomationService _gemini;
    private readonly ResearchAgentOptions _options;
    private readonly ILogger<ResearchJobWorker> _logger;

    public ResearchJobWorker(
        ResearchJobTracker tracker,
        GeminiAutomationService gemini,
        IOptions<ResearchAgentOptions> options,
        ILogger<ResearchJobWorker> logger)
    {
        _tracker = tracker;
        _gemini = gemini;
        _options = options.Value;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation(
            "ResearchJobWorker started — processing jobs sequentially " +
            "(rate limit: {Limit}/day, timeout: {Timeout} min)",
            _options.DailyRateLimit, _options.ResearchTimeoutMinutes);

        await foreach (var job in _tracker.Reader.ReadAllAsync(stoppingToken))
        {
            // ── Rate limit check ──
            if (_tracker.IsRateLimited(_options.DailyRateLimit))
            {
                job.Status = JobStatus.RateLimited;
                job.ErrorMessage =
                    $"Daily rate limit reached ({_options.DailyRateLimit}/day). " +
                    $"Completed today: {_tracker.TodayCompletions}. " +
                    "Job will not be retried — resubmit tomorrow.";
                job.CompletedAt = DateTimeOffset.UtcNow;

                _logger.LogWarning(
                    "[{JobId}] Rate limited — {Completions}/{Limit} today",
                    job.Id, _tracker.TodayCompletions, _options.DailyRateLimit);
                continue;
            }

            // ── Process the job ──
            job.Status = JobStatus.Running;
            job.StartedAt = DateTimeOffset.UtcNow;
            _tracker.SetCurrentJob(job);

            _logger.LogInformation(
                "[{JobId}] Processing research job for '{DocName}' " +
                "(queue depth: {Depth}, today: {Today}/{Limit})",
                job.Id, job.DocumentName, _tracker.QueueDepth,
                _tracker.TodayCompletions, _options.DailyRateLimit);

            try
            {
                var result = await _gemini.ExecuteResearchAsync(job, stoppingToken);

                job.DocumentUrl = result.DocumentUrl;
                job.DocumentRenamed = result.DocumentRenamed;
                job.Status = result.DocumentRenamed
                    ? JobStatus.Completed
                    : JobStatus.CompletedWithWarning;

                _tracker.RecordCompletion();

                _logger.LogInformation(
                    "[{JobId}] Research complete — status: {Status}, url: {Url}",
                    job.Id, job.Status, job.DocumentUrl);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                job.Status = JobStatus.Failed;
                job.ErrorMessage = "API shutdown — job cancelled";
                _logger.LogWarning("[{JobId}] Job cancelled due to shutdown", job.Id);
                break;
            }
            catch (Exception ex)
            {
                job.Status = JobStatus.Failed;
                job.ErrorMessage = ex.Message;
                _logger.LogError(ex, "[{JobId}] Research job failed", job.Id);
            }
            finally
            {
                job.CompletedAt = DateTimeOffset.UtcNow;
                _tracker.SetCurrentJob(null);
            }

            // ── Inter-job delay ──
            if (_options.InterJobDelaySeconds > 0 &&
                !stoppingToken.IsCancellationRequested)
            {
                _logger.LogDebug("Inter-job delay: {Seconds}s",
                    _options.InterJobDelaySeconds);
                await Task.Delay(
                    _options.InterJobDelaySeconds * 1_000,
                    stoppingToken);
            }
        }

        _logger.LogInformation("ResearchJobWorker stopped");
    }
}

