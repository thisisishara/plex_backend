import hashlib
from io import BytesIO
from io import StringIO
from typing import Any

import numpy as np
import pandas as pd
from markitdown import MarkItDown
from sanic.request import File

from plex.shared.exceptions.results import ColumnCountMismatchError
from plex.shared.exceptions.results import CSVParsingError
from plex.shared.exceptions.results import InsufficientDataPointsError


def build_cors_origins(cors_origin_str: str) -> str | list:
    origin_list = [str(origin).strip() for origin in cors_origin_str.split(",")]
    return "*" if "*" in origin_list else origin_list[0] if len(origin_list) == 1 else origin_list


def convert_to_markdown(file: File) -> str:
    """Given a PDF file sent to Sanic, converts its content to markdown/text.

    Args:
        file (File): The source PDF file

    Returns:
        str: Markdown text extracted from the source file
    """

    md = MarkItDown()
    result = md.convert_stream(BytesIO(file.body), file_extension=file.name.split(".")[-1])
    return result.text_content


def generate_content_hash(content: str) -> str:
    """Given a string, hashes it using sha256.

    Args:
        content (str): text content

    Returns:
        str: hashed string
    """

    return hashlib.sha256(content.encode()).hexdigest()


def convert_to_mappable(elements: list[list[Any]]) -> list[list[Any]]:
    """Converts a given list of lists element for a table visualization by padding missing column values.

    This allows accurately visualizing table values if
    the original row element count is not fixed. Specially
    used here to parse the LLM output of the P&L statement

    Args:
        elements (list[list[Any]]): original nested list of values

    Returns:
        list[list[Any]]: padded nested list of values
    """

    if not elements:
        return [["Could not extract P&L data"]]

    max_columns = max(len(sub_elements) for sub_elements in elements)
    padded_rows = [element + (["_"] * (max_columns - len(element))) for element in elements]

    return padded_rows


def load_csv(file: File) -> list[list[Any]]:
    """Loads a CSV file uploaded to Sanic reliably using Pandas and returns a list of lists.

    Args:
        file (File): Source CSV file

    Returns:
        list[list[Any]]: parsed nested list of values
    """

    try:
        file_stream = StringIO(file.body.decode("utf-8"))
        df = pd.read_csv(file_stream)
        return [df.columns.tolist()] + df.values.tolist()
    except Exception as e:
        raise CSVParsingError from e


def convert_data_to_dict(data: list[list[str]]) -> dict[str, str]:
    """Converts a given nested list of values that represents rows in a table to a flattened dictionary key and value
    pairs to prepare them for evaluation.

    Args:
        data (list[list[str]]): source nested list of values

    Returns:
        dict[str, str]: Flattened dictionary constructed
    """

    if len(data) < 2:
        raise InsufficientDataPointsError

    data_dict = {}
    for row in data[1:]:
        key_prefix = str(row[0]).lower()
        for index, value in enumerate(row[1:], start=1):
            key = f"{key_prefix}_{index}"
            cleaned_value = str(value).strip()
            data_dict[key] = cleaned_value or "-"

    return data_dict


# Note: these metric calculates were defined
# manually using numpy due to an error in
# Docker deployment caused by scikit-learn
def precision_score(y_true: list[int], y_pred: list[int]) -> float:
    true_positives = np.sum((np.array(y_true) == 1) & (np.array(y_pred) == 1))
    predicted_positives = np.sum(y_pred)
    return true_positives / predicted_positives if predicted_positives > 0 else 0


def recall_score(y_true: list[int], y_pred: list[int]) -> float:
    true_positives = np.sum((np.array(y_true) == 1) & (np.array(y_pred) == 1))
    actual_positives = np.sum(y_true)
    return true_positives / actual_positives if actual_positives > 0 else 0


def f1_score(y_true: list[int], y_pred: list[int]) -> float:
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0


def evaluate_extracted_vs_reference(
    extracted_data: list[list[str]],
    reference_data: list[list[str]],
    source: str,
    reference: str,
) -> dict[str, Any]:
    """Takes in an extracted and reference P&L tables in the form of nested lists and evaluates the extraction
    performance by converting them to a flattened dictionary to compare the corresponding values of the two tables.

    Args:
        extracted_data (list[list[str]]): Table values of the extracted P&L statement
        reference_data (list[list[str]]): Table values of the reference CSV to take as
                                        the ground truth values
        source (str): Source file name
        reference (str): Reference file name

    Returns:
        dict[str, Any]: Evaluation scores along with metadata
    """

    if extracted_data and reference_data:
        if len(extracted_data[0]) != len(reference_data[0]):
            raise ColumnCountMismatchError

    extracted_dict = convert_data_to_dict(extracted_data)
    reference_dict = convert_data_to_dict(reference_data)

    all_line_items = set(reference_dict.keys()).union(set(extracted_dict.keys()))

    y_true = []
    y_pred = []

    for item in all_line_items:
        if item in reference_dict and item in extracted_dict:
            if reference_dict[item] == extracted_dict[item]:
                y_true.append(1)
                y_pred.append(1)
            else:
                y_true.append(1)
                y_pred.append(0)
        elif item in reference_dict:
            y_true.append(1)
            y_pred.append(0)
        elif item in extracted_dict:
            y_true.append(0)
            y_pred.append(1)

    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    return {
        "extracted_data_from": source,
        "reference_data_from": reference,
        "precision": precision,
        "recall": recall,
        "f1-score": f1,
    }
