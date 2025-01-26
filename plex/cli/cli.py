import importlib
import os.path
from functools import partial

import click
from dotenv import load_dotenv
from sanic import Sanic
from sanic.log import logger
from sanic.worker.loader import AppLoader

from plex.api import create_app
from plex.core.constants import PACKAGE_NAME


@click.group()
def plex_cli() -> None:
    """CLI entrypoint."""


# noinspection PyBroadException
@plex_cli.command()
def run() -> None:
    """Runs the Sanic Server."""

    try:
        click.echo("▶️ Starting the API Server...")

        if os.path.isfile(".env"):
            from plex.core import constants

            click.echo("🔄️ Loading .env variables...")
            load_dotenv(".env")
            importlib.reload(constants)

        from plex.shared.db.migrations import MongoMigrations

        click.echo("♾️ Running MongoDB Migrations...")
        with MongoMigrations() as migrations:
            migrations.run()

        loader = AppLoader(factory=partial(create_app, PACKAGE_NAME))
        app = loader.load()

        app.prepare(
            host=app.config.get("HOST"),
            port=app.config.get("PORT"),
            workers=app.config.get("WORKERS", 1),
            access_log=app.config.get("ACCESS_LOG", False),
            debug=app.config.get("DEBUG_MODE", True),
        )

        Sanic.serve(primary=app, app_loader=loader)

    except KeyboardInterrupt:
        click.echo("Server stopped gracefully")

    except Exception:
        logger.exception("Unhandled exception occurred")
