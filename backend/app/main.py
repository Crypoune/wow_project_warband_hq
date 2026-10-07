from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.health import router as health_router
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
)


app = FastAPI(
    title="Warband HQ API",
    description="Backend API for Warband HQ",
    version="0.1.0",
)

app.add_exception_handler(Exception, http_exception_handler)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.include_router(health_router)
