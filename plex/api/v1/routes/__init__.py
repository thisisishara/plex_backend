from sanic import Blueprint

from plex.api.v1.routes.results import results
from plex.api.v1.routes.sources import sources

v1_routes = Blueprint.group(sources, results, url_prefix="/api/v1")
