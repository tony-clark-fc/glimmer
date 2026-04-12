"""Domain stakeholder and identity persistence tests.

TEST:Domain.StakeholderIdentity.MultiIdentityLinking
"""

from __future__ import annotations

from app.models.portfolio import Project
from app.models.stakeholder import (
    Stakeholder,
    StakeholderIdentity,
    StakeholderProjectLink,
)


class TestStakeholderBasics:
    """Stakeholder CRUD basics."""

    def test_create_stakeholder_persists(self, db_session) -> None:
        s = Stakeholder(display_name="Alice Chen")
        db_session.add(s)
        db_session.flush()

        fetched = db_session.get(Stakeholder, s.id)
        assert fetched is not None
        assert fetched.display_name == "Alice Chen"

    def test_stakeholder_fields_persist(self, db_session) -> None:
        s = Stakeholder(
            display_name="Bob Alvarez",
            organization="Acme Corp",
            role_title="VP Engineering",
            notes="Key decision-maker",
            relationship_importance="high",
            communication_style_hints="Prefers concise, data-driven messages",
        )
        db_session.add(s)
        db_session.flush()

        fetched = db_session.get(Stakeholder, s.id)
        assert fetched is not None
        assert fetched.organization == "Acme Corp"
        assert fetched.role_title == "VP Engineering"
        assert fetched.relationship_importance == "high"
        assert "concise" in fetched.communication_style_hints


class TestMultiIdentityLinking:
    """TEST:Domain.StakeholderIdentity.MultiIdentityLinking

    A stakeholder can have multiple identities across channels
    without forced merging.
    """

    def test_stakeholder_has_multiple_email_identities(self, db_session) -> None:
        """One stakeholder with two email addresses."""
        s = Stakeholder(display_name="Carol Davis")
        db_session.add(s)
        db_session.flush()

        id1 = StakeholderIdentity(
            stakeholder_id=s.id,
            channel_type="email",
            identity_value="carol@company.com",
        )
        id2 = StakeholderIdentity(
            stakeholder_id=s.id,
            channel_type="email",
            identity_value="carol.davis@personal.com",
        )
        db_session.add_all([id1, id2])
        db_session.flush()

        db_session.refresh(s)
        assert len(s.identities) == 2
        values = {i.identity_value for i in s.identities}
        assert values == {"carol@company.com", "carol.davis@personal.com"}

    def test_stakeholder_has_cross_channel_identities(self, db_session) -> None:
        """One stakeholder with email + telegram identities."""
        s = Stakeholder(display_name="Dan Evans")
        db_session.add(s)
        db_session.flush()

        email_id = StakeholderIdentity(
            stakeholder_id=s.id,
            channel_type="email",
            identity_value="dan@example.com",
        )
        tg_id = StakeholderIdentity(
            stakeholder_id=s.id,
            channel_type="telegram",
            identity_value="@danevans",
        )
        db_session.add_all([email_id, tg_id])
        db_session.flush()

        db_session.refresh(s)
        channels = {i.channel_type for i in s.identities}
        assert channels == {"email", "telegram"}

    def test_identity_tenant_context_persists(self, db_session) -> None:
        """Tenant/workspace context is preserved on identities."""
        s = Stakeholder(display_name="Eve Fischer")
        db_session.add(s)
        db_session.flush()

        identity = StakeholderIdentity(
            stakeholder_id=s.id,
            channel_type="email",
            identity_value="eve@contoso.com",
            tenant_context="contoso.onmicrosoft.com",
            verification_state="confirmed",
        )
        db_session.add(identity)
        db_session.flush()

        fetched = db_session.get(StakeholderIdentity, identity.id)
        assert fetched is not None
        assert fetched.tenant_context == "contoso.onmicrosoft.com"
        assert fetched.verification_state == "confirmed"

    def test_two_stakeholders_same_channel_different_identities(
        self, db_session
    ) -> None:
        """Different stakeholders can have identities in the same channel."""
        s1 = Stakeholder(display_name="Grace")
        s2 = Stakeholder(display_name="Heidi")
        db_session.add_all([s1, s2])
        db_session.flush()

        id1 = StakeholderIdentity(
            stakeholder_id=s1.id,
            channel_type="email",
            identity_value="grace@example.com",
        )
        id2 = StakeholderIdentity(
            stakeholder_id=s2.id,
            channel_type="email",
            identity_value="heidi@example.com",
        )
        db_session.add_all([id1, id2])
        db_session.flush()

        db_session.refresh(s1)
        db_session.refresh(s2)
        assert len(s1.identities) == 1
        assert len(s2.identities) == 1
        assert s1.identities[0].identity_value != s2.identities[0].identity_value

    def test_identity_not_auto_merged(self, db_session) -> None:
        """Two stakeholders with overlapping identity values remain separate."""
        s1 = Stakeholder(display_name="Ivan")
        s2 = Stakeholder(display_name="Judy")
        db_session.add_all([s1, s2])
        db_session.flush()

        # Both share a similar-looking address domain but belong to
        # different stakeholders — model must keep them separate.
        db_session.add(
            StakeholderIdentity(
                stakeholder_id=s1.id,
                channel_type="email",
                identity_value="contact@acme.com",
            )
        )
        db_session.add(
            StakeholderIdentity(
                stakeholder_id=s2.id,
                channel_type="email",
                identity_value="support@acme.com",
            )
        )
        db_session.flush()

        db_session.refresh(s1)
        db_session.refresh(s2)
        assert s1.identities[0].stakeholder_id == s1.id
        assert s2.identities[0].stakeholder_id == s2.id


