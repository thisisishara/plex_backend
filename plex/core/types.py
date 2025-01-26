from typing import Any
from typing import TypedDict


class SourceFile(TypedDict):
    file_name: str
    file_size: float
    content: str
    content_hash: str
    timestamp: str


class ResultFile(TypedDict):
    file_name: str
    content: list[list[Any]]
    timestamp: str
