from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Uniformise le format des erreurs HTTP."""

    detail = exc.detail

    if isinstance(detail, dict) and "message" in detail:
        content = {"message": detail["message"]}
    elif isinstance(detail, dict):
        content = {"detail": detail}
    elif isinstance(detail, str):
        content = {"message": detail}
    else:
        content = {"message": "HTTP error"}

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Uniformise le format des erreurs de validation."""

    return JSONResponse(
        status_code=422,
        content={
            "message": "Invalid request data",
            "errors": exc.errors(),
        },
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Masque les détails des erreurs internes inattendues."""

    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )
