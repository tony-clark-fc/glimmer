namespace ResearchAgent.Models;

/// <summary>
/// HTTP POST request body for <c>POST /api/research</c>.
/// The consumer sends a fully-formed prompt and the desired Google Doc filename.
/// </summary>
public class ResearchRequest
{
    /// <summary>
    /// The complete research prompt to send to Gemini Deep Research.
    /// The API does not generate or modify this — prompt ownership belongs to the consumer.
    /// </summary>
    public required string Prompt { get; init; }

    /// <summary>
    /// Desired filename for the Google Doc created by Gemini Deep Research.
    /// The API will rename the exported doc to this name via Playwright.
    /// Example: "AUS-TGP-LVG-SOC-20260323"
    /// </summary>
    public required string DocumentName { get; init; }
}

