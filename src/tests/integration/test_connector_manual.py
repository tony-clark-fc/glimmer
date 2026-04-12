"""Manual import labeling and routing tests.

TEST:Connector.ManualImport.LabelingAndRouting
"""

from __future__ import annotations

from app.connectors.manual.importer import ManualImportHandler


class TestManualImportLabelingAndRouting:
    """TEST:Connector.ManualImport.LabelingAndRouting

    Proves unsupported-channel input remains explicit and auditable.
    """

    def test_signal_type_is_manual_paste(self) -> None:
        result = ManualImportHandler.normalize_manual_import(
            content="Hey, can we reschedule?"
        )
        assert result.signal_type == "manual_paste"

    def test_content_is_preserved(self) -> None:
        result = ManualImportHandler.normalize_manual_import(
            content="The deadline moved to Friday."
        )
        assert result.content == "The deadline moved to Friday."

    def test_source_label_is_preserved(self) -> None:
        result = ManualImportHandler.normalize_manual_import(
            content="msg",
            source_label="WhatsApp - Project Alpha",
        )
        assert result.source_label == "WhatsApp - Project Alpha"

    def test_metadata_marks_manual_import(self) -> None:
        result = ManualImportHandler.normalize_manual_import(content="test")
        assert result.raw_metadata["import_mode"] == "manual"
        assert result.raw_metadata["provider"] == "manual"

    def test_source_channel_preserved_in_metadata(self) -> None:
        result = ManualImportHandler.normalize_manual_import(
            content="msg",
            source_channel="whatsapp",
        )
        assert result.raw_metadata["source_channel"] == "whatsapp"

    def test_operator_notes_preserved_in_metadata(self) -> None:
        result = ManualImportHandler.normalize_manual_import(
            content="msg",
            operator_notes="Copied from client WhatsApp group",
        )
        assert result.raw_metadata["operator_notes"] == "Copied from client WhatsApp group"

    def test_minimal_import_works(self) -> None:
        """Only content is required — everything else is optional."""
        result = ManualImportHandler.normalize_manual_import(content="Just a note.")
        assert result.content == "Just a note."
        assert result.signal_type == "manual_paste"
        assert result.source_label is None

