namespace ResearchAgent.Models;

/// <summary>
/// Internal job state tracked in memory by <see cref="Services.ResearchJobTracker"/>.
/// Not persisted — lost on API restart. The consumer's primary delivery
/// mechanism is monitoring Google Drive, not polling job status.
/// </summary>
public class ResearchJob
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public required string Prompt { get; init; }
    public required string DocumentName { get; init; }

    public string Status { get; set; } = JobStatus.Queued;
    public string? DocumentUrl { get; set; }
    public bool DocumentRenamed { get; set; }
    public string? ErrorMessage { get; set; }

    public DateTimeOffset QueuedAt { get; init; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? StartedAt { get; set; }
    public DateTimeOffset? CompletedAt { get; set; }
}

/// <summary>
/// Job status constants.
/// </summary>
public static class JobStatus
{
    public const string Queued = "Queued";
    public const string Running = "Running";
    public const string Completed = "Completed";
    public const string CompletedWithWarning = "CompletedWithWarning";
    public const string Failed = "Failed";
    public const string RateLimited = "RateLimited";
}

