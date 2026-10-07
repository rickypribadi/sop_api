import logging

from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from configs.config import settings
from routes import api


def init_app():
    app = FastAPI(title="SKELETON FASTAPI",
                  contact={
                      "name": "developer",
                      "email": "ginanjar.sumantri@agungsedayu.com"
                  },
                  description="This is a service for Archive.",
                  version="2.0",
                  docs_url="/skeleton/docs",
                  redoc_url="/skeleton/redoc",
                  openapi_url="/skeleton/openapi.json")

    @app.get("/")
    async def home():
        return {"message": "Hello World"}

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

    app.include_router(api.api_router, prefix="/skeleton")
    
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
