namespace ResearchAgent.Models;

/// <summary>
/// Response DTO for the <c>GET /api/status</c> endpoint.
/// Reports the agent's operational state so consumers (e.g., QuestResearch's
/// ResearchBacklogWorker) can determine when to submit new requests.
/// ARCH:ResearchAgentStatusAPI
/// </summary>
public class StatusResponse
{
    /// <summary>"Busy" if a research or chat operation is active, "Idle" otherwise.</summary>
    public required string Status { get; init; }

    /// <summary>Number of jobs waiting in the internal queue.</summary>
    public int QueueDepth { get; init; }

    /// <summary>Research jobs completed today (UTC).</summary>
    public int TodayCompletions { get; init; }

    /// <summary>Configured maximum completions per day.</summary>
    public int DailyRateLimit { get; init; }

    /// <summary>Whether the daily rate limit has been reached.</summary>
    public bool IsRateLimited { get; init; }

    /// <summary>ID of the currently executing job, or null when idle.</summary>
    public Guid? CurrentJobId { get; init; }

    /// <summary>Document name of the currently executing job, or null when idle.</summary>
    public string? CurrentDocumentName { get; init; }
}

