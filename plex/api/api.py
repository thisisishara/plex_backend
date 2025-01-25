import os
from datetime import UTC
from datetime import datetime

from sanic import HTTPResponse
from sanic import Request
from sanic import Sanic
from sanic import response

from plex.api.v1.routes import v1_routes
from plex.core.db.utils import SanicInMemoryDatabase


def create_app(app_name: str) -> Sanic:
    app = Sanic(app_name, strict_slashes=False)

    # wrap Sanic app with an
    # in memory database client
    SanicInMemoryDatabase(app=app)

    # # wrap Sanic app with a
    # # Qdrant async client
    # SanicQdrant(app=app)

    # setting Sanic app configs
    app.config.HOST = os.environ.get("PLEX_ROUTER_HOST", "0.0.0.0")
    app.config.PORT = int(os.environ.get("PLEX_ROUTER_PORT", 8000))
    app.config.WORKERS = int(os.environ.get("PLEX_ROUTER_WORKERS", 2))
    app.config.ACCESS_LOG = str(os.environ.get("PLEX_ROUTER_ACCESS_LOG", "false")).lower() == "true"
    app.config.DEBUG_MODE = str(os.environ.get("PLEX_ROUTER_DEBUG_MODE", "true")).lower() == "true"

    # setting cors origin configs
    cors_origin_str = str(os.environ.get("PLEX_ROUTER_CORS_ORIGIN", "*")).strip()
    origin_list = [str(origin).strip() for origin in cors_origin_str.split(",")]
    app.config.CORS_ORIGINS = "*" if "*" in origin_list else origin_list[0] if len(origin_list) == 1 else origin_list

    # noinspection PyUnusedLocal
    @app.get("/")
    async def healthcheck(request: Request) -> HTTPResponse:
        return response.json({"status": "ok", "timestamp": datetime.now(UTC).isoformat()})

    # register other app routes
    app.blueprint(v1_routes)

    return app
