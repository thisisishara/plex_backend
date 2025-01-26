from datetime import datetime
from datetime import UTC

from sanic import HTTPResponse
from sanic import Request
from sanic import response
from sanic import Sanic

from plex.api.v1.routes import v1_routes
from plex.core.constants import ACCESS_LOG
from plex.core.constants import CORS_ORIGIN_STR
from plex.core.constants import DEBUG_MODE
from plex.core.constants import HOST
from plex.core.constants import MONGO_DB
from plex.core.constants import MONGO_URI
from plex.core.constants import PORT
from plex.core.constants import WORKERS
from plex.core.db.utils import SanicMotor
from plex.core.utils import build_cors_origins


def create_app(app_name: str) -> Sanic:
    app = Sanic(app_name, strict_slashes=False)

    # setting Sanic app configs
    app.config.HOST = HOST
    app.config.PORT = PORT
    app.config.WORKERS = WORKERS
    app.config.ACCESS_LOG = ACCESS_LOG
    app.config.DEBUG_MODE = DEBUG_MODE
    app.config.DEBUG_MODE = DEBUG_MODE
    app.config.DEBUG_MODE = DEBUG_MODE
    # setting cors origin configs
    app.config.CORS_ORIGINS = build_cors_origins(CORS_ORIGIN_STR)
    # motor configs
    app.config.MONGO_URI = MONGO_URI
    app.config.MONGO_DB = MONGO_DB

    # wrap Sanic app with an
    # in memory database client
    SanicMotor().init_app(app=app)

    # noinspection PyUnusedLocal
    @app.get("/")
    async def healthcheck(request: Request) -> HTTPResponse:
        return response.json({"status": "ok", "timestamp": datetime.now(UTC).isoformat()})

    # register other app routes
    app.blueprint(v1_routes)

    return app
