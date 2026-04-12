"""Persona asset and classification persistence tests.

TEST:Domain.Persona.AssetsAndClassificationPersist
"""

from __future__ import annotations

from app.models.persona import (
    PersonaAsset,
    PersonaClassification,
    PersonaSelectionEvent,
)


class TestPersonaAssetsAndClassification:
    """TEST:Domain.Persona.AssetsAndClassificationPersist"""

    def test_persona_asset_persists(self, db_session) -> None:
        asset = PersonaAsset(
            label="Friendly Morning",
            asset_path="/assets/persona/friendly_morning.png",
            asset_type="avatar",
            is_active=True,
            is_default=True,
            notes="Default morning greeting persona",
        )
        db_session.add(asset)
        db_session.flush()

        fetched = db_session.get(PersonaAsset, asset.id)
        assert fetched is not None
        assert fetched.label == "Friendly Morning"
        assert fetched.is_default is True

    def test_asset_has_multiple_classifications(self, db_session) -> None:
        asset = PersonaAsset(
            label="Focused",
            asset_path="/assets/persona/focused.png",
            asset_type="avatar",
        )
        db_session.add(asset)
        db_session.flush()

        c1 = PersonaClassification(
            asset_id=asset.id,
            classification_type="mood",
            classification_value="focused",
        )
        c2 = PersonaClassification(
            asset_id=asset.id,
            classification_type="suitability",
            classification_value="drafting",
        )
        c3 = PersonaClassification(
            asset_id=asset.id,
            classification_type="tone",
            classification_value="professional",
        )
        db_session.add_all([c1, c2, c3])
        db_session.flush()

        db_session.refresh(asset)
        assert len(asset.classifications) == 3
        types = {c.classification_type for c in asset.classifications}
        assert types == {"mood", "suitability", "tone"}

    def test_persona_selection_event_persists(self, db_session) -> None:
        asset = PersonaAsset(
            label="Supportive",
            asset_path="/assets/persona/supportive.png",
            asset_type="avatar",
        )
        db_session.add(asset)
        db_session.flush()

        event = PersonaSelectionEvent(
            asset_id=asset.id,
            interaction_context="briefing",
            selection_reason="Operator has high calendar pressure today",
        )
        db_session.add(event)
        db_session.flush()

        fetched = db_session.get(PersonaSelectionEvent, event.id)
        assert fetched is not None
        assert fetched.interaction_context == "briefing"
        assert "calendar pressure" in fetched.selection_reason

    def test_multiple_assets_with_different_defaults(self, db_session) -> None:
        a1 = PersonaAsset(
            label="Default",
            asset_path="/assets/default.png",
            asset_type="avatar",
            is_default=True,
        )
        a2 = PersonaAsset(
            label="Alternative",
            asset_path="/assets/alt.png",
            asset_type="avatar",
            is_default=False,
        )
        db_session.add_all([a1, a2])
        db_session.flush()

        assert db_session.get(PersonaAsset, a1.id).is_default is True
        assert db_session.get(PersonaAsset, a2.id).is_default is False

