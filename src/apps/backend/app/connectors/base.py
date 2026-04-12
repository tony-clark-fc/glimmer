"""Abstract base connector — contract for all provider-specific connectors.

ARCH:ConnectorIsolation
ARCH:ConnectorPrinciple.SourceIsolation

Each provider connector inherits from BaseConnector and implements
provider-specific fetch and normalization logic. The framework handles
persistence and intake handoff.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.connectors.contracts import ConnectorExecutionContext, FetchResult


class BaseConnector(ABC):
    """Abstract contract for all Glimmer connectors.

    Subclasses implement provider-specific logic for fetching and normalizing
    source material. The connector framework calls these methods and handles
    persistence and intake handoff externally.

    Connectors must:
    - Remain read-only (no outbound side effects)
    - Preserve provider/account/thread/event provenance
    - Return normalized records, not raw provider payloads
    - Not perform triage, classification, or planning

    ARCH:ConnectorLayerScope
    ARCH:ConnectorPrinciple.ReadFirst
    """

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Provider type identifier (e.g. 'google', 'microsoft', 'telegram')."""
        ...

    @property
    @abstractmethod
    def connector_type(self) -> str:
        """Specific connector type (e.g. 'gmail', 'google_calendar', 'microsoft_mail')."""
        ...

    @property
    @abstractmethod
    def supported_profile_types(self) -> list[str]:
        """Profile types this connector can operate against."""
        ...

    @abstractmethod
    def fetch_and_normalize(
        self, context: ConnectorExecutionContext
    ) -> FetchResult:
        """Fetch source material and normalize into internal record shapes.

        This is the primary method each provider connector must implement.
        It receives a resolved execution context (account + profile) and
        returns normalized records ready for persistence.

        Implementations must:
        - Use only the resolved account/profile from context
        - Preserve all provenance metadata
        - Return normalized data, not raw provider responses
        - Not mutate any accepted state or trigger business logic
        """
        ...

    @abstractmethod
    def validate_credentials(
        self, context: ConnectorExecutionContext
    ) -> bool:
        """Check whether the current credentials are valid for this context.

        Returns True if credentials are usable, False if expired/revoked.
        This should be a lightweight check, not a full fetch.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} provider={self.provider_type} type={self.connector_type}>"

