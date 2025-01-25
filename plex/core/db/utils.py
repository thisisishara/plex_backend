from typing import Any

from sanic import Sanic
from sanic.log import logger

from plex.core.db.in_memory_db import InMemoryDatabase


class SanicInMemoryDatabase:
    app: Sanic
    in_memory_db: InMemoryDatabase

    def __init__(self, app: Sanic) -> None:
        self.init_app(app=app)

    def init_app(self, app: Sanic) -> None:
        self.app = app

        @app.listener("before_server_start")
        async def configure_db(_app: Sanic, _loop: Any) -> None:
            self.in_memory_db = InMemoryDatabase()
            setattr(_app.ctx, "in_memory_db", self.in_memory_db)
            logger.info("[sanic-in-memory-db] initialized ✅")

        @app.listener("after_server_stop")
        async def log_db_shutdown(_app: Sanic, _loop: Any) -> None:
            logger.info("[sanic-in-memory-db] data cleared ✅")
