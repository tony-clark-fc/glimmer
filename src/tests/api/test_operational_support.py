"""Operational support surface tests.

TEST:Foundation.AgentSupport.CoreSurfacesPresent

Verifies that the control documents, module instructions, agent skills,
and agent tools surfaces exist in the repository at expected locations.
"""

from __future__ import annotations

import os
from pathlib import Path

# Repo root is 4 levels up from this file: tests/api/ -> tests/ -> src/ -> Glimmer/
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"


def _exists(rel_path: str) -> bool:
    return (SRC / rel_path).exists() or (REPO_ROOT / rel_path).exists()


# ── TEST:Foundation.AgentSupport.CoreSurfacesPresent ─────────────────


class TestControlDocumentsExist:
    """Control-document directories contain at least one file."""

    def test_requirements_dir(self) -> None:
        d = SRC / "1. Requirements"
        assert d.is_dir(), f"Missing: {d}"
        assert any(d.iterdir()), "Requirements directory is empty"

    def test_architecture_dir(self) -> None:
        d = SRC / "2. Architecture"
        assert d.is_dir(), f"Missing: {d}"
        assert any(d.iterdir()), "Architecture directory is empty"

    def test_build_plan_dir(self) -> None:
        d = SRC / "3. Build Plan"
        assert d.is_dir(), f"Missing: {d}"
        assert any(d.iterdir()), "Build Plan directory is empty"

    def test_verification_dir(self) -> None:
        d = SRC / "4. Verification"
        assert d.is_dir(), f"Missing: {d}"
        assert any(d.iterdir()), "Verification directory is empty"

    def test_working_dir(self) -> None:
        d = SRC / "5. Working"
        assert d.is_dir(), f"Missing: {d}"
        assert any(d.iterdir()), "Working directory is empty"


class TestModuleInstructionsExist:
    """Module-scoped instruction files are present."""

    EXPECTED = [
        ".github/copilot-instructions.md",
        ".github/instructions/backend_orchestration_instructions.md",
        ".github/instructions/frontend_workspace_instructions.md",
        ".github/instructions/data_and_retrieval_instructions.md",
        ".github/instructions/connectors_instructions.md",
        ".github/instructions/testing_and_verification_instructions.md",
        ".github/instructions/voice_and_companion_instructions.md",
    ]

    def test_all_instruction_files_present(self) -> None:
        missing = [p for p in self.EXPECTED if not (REPO_ROOT / p).is_file()]
        assert not missing, f"Missing instruction files: {missing}"


class TestAgentSupportSurfacesExist:
    """Agent Skills and Agent Tools directories are present with READMEs."""

    def test_agent_skills_dir(self) -> None:
        d = SRC / "8. Agent Skills"
        assert d.is_dir(), f"Missing: {d}"
        assert any(f.suffix == ".md" for f in d.iterdir()), "No .md files in Agent Skills"

    def test_agent_tools_dir(self) -> None:
        d = SRC / "9. Agent Tools"
        assert d.is_dir(), f"Missing: {d}"
        assert any(f.name == "README.md" for f in d.iterdir()), "No README.md in Agent Tools"


class TestApplicationStructureExists:
    """Backend and frontend application areas exist with expected shape."""

    def test_backend_app_package(self) -> None:
        assert (SRC / "apps" / "backend" / "app" / "__init__.py").is_file()

    def test_backend_pyproject(self) -> None:
        assert (SRC / "apps" / "backend" / "pyproject.toml").is_file()

    def test_backend_alembic(self) -> None:
        assert (SRC / "apps" / "backend" / "alembic.ini").is_file()
        assert (SRC / "apps" / "backend" / "alembic" / "env.py").is_file()

    def test_frontend_package_json(self) -> None:
        assert (SRC / "apps" / "web" / "package.json").is_file()

    def test_frontend_layout(self) -> None:
        assert (SRC / "apps" / "web" / "src" / "app" / "layout.tsx").is_file()

    def test_test_directories_exist(self) -> None:
        for name in ("api", "integration", "graph", "browser"):
            d = SRC / "tests" / name
            assert d.is_dir(), f"Missing test directory: {d}"

