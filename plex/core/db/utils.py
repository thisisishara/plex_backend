from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic
from sanic.log import logger

MONGO_URI_CONFIG_NAME = "MONGO_URI"
MONGO_DB_CONFIG_NAME = "MONGO_DB"


class SanicMotor:
    """Wraps sanic app with an async motor client."""

    motor_aioclient: AsyncIOMotorClient
    app: Sanic
    mongo_url: str
    mongo_db: str
    uri_config_name: str
    db_config_name: str

    def __init__(
        self,
        app: Sanic = None,
        uri_config_name: str = MONGO_URI_CONFIG_NAME,
        db_config_name: str = MONGO_DB_CONFIG_NAME,
        mongo_url: str = "",
        mongo_db: str = "",
    ) -> None:
        self.uri_config_name = uri_config_name
        self.db_config_name = db_config_name
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

        if app:
            self.init_app(app=app)

    def init_app(
        self,
        app: Sanic,
        uri_config_name: str | None = None,
        db_config_name: str | None = None,
        mongo_url: str | None = None,
        mongo_db: str | None = None,
    ) -> None:
        self.app = app

        if uri_config_name:
            self.uri_config_name = uri_config_name

        if db_config_name:
            self.db_config_name = db_config_name

        if mongo_url:
            self.mongo_url = mongo_url

        if mongo_db:
            self.mongo_db = mongo_db

        @app.listener("before_server_start")
        async def configure_motor(_app: Sanic, _loop: Any) -> None:
            _mongo_url = self.mongo_url or _app.config.get(self.uri_config_name)
            _mongo_db = self.mongo_db or _app.config.get(self.db_config_name)

            if not _mongo_url or not _mongo_db:
                raise ValueError(
                    f"You must specify mongo_url, mongo_db or set the {MONGO_URI_CONFIG_NAME} "
                    f"and {MONGO_DB_CONFIG_NAME} Sanic config variables",
                )

            self.motor_aioclient = AsyncIOMotorClient(_mongo_url)
            setattr(_app.ctx, "motor", self.motor_aioclient)
            setattr(_app.ctx, "motor_db", self.motor_aioclient[_mongo_db])
            logger.info("[sanic-motor] connected ✅")

        @app.listener("after_server_stop")
        async def close_motor(_app: Sanic, _loop: Any) -> None:
            logger.info("[sanic-motor] closing")
            self.motor_aioclient.close()
            logger.info("[sanic-motor] disconnected ☑️")
