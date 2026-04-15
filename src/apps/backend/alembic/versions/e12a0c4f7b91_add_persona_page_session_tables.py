"""add_persona_page_session_tables

Revision ID: e12a0c4f7b91
Revises: 1c7c7d6aa26a
Create Date: 2026-04-15 18:00:00.000000

PLAN:WorkstreamE.PackageE12.PersonaPageConversationUi
ARCH:PersonaPageSessionModel
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e12a0c4f7b91'
down_revision: Union[str, Sequence[str], None] = '1c7c7d6aa26a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add persona page session and message tables."""
    op.create_table(
        'persona_page_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('channel_session_id', sa.UUID(), nullable=False),
        sa.Column('session_status', sa.String(length=50), nullable=False),
        sa.Column('workspace_mode', sa.String(length=50), nullable=True),
        sa.Column('summary_intent', sa.Text(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['channel_session_id'], ['channel_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'persona_page_messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('ordering', sa.Integer(), nullable=False),
        sa.Column('workspace_mode', sa.String(length=50), nullable=True),
        sa.Column('inference_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['persona_page_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Remove persona page session and message tables."""
    op.drop_table('persona_page_messages')
    op.drop_table('persona_page_sessions')