class TestStakeholderProjectLink:
    """Stakeholder-project linking with per-project context."""

    def test_link_stakeholder_to_project(self, db_session) -> None:
        project = Project(name="Link Test Project")
        stakeholder = Stakeholder(display_name="Karen Lee")
        db_session.add_all([project, stakeholder])
        db_session.flush()

        link = StakeholderProjectLink(
            stakeholder_id=stakeholder.id,
            project_id=project.id,
            relationship_type="client",
            importance_within_project="high",
            notes="Primary point of contact",
        )
        db_session.add(link)
        db_session.flush()

        fetched = db_session.get(StakeholderProjectLink, link.id)
        assert fetched is not None
        assert fetched.stakeholder_id == stakeholder.id
        assert fetched.project_id == project.id
        assert fetched.relationship_type == "client"
        assert fetched.importance_within_project == "high"

    def test_stakeholder_linked_to_multiple_projects(self, db_session) -> None:
        """Same stakeholder can appear in multiple projects with different roles."""
        p1 = Project(name="Project X")
        p2 = Project(name="Project Y")
        s = Stakeholder(display_name="Larry Morgan")
        db_session.add_all([p1, p2, s])
        db_session.flush()

        link1 = StakeholderProjectLink(
            stakeholder_id=s.id,
            project_id=p1.id,
            relationship_type="sponsor",
        )
        link2 = StakeholderProjectLink(
            stakeholder_id=s.id,
            project_id=p2.id,
            relationship_type="advisor",
        )
        db_session.add_all([link1, link2])
        db_session.flush()

        db_session.refresh(s)
        assert len(s.project_links) == 2
        types = {pl.relationship_type for pl in s.project_links}
        assert types == {"sponsor", "advisor"}

    def test_link_open_commitments_persist(self, db_session) -> None:
        """Open commitments on a project link persist correctly."""
        project = Project(name="Commitment Project")
        stakeholder = Stakeholder(display_name="Mallory")
        db_session.add_all([project, stakeholder])
        db_session.flush()

        link = StakeholderProjectLink(
            stakeholder_id=stakeholder.id,
            project_id=project.id,
            open_commitments="Deliver API spec by end of week",
        )
        db_session.add(link)
        db_session.flush()

        fetched = db_session.get(StakeholderProjectLink, link.id)
        assert fetched is not None
        assert "API spec" in fetched.open_commitments

