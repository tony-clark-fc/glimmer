using System.Collections.Concurrent;
using System.Threading.Channels;
using ResearchAgent.Models;

namespace ResearchAgent.Services;

/// <summary>
/// In-memory job registry and queue for research requests.
/// Jobs are tracked in a ConcurrentDictionary for status polling and
/// dispatched to the <see cref="ResearchJobWorker"/> via a bounded Channel.
///
/// Not persisted — all state is lost on API restart. The consumer's primary
/// delivery mechanism is monitoring Google Drive, not this API.
/// </summary>
public class ResearchJobTracker
{
    private readonly ConcurrentDictionary<Guid, ResearchJob> _jobs = new();
    private readonly Channel<ResearchJob> _channel =
        Channel.CreateBounded<ResearchJob>(new BoundedChannelOptions(100)
        {
            FullMode = BoundedChannelFullMode.Wait
        });

    // ── Rate limiting (daily, UTC) ──
    private int _dailyCompletions;
    private DateOnly _currentDay = DateOnly.FromDateTime(DateTime.UtcNow);
    private readonly object _rateLock = new();

    // ── Current job tracking ──
    private volatile ResearchJob? _currentJob;

    /// <summary>Channel reader consumed by <see cref="ResearchJobWorker"/>.</summary>
    public ChannelReader<ResearchJob> Reader => _channel.Reader;

    /// <summary>
    /// The job currently being processed, or null if idle.
    /// Set by <see cref="ResearchJobWorker"/> at job start/end.
    /// </summary>
    public ResearchJob? CurrentJob => _currentJob;

    /// <summary>Set the currently executing job. Call with null when job completes.</summary>
    public void SetCurrentJob(ResearchJob? job) => _currentJob = job;

    /// <summary>Number of jobs completed today (UTC).</summary>
    public int TodayCompletions
    {
        get
        {
            lock (_rateLock)
            {
                ResetDayIfNeeded();
                return _dailyCompletions;
            }
        }
    }

    /// <summary>Number of jobs currently in the queue.</summary>
    public int QueueDepth => _channel.Reader.Count;

    /// <summary>
    /// Enqueue a new research job. Returns the job with its assigned ID.
    /// </summary>
    public ResearchJob Enqueue(ResearchRequest request)
    {
        var job = new ResearchJob
        {
            Prompt = request.Prompt,
            DocumentName = request.DocumentName
        };

        _jobs[job.Id] = job;

        if (!_channel.Writer.TryWrite(job))
        {
            job.Status = JobStatus.Failed;
            job.ErrorMessage = "Job queue is full — try again later";
        }

        return job;
    }

    /// <summary>Get job by ID. Returns null if not found.</summary>
    public ResearchJob? GetJob(Guid id) =>
        _jobs.GetValueOrDefault(id);

    /// <summary>
    /// Check whether the daily rate limit has been reached.
    /// </summary>
    public bool IsRateLimited(int dailyLimit)
    {
        if (dailyLimit <= 0) return false;

        lock (_rateLock)
        {
            ResetDayIfNeeded();
            return _dailyCompletions >= dailyLimit;
        }
    }

    /// <summary>
    /// Record a completed job for rate limiting purposes.
    /// </summary>
    public void RecordCompletion()
    {
        lock (_rateLock)
        {
            ResetDayIfNeeded();
            _dailyCompletions++;
        }
    }

    private void ResetDayIfNeeded()
    {
        var today = DateOnly.FromDateTime(DateTime.UtcNow);
        if (today != _currentDay)
        {
            _currentDay = today;
            _dailyCompletions = 0;
        }
    }
}

