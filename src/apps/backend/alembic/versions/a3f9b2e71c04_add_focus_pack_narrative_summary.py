"""Add narrative_summary to focus_packs.

Revision ID: a3f9b2e71c04
Revises: 1c7c7d6aa26a
Create Date: 2026-04-14

PLAN:WorkstreamI.PackageI8.OrchestrationWiring
Adds a text column for LLM-generated narrative priority summaries.
"""

from alembic import op
import sqlalchemy as sa

revision = "a3f9b2e71c04"
down_revision = "1c7c7d6aa26a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "focus_packs",
        sa.Column("narrative_summary", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("focus_packs", "narrative_summary")

