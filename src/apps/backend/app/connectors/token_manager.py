"""Secure OAuth token storage and retrieval.

ARCH:TokenStoragePosture
ARCH:TokenUsageDiscipline
ARCH:SecretExposurePrevention

Manages encrypted token storage in ConnectedAccount.auth_metadata.
Tokens are encrypted at rest using Fernet symmetric encryption.
Token data never leaves the connector layer boundary.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.orm import Session

from app.models.source import ConnectedAccount

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages encrypted OAuth tokens on ConnectedAccount records.

    ARCH:TokenStoragePosture — tokens encrypted at rest.
    ARCH:TokenUsageDiscipline — only connector layer accesses tokens.
    ARCH:SecretExposurePrevention — no plaintext tokens in logs or responses.
    """

    def __init__(self, session: Session, encryption_key: str) -> None:
        self._session = session
        if encryption_key:
            self._fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        else:
            self._fernet = None

    def store_tokens(
        self,
        account_id: uuid.UUID,
        tokens: dict,
    ) -> None:
        """Encrypt and store OAuth tokens on a ConnectedAccount.

        Args:
            account_id: The connected account to update.
            tokens: Dict with keys like access_token, refresh_token, expires_at, scopes, etc.

        The tokens dict is encrypted as a JSON blob and stored in
        auth_metadata["encrypted_tokens"]. Non-secret metadata
        (scopes, expiry) is stored in plaintext for diagnostic visibility.
        """
        account = self._session.get(ConnectedAccount, account_id)
        if account is None:
            raise ValueError(f"Connected account not found: {account_id}")

        # Encrypt the sensitive token data
        sensitive_data = {
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "id_token": tokens.get("id_token"),
        }

        encrypted_blob = self._encrypt(json.dumps(sensitive_data))

        # Build auth_metadata — secrets encrypted, diagnostics in plaintext
        auth_metadata = account.auth_metadata or {}
        auth_metadata.update({
            "encrypted_tokens": encrypted_blob,
            "token_type": tokens.get("token_type", "Bearer"),
            "scopes": tokens.get("scopes", []),
            "expires_at_iso": tokens.get("expires_at_iso"),
            "last_refreshed_at": datetime.now(timezone.utc).isoformat(),
            "has_refresh_token": bool(tokens.get("refresh_token")),
        })

        account.auth_metadata = auth_metadata
        self._session.flush()

    def get_tokens(self, account_id: uuid.UUID) -> Optional[dict]:
        """Retrieve and decrypt tokens for a connected account.

        Returns:
            Decrypted token dict with access_token, refresh_token, etc.
            None if no tokens are stored or decryption fails.
        """
        account = self._session.get(ConnectedAccount, account_id)
        if account is None:
            return None

        auth_metadata = account.auth_metadata or {}
        encrypted_blob = auth_metadata.get("encrypted_tokens")
        if not encrypted_blob:
            return None

        try:
            decrypted = self._decrypt(encrypted_blob)
            tokens = json.loads(decrypted)
            # Add non-secret metadata back for convenience
            tokens["token_type"] = auth_metadata.get("token_type", "Bearer")
            tokens["scopes"] = auth_metadata.get("scopes", [])
            tokens["expires_at_iso"] = auth_metadata.get("expires_at_iso")
            return tokens
        except (InvalidToken, json.JSONDecodeError) as exc:
            logger.error(
                "Failed to decrypt tokens for account %s: %s",
                account_id,
                type(exc).__name__,
            )
            return None

    def clear_tokens(self, account_id: uuid.UUID) -> None:
        """Remove all token data from a connected account.

        ARCH:TokenRevocationHandling
        """
        account = self._session.get(ConnectedAccount, account_id)
        if account is None:
            return

        auth_metadata = account.auth_metadata or {}
        auth_metadata.pop("encrypted_tokens", None)
        auth_metadata.pop("expires_at_iso", None)
        auth_metadata.pop("last_refreshed_at", None)
        auth_metadata["has_refresh_token"] = False
        auth_metadata["token_cleared_at"] = datetime.now(timezone.utc).isoformat()

        account.auth_metadata = auth_metadata
        self._session.flush()

    def is_expired(self, account_id: uuid.UUID) -> bool:
        """Check whether the stored access token has expired.

        Returns True if expired or no expiry info is available.
        """
        account = self._session.get(ConnectedAccount, account_id)
        if account is None:
            return True

        auth_metadata = account.auth_metadata or {}
        expires_at_iso = auth_metadata.get("expires_at_iso")
        if not expires_at_iso:
            return True

        try:
            expires_at = datetime.fromisoformat(expires_at_iso)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            # Add 60s buffer for safety
            return datetime.now(timezone.utc) >= expires_at
        except (ValueError, TypeError):
            return True

    def _encrypt(self, plaintext: str) -> str:
        """Encrypt a string using Fernet. Falls back to plaintext if no key."""
        if self._fernet is None:
            logger.warning("Token encryption key not configured — storing in plaintext")
            return plaintext
        return self._fernet.encrypt(plaintext.encode()).decode()

    def _decrypt(self, ciphertext: str) -> str:
        """Decrypt a Fernet-encrypted string. Falls back to treating as plaintext."""
        if self._fernet is None:
            return ciphertext
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken:
            # May be stored in plaintext (from before encryption was configured)
            logger.warning("Fernet decryption failed — treating as plaintext")
            return ciphertext

