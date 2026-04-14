namespace ResearchAgent.Models;

/// <summary>
/// HTTP POST request body for <c>POST /api/chat</c>.
/// Sends a prompt to Gemini in the specified mode and returns the
/// response synchronously. Unlike <see cref="ResearchRequest"/>, which
/// is fire-and-forget via Deep Research, this is a blocking call.
/// </summary>
public class ChatRequest
{
    /// <summary>
    /// The prompt to send to Gemini.
    /// </summary>
    public required string Prompt { get; init; }

    /// <summary>
    /// Gemini mode to use. Valid values: "Fast", "Thinking", "Pro".
    /// Default: "Pro".
    /// </summary>
    public string Mode { get; init; } = "Pro";
}

