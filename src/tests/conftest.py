"""Root conftest — shared fixtures for the Glimmer test suite.

Provides a configured test client, isolated test database session,
and programmatic marker application for verification-pack membership.

WORKG:WG1 — Core test harness baseline
WORKG:WG3 — Smoke pack markers
WORKG:WG4 — Workstream pack markers
"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.main import create_app
from app.models import Base


# ── Exclude live/ tests from normal collection ───────────────────────
# Live browser tests require a real Chrome instance and are run
# explicitly via `pytest tests/live/ -v -s`. They must not be
# collected by the standard `pytest tests/` command.
collect_ignore_glob = ["live/*"]


# ── Disable LLM per-task toggles in tests by default ─────────────────
# Unless a test explicitly enables LLM, the graph/service wiring
# should use the deterministic path.  This avoids tests hanging on
# unreachable LM Studio.
os.environ.setdefault("GLIMMER_INFERENCE_LLM_CLASSIFICATION_ENABLED", "false")
os.environ.setdefault("GLIMMER_INFERENCE_LLM_EXTRACTION_ENABLED", "false")
os.environ.setdefault("GLIMMER_INFERENCE_LLM_PRIORITIZATION_ENABLED", "false")
os.environ.setdefault("GLIMMER_INFERENCE_LLM_DRAFTING_ENABLED", "false")
os.environ.setdefault("GLIMMER_INFERENCE_LLM_BRIEFING_ENABLED", "false")


# ── Pack membership: file-path → markers ─────────────────────────────
# Maps test file name prefixes to their verification-pack markers.
# Applied programmatically so no test file needs modification.

_FILE_PACK_MAP: dict[str, list[str]] = {
    # Smoke + Foundation (Workstream A)
    "test_smoke": ["smoke", "workstream_a", "release"],
    "test_persistence_baseline": ["workstream_a"],
    # Workstream B — Domain and Memory
    "test_domain_audit": ["workstream_b", "data_integrity", "release"],
    "test_domain_channel": ["workstream_b"],
    "test_domain_drafting": ["workstream_b"],
    "test_domain_execution": ["workstream_b"],
    "test_domain_interpretation": ["workstream_b", "data_integrity"],
    "test_domain_operator": ["workstream_b"],
    "test_domain_persona": ["workstream_b"],
    "test_domain_portfolio": ["workstream_b", "release"],
    "test_domain_source": ["workstream_b", "data_integrity", "release"],
    "test_domain_stakeholder": ["workstream_b"],
    "test_domain_summary": ["workstream_b", "data_integrity"],
    # Workstream C — Connectors
    "test_connector_context": ["workstream_c"],
    "test_connector_framework": ["workstream_c", "release"],
    "test_connector_gcal": ["workstream_c"],
    "test_connector_gmail": ["workstream_c", "release"],
    "test_connector_intake": ["workstream_c"],
    "test_connector_dispatch": ["workstream_c", "workstream_d", "workstream_i", "release"],
    "test_connector_manual": ["workstream_c"],
    "test_connector_mscal": ["workstream_c"],
    "test_connector_msmail": ["workstream_c"],
    "test_connector_sync": ["workstream_c"],
    "test_connector_telegram": ["workstream_c"],
    # Workstream D — Triage and Prioritization
    "test_triage_classification": ["workstream_d", "release"],
    "test_triage_extraction": ["workstream_d"],
    "test_triage_intake": ["workstream_d", "release"],
    "test_triage_api": ["workstream_d"],
    "test_planner_focus": ["workstream_d", "release"],
    "test_planner_nextsteps": ["workstream_d"],
    "test_planner_refresh": ["workstream_d"],
    "test_drafting_handoff": ["workstream_d"],
    "test_triage_pipeline": ["workstream_d", "workstream_i", "release"],
    "test_draft_creation": ["workstream_e", "workstream_i", "release"],
    # Workstream E — Drafting and UI
    "test_projects_drafts": ["workstream_e", "release"],
    "test_project_crud": ["workstream_e", "release"],
    "test_persona": ["workstream_e"],
    "test_persona_conversation": ["workstream_e", "release"],
    "test_staged_persistence": ["workstream_e", "release"],
    "test_paste_in": ["workstream_e", "release"],
    "test_contextual_ask": ["workstream_e", "release"],
    "test_operator": ["workstream_e"],
    "test_operational_support": ["workstream_e"],
    # Workstream F — Voice and Companion
    "test_voice_session_bootstrap": ["workstream_f"],
    "test_voice_transcript_normalization": ["workstream_f"],
    "test_voice_continuity": ["workstream_f"],
    "test_voice_routing": ["workstream_f", "release"],
    "test_voice_spoken_briefing": ["workstream_f"],
    "test_voice_api": ["workstream_f"],
    "test_telegram_companion": ["workstream_f"],
    "test_telegram_api": ["workstream_f"],
    "test_cross_surface_handoff": ["workstream_f", "release"],
    # Data integrity (cross-cutting — additional tests)
    "test_data_integrity_pack": ["data_integrity", "release"],
    # Workstream H — Deep Research and Expert Advice
    "test_research_models": ["workstream_h", "data_integrity"],
    "test_research_adapter": ["workstream_h", "release"],
    "test_research_escalation": ["workstream_h", "release"],
    "test_research_api": ["workstream_h", "release"],
    "test_chrome_lifecycle": ["workstream_h", "release"],
    # Live browser tests (excluded from normal collection, run explicitly)
    "test_live_browser_connection": ["workstream_h", "manual_only"],
    "test_live_expert_advice": ["workstream_h", "manual_only"],
    # Workstream I — LLM Integration Layer
    "test_inference_provider": ["workstream_i"],
    "test_prompt_framework": ["workstream_i"],
    "test_llm_classification": ["workstream_i"],
    "test_llm_extraction": ["workstream_i"],
    "test_llm_tasks": ["workstream_i"],
    "test_llm_orchestration": ["workstream_i", "release"],
    "test_llm_wiring": ["workstream_i", "release"],
    "test_inference_api": ["workstream_i", "release"],
    "test_live_llm_classification": ["workstream_i", "manual_only"],
}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Apply verification-pack markers to collected tests based on file name."""
    for item in items:
        filename = os.path.basename(item.fspath)
        stem = filename.replace(".py", "")
        if stem in _FILE_PACK_MAP:
            for marker_name in _FILE_PACK_MAP[stem]:
                item.add_marker(getattr(pytest.mark, marker_name))


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for verification packs."""
    markers = [
        "smoke: Smoke pack — baseline startup and reachability proof",
        "workstream_a: Workstream A — Foundation verification",
        "workstream_b: Workstream B — Domain and Memory verification",
        "workstream_c: Workstream C — Connectors verification",
        "workstream_d: Workstream D — Triage and Prioritization verification",
        "workstream_e: Workstream E — Drafting and UI verification",
        "workstream_f: Workstream F — Voice and Companion verification",
        "workstream_h: Workstream H — Deep Research and Expert Advice verification",
        "workstream_i: Workstream I — LLM Integration Layer verification",
        "data_integrity: Data-integrity regression — cross-cutting memory spine protection",
        "release: Release pack — representative cross-system confidence",
        "manual_only: Manual-only scenario — requires human verification",
        "deferred: Deferred scenario — automation not yet practical",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def test_engine():
    """Create a SQLAlchemy engine pointed at the test database."""
    settings = get_settings()
    engine = create_engine(settings.test_database_url, echo=False)
    # Ensure tables exist in the test database
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    """Provide a transactional database session that rolls back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient against a fresh app instance."""
    app = create_app()
    with TestClient(app) as c:
        yield c







