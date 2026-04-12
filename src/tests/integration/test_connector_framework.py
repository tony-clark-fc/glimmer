"""Connector framework boundary isolation tests.

TEST:Connector.Framework.ProviderBoundaryIsolation
TEST:Connector.Security.ReadFirstNoAutoSendPreserved
"""

from __future__ import annotations

import inspect

from app.connectors.base import BaseConnector
from app.connectors.google.gmail import GmailConnector
from app.connectors.google.calendar import GoogleCalendarConnector
from app.connectors.microsoft.mail import MicrosoftMailConnector
from app.connectors.microsoft.calendar import MicrosoftCalendarConnector
from app.connectors.telegram.intake import TelegramIntakeConnector
from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    IntakeReference,
    NormalizedMessageData,
    NormalizedEventData,
    NormalizedSignalData,
    NormalizedThreadData,
    SyncCheckpoint,
)


class TestProviderBoundaryIsolation:
    """TEST:Connector.Framework.ProviderBoundaryIsolation

    Proves that provider SDK details do not leak upward into
    orchestration, domain, or UI layers. Connectors have clear
    contracts and isolated provider boundaries.
    """

    def test_all_connectors_inherit_from_base(self) -> None:
        """All provider connectors implement the BaseConnector contract."""
        connectors = [
            GmailConnector,
            GoogleCalendarConnector,
            MicrosoftMailConnector,
            MicrosoftCalendarConnector,
            TelegramIntakeConnector,
        ]
        for cls in connectors:
            assert issubclass(cls, BaseConnector), (
                f"{cls.__name__} must inherit from BaseConnector"
            )

    def test_connectors_expose_provider_type(self) -> None:
        """Each connector declares its provider type."""
        expected = {
            GmailConnector: "google",
            GoogleCalendarConnector: "google",
            MicrosoftMailConnector: "microsoft",
            MicrosoftCalendarConnector: "microsoft",
            TelegramIntakeConnector: "telegram",
        }
        for cls, expected_type in expected.items():
            instance = cls()
            assert instance.provider_type == expected_type

    def test_connectors_expose_connector_type(self) -> None:
        """Each connector declares its specific connector type."""
        expected = {
            GmailConnector: "gmail",
            GoogleCalendarConnector: "google_calendar",
            MicrosoftMailConnector: "microsoft_mail",
            MicrosoftCalendarConnector: "microsoft_calendar",
            TelegramIntakeConnector: "telegram_intake",
        }
        for cls, expected_type in expected.items():
            instance = cls()
            assert instance.connector_type == expected_type

    def test_connectors_expose_supported_profile_types(self) -> None:
        """Each connector lists its supported profile types."""
        instances = [
            GmailConnector(),
            GoogleCalendarConnector(),
            MicrosoftMailConnector(),
            MicrosoftCalendarConnector(),
            TelegramIntakeConnector(),
        ]
        for instance in instances:
            profiles = instance.supported_profile_types
            assert isinstance(profiles, list)
            assert len(profiles) > 0

    def test_provider_directories_are_separate(self) -> None:
        """Provider implementations live in separate modules."""
        assert GmailConnector.__module__.startswith("app.connectors.google")
        assert GoogleCalendarConnector.__module__.startswith("app.connectors.google")
        assert MicrosoftMailConnector.__module__.startswith("app.connectors.microsoft")
        assert MicrosoftCalendarConnector.__module__.startswith("app.connectors.microsoft")
        assert TelegramIntakeConnector.__module__.startswith("app.connectors.telegram")

    def test_contracts_are_framework_level_not_provider_specific(self) -> None:
        """Shared contracts live in the framework, not inside provider modules."""
        assert ConnectorExecutionContext.__module__ == "app.connectors.contracts"
        assert FetchResult.__module__ == "app.connectors.contracts"
        assert IntakeReference.__module__ == "app.connectors.contracts"
        assert NormalizedMessageData.__module__ == "app.connectors.contracts"
        assert NormalizedEventData.__module__ == "app.connectors.contracts"
        assert NormalizedSignalData.__module__ == "app.connectors.contracts"

    def test_base_connector_abc_has_required_interface(self) -> None:
        """BaseConnector defines the expected abstract interface."""
        abstract_methods = set()
        for name, method in inspect.getmembers(BaseConnector):
            if getattr(method, "__isabstractmethod__", False):
                abstract_methods.add(name)
        
        assert "provider_type" in abstract_methods
        assert "connector_type" in abstract_methods
        assert "supported_profile_types" in abstract_methods
        assert "fetch_and_normalize" in abstract_methods
        assert "validate_credentials" in abstract_methods


class TestReadFirstNoAutoSend:
    """TEST:Connector.Security.ReadFirstNoAutoSendPreserved

    Proves external-boundary behavior does not silently create
    outbound side effects.
    """

    def test_base_connector_has_no_send_methods(self) -> None:
        """BaseConnector contract has no send/write/modify methods."""
        public_methods = [
            name for name in dir(BaseConnector)
            if not name.startswith("_") and callable(getattr(BaseConnector, name, None))
        ]
        send_terms = {"send", "write", "modify", "delete", "update", "post", "put", "patch"}
        for method_name in public_methods:
            for term in send_terms:
                assert term not in method_name.lower(), (
                    f"BaseConnector should not have outbound method: {method_name}"
                )

    def test_connectors_have_no_send_methods(self) -> None:
        """No provider connector exposes send/write/modify methods."""
        connectors = [
            GmailConnector,
            GoogleCalendarConnector,
            MicrosoftMailConnector,
            MicrosoftCalendarConnector,
            TelegramIntakeConnector,
        ]
        send_terms = {"send", "write", "modify", "delete", "put", "patch"}
        for cls in connectors:
            public_methods = [
                name for name in dir(cls)
                if not name.startswith("_") and callable(getattr(cls, name, None))
            ]
            for method_name in public_methods:
                for term in send_terms:
                    assert term not in method_name.lower(), (
                        f"{cls.__name__} should not have outbound method: {method_name}"
                    )

    def test_fetch_result_is_read_only_shape(self) -> None:
        """FetchResult contains only normalized read data, no action fields."""
        fields = set(FetchResult.model_fields.keys())
        assert "messages" in fields
        assert "threads" in fields
        assert "events" in fields
        assert "signals" in fields
        assert "checkpoint" in fields
        # No action/send/modify fields
        action_terms = {"send", "action", "reply", "forward", "modify"}
        for field_name in fields:
            for term in action_terms:
                assert term not in field_name.lower(), (
                    f"FetchResult should not have action field: {field_name}"
                )

