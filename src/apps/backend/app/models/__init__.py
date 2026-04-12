"""SQLAlchemy declarative base for all Glimmer domain models."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Root declarative base — all domain models inherit from this."""

    pass


# Import all model modules so they register with Base.metadata.
# This import block must be kept current as new model files are added.
from app.models.portfolio import Project, ProjectWorkstream, Milestone  # noqa: E402, F401
from app.models.stakeholder import Stakeholder, StakeholderIdentity, StakeholderProjectLink  # noqa: E402, F401
from app.models.source import (  # noqa: E402, F401
    ConnectedAccount, AccountProfile, MessageThread, Message,
    CalendarEvent, ImportedSignal,
)
from app.models.interpretation import (  # noqa: E402, F401
    MessageClassification, ExtractedAction, ExtractedDecision,
    ExtractedDeadlineSignal,
)
from app.models.execution import (  # noqa: E402, F401
    WorkItem, DecisionRecord, RiskRecord, BlockerRecord, WaitingOnRecord,
)
from app.models.drafting import (  # noqa: E402, F401
    Draft, DraftVariant, BriefingArtifact, FocusPack,
)
from app.models.persona import (  # noqa: E402, F401
    PersonaAsset, PersonaClassification, PersonaSelectionEvent,
)
from app.models.channel import (  # noqa: E402, F401
    ChannelSession, TelegramConversationState, VoiceSessionState,
)
from app.models.summary import ProjectSummary, RefreshEvent  # noqa: E402, F401
from app.models.audit import AuditRecord  # noqa: E402, F401
