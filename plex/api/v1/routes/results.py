import json

from sanic import Blueprint
from sanic import HTTPResponse
from sanic import Request
from sanic import response
from sanic.log import logger
from sanic.request import File

from plex.core.utils import evaluate_extracted_vs_reference
from plex.core.utils import load_csv
from plex.shared.exceptions.results import ColumnCountMismatchError
from plex.shared.exceptions.results import CSVParsingError
from plex.shared.exceptions.results import DataFileNotSpecifiedError
from plex.shared.exceptions.results import InsufficientDataPointsError

results = Blueprint("results", url_prefix="/results")


# noinspection PyBroadException
@results.post("/evaluate")
async def evaluate_results(request: Request) -> HTTPResponse:
    try:
        if "extracted_data" not in request.form:
            raise DataFileNotSpecifiedError("A valid extracted data file is not specified")

        extracted_data_content = request.form.get("extracted_data")
        if not extracted_data_content:
            raise DataFileNotSpecifiedError("A valid extracted data file is not specified")

        if "attachments" not in request.files:
            raise DataFileNotSpecifiedError("A valid reference data file is not specified")

        file: File = request.files.get("attachments")
        if not file:
            raise DataFileNotSpecifiedError("A valid reference data file is not specified")

        reference_data = load_csv(file)
        extracted_data = json.loads(extracted_data_content)
        source_file_name = request.form.get("source", "Unknown")
        reference_file_name = file.name

        if not extracted_data or not reference_data:
            raise DataFileNotSpecifiedError("Extracted and reference data cannot be empty")

        evaluation_result = evaluate_extracted_vs_reference(
            extracted_data=extracted_data,
            reference_data=reference_data,
            source=source_file_name,
            reference=reference_file_name,
        )

        return response.json({"results": evaluation_result})

    except (DataFileNotSpecifiedError, InsufficientDataPointsError, ColumnCountMismatchError) as e:
        logger.exception(e)
        return response.json({"error": e.message}, status=400)

    except CSVParsingError as e:
        logger.exception(e)
        return response.json(
            {"error": "Could not parse the reference CSV. Make sure it is correctly formatted"},
            status=400,
        )

    except Exception:
        logger.exception("An error occurred during the evaluation")
        return response.json({"error": "An error occurred during the evaluation"}, status=500)
