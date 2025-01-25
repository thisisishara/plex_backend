from sanic import Blueprint
from plex.api.v1.routes.actions import actions
from plex.api.v1.routes.results import results
from plex.api.v1.routes.sources import sources

v1_routes = Blueprint.group(actions, results, sources, url_prefix="/api/v1")
