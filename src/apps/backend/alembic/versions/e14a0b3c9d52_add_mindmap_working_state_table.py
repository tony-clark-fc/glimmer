"""add_mindmap_working_state_table

Revision ID: e14a0b3c9d52
Revises: e12a0c4f7b91
Create Date: 2026-04-16 12:00:00.000000

PLAN:WorkstreamE.PackageE14.PersonaPageStagedPersistence
ARCH:MindMapWorkingStateModel
ARCH:PersonaPage.StagedPersistence
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e14a0b3c9d52'
down_revision: Union[str, Sequence[str], None] = 'e12a0c4f7b91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add mindmap_working_states table for session backup/resumption."""
    op.create_table(
        'mindmap_working_states',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('candidate_nodes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('candidate_edges', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('state_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['persona_page_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id'),
    )


def downgrade() -> None:
    """Remove mindmap_working_states table."""
    op.drop_table('mindmap_working_states')

