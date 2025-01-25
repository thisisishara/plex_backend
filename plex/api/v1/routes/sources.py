from datetime import datetime, UTC

from sanic import Blueprint, Request, HTTPResponse, response
from sanic.log import logger
from sanic.request import File

from plex.core.db.in_memory_db import InMemoryDatabase
from plex.core.utils import generate_content_hash, convert_to_markdown
from plex.shared.exceptions.Source import SourceFileNotSpecifiedError, EmptySourceFileContentError, \
    SourceFileExistsError

sources = Blueprint("sources", url_prefix="/sources")


# noinspection PyBroadException
@sources.get("/")
async def retrieve_sources(request: Request) -> HTTPResponse:
    try:
        db: InMemoryDatabase = request.app.ctx["in_memory_db"]
        return response.json({"sources": db.retrieve_sources()})

    except Exception:
        logger.exception("An error occurred while retrieving sources")
        return response.json({"error": "An error occurred while retrieving sources"}, status=500)


# noinspection PyBroadException
@sources.post("/")
async def add_source(request: Request) -> HTTPResponse:
    try:
        if "attachments" not in request.files:
            raise SourceFileNotSpecifiedError("A valid source file is not specified")

        attachments = request.files.getlist("attachments")
        if not attachments:
            raise SourceFileNotSpecifiedError("A valid source file is not specified")

        file: File = attachments[0]
        content = convert_to_markdown(file)

        if not content:
            raise EmptySourceFileContentError("The provided source file content is empty")

        source_data = {
            "file_name": file.name,
            "file_size": len(file.body),
            "content": content,
            "content_hash": generate_content_hash(content),
            "timestamp": datetime.now(UTC)
        }

        db: InMemoryDatabase = request.app.ctx["in_memory_db"]

        if db.source_exists(source_data=source_data):
            raise SourceFileExistsError("The source file already exists")

        inserted_source = db.add_source(source_data=source_data)
        return response.json({"source": inserted_source})

    except (SourceFileNotSpecifiedError, EmptySourceFileContentError) as e:
        logger.exception(e)
        return response.json({"error": e.message}, status=400)

    except SourceFileExistsError as e:
        logger.exception(e)
        return response.json({"error": e.message}, status=409)

    except Exception:
        logger.exception("An error occurred while uploading the source file")
        return response.json({"error": "An error occurred while uploading the source file"}, status=500)
