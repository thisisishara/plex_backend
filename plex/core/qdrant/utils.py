from typing import Any

from qdrant_client import AsyncQdrantClient
from sanic import Sanic
from sanic.log import logger

QDRANT_URL_CONFIG_NAME = "QDRANT_URL"
QDRANT_API_KEY_CONFIG_NAME = "QDRANT_API_KEY"


class SanicQdrant:
    qdrant_aioclient: AsyncQdrantClient
    app: Sanic
    qdrant_url: str
    qdrant_api_key: str
    url_config_name: str
    api_key_config_name: str

    def __init__(
        self,
        app: Sanic = None,
        url_config_name: str = QDRANT_URL_CONFIG_NAME,
        api_key_config_name: str = QDRANT_API_KEY_CONFIG_NAME,
        qdrant_url: str = "",
        qdrant_api_key: str = "",
    ) -> None:
        self.url_config_name = url_config_name
        self.api_key_config_name = api_key_config_name
        self.qdrant_url = qdrant_url
        self.qdrant_api_key = qdrant_api_key

        if app:
            self.init_app(app=app)

    def init_app(
        self,
        app: Sanic,
        url_config_name: str | None = None,
        api_key_config_name: str | None = None,
        qdrant_url: str | None = None,
        qdrant_api_key: str | None = None,
    ) -> None:
        self.app = app

        if url_config_name:
            self.url_config_name = url_config_name

        if api_key_config_name:
            self.api_key_config_name = api_key_config_name

        if qdrant_url:
            self.qdrant_url = qdrant_url

        if qdrant_api_key:
            self.qdrant_api_key = qdrant_api_key

        @app.listener("before_server_start")
        async def configure_qdrant(_app: Sanic, _loop: Any) -> None:
            _qdrant_url = self.qdrant_url or _app.config.get(self.url_config_name)
            _qdrant_api_key = self.qdrant_api_key or _app.config.get(
                self.api_key_config_name,
            )

            if not _qdrant_url:
                raise ValueError(
                    f"You must specify qdrant_url or set the {QDRANT_URL_CONFIG_NAME} Sanic config variable",
                )

            self.qdrant_aioclient = AsyncQdrantClient(
                url=_qdrant_url,
                api_key=_qdrant_api_key,
                prefer_grpc=False,
            )
            setattr(_app.ctx, "qdrant", self.qdrant_aioclient)
            logger.info("[sanic-qdrant] connected ✅")

        @app.listener("after_server_stop")
        async def close_qdrant(_app: Sanic, _loop: Any) -> None:
            logger.info("[sanic-qdrant] closing")
            await self.qdrant_aioclient.close()
            logger.info("[sanic-qdrant] disconnected ☑️")
