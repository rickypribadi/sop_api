import logging
import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.logger import logger as fastapi_logger
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from configs.config import settings
from routes import api

_docs_basic = HTTPBasic()


def verify_docs_credentials(
    credentials: HTTPBasicCredentials = Depends(_docs_basic),
) -> str:
    """HTTP Basic auth untuk Swagger/ReDoc. Kredensial dari env."""
    user_ok = secrets.compare_digest(
        credentials.username, settings.DOCS_USERNAME
    )
    pass_ok = secrets.compare_digest(
        credentials.password, settings.DOCS_PASSWORD
    )
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kredensial dokumentasi tidak valid",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def init_app():
    # Nonaktifkan docs bawaan; kita sajikan sendiri dengan proteksi Basic auth.
    app = FastAPI(title="SOP FASTAPI",
                  contact={
                      "name": "developer",
                      "email": "rickypribadi79@gmail.com"
                  },
                  description="This is a service for SOP Web",
                  version="2.0",
                  docs_url=None,
                  redoc_url=None,
                  openapi_url=None)

    _OPENAPI_URL = "/sop/openapi.json"

    @app.get("/")
    async def home():
        return {"message": "Hello World"}

    @app.get(_OPENAPI_URL, include_in_schema=False)
    async def openapi(_: str = Depends(verify_docs_credentials)):
        return JSONResponse(app.openapi())

    @app.get("/sop/docs", include_in_schema=False)
    async def swagger_ui(_: str = Depends(verify_docs_credentials)):
        return get_swagger_ui_html(
            openapi_url=_OPENAPI_URL, title=f"{app.title} - Swagger UI"
        )

    @app.get("/sop/redoc", include_in_schema=False)
    async def redoc_ui(_: str = Depends(verify_docs_credentials)):
        return get_redoc_html(
            openapi_url=_OPENAPI_URL, title=f"{app.title} - ReDoc"
        )

    # app.add_middleware(ContextMiddleware)
    app.add_middleware(
        SQLAlchemyMiddleware,
        db_url=settings.DB_CONFIG,
        engine_args={
            "echo": False,
            "pool_pre_ping": True,
            "pool_recycle": 1800
        },
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(api.api_router, prefix="/sop/api")

    add_pagination(app)

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    gunicorn_logger = logging.getLogger("gunicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

    fastapi_logger.handlers = gunicorn_error_logger.handlers

    if __name__ != "__main__":
        fastapi_logger.setLevel(gunicorn_logger.level)
    else:
        fastapi_logger.setLevel(logging.DEBUG)

    return app


app = init_app()
