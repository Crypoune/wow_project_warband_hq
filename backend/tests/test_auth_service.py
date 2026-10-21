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
    """Vérifie que le portrait inset est privilégié lorsqu'il existe."""

    with patch(
        "app.services.auth_service.httpx.get",
    ) as mock_get:
        # On simule une réponse Blizzard contenant les deux portraits.
        mock_get.return_value.json.return_value = {
            "assets": [
                {
                    "key": "avatar",
                    "value": "https://example.com/avatar.jpg",
                },
                {
                    "key": "inset",
                    "value": "https://example.com/inset.jpg",
                },
            ],
        }
        mock_get.return_value.raise_for_status.return_value = None

        result = auth_service.get_character_media(
            "fake-access-token",
            "dalaran",
            "Fastnfurieuz",
        )

    assert result == "https://example.com/inset.jpg"


def test_get_character_media_falls_back_to_avatar(auth_service):
    """Vérifie que le portrait avatar est utilisé sans inset."""

    with patch(
        "app.services.auth_service.httpx.get",
    ) as mock_get:
        # Cette fois, seul le portrait avatar est disponible.
        mock_get.return_value.json.return_value = {
            "assets": [
                {
                    "key": "avatar",
                    "value": "https://example.com/avatar.jpg",
                },
            ],
        }
        mock_get.return_value.raise_for_status.return_value = None

        result = auth_service.get_character_media(
            "fake-access-token",
            "dalaran",
            "Fastnfurieuz",
        )

    assert result == "https://example.com/avatar.jpg"


def test_get_character_media_returns_none_without_available_assets(
    auth_service,
):
    """Vérifie qu'aucune URL n'est renvoyée sans portrait exploitable."""

    with patch(
        "app.services.auth_service.httpx.get",
    ) as mock_get:
        # Une liste d'assets vide ne fournit aucun portrait.
        mock_get.return_value.json.return_value = {"assets": []}
        mock_get.return_value.raise_for_status.return_value = None

        result = auth_service.get_character_media(
            "fake-access-token",
            "dalaran",
            "Fastnfurieuz",
        )

    assert result is None


def test_get_character_media_uses_cache(auth_service):
    """Vérifie qu'un portrait en cache évite un nouvel appel HTTP."""

    cache_key = ("dalaran", "fastnfurieuz")

    # On garantit que ce test commence sans entrée préexistante.
    AuthService._character_media_cache.pop(cache_key, None)

    with patch(
        "app.services.auth_service.httpx.get",
    ) as mock_get:
        mock_get.return_value.json.return_value = {
            "assets": [
                {
                    "key": "inset",
                    "value": "https://example.com/inset.jpg",
                },
            ],
        }
        mock_get.return_value.raise_for_status.return_value = None

        # Premier appel : le portrait est récupéré et mis en cache.
        first_result = auth_service.get_character_media(
            "fake-access-token",
            "dalaran",
            "Fastnfurieuz",
        )

        # Deuxième appel : le résultat doit venir du cache.
        second_result = auth_service.get_character_media(
            "fake-access-token",
            "dalaran",
            "Fastnfurieuz",
        )

    assert first_result == "https://example.com/inset.jpg"
    assert second_result == first_result

    # Un seul appel HTTP doit avoir été effectué pour les deux demandes.
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
