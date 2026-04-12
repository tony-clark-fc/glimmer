"""Manual import handler — bounded fallback for unsupported channels.

ARCH:ManualImportBoundary
ARCH:ManualImportDiscipline

Responsible for:
- Accepting pasted or uploaded communication text
- Preserving that it was manually imported
- Creating ImportedSignal records with explicit source labeling
- Routing content into normal triage and planning flows

Manual import is an explicit product boundary, not a placeholder for
unsupported scraping or unofficial API behavior.
"""

from __future__ import annotations

from typing import Optional

from app.connectors.contracts import NormalizedSignalData


class ManualImportHandler:
    """Handler for manual import of unsupported-channel content.

    ARCH:ManualImportBoundary
    ARCH:ManualImportDiscipline
    """

    @staticmethod
    def normalize_manual_import(
        content: str,
        source_label: Optional[str] = None,
        source_channel: Optional[str] = None,
        operator_notes: Optional[str] = None,
    ) -> NormalizedSignalData:
        """Normalize manually imported content into an ImportedSignal.

        Preserves:
        - Manual import origin (always explicit)
        - Optional source labeling (e.g. "WhatsApp - Project X")
        - Optional channel indication
        - Operator notes about the import

        The import mode is always explicitly 'manual_paste' — this is
        never confused with API-imported content.
        """
        metadata: dict = {
            "import_mode": "manual",
            "provider": "manual",
        }
        if source_channel:
            metadata["source_channel"] = source_channel
        if operator_notes:
            metadata["operator_notes"] = operator_notes

        return NormalizedSignalData(
            signal_type="manual_paste",
            source_label=source_label,
            content=content,
            raw_metadata=metadata,
        )

