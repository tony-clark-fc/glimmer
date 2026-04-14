"""Tests for Chrome browser lifecycle management — auto-launch, health monitor,
Telegram notifier, and health endpoint.

TEST:Research.Failure.BrowserUnavailableHandledSafely
ARCH:BrowserResearchSecurityBoundary
ARCH:ResearchAdapterSafetyBoundary

Covers:
- Chrome auto-launch behavior (launch_chrome)
- ChromeHealthMonitor state tracking and transitions
- TelegramNotifier contract
- /health/research endpoint
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.research.browser import ChromeBrowserProvider, _is_port_open
from app.research.config import ChromeConfig
from app.research.chrome_monitor import ChromeHealthMonitor
from app.services.telegram_notifier import TelegramNotifier


# ── Chrome Auto-Launch Tests ─────────────────────────────────────


class TestChromeAutoLaunch:
    """Tests for ChromeBrowserProvider.launch_chrome() auto-launch behavior."""

    @pytest.mark.asyncio
    async def test_launch_chrome_returns_true_if_port_already_open(self) -> None:
        """Idempotent: if Chrome is already running, launch is a no-op."""
        config = ChromeConfig(remote_debugging_port=9222)
        provider = ChromeBrowserProvider(config)

        with patch(
            "app.research.browser._is_port_open", return_value=True
        ):
            result = await provider.launch_chrome()
            assert result is True

    @pytest.mark.asyncio
    async def test_launch_chrome_fails_without_exe_path(self) -> None:
        """launch_chrome returns False if Chrome executable doesn't exist."""
        config = ChromeConfig(
            remote_debugging_port=19999,
            exe_path="/nonexistent/chrome",
            user_data_dir="/tmp/test-profile",
        )
        provider = ChromeBrowserProvider(config)

        result = await provider.launch_chrome()
        assert result is False

    @pytest.mark.asyncio
    async def test_launch_chrome_fails_without_user_data_dir(self) -> None:
        """launch_chrome returns False if user_data_dir is not configured."""
        config = ChromeConfig(
            remote_debugging_port=19999,
            exe_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            user_data_dir="",  # empty
        )
        provider = ChromeBrowserProvider(config)

        result = await provider.launch_chrome()
        assert result is False

    @pytest.mark.asyncio
    async def test_launch_chrome_calls_subprocess(self) -> None:
        """launch_chrome spawns Chrome with the correct flags."""
        config = ChromeConfig(
            remote_debugging_port=19999,
            exe_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            user_data_dir="~/Library/Test/ChromeProfile",
            profile_name="TestProfile",
        )
        provider = ChromeBrowserProvider(config)

        mock_process = MagicMock()
        with (
            patch(
                "app.research.browser._is_port_open",
                side_effect=[False, False, True],  # closed, closed, then open
            ),
            patch(
                "asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_process,
            ) as mock_exec,
        ):
            result = await provider.launch_chrome()
            assert result is True
            # Verify Chrome was called with the right args
            call_args = mock_exec.call_args[0]
            assert "--remote-debugging-port=19999" in call_args
            assert "--profile-directory=TestProfile" in call_args
            assert "--no-first-run" in call_args
            assert "--no-default-browser-check" in call_args

    @pytest.mark.asyncio
    async def test_launch_chrome_timeout_returns_false(self) -> None:
        """launch_chrome returns False if port doesn't open within timeout."""
        config = ChromeConfig(
            remote_debugging_port=19999,
            exe_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            user_data_dir="~/Library/Test/ChromeProfile",
        )
        provider = ChromeBrowserProvider(config)

        with (
            patch(
                "app.research.browser._is_port_open",
                return_value=False,  # port never opens
            ),
            patch(
                "asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
            ),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await provider.launch_chrome()
            assert result is False

    @pytest.mark.asyncio
    async def test_get_browser_attempts_auto_launch(self) -> None:
        """get_browser() calls launch_chrome when port is closed."""
        config = ChromeConfig(remote_debugging_port=19999)
        provider = ChromeBrowserProvider(config)

        # Mock launch_chrome to return False (launch failed)
        provider.launch_chrome = AsyncMock(return_value=False)

        result = await provider.get_browser()
        assert result is None
        provider.launch_chrome.assert_called_once()


# ── Chrome Health Monitor Tests ──────────────────────────────────


class TestChromeHealthMonitor:
    """Tests for ChromeHealthMonitor state tracking and transitions."""

    def test_initial_status_is_unknown(self) -> None:
        """Monitor starts in 'unknown' state."""
        monitor = ChromeHealthMonitor(ChromeConfig(remote_debugging_port=19999))
        assert monitor.status == "unknown"
        assert monitor.last_check_at is None
        assert monitor.consecutive_failures == 0

    @pytest.mark.asyncio
    async def test_check_detects_available(self) -> None:
        """When port is open, status transitions to 'available'."""
        monitor = ChromeHealthMonitor(ChromeConfig(remote_debugging_port=19999))

        with patch(
            "app.research.chrome_monitor._is_port_open", return_value=True
        ):
            await monitor._check_once()

        assert monitor.status == "available"
        assert monitor.last_check_at is not None
        assert monitor.consecutive_failures == 0

    @pytest.mark.asyncio
    async def test_check_detects_unavailable(self) -> None:
        """When port is closed, status transitions to 'unavailable'."""
        monitor = ChromeHealthMonitor(ChromeConfig(remote_debugging_port=19999))
        # Mock launch_chrome to prevent actual subprocess attempts
        monitor._browser_provider.launch_chrome = AsyncMock(return_value=False)

        with patch(
            "app.research.chrome_monitor._is_port_open", return_value=False
        ):
            await monitor._check_once()

        assert monitor.status == "unavailable"
        assert monitor.consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_transition_available_to_unavailable_triggers_launch(self) -> None:
        """Transition to unavailable triggers auto-launch attempt."""
        monitor = ChromeHealthMonitor(ChromeConfig(remote_debugging_port=19999))
        monitor.status = "available"  # pretend was available

        launch_mock = AsyncMock(return_value=False)
        monitor._browser_provider.launch_chrome = launch_mock

        with patch(
            "app.research.chrome_monitor._is_port_open", return_value=False
        ):
            await monitor._check_once()

        launch_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_transition_available_to_unavailable_with_successful_relaunch(self) -> None:
        """If auto-launch succeeds, status returns to 'available'."""
        monitor = ChromeHealthMonitor(ChromeConfig(remote_debugging_port=19999))
        monitor.status = "available"

        launch_mock = AsyncMock(return_value=True)
        monitor._browser_provider.launch_chrome = launch_mock

        with patch(
            "app.research.chrome_monitor._is_port_open", return_value=False
        ):
            await monitor._check_once()

        assert monitor.status == "available"
        assert monitor.consecutive_failures == 0

    @pytest.mark.asyncio
    async def test_transition_unavailable_to_available_fires_restored(self) -> None:
        """Transition from unavailable → available fires on_chrome_restored."""
        notifier = TelegramNotifier(bot_token="", chat_id="")
        monitor = ChromeHealthMonitor(
            ChromeConfig(remote_debugging_port=19999),
            notifier=notifier,
        )
        monitor.status = "unavailable"

        with patch(
            "app.research.chrome_monitor._is_port_open", return_value=True
        ):
            await monitor._check_once()

        assert monitor.status == "available"
        assert monitor.last_transition_at is not None

    @pytest.mark.asyncio
    async def test_consecutive_failures_increment(self) -> None:
        """Consecutive failures counter increments on each failed check."""
        monitor = ChromeHealthMonitor(ChromeConfig(remote_debugging_port=19999))
        monitor._browser_provider.launch_chrome = AsyncMock(return_value=False)

        with patch(
            "app.research.chrome_monitor._is_port_open", return_value=False
        ):
            await monitor._check_once()
            await monitor._check_once()
            await monitor._check_once()

        assert monitor.consecutive_failures == 3

    @pytest.mark.asyncio
    async def test_consecutive_failures_reset_on_success(self) -> None:
        """Consecutive failures counter resets when port becomes available."""
        monitor = ChromeHealthMonitor(ChromeConfig(remote_debugging_port=19999))
        monitor.consecutive_failures = 5
        monitor.status = "unavailable"

        with patch(
            "app.research.chrome_monitor._is_port_open", return_value=True
        ):
            await monitor._check_once()

        assert monitor.consecutive_failures == 0

    def test_get_status_dict_shape(self) -> None:
        """get_status_dict returns expected keys."""
        monitor = ChromeHealthMonitor(ChromeConfig(remote_debugging_port=19999))
        status = monitor.get_status_dict()

        assert "chrome_status" in status
        assert "chrome_port" in status
        assert "chrome_port_open" in status
        assert "last_check_at" in status
        assert "last_transition_at" in status
        assert "consecutive_failures" in status
        assert "monitor_running" in status
        assert status["chrome_port"] == 19999
        assert status["monitor_running"] is False

    @pytest.mark.asyncio
    async def test_start_and_stop(self) -> None:
        """Monitor can be started and stopped cleanly."""
        monitor = ChromeHealthMonitor(
            ChromeConfig(remote_debugging_port=19999),
            check_interval_seconds=0.1,
        )
        task = monitor.start()
        assert monitor.is_running is True

        await asyncio.sleep(0.05)
        await monitor.stop()
        assert monitor.is_running is False


# ── Telegram Notifier Tests ──────────────────────────────────────


class TestTelegramNotifier:
    """Tests for TelegramNotifier contract."""

    def test_not_configured_when_empty(self) -> None:
        """Notifier reports not configured when token/chat_id are empty."""
        notifier = TelegramNotifier(bot_token="", chat_id="")
        assert notifier.is_configured is False

    def test_configured_when_both_set(self) -> None:
        """Notifier reports configured when both values are set."""
        notifier = TelegramNotifier(bot_token="123:abc", chat_id="456")
        assert notifier.is_configured is True

    def test_not_configured_when_only_token(self) -> None:
        """Notifier is not configured with only a token."""
        notifier = TelegramNotifier(bot_token="123:abc", chat_id="")
        assert notifier.is_configured is False

    @pytest.mark.asyncio
    async def test_send_alert_skips_when_not_configured(self) -> None:
        """send_alert silently returns False when not configured."""
        notifier = TelegramNotifier(bot_token="", chat_id="")
        result = await notifier.send_alert("test message")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_alert_calls_telegram_api(self) -> None:
        """send_alert posts to the Telegram Bot API."""
        notifier = TelegramNotifier(bot_token="123:abc", chat_id="456")

        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        notifier._client = mock_client

        result = await notifier.send_alert("Chrome is down!")
        assert result is True
        mock_client.post.assert_called_once()

        # Verify the URL and payload shape
        call_args = mock_client.post.call_args
        assert "/bot123:abc/sendMessage" in call_args[0][0]
        payload = call_args[1]["json"]
        assert payload["chat_id"] == "456"
        assert payload["text"] == "Chrome is down!"

    @pytest.mark.asyncio
    async def test_send_alert_handles_api_failure(self) -> None:
        """send_alert returns False on API error."""
        notifier = TelegramNotifier(bot_token="123:abc", chat_id="456")

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        notifier._client = mock_client

        result = await notifier.send_alert("test")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_alert_handles_exception(self) -> None:
        """send_alert returns False on network exception."""
        notifier = TelegramNotifier(bot_token="123:abc", chat_id="456")

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=Exception("Network error"))
        notifier._client = mock_client

        result = await notifier.send_alert("test")
        assert result is False

    @pytest.mark.asyncio
    async def test_close_cleans_up_client(self) -> None:
        """close() properly shuts down the HTTP client."""
        notifier = TelegramNotifier(bot_token="123:abc", chat_id="456")
        mock_client = AsyncMock()
        notifier._client = mock_client

        await notifier.close()
        mock_client.aclose.assert_called_once()
        assert notifier._client is None


