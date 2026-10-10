import pytest
from unittest.mock import patch

from app.core.config import settings
from app.services.auth_service import (
    AuthService,
    InvalidBlizzardProfileError,
)


@pytest.fixture
def auth_service():
    return AuthService(settings)


@pytest.mark.parametrize("invalid_profile", [None, [], "unexpected"])
def test_get_account_characters_rejects_invalid_profile(
    auth_service,
    invalid_profile,
):
    """Vérifie qu'un profil Blizzard de structure invalide est rejeté."""

    with patch.object(
        auth_service,
        "get_account_profile",
        return_value=invalid_profile,
    ):
        with pytest.raises(
            InvalidBlizzardProfileError,
            match="Invalid Blizzard profile structure"
        ):
            auth_service.get_account_characters("fake-access-token")


@pytest.mark.parametrize(
    "invalid_accounts",
    [None, "unexpected", [None]],
)
def test_get_account_characters_rejects_invalid_accounts(
    auth_service,
    invalid_accounts,
):
    """Vérifie qu'une liste de comptes Blizzard mal formée est rejetée."""

    with patch.object(
        auth_service,
        "get_account_profile",
        return_value={"wow_accounts": invalid_accounts},
    ):
        with pytest.raises(
            InvalidBlizzardProfileError,
            match="Invalid Blizzard profile structure"
        ):
            auth_service.get_account_characters("fake-access-token")

@pytest.mark.parametrize(
    "invalid_characters",
    [None, "unexpected", [None]],
)
def test_get_account_characters_rejects_invalid_characters(
    auth_service,
    invalid_characters,
):
    """Vérifie qu'une liste de personnages mal formée est rejetée."""

    profile = {
        "wow_accounts": [
            {"characters": invalid_characters},
        ],
    }

    with patch.object(
        auth_service,
        "get_account_profile",
        return_value=profile,
    ):
        with pytest.raises(
            InvalidBlizzardProfileError,
            match="Invalid Blizzard profile structure"
        ):
            auth_service.get_account_characters("fake-access-token")

@pytest.mark.parametrize(
    "invalid_entry",
    [
        {"realm": "unexpected"},
        {"playable_class": "unexpected"},
        {"playable_race": "unexpected"},
        {"faction": "unexpected"},
        {"character": "unexpected"},
    ],
)
def test_get_account_characters_rejects_invalid_nested_data(
    auth_service,
    invalid_entry,
):
    """Vérifie que les objets imbriqués mal formés sont rejetés."""

    profile = {
        "wow_accounts": [
            {
                "characters": [
                    {
                        "id": 123,
                        "name": "Test",
                        **invalid_entry,
                    }
                ],
            },
        ],
    }

    with patch.object(
        auth_service,
        "get_account_profile",
        return_value=profile,
    ):
        with pytest.raises(
            InvalidBlizzardProfileError,
            match="Invalid Blizzard profile structure"
        ):
            auth_service.get_account_characters("fake-access-token")
