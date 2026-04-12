"""Glimmer connector layer — bounded external-ingestion boundary.

ARCH:ConnectorIsolation
ARCH:ConnectorLayerIntent

This package contains the connector framework, provider-specific boundaries,
normalization contracts, and intake handoff logic. Connectors authenticate,
fetch, normalize, persist, and hand off. They do NOT perform triage, planning,
drafting, or accepted-state mutation.
"""

