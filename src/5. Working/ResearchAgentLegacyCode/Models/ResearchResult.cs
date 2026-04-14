namespace ResearchAgent.Models;

/// <summary>
/// Result returned by <see cref="Services.GeminiAutomationService"/> after
/// a single Gemini Deep Research execution completes.
/// </summary>
public class ResearchResult
{
    /// <summary>
    /// URL of the Google Doc created by Gemini's "Export to Docs" action.
    /// </summary>
    public required string DocumentUrl { get; init; }

    /// <summary>
    /// Whether the document was successfully renamed to the requested name.
    /// False means the doc was created but the rename failed (still usable).
    /// </summary>
    public required bool DocumentRenamed { get; init; }
}

