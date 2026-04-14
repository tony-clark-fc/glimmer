namespace ResearchAgent.Models;

/// <summary>
/// Chrome/CDP configuration — same shape as QuestResearch.Models.ChromeOptions.
/// Shares the same Chrome profile (provisioned via CHROME_PROFILE_SETUP_GUIDE.md).
/// Bound to the "Chrome" section of appsettings.json.
/// </summary>
public class ChromeOptions
{
    public const string SectionName = "Chrome";

    /// <summary>
    /// Full path to the Chrome executable.
    /// Windows: C:\Program Files\Google\Chrome\Application\chrome.exe
    /// macOS:   /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
    /// </summary>
    public string ExePath { get; set; } = string.Empty;

    /// <summary>
    /// Chrome user data directory — an isolated directory (NOT your default profile)
    /// set up specifically for Gemini Deep Research.
    /// Carries the Google account session, cookies, and browsing history.
    /// </summary>
    public string UserDataDir { get; set; } = string.Empty;

    /// <summary>
    /// Chrome profile directory name within <see cref="UserDataDir"/>.
    /// Typically "Default".
    /// </summary>
    public string ProfileName { get; set; } = "Default";

    /// <summary>
    /// Google account email used for Gemini Pro subscription.
    /// Used for logging/diagnostics only — the actual session lives in the profile.
    /// </summary>
    public string GoogleAccount { get; set; } = string.Empty;

    /// <summary>
    /// Port for Chrome DevTools Protocol (CDP) remote debugging.
    /// Must match the port Chrome was launched with.
    /// </summary>
    public int RemoteDebuggingPort { get; set; } = 9222;

    /// <summary>
    /// Maximum seconds to wait when connecting to Chrome via CDP.
    /// </summary>
    public int ConnectionTimeoutSeconds { get; set; } = 30;
}

