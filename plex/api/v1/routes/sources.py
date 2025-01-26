from datetime import datetime
from datetime import UTC

from sanic import Blueprint
from sanic import HTTPResponse
from sanic import Request
from sanic import response
from sanic.log import logger
from sanic.request import File

from plex.core.analyzer import ReportAnalyzer
from plex.core.db.collections.source import SourceCollection
from plex.core.db.collections.source import SourceFile
from plex.core.types import ResultFile
from plex.core.utils import convert_to_markdown
from plex.core.utils import generate_content_hash
from plex.shared.exceptions.source import EmptySourceFileContentError
from plex.shared.exceptions.source import QuarterNotSpecifiedError
from plex.shared.exceptions.source import SourceFileExistsError
from plex.shared.exceptions.source import SourceFileNotFoundError
from plex.shared.exceptions.source import SourceFileNotSpecifiedError

sources = Blueprint("sources", url_prefix="/sources")


# noinspection PyBroadException
@sources.get("/")
async def retrieve_sources(request: Request) -> HTTPResponse:
    try:
        return response.json({"sources": await SourceCollection.retrieve_all(app=request.app)})

    except Exception:
        logger.exception("An error occurred while retrieving sources")
        return response.json({"error": "An error occurred while retrieving sources"}, status=500)


# noinspection PyBroadException
@sources.get("/names")
async def retrieve_source_names(request: Request) -> HTTPResponse:
    try:
        return response.json({"sources": await SourceCollection.retrieve_all_names(app=request.app)})

    except Exception:
        logger.exception("An error occurred while retrieving source names")
        return response.json({"error": "An error occurred while retrieving source names"}, status=500)


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

        source_data: SourceFile = {
            "file_name": file.name,
            "file_size": len(file.body),
            "content": content,
            "content_hash": generate_content_hash(content),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        inserted_source = await SourceCollection.add_one(source_data=source_data, app=request.app)
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


# noinspection PyBroadException
@sources.post("/analyze")
async def analyze_source(request: Request) -> HTTPResponse:
    try:
        if "report" not in request.json:
            raise SourceFileNotSpecifiedError("A valid source file is not specified")

        if "quarter" not in request.json:
            raise QuarterNotSpecifiedError("A specific quarter is not specified")

        source = await SourceCollection.retrieve_one(file_name=request.json["report"], app=request.app)
        quarter = request.json["quarter"]
        selected_extraction = request.json.get("selected_extraction", False)

        results: ResultFile = await ReportAnalyzer().run(
            source=source,
            quarter=quarter,
            selected_extraction=selected_extraction,
        )

        return response.json(
            {
                "analysis": {
                    **results,
                    "timestamp": datetime.fromisoformat(results["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
                },
            },
        )

    except (SourceFileNotSpecifiedError, QuarterNotSpecifiedError) as e:
        logger.exception(e)
        return response.json({"error": e.message}, status=400)

    except SourceFileNotFoundError as e:
        logger.exception(e)
        return response.json({"error": e.message}, status=404)

    except Exception:
        logger.exception("An error occurred while analyzing the source file")
        return response.json({"error": "An error occurred while analyzing the source file"}, status=500)
