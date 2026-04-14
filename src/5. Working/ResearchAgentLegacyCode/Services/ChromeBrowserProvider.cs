using System.Net.Sockets;
using Microsoft.Extensions.Options;
using Microsoft.Playwright;
using ResearchAgent.Models;

namespace ResearchAgent.Services;

/// <summary>
/// Singleton service that manages the Chrome browser connection via CDP.
/// ResearchAgent REQUIRES real Chrome (no Playwright Chromium fallback) because
/// Gemini Deep Research needs the operator's Google account session and Gemini
/// Pro subscription, which live in the Chrome profile.
///
/// The Chrome profile is shared with QuestResearch (same CHROME_PROFILE_SETUP_GUIDE.md).
/// Only one process may connect to Chrome on the CDP port at a time — QuestResearch
/// and ResearchAgent must not run simultaneously.
///
/// Chrome is auto-launched if not already running (ported from legacy EnsureChromeRunning).
/// To start manually:
///   chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\PlaywrightProfiles\Gemini"
///              --profile-directory=Default --no-first-run --no-default-browser-check
/// </summary>
public class ChromeBrowserProvider : IAsyncDisposable
{
    private readonly ChromeOptions _options;
    private readonly ILogger<ChromeBrowserProvider> _logger;

    private IPlaywright? _playwright;
    private IBrowser? _browser;
    private readonly SemaphoreSlim _initLock = new(1, 1);
    private bool _initialized;

    public ChromeBrowserProvider(
        IOptions<ChromeOptions> options,
        ILogger<ChromeBrowserProvider> logger)
    {
        _options = options.Value;
        _logger = logger;
    }

    /// <summary>Whether a browser is currently connected.</summary>
    public bool IsAvailable => _browser?.IsConnected == true;

    /// <summary>
    /// Quick check: is Chrome's CDP port accepting connections?
    /// Does NOT trigger initialization — safe for health checks.
    /// </summary>
    public bool IsChromePortOpen => IsPortOpen(_options.RemoteDebuggingPort);

    /// <summary>
    /// Get the shared browser instance. Initializes on first call.
    /// Reconnects automatically if the browser has disconnected.
    /// Returns null if Chrome is not reachable.
    /// </summary>
    public async Task<IBrowser?> GetBrowserAsync(CancellationToken ct = default)
    {
        // Fast path — already connected
        if (_initialized && _browser?.IsConnected == true)
            return _browser;

        await _initLock.WaitAsync(ct);
        try
        {
            // Double-check after acquiring lock
            if (_initialized && _browser?.IsConnected == true)
                return _browser;

            // Clean up if previously connected but now disconnected
            if (_initialized)
            {
                _logger.LogWarning("Chrome browser disconnected — attempting reconnection");
                await CleanupAsync();
                _initialized = false;
            }

            // Auto-launch Chrome if not running (ported from legacy EnsureChromeRunning)
            if (!IsPortOpen(_options.RemoteDebuggingPort))
            {
                _logger.LogInformation(
                    "Chrome not detected on port {Port} — launching automatically",
                    _options.RemoteDebuggingPort);

                if (!LaunchChrome())
                {
                    _logger.LogError(
                        "Failed to launch Chrome. Start it manually:\n" +
                        "  \"{ExePath}\" --remote-debugging-port={Port} " +
                        "--user-data-dir=\"{DataDir}\" --profile-directory={Profile} " +
                        "--no-first-run --no-default-browser-check",
                        _options.ExePath, _options.RemoteDebuggingPort,
                        _options.UserDataDir, _options.ProfileName);
                    return null;
                }
            }

            _logger.LogInformation(
                "Connecting to Chrome via CDP on port {Port}",
                _options.RemoteDebuggingPort);

            _playwright = await Playwright.CreateAsync();

            var cdpUrl = $"http://localhost:{_options.RemoteDebuggingPort}";
            _browser = await _playwright.Chromium.ConnectOverCDPAsync(cdpUrl,
                new BrowserTypeConnectOverCDPOptions
                {
                    Timeout = _options.ConnectionTimeoutSeconds * 1000
                });

            _initialized = true;

            _logger.LogInformation(
                "Connected to Chrome via CDP (port {Port}, profile: {Profile}, account: {Account})",
                _options.RemoteDebuggingPort, _options.ProfileName, _options.GoogleAccount);

            return _browser;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to connect to Chrome via CDP on port {Port}",
                _options.RemoteDebuggingPort);
            await CleanupAsync();
            return null;
        }
        finally
        {
            _initLock.Release();
        }
    }

    /// <summary>
    /// Launch Chrome with CDP remote debugging enabled.
    /// Ported from legacy EnsureChromeRunning().
    /// Returns true if Chrome started and the CDP port opened within ~5 seconds.
    /// </summary>
    private bool LaunchChrome()
    {
        try
        {
            if (string.IsNullOrWhiteSpace(_options.ExePath) || !File.Exists(_options.ExePath))
            {
                _logger.LogError("Chrome executable not found at '{ExePath}'", _options.ExePath);
                return false;
            }

            var args = $"--remote-debugging-port={_options.RemoteDebuggingPort} " +
                       $"--user-data-dir=\"{_options.UserDataDir}\" " +
                       $"--profile-directory={_options.ProfileName} " +
                       "--no-first-run --no-default-browser-check";

            _logger.LogInformation("Launching Chrome: \"{ExePath}\" {Args}",
                _options.ExePath, args);

            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
            {
                FileName = _options.ExePath,
                Arguments = args,
                UseShellExecute = false
            });

            // Wait for CDP port to open (up to 5 seconds)
            for (var i = 0; i < 10; i++)
            {
                Thread.Sleep(500);
                if (IsPortOpen(_options.RemoteDebuggingPort))
                {
                    _logger.LogInformation(
                        "Chrome started — CDP port {Port} is now open",
                        _options.RemoteDebuggingPort);
                    return true;
                }
            }

            _logger.LogError(
                "Chrome launched but CDP port {Port} did not open within 5 seconds",
                _options.RemoteDebuggingPort);
            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to launch Chrome process");
            return false;
        }
    }

    private static bool IsPortOpen(int port)
    {
        try
        {
            using var client = new TcpClient();
            // Use synchronous Connect with a short timeout — ConnectAsync + Wait is unreliable
            client.SendTimeout = 1_000;
            client.ReceiveTimeout = 1_000;
            client.Connect("127.0.0.1", port);
            return true;
        }
        catch
        {
            return false;
        }
    }

    private async Task CleanupAsync()
    {
        if (_browser is not null)
        {
            try { await _browser.CloseAsync(); } catch { /* best effort */ }
            _browser = null;
        }

        if (_playwright is not null)
        {
            _playwright.Dispose();
            _playwright = null;
        }
    }

    public async ValueTask DisposeAsync()
    {
        await CleanupAsync();
        _initLock.Dispose();
        GC.SuppressFinalize(this);
    }
}