# ── Health Endpoint Tests ────────────────────────────────────────


class TestResearchHealthEndpoint:
    """Tests for GET /health/research endpoint."""

    def test_health_research_returns_status(self, client) -> None:
        """Endpoint returns Chrome status with all expected fields."""
        response = client.get("/health/research")
        assert response.status_code == 200
        data = response.json()
        assert "chrome_status" in data
        assert "chrome_port" in data
        assert "chrome_port_open" in data
        assert "monitor_running" in data
        assert isinstance(data["consecutive_failures"], int)

    def test_health_research_returns_port_number(self, client) -> None:
        """Endpoint returns the configured CDP port number."""
        response = client.get("/health/research")
        data = response.json()
        assert isinstance(data["chrome_port"], int)

    def test_health_research_chrome_status_values(self, client) -> None:
        """Chrome status is one of the expected values."""
        response = client.get("/health/research")
        data = response.json()
        assert data["chrome_status"] in ("available", "unavailable", "unknown")

    def test_health_research_monitor_running_with_lifespan(self, client) -> None:
        """Monitor is running when the app lifespan is active."""
        response = client.get("/health/research")
        data = response.json()
        # The lifespan starts the monitor, so it should be running
        assert data["monitor_running"] is True

    def test_original_health_endpoint_unchanged(self, client) -> None:
        """Original /health endpoint still works."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "app_name" in data
        assert "database" in data


# ── Port Check Utility Test ──────────────────────────────────────


class TestPortCheck:
    """Tests for the _is_port_open utility."""

    def test_closed_port_returns_false(self) -> None:
        """_is_port_open returns False for a port nobody is listening on."""
        assert _is_port_open(19999) is False

    def test_port_check_does_not_raise(self) -> None:
        """_is_port_open handles errors gracefully."""
        # Port 0 is invalid, should return False not raise
        assert _is_port_open(0) is False


