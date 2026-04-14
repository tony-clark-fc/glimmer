"""Tests for the Gemini adapter contracts and service boundary.

TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse
TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected
TEST:ExpertAdvice.Failure.GeminiUnavailableHandledSafely
TEST:Research.Failure.BrowserUnavailableHandledSafely
TEST:Research.Security.NoUnboundedActionTaking

These are contract-level tests that verify the adapter's behavior
using mocks/fakes instead of a live browser.
"""

from __future__ import annotations

import pytest

from app.research.config import ChromeConfig, ResearchAdapterConfig
from app.research.contracts import (
    AdapterHealthCheck,
    AdapterStatus,
    ChatRequest,
    ChatResult,
    ResearchRequest,
    ResearchResult,
)
from app.research.adapter import GeminiAdapter


# ── Contract model tests ──────────────────────────────────────────────


class TestChatRequestContract:
    """Verify ChatRequest Pydantic contract behavior."""

    def test_valid_request(self) -> None:
        req = ChatRequest(prompt="What is 2+2?", mode="Fast")
        assert req.prompt == "What is 2+2?"
        assert req.mode == "Fast"

    def test_default_mode_is_pro(self) -> None:
        req = ChatRequest(prompt="Test")
        assert req.mode == "Pro"

    def test_empty_prompt_rejected(self) -> None:
        with pytest.raises(Exception):
            ChatRequest(prompt="", mode="Fast")


class TestChatResultContract:
    def test_valid_result(self) -> None:
        result = ChatResult(
            response_text="The answer is 4.",
            mode="Fast",
            duration_ms=1500,
        )
        assert result.response_text == "The answer is 4."
        assert result.mode == "Fast"
        assert result.duration_ms == 1500


class TestResearchRequestContract:
    def test_valid_request(self) -> None:
        req = ResearchRequest(
            prompt="Research soil carbon benchmarks",
            document_name="SOC-Research-20260414",
        )
        assert req.prompt == "Research soil carbon benchmarks"
        assert req.document_name == "SOC-Research-20260414"

    def test_empty_prompt_rejected(self) -> None:
        with pytest.raises(Exception):
            ResearchRequest(prompt="", document_name="Test")

    def test_empty_document_name_rejected(self) -> None:
        with pytest.raises(Exception):
            ResearchRequest(prompt="Test", document_name="")


class TestResearchResultContract:
    def test_valid_result(self) -> None:
        result = ResearchResult(
            document_url="https://docs.google.com/document/d/1abc",
            document_renamed=True,
        )
        assert result.document_url.startswith("https://docs.google.com")
        assert result.document_renamed is True


class TestAdapterStatusContract:
    def test_idle_status(self) -> None:
        status = AdapterStatus(
            status="Idle",
            browser_available=True,
            queue_depth=0,
            today_completions=3,
            daily_rate_limit=19,
            is_rate_limited=False,
        )
        assert status.status == "Idle"
        assert status.browser_available is True

    def test_busy_status(self) -> None:
        status = AdapterStatus(
            status="Busy",
            browser_available=True,
        )
        assert status.status == "Busy"


class TestAdapterHealthCheckContract:
    def test_healthy(self) -> None:
        health = AdapterHealthCheck(
            status="healthy",
            chrome_port_open=True,
            chrome_connected=True,
        )
        assert health.status == "healthy"

    def test_unhealthy(self) -> None:
        health = AdapterHealthCheck(
            chrome_port_open=False,
            chrome_connected=False,
        )
        assert health.chrome_port_open is False


# ── Configuration tests ───────────────────────────────────────────────


class TestChromeConfig:
    def test_defaults(self) -> None:
        config = ChromeConfig()
        assert config.remote_debugging_port == 9222
        assert config.profile_name == "Default"
        assert config.connection_timeout_seconds == 30

    def test_custom_port(self) -> None:
        config = ChromeConfig(remote_debugging_port=9333)
        assert config.remote_debugging_port == 9333


class TestResearchAdapterConfig:
    def test_defaults(self) -> None:
        config = ResearchAdapterConfig()
        assert config.research_timeout_minutes == 60
        assert config.daily_rate_limit == 19
        assert config.chat_response_timeout_seconds == 300
        assert config.valid_modes == ["Fast", "Thinking", "Pro"]
        assert config.default_chat_mode == "Pro"

    def test_valid_modes_list(self) -> None:
        """TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected —
        Valid modes include Fast, Thinking, and Pro."""
        config = ResearchAdapterConfig()
        assert "Fast" in config.valid_modes
        assert "Thinking" in config.valid_modes
        assert "Pro" in config.valid_modes


# ── Adapter behavior tests (no live browser) ──────────────────────────


