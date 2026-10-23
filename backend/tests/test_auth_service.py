from unittest.mock import patch

import pytest

from app.core.config import settings
from app.services.auth_service import (
    AuthService,
    InvalidBlizzardProfileError,
)


@pytest.fixture
def auth_service():
    """Crée un service propre pour chaque test."""

    # Le cache est partagé au niveau de la classe : on le vide avant
    # et après chaque test pour éviter les interférences entre tests.
    AuthService._character_media_cache.clear()
    service = AuthService(settings)

    yield service

    AuthService._character_media_cache.clear()


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
            match="Invalid Blizzard profile structure",
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
            match="Invalid Blizzard profile structure",
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
            match="Invalid Blizzard profile structure",
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
            match="Invalid Blizzard profile structure",
        ):
            auth_service.get_account_characters("fake-access-token")


def test_get_character_media_prefers_inset(auth_service):
    """Privilégie inset pour le portrait et récupère le rendu main."""

    with patch("app.services.auth_service.httpx.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "assets": [
                {"key": "avatar", "value": "https://example.com/avatar.jpg"},
                {"key": "inset", "value": "https://example.com/inset.jpg"},
                {"key": "main", "value": "https://example.com/main.jpg"},
            ],
        }
        mock_get.return_value.raise_for_status.return_value = None

        result = auth_service.get_character_media(
            "fake-access-token", "dalaran", "Fastnfurieuz"
        )

    assert result == {
        "portrait_url": "https://example.com/inset.jpg",
        "main_art_url": "https://example.com/main.jpg",
    }


def test_get_character_media_falls_back_to_avatar(auth_service):
    """Utilise avatar lorsque inset est absent."""

    with patch("app.services.auth_service.httpx.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "assets": [
                {"key": "avatar", "value": "https://example.com/avatar.jpg"},
                {"key": "main", "value": "https://example.com/main.jpg"},
            ],
        }
        mock_get.return_value.raise_for_status.return_value = None

        result = auth_service.get_character_media(
            "fake-access-token", "dalaran", "Fastnfurieuz"
        )

    assert result == {
        "portrait_url": "https://example.com/avatar.jpg",
        "main_art_url": "https://example.com/main.jpg",
    }


def test_get_character_media_returns_none_without_available_assets(
    auth_service,
):
    """Retourne des URL nulles si aucun média n'est disponible."""

    with patch("app.services.auth_service.httpx.get") as mock_get:
        mock_get.return_value.json.return_value = {"assets": []}
        mock_get.return_value.raise_for_status.return_value = None

        result = auth_service.get_character_media(
            "fake-access-token", "dalaran", "Fastnfurieuz"
        )

    assert result == {
        "portrait_url": None,
        "main_art_url": None,
    }


def test_get_character_media_uses_cache(auth_service):
    """Le cache conserve les deux médias sans nouvel appel HTTP."""

    cache_key = ("dalaran", "fastnfurieuz")
    AuthService._character_media_cache.pop(cache_key, None)

    with patch("app.services.auth_service.httpx.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "assets": [
                {"key": "inset", "value": "https://example.com/inset.jpg"},
                {"key": "main", "value": "https://example.com/main.jpg"},
            ],
        }
        mock_get.return_value.raise_for_status.return_value = None

        first_result = auth_service.get_character_media(
            "fake-access-token", "dalaran", "Fastnfurieuz"
        )
        second_result = auth_service.get_character_media(
            "fake-access-token", "dalaran", "Fastnfurieuz"
        )

    expected = {
        "portrait_url": "https://example.com/inset.jpg",
        "main_art_url": "https://example.com/main.jpg",
    }

    assert first_result == expected
    assert second_result == expected
    mock_get.assert_called_once()


def test_get_character_profile_returns_profile(auth_service):
    """Vérifie que le profil détaillé est correctement récupéré."""

    expected_profile = {
        "name": "Fastnfurieuz",
        "average_item_level": 250,
        "equipped_item_level": 248,
    }

    with patch(
        "app.services.auth_service.httpx.get",
    ) as mock_get:
        mock_get.return_value.json.return_value = expected_profile
        mock_get.return_value.raise_for_status.return_value = None

        result = auth_service.get_character_profile(
            "fake-access-token",
            "dalaran",
            "Fastnfurieuz",
        )

    assert result == expected_profile

    # Vérifie que l'endpoint individuel et les paramètres sont corrects.
    mock_get.assert_called_once_with(
        "https://eu.api.blizzard.com/profile/wow/character/dalaran/fastnfurieuz",
        params={
            "namespace": "profile-eu",
            "locale": "fr_FR",
        },
        headers={
            "Authorization": "Bearer fake-access-token",
        },
        timeout=10.0,
    )


def test_get_character_profile_rejects_invalid_response(auth_service):
    """Vérifie qu'une réponse qui n'est pas un dictionnaire est rejetée."""

    with patch(
        "app.services.auth_service.httpx.get",
    ) as mock_get:
        mock_get.return_value.json.return_value = []

        with pytest.raises(
            InvalidBlizzardProfileError,
            match="Invalid Blizzard profile structure",
        ):
            auth_service.get_character_profile(
                "fake-access-token",
                "dalaran",
                "Fastnfurieuz",
            )


def test_get_character_equipment_returns_equipment(auth_service):
    """Vérifie que l'équipement Blizzard est correctement récupéré."""

    expected_equipment = {
        "equipped_items": [
            {
                "slot": {"type": "HEAD", "name": "Tête"},
                "item": {"id": 12345},
                "level": {"value": 250},
            }
        ]
    }

    with patch(
        "app.services.auth_service.httpx.get",
    ) as mock_get:
        mock_get.return_value.json.return_value = expected_equipment
        mock_get.return_value.raise_for_status.return_value = None

        result = auth_service.get_character_equipment(
            "fake-access-token",
            "dalaran",
            "Fastnfurieuz",
        )

    assert result == expected_equipment

    # Vérifie l'endpoint, le namespace et l'authentification.
    call_args = mock_get.call_args
    assert call_args.args[0].endswith(
        "/profile/wow/character/dalaran/fastnfurieuz/equipment"
    )
    assert call_args.kwargs["params"]["namespace"] == "profile-eu"
    assert call_args.kwargs["headers"]["Authorization"] == (
        "Bearer fake-access-token"
    )


def test_get_character_equipment_rejects_invalid_response(auth_service):
    """Vérifie qu'une réponse sans liste d'objets est rejetée."""

    with patch(
        "app.services.auth_service.httpx.get",
    ) as mock_get:
        mock_get.return_value.json.return_value = {}
        mock_get.return_value.raise_for_status.return_value = None

        with pytest.raises(InvalidBlizzardProfileError):
            auth_service.get_character_equipment(
                "fake-access-token",
                "dalaran",
                "Fastnfurieuz",
            )
