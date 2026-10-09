from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
)


app = FastAPI(
    title="Warband HQ API",
    description="Backend API for Warband HQ",
    version="0.1.0",
)

# Autorise le frontend React à communiquer avec le backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gère la session signée conservée dans le cookie du navigateur.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    same_site="lax",
    https_only=False,
)

app.add_exception_handler(Exception, http_exception_handler)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.include_router(health_router)
app.include_router(auth_router)
