namespace ResearchAgent.Models;

/// <summary>
/// Result returned by <see cref="Services.GeminiAutomationService.ExecuteChatAsync"/>
/// after a synchronous Gemini chat interaction completes.
/// </summary>
public class ChatResult
{
    /// <summary>
    /// The full text of Gemini's response, captured via the "Copy response" button.
    /// </summary>
    public required string ResponseText { get; init; }

    /// <summary>
    /// The Gemini mode that was actually used (Fast / Thinking / Pro).
    /// </summary>
    public required string Mode { get; init; }

    /// <summary>
    /// Wall-clock duration of the chat interaction in milliseconds
    /// (from prompt send to response capture).
    /// </summary>
    public required long DurationMs { get; init; }
}

