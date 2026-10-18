
import pytest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import (
    CurrentAuth,
    get_current_admin,
    get_current_auth,
    get_current_user,
)


client = TestClient(app)
AUTH = CurrentAuth(user_id=1, access_token="test-access-token")


def override_auth():
    return AUTH


def override_admin():
    return AUTH


def setup_function():
    app.dependency_overrides[get_current_auth] = override_auth
    app.dependency_overrides[get_current_admin] = override_admin


def teardown_function():
    app.dependency_overrides.clear()


def test_get_tags_success():
    tags = [{"id": 1, "name": "Raid"}]

    with patch("app.api.tags.tag_service.get_tags", return_value=tags):
        response = client.get("/api/tags")

    assert response.status_code == 200
    assert response.json() == {"tags": tags}


def test_create_tag_success():
    tag = {"id": 1, "name": "Raid"}

    with patch(
        "app.api.tags.tag_service.create_tag",
        return_value=tag,
    ) as service:
        response = client.post("/api/tags", json={"name": "Raid"})

    assert response.status_code == 200
    assert response.json() == {"tag": tag}
    service.assert_called_once_with(name="Raid")


def test_create_tag_rejects_empty_name():
    response = client.post("/api/tags", json={"name": ""})

    assert response.status_code == 422


def test_create_tag_rejects_name_over_50_characters():
    response = client.post("/api/tags", json={"name": "a" * 51})

    assert response.status_code == 422


def test_get_tag_success():
    tag = {"id": 1, "name": "Raid"}

    with patch("app.api.tags.tag_service.get_tags", return_value=[tag]):
        response = client.get("/api/tags/1")

    assert response.status_code == 200
    assert response.json() == {"tag": tag}


def test_get_tag_not_found():
    with patch("app.api.tags.tag_service.get_tags", return_value=[]):
        response = client.get("/api/tags/999")

    assert response.status_code == 404


def test_get_character_tags_success():
    tags = [{"id": 1, "name": "Raid"}]

    with patch(
        "app.api.characters.tag_service.get_character_tags",
        return_value=tags,
    ):
        response = client.get("/api/characters/10/tags")

    assert response.status_code == 200
    assert response.json() == {"tags": tags}


def test_assign_character_tag_success():
    with patch(
        "app.api.characters.tag_service.assign_tag",
        return_value=True,
    ) as service:
        response = client.post("/api/characters/10/tags/1")

    assert response.status_code == 200
    assert response.json() == {"message": "Tag assigned successfully"}
    service.assert_called_once_with(
        user_id=1,
        character_id=10,
        tag_id=1,
    )


def test_remove_character_tag_success():
    with patch(
        "app.api.characters.tag_service.remove_tag",
        return_value=True,
    ) as service:
        response = client.delete("/api/characters/10/tags/1")

    assert response.status_code == 200
    assert response.json() == {"message": "Tag removed successfully"}
    service.assert_called_once_with(
        user_id=1,
        character_id=10,
        tag_id=1,
    )


@pytest.mark.parametrize(
    ("method", "url", "service_path"),
    [
        ("post", "/api/characters/10/tags/1", "assign_tag"),
        ("delete", "/api/characters/10/tags/1", "remove_tag"),
    ],
)
def test_character_tag_route_handles_service_value_error(
    method,
    url,
    service_path,
):
    with patch(
        f"app.api.characters.tag_service.{service_path}",
        side_effect=ValueError("Tag introuvable."),
    ):
        response = getattr(client, method)(url)

    assert response.status_code == 404
    assert response.json()["message"] == "Tag introuvable."


def test_update_tag_success():
    tag = {"id": 1, "name": "Mythique"}

    with patch(
        "app.api.tags.tag_service.update_tag",
        return_value=tag,
    ) as service:
        response = client.patch(
            "/api/tags/1",
            json={"name": "Mythique"},
        )

    assert response.status_code == 200
    assert response.json() == {"tag": tag}
    service.assert_called_once_with(tag_id=1, name="Mythique")


def test_update_tag_not_found():
    with patch(
        "app.api.tags.tag_service.update_tag",
        side_effect=ValueError("Tag introuvable."),
    ):
        response = client.patch(
            "/api/tags/999",
            json={"name": "Mythique"},
        )

    assert response.status_code == 404
    assert response.json()["message"] == "Tag introuvable."


def test_delete_tag_success():
    with patch(
        "app.api.tags.tag_service.delete_tag",
        return_value=True,
    ) as service:
        response = client.delete("/api/tags/1")

    assert response.status_code == 200
    assert response.json() == {"message": "Tag deleted successfully"}
    service.assert_called_once_with(tag_id=1)


def test_delete_tag_not_found():
    with patch(
        "app.api.tags.tag_service.delete_tag",
        side_effect=ValueError("Tag introuvable."),
    ):
        response = client.delete("/api/tags/999")

    assert response.status_code == 404
    assert response.json()["message"] == "Tag introuvable."


def test_update_tag_rejects_empty_name():
    response = client.patch(
        "/api/tags/1",
        json={"name": ""},
    )

    assert response.status_code == 422


def test_update_tag_rejects_name_over_50_characters():
    response = client.patch(
        "/api/tags/1",
        json={"name": "a" * 51},
    )

    assert response.status_code == 422


def test_get_current_admin_rejects_non_admin():
    non_admin = SimpleNamespace(id=2, role="USER")

    app.dependency_overrides[get_current_user] = lambda: non_admin
    app.dependency_overrides.pop(get_current_admin, None)

    try:
        response = client.post("/api/tags", json={"name": "Raid"})

        assert response.status_code == 403
        assert response.json()["message"] == (
            "Administrator privileges required"
        )
    finally:
        app.dependency_overrides.clear()


def test_get_current_admin_accepts_admin():
    admin = SimpleNamespace(id=1, role="ADMIN")

    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides.pop(get_current_admin, None)

    try:
        with patch(
            "app.api.tags.tag_service.create_tag",
            return_value={"id": 1, "name": "Raid"},
        ):
            response = client.post("/api/tags", json={"name": "Raid"})

        assert response.status_code == 200
        assert response.json() == {"tag": {"id": 1, "name": "Raid"}}
    finally:
        app.dependency_overrides.clear()