class TestGeminiAdapterBehavior:
    """Contract-level tests for adapter behavior without a live browser."""

    def test_adapter_starts_idle(self) -> None:
        adapter = GeminiAdapter()
        assert adapter.is_busy is False

    @pytest.mark.asyncio
    async def test_adapter_health_without_chrome(self) -> None:
        """TEST:Research.Failure.BrowserUnavailableHandledSafely —
        Health check returns safely when Chrome is not running."""
        adapter = GeminiAdapter(
            chrome_config=ChromeConfig(remote_debugging_port=19999)
        )
        health = await adapter.get_health()
        assert health.chrome_port_open is False
        assert health.chrome_connected is False

    @pytest.mark.asyncio
    async def test_adapter_status_without_chrome(self) -> None:
        adapter = GeminiAdapter(
            chrome_config=ChromeConfig(remote_debugging_port=19999)
        )
        status = await adapter.get_status()
        assert status.status == "Idle"
        assert status.browser_available is False

    @pytest.mark.asyncio
    async def test_chat_fails_without_chrome(self) -> None:
        """TEST:ExpertAdvice.Failure.GeminiUnavailableHandledSafely —
        Chat raises a clear error when Chrome is not available."""
        adapter = GeminiAdapter(
            chrome_config=ChromeConfig(remote_debugging_port=19999)
        )
        with pytest.raises(RuntimeError, match="Chrome is not available"):
            await adapter.execute_chat(
                ChatRequest(prompt="Test", mode="Fast")
            )

    @pytest.mark.asyncio
    async def test_research_fails_without_chrome(self) -> None:
        """TEST:Research.Failure.BrowserUnavailableHandledSafely —
        Research raises a clear error when Chrome is not available."""
        adapter = GeminiAdapter(
            chrome_config=ChromeConfig(remote_debugging_port=19999)
        )
        with pytest.raises(RuntimeError, match="Chrome is not available"):
            await adapter.execute_research(
                ResearchRequest(
                    prompt="Test research",
                    document_name="Test-Doc",
                )
            )

    @pytest.mark.asyncio
    async def test_chat_rejects_invalid_mode(self) -> None:
        """TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected —
        Invalid mode names are rejected."""
        adapter = GeminiAdapter()
        with pytest.raises(ValueError, match="Invalid mode"):
            await adapter.execute_chat(
                ChatRequest(prompt="Test", mode="InvalidMode")
            )

    @pytest.mark.asyncio
    async def test_check_browser_returns_false_when_not_running(
        self,
    ) -> None:
        adapter = GeminiAdapter(
            chrome_config=ChromeConfig(remote_debugging_port=19999)
        )
        available = await adapter.check_browser_available()
        assert available is False


# ── Security boundary tests ───────────────────────────────────────────


class TestResearchSecurityBoundary:
    """TEST:Research.Security.NoUnboundedActionTaking
    ARCH:BrowserResearchSecurityBoundary"""

    def test_adapter_config_has_daily_rate_limit(self) -> None:
        """Rate limiting is configured by default."""
        config = ResearchAdapterConfig()
        assert config.daily_rate_limit > 0

    def test_adapter_config_has_bounded_timeouts(self) -> None:
        """Timeouts prevent unbounded operations."""
        config = ResearchAdapterConfig()
        assert config.research_timeout_minutes > 0
        assert config.chat_response_timeout_seconds > 0
        assert config.plan_timeout_seconds > 0


class TestWhitelistedDestinations:
    """ARCH:BrowserResearchSecurityBoundary
    TEST:Research.Security.NoUnboundedActionTaking

    The adapter MUST only navigate to whitelisted destinations.
    This is a load-bearing security rule.
    """

    def test_gemini_domain_is_allowed(self) -> None:
        """gemini.google.com is on the allowlist."""
        from app.research._browser_helpers import validate_destination_url
        validate_destination_url("https://gemini.google.com/")
        validate_destination_url("https://gemini.google.com/app")

    def test_docs_domain_is_allowed(self) -> None:
        """docs.google.com is on the allowlist (research exports to Google Docs)."""
        from app.research._browser_helpers import validate_destination_url
        validate_destination_url("https://docs.google.com/document/d/abc123/edit")

    def test_accounts_domain_is_allowed(self) -> None:
        """accounts.google.com is on the allowlist (sign-in redirects)."""
        from app.research._browser_helpers import validate_destination_url
        validate_destination_url("https://accounts.google.com/signin")

    def test_arbitrary_url_is_blocked(self) -> None:
        """Navigation to an arbitrary website is blocked."""
        from app.research._browser_helpers import (
            DestinationBlockedError,
            validate_destination_url,
        )
        with pytest.raises(DestinationBlockedError):
            validate_destination_url("https://evil.com/phishing")

    def test_google_search_is_blocked(self) -> None:
        """Even google.com (non-Gemini) is blocked."""
        from app.research._browser_helpers import (
            DestinationBlockedError,
            validate_destination_url,
        )
        with pytest.raises(DestinationBlockedError):
            validate_destination_url("https://www.google.com/search?q=test")

    def test_youtube_is_blocked(self) -> None:
        """YouTube is not a whitelisted destination."""
        from app.research._browser_helpers import (
            DestinationBlockedError,
            validate_destination_url,
        )
        with pytest.raises(DestinationBlockedError):
            validate_destination_url("https://youtube.com/watch?v=abc")

    def test_mail_is_blocked(self) -> None:
        """Gmail is explicitly NOT a whitelisted destination for MVP."""
        from app.research._browser_helpers import (
            DestinationBlockedError,
            validate_destination_url,
        )
        with pytest.raises(DestinationBlockedError):
            validate_destination_url("https://mail.google.com/mail/u/0/")

    def test_localhost_is_blocked(self) -> None:
        """Localhost URLs are blocked."""
        from app.research._browser_helpers import (
            DestinationBlockedError,
            validate_destination_url,
        )
        with pytest.raises(DestinationBlockedError):
            validate_destination_url("http://localhost:8080/admin")

    def test_empty_url_is_blocked(self) -> None:
        """Empty or malformed URLs are blocked."""
        from app.research._browser_helpers import (
            DestinationBlockedError,
            validate_destination_url,
        )
        with pytest.raises(DestinationBlockedError):
            validate_destination_url("")

    def test_allowlist_is_frozen(self) -> None:
        """The allowlist is a frozenset — cannot be modified at runtime."""
        from app.research._browser_helpers import ALLOWED_DESTINATION_DOMAINS
        assert isinstance(ALLOWED_DESTINATION_DOMAINS, frozenset)
        assert len(ALLOWED_DESTINATION_DOMAINS) == 3


