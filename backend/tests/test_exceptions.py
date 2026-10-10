import asyncio

import pytest
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
)


def make_request():
    """Construit une requête HTTP minimale pour les tests."""

    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 12345),
            "scheme": "http",
            "http_version": "1.1",
        }
    )


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (400, "Invalid OAuth state"),
        (401, "Authentication required"),
        (502, "Unable to contact Blizzard"),
    ],
)
def test_http_exception_handler_returns_consistent_format(
    status_code,
    message,
):
    """Vérifie le statut et le format des erreurs HTTP."""

    request = make_request()
    exception = HTTPException(
        status_code=status_code,
        detail={"message": message},
    )

    response = asyncio.run(
        http_exception_handler(request, exception)
    )

    assert response.status_code == status_code
    assert response.body == (
        f'{{"message":"{message}"}}'.encode()
    )


def test_validation_exception_handler_returns_consistent_format():
    """Vérifie le format des erreurs de validation."""

    request = make_request()
    exception = RequestValidationError(
        [
            {
                "type": "missing",
                "loc": ("body", "character_ids"),
                "msg": "Field required",
                "input": {},
            }
        ]
    )

    response = asyncio.run(
        validation_exception_handler(request, exception)
    )
    body = response.body.decode()

    assert response.status_code == 422
    assert '"message":"Invalid request data"' in body
    assert '"errors":' in body
