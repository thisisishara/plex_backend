import hashlib
from io import BytesIO
from io import StringIO
from typing import Any

import pandas as pd
from markitdown import MarkItDown
from sanic.request import File
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

from plex.shared.exceptions.results import ColumnCountMismatchError
from plex.shared.exceptions.results import CSVParsingError
from plex.shared.exceptions.results import InsufficientDataPointsError


def build_cors_origins(cors_origin_str: str) -> str | list:
    origin_list = [str(origin).strip() for origin in cors_origin_str.split(",")]
    return "*" if "*" in origin_list else origin_list[0] if len(origin_list) == 1 else origin_list


def bytes_to_string(size_in_bytes: int) -> str:
    if size_in_bytes == 0:
        return "0 B"

    units = ("B", "KB", "MB", "GB", "TB")
    i = min(4, int(size_in_bytes.bit_length() / 10))
    size = size_in_bytes / (1 << (i * 10))

    return f"{size:.1f} {units[i]}" if size >= 100 else f"{size:.2f} {units[i]}"


def convert_to_markdown(file: File) -> str:
    md = MarkItDown()
    result = md.convert_stream(BytesIO(file.body), file_extension=file.name.split(".")[-1])
    return result.text_content


def generate_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def convert_to_mappable(elements: list[list[Any]], separator: str = ",") -> list[list[Any]]:
    if not elements:
        return [["Could not extract P&L data"]]

    max_columns = max(len(sub_elements) for sub_elements in elements)
    padded_rows = [element + (["_"] * (max_columns - len(element))) for element in elements]

    return padded_rows


def load_csv(file: File) -> list[list[Any]]:
    try:
        file_stream = StringIO(file.body.decode("utf-8"))
        df = pd.read_csv(file_stream)
        return [df.columns.tolist()] + df.values.tolist()
    except Exception as e:
        raise CSVParsingError from e


def convert_data_to_dict(data: list[list[str]]) -> dict[str, str]:
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


def evaluate_extracted_vs_reference(
    extracted_data: list[list[str]],
    reference_data: list[list[str]],
    source: str,
    reference: str,
) -> dict[str, Any]:
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
