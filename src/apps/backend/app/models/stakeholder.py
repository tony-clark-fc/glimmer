"""Stakeholder and identity domain models.

ARCH:StakeholderModel
ARCH:StakeholderIdentityModel
ARCH:StakeholderProjectLinkModel

These entities allow multi-identity stakeholder tracking without
premature identity merging.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


class Stakeholder(Base):
    """A person or meaningful external/internal actor related to projects."""

    __tablename__ = "stakeholders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    role_title: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    relationship_importance: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    communication_style_hints: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    identities: Mapped[list["StakeholderIdentity"]] = relationship(
        back_populates="stakeholder", cascade="all, delete-orphan"
    )
    project_links: Mapped[list["StakeholderProjectLink"]] = relationship(
        back_populates="stakeholder", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Stakeholder {self.id!s:.8} name={self.display_name!r}>"


class StakeholderIdentity(Base):
    """One concrete addressable identity for a stakeholder.

    Allows a single stakeholder to have multiple email addresses,
    Telegram handles, etc. without forced merging.
    """

    __tablename__ = "stakeholder_identities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    stakeholder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stakeholders.id", ondelete="CASCADE"),
        nullable=False,
    )
    channel_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # email, telegram, slack, etc.
    identity_value: Mapped[str] = mapped_column(
        String(512), nullable=False
    )  # the email address, handle, etc.
    tenant_context: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )  # workspace / domain where relevant
    verification_state: Mapped[str] = mapped_column(
        String(50), nullable=False, default="unverified"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    stakeholder: Mapped["Stakeholder"] = relationship(
        back_populates="identities"
    )

    def __repr__(self) -> str:
        return (
            f"<StakeholderIdentity {self.id!s:.8} "
            f"{self.channel_type}:{self.identity_value!r}>"
        )


class StakeholderProjectLink(Base):
    """Relationship between a stakeholder and a project.

    Supports per-project role, salience, and context.
    """

    __tablename__ = "stakeholder_project_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    stakeholder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stakeholders.id", ondelete="CASCADE"),
        nullable=False,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    relationship_type: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # client, sponsor, lead, etc.
    importance_within_project: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    open_commitments: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    stakeholder: Mapped["Stakeholder"] = relationship(
        back_populates="project_links"
    )

    def __repr__(self) -> str:
        return (
            f"<StakeholderProjectLink {self.id!s:.8} "
            f"stakeholder={self.stakeholder_id!s:.8} "
            f"project={self.project_id!s:.8}>"
        )

