"""HTTP application for advertisement moderation."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from routers.predict import router as prediction_router

logger = logging.getLogger(__name__)

app = FastAPI(title="Advertisement Moderation API", version="1.0.0")
app.include_router(prediction_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"detail": errors})


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unexpected error while processing %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def custom_openapi() -> dict:
    """Keep the documented validation status consistent with the handler."""
    if app.openapi_schema is None:
        schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
        schema["paths"]["/predict"]["post"]["responses"].pop("422", None)
        app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
