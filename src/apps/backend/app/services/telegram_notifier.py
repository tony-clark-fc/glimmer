"""Telegram operator alert service — internal system health notifications.

This is a lightweight push-notification channel for operational alerts
(Chrome down, Chrome recovered, etc.). It is NOT the Telegram companion
interaction service (app/services/telegram.py) — those are separate concerns.

This module sends one-way alerts via the Telegram Bot API. It does not
receive messages, manage sessions, or process user input.

This is an internal operational alert, not user-facing messaging — it
does not violate Glimmer's no-auto-send rule for external communications.

ARCH:BrowserResearchSecurityBoundary
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Telegram Bot API base URL
_TELEGRAM_API = "https://api.telegram.org"


class TelegramNotifier:
    """Sends operational alerts to the operator via Telegram Bot API.

    If bot_token or chat_id is empty, all sends are silently skipped
    (degraded mode, not an error).
    """

    def __init__(
        self,
        bot_token: str = "",
        chat_id: str = "",
    ) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def is_configured(self) -> bool:
        """Whether Telegram alerts are fully configured."""
        return bool(self._bot_token) and bool(self._chat_id)

    async def send_alert(self, message: str) -> bool:
        """Send a text alert to the operator.

        Returns True if sent successfully, False otherwise.
        Silently returns False if not configured (not an error).
        """
        if not self.is_configured:
            logger.debug(
                "Telegram notifier not configured — skipping alert"
            )
            return False

        url = f"{_TELEGRAM_API}/bot{self._bot_token}/sendMessage"
        payload = {
            "chat_id": self._chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        try:
            if self._client is None:
                self._client = httpx.AsyncClient(timeout=10.0)

            response = await self._client.post(url, json=payload)

            if response.status_code == 200:
                logger.info("Telegram alert sent successfully")
                return True
            else:
                logger.warning(
                    "Telegram alert failed: %d %s",
                    response.status_code,
                    response.text[:200],
                )
                return False

        except Exception:
            logger.exception("Failed to send Telegram alert")
            return False

    async def close(self) -> None:
        """Clean up the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

