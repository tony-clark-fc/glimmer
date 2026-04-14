namespace ResearchAgent.Models;

/// <summary>
/// HTTP response body returned by research API endpoints.
/// </summary>
public class ResearchResponse
{
    public required Guid JobId { get; init; }
    public required string Status { get; init; }
    public string? Message { get; init; }
    public string? DocumentUrl { get; init; }
    public DateTimeOffset? QueuedAt { get; init; }
    public DateTimeOffset? StartedAt { get; init; }
    public DateTimeOffset? CompletedAt { get; init; }
}

