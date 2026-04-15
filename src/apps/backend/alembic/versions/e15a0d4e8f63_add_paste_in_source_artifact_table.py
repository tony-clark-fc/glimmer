"""add_paste_in_source_artifact_table

Revision ID: e15a0d4e8f63
Revises: e14a0b3c9d52
Create Date: 2026-04-16 18:00:00.000000

PLAN:WorkstreamE.PackageE15.PersonaPagePasteIn
ARCH:PasteInSourceArtifactModel
ARCH:PersonaPage.PasteInPipeline
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e15a0d4e8f63'
down_revision: Union[str, Sequence[str], None] = 'e14a0b3c9d52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add paste_in_source_artifacts table for raw paste-in provenance."""
    op.create_table(
        'paste_in_source_artifacts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('raw_content', sa.Text(), nullable=False),
        sa.Column('paste_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('content_type_hint', sa.String(50), nullable=False, server_default='freeform'),
        sa.Column('extraction_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('linked_candidate_node_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['persona_page_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_paste_in_source_artifacts_session_id', 'paste_in_source_artifacts', ['session_id'])


def downgrade() -> None:
    """Remove paste_in_source_artifacts table."""
    op.drop_index('ix_paste_in_source_artifacts_session_id', table_name='paste_in_source_artifacts')
    op.drop_table('paste_in_source_artifacts')

