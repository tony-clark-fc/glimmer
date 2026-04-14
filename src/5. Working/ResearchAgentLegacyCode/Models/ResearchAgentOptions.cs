namespace ResearchAgent.Models;

/// <summary>
/// Configuration for the ResearchAgent API — timeouts, rate limits, and behavior.
/// Bound to the "ResearchAgent" section of appsettings.json.
/// </summary>
public class ResearchAgentOptions
{
    public const string SectionName = "ResearchAgent";

    /// <summary>
    /// Maximum minutes to wait for Gemini Deep Research to complete.
    /// Deep Research typically takes 5–30 minutes but can exceed 45.
    /// </summary>
    public int ResearchTimeoutMinutes { get; set; } = 60;

    /// <summary>
    /// Maximum seconds to wait for the research plan to appear
    /// (the "Start research" button) after sending the prompt.
    /// </summary>
    public int PlanTimeoutSeconds { get; set; } = 240;

    /// <summary>
    /// Maximum research jobs completed per calendar day (UTC).
    /// Gemini Pro has undocumented rate limits — legacy used 19/day.
    /// Set to 0 to disable rate limiting.
    /// </summary>
    public int DailyRateLimit { get; set; } = 19;

    /// <summary>
    /// Seconds to wait after "Export to Docs" before interacting with the
    /// Google Doc. Gives Google Drive backend time to finish saving.
    /// </summary>
    public int ExportSettleSeconds { get; set; } = 15;

    /// <summary>
    /// Seconds to wait between completing one job and starting the next.
    /// Prevents hammering Gemini with back-to-back requests.
    /// </summary>
    public int InterJobDelaySeconds { get; set; } = 5;

    /// <summary>
    /// Maximum seconds to wait for a Gemini chat response (non-Deep-Research).
    /// "Thinking" and "Pro" modes can take 30–90+ seconds for complex prompts.
    /// Default: 300 (5 minutes).
    /// </summary>
    public int ChatResponseTimeoutSeconds { get; set; } = 300;

    /// <summary>
    /// Valid Gemini mode names accepted by the <c>/api/chat</c> endpoint.
    /// Must match the visible text in the Gemini mode picker dropdown.
    /// </summary>
    public static readonly string[] ValidModes = ["Fast", "Thinking", "Pro"];
}

