"""API tests for project CRUD — create, read, update, archive.

TEST:ProjectCRUD.Api.CreateReadUpdateArchive
TEST:ProjectCRUD.Api.ValidationRejectsEmptyName
TEST:ProjectCRUD.Api.ArchiveFiltersFromListByDefault
TEST:ProjectCRUD.Api.ArchiveEndpointSetsStatusAndFlag

REQ:ProjectCRUD
PLAN:WorkstreamE.PackageE11.ProjectCrudApi
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.db import get_session


# ── Fixtures ─────────────────────────────────────────────────────

_CLEANUP_TABLES = [
    "extracted_actions",
    "waiting_on_records",
    "blocker_records",
    "work_items",
    "projects",
]


@pytest.fixture(autouse=True)
def _clean_tables(client):
    """Ensure tables are clean before and after each test."""
    session = get_session()
    for table in _CLEANUP_TABLES:
        session.execute(text(f"DELETE FROM {table}"))
    session.commit()
    session.close()
    yield
    session = get_session()
    for table in _CLEANUP_TABLES:
        session.execute(text(f"DELETE FROM {table}"))
    session.commit()
    session.close()


# ── Create ───────────────────────────────────────────────────────


class TestCreateProject:
    """TEST:ProjectCRUD.Api.CreateReadUpdateArchive"""

    def test_create_returns_201_with_detail(self, client):
        resp = client.post("/projects", json={
            "name": "New Project",
            "objective": "Build something",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "New Project"
        assert data["objective"] == "Build something"
        assert data["status"] == "active"
        assert data["archived"] is False
        assert "id" in data
        assert "created_at" in data

    def test_create_with_all_fields(self, client):
        resp = client.post("/projects", json={
            "name": "Full Project",
            "objective": "Full objective",
            "short_summary": "A summary",
            "status": "planning",
            "phase": "discovery",
            "priority_band": "high",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["phase"] == "discovery"
        assert data["priority_band"] == "high"
        assert data["short_summary"] == "A summary"
        assert data["status"] == "planning"

    def test_create_defaults_status_to_active(self, client):
        resp = client.post("/projects", json={"name": "Defaulted"})
        assert resp.status_code == 201
        assert resp.json()["status"] == "active"

    def test_create_rejects_empty_name(self, client):
        """TEST:ProjectCRUD.Api.ValidationRejectsEmptyName"""
        resp = client.post("/projects", json={"name": ""})
        assert resp.status_code == 422

    def test_create_rejects_whitespace_only_name(self, client):
        resp = client.post("/projects", json={"name": "   "})
        assert resp.status_code == 422

    def test_create_strips_name_whitespace(self, client):
        resp = client.post("/projects", json={"name": "  Trimmed  "})
        assert resp.status_code == 201
        assert resp.json()["name"] == "Trimmed"

    def test_created_project_appears_in_list(self, client):
        create_resp = client.post("/projects", json={"name": "Listed"})
        assert create_resp.status_code == 201
        project_id = create_resp.json()["id"]

        list_resp = client.get("/projects")
        assert list_resp.status_code == 200
        ids = [p["id"] for p in list_resp.json()]
        assert project_id in ids


# ── Read ─────────────────────────────────────────────────────────


class TestReadProject:
    def test_get_project_detail(self, client):
        create_resp = client.post("/projects", json={
            "name": "Readable",
            "objective": "Detail test",
        })
        pid = create_resp.json()["id"]

        resp = client.get(f"/projects/{pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Readable"
        assert data["objective"] == "Detail test"
        assert isinstance(data["open_items"], list)
        assert isinstance(data["blockers"], list)

    def test_get_nonexistent_returns_404(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/projects/{fake_id}")
        assert resp.status_code == 404


# ── Update ───────────────────────────────────────────────────────


class TestUpdateProject:
    def test_update_name(self, client):
        create_resp = client.post("/projects", json={"name": "Original"})
        pid = create_resp.json()["id"]

        resp = client.patch(f"/projects/{pid}", json={"name": "Renamed"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"

    def test_partial_update_preserves_unset_fields(self, client):
        create_resp = client.post("/projects", json={
            "name": "Partial",
            "objective": "Keep me",
            "phase": "design",
        })
        pid = create_resp.json()["id"]

        resp = client.patch(f"/projects/{pid}", json={"phase": "build"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["phase"] == "build"
        assert data["objective"] == "Keep me"
        assert data["name"] == "Partial"

    def test_update_rejects_empty_name(self, client):
        create_resp = client.post("/projects", json={"name": "Valid"})
        pid = create_resp.json()["id"]

        resp = client.patch(f"/projects/{pid}", json={"name": ""})
        assert resp.status_code == 422

    def test_update_nonexistent_returns_404(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.patch(f"/projects/{fake_id}", json={"name": "Nope"})
        assert resp.status_code == 404

    def test_update_status(self, client):
        create_resp = client.post("/projects", json={"name": "Statusful"})
        pid = create_resp.json()["id"]

        resp = client.patch(f"/projects/{pid}", json={"status": "paused"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "paused"


# ── Archive ──────────────────────────────────────────────────────


class TestArchiveProject:
    """TEST:ProjectCRUD.Api.ArchiveEndpointSetsStatusAndFlag"""

    def test_archive_sets_status_and_flag(self, client):
        create_resp = client.post("/projects", json={"name": "Archivable"})
        pid = create_resp.json()["id"]

        resp = client.post(f"/projects/{pid}/archive")
        assert resp.status_code == 200
        data = resp.json()
        assert data["archived"] is True
        assert data["status"] == "archived"

    def test_archive_nonexistent_returns_404(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.post(f"/projects/{fake_id}/archive")
        assert resp.status_code == 404

    def test_archive_already_archived_returns_409(self, client):
        create_resp = client.post("/projects", json={"name": "Double"})
        pid = create_resp.json()["id"]

        client.post(f"/projects/{pid}/archive")
        resp = client.post(f"/projects/{pid}/archive")
        assert resp.status_code == 409

    def test_archived_project_excluded_from_list_by_default(self, client):
        """TEST:ProjectCRUD.Api.ArchiveFiltersFromListByDefault"""
        create_resp = client.post("/projects", json={"name": "WillArchive"})
        pid = create_resp.json()["id"]

        client.post(f"/projects/{pid}/archive")

        list_resp = client.get("/projects")
        ids = [p["id"] for p in list_resp.json()]
        assert pid not in ids

    def test_archived_project_included_with_query_param(self, client):
        create_resp = client.post("/projects", json={"name": "Included"})
        pid = create_resp.json()["id"]

        client.post(f"/projects/{pid}/archive")

        list_resp = client.get("/projects?include_archived=true")
        ids = [p["id"] for p in list_resp.json()]
        assert pid in ids

    def test_archived_project_still_accessible_by_id(self, client):
        create_resp = client.post("/projects", json={"name": "StillGet"})
        pid = create_resp.json()["id"]

        client.post(f"/projects/{pid}/archive")

        resp = client.get(f"/projects/{pid}")
        assert resp.status_code == 200
        assert resp.json()["archived"] is True

