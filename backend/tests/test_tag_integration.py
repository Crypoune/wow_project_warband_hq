
import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.models import User, Character, Tag, CharacterTag
from app.services.tag_service import TagService


@pytest.fixture
def integration_context():
    url = make_url(os.environ["DATABASE_URL"])

    if url.database != "warband_hq_test":
        pytest.fail("Sécurité : les tests doivent utiliser warband_hq_test.")

    engine = create_engine(url)
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    # Identifiants uniques pour éviter les collisions entre exécutions.
    suffix = uuid4().hex
    tag_name = f"Integration Raid {suffix}"

    with Session() as db:
        user = User(blizzard_account_id=f"integration-user-{suffix}")
        other_user = User(blizzard_account_id=f"integration-other-{suffix}")

        db.add_all([user, other_user])
        db.commit()
        db.refresh(user)
        db.refresh(other_user)

        character = Character(
            blizzard_character_id=900001,
            user_id=user.id,
        )
        other_character = Character(
            blizzard_character_id=900002,
            user_id=other_user.id,
        )

        db.add_all([character, other_character])
        db.commit()
        db.refresh(character)
        db.refresh(other_character)

        ids = {
            "user": user.id,
            "other_user": other_user.id,
            "character": character.id,
            "other_character": other_character.id,
            "tag_name": tag_name,
        }

    try:
        yield ids
    finally:
        with Session() as db:
            # Supprimer d'abord les associations des personnages de test.
            db.query(CharacterTag).filter(
                CharacterTag.character_id.in_(
                    [ids["character"], ids["other_character"]]
                )
            ).delete(synchronize_session=False)

            # Les tags sont globaux : supprimer uniquement celui créé
            # par ce test, jamais tous les tags du catalogue.
            db.query(Tag).filter(Tag.name == ids["tag_name"]).delete(
                synchronize_session=False
            )

            db.query(Character).filter(
                Character.id.in_(
                    [ids["character"], ids["other_character"]]
                )
            ).delete(synchronize_session=False)

            db.query(User).filter(
                User.id.in_([ids["user"], ids["other_user"]])
            ).delete(synchronize_session=False)

            db.commit()

        engine.dispose()


def test_tag_lifecycle(integration_context):
    service = TagService()
    user_id = integration_context["user"]
    character_id = integration_context["character"]

    tag = service.create_tag(f"  {integration_context['tag_name']}  ")

    assert tag["name"] == integration_context["tag_name"]
    assert any(
        t["id"] == tag["id"]
        for t in service.get_tags()
    )

    assert service.assign_tag(user_id, character_id, tag["id"]) is True
    assert service.get_character_tags(user_id, character_id) == [tag]

    assert service.remove_tag(user_id, character_id, tag["id"]) is True
    assert service.get_character_tags(user_id, character_id) == []


def test_global_tag_can_be_assigned_by_another_user(integration_context):
    service = TagService()

    tag = service.create_tag(integration_context["tag_name"])

    # Un tag du catalogue global est utilisable par un autre utilisateur
    # sur son propre personnage.
    assert service.assign_tag(
        integration_context["other_user"],
        integration_context["other_character"],
        tag["id"],
    ) is True

    assert service.get_character_tags(
        integration_context["other_user"],
        integration_context["other_character"],
    ) == [tag]


def test_user_cannot_assign_tag_to_another_users_character(
    integration_context,
):
    service = TagService()
    tag = service.create_tag(integration_context["tag_name"])

    with pytest.raises(ValueError, match="Personnage introuvable"):
        service.assign_tag(
            integration_context["user"],
            integration_context["other_character"],
            tag["id"],
        )
