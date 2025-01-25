import click
from sanic import Sanic
from sanic.log import logger
from sanic.worker.loader import AppLoader

from plex.api import create_app


@click.group()
def plex_cli() -> None:
    """CLI entrypoint"""


# noinspection PyBroadException
@plex_cli.command()
def run() -> None:
    """Runs the Sanic Server"""

    try:
        click.echo("▶️ Starting the API Server...")
        from functools import partial

        loader = AppLoader(factory=partial(create_app, "plex_api"))
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
