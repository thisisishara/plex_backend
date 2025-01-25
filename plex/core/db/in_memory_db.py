from datetime import datetime
from typing import TypedDict


class FinancialStatement(TypedDict):
    file_name: str
    file_size: float
    content: str
    content_hash: str
    timestamp: datetime


class PLStatement(TypedDict):
    file_name: str
    content: str
    timestamp: datetime


class InMemoryDatabase:
    """Instantiates an in-memory database to store
    source financial statements and extracted profit
    and loss statements as results.

    In a production setting, this must be replaced
    with a production-ready database like mongodb"""

    _sources: dict[str, FinancialStatement]
    _results: dict[str, PLStatement]

    def __init__(self) -> None:
        self._sources: dict[str, FinancialStatement] = {}
        self._results: dict[str, PLStatement] = {}

    # sources related db operations
    def retrieve_sources(self) -> list[FinancialStatement]:
        return list(self._sources.values())

    def add_source(self, source_data: FinancialStatement) -> FinancialStatement:
        self._sources[source_data["file_name"]] = source_data
        return source_data

    # def retrieve_source(self, file_name: str) -> FinancialStatement:
    #     source = self._sources.get(file_name, None)
    #     if not source:
    #         raise Exception(f"Source {file_name} was not found")
    #
    #     return source

    def source_exists(self, source_data: FinancialStatement) -> bool:
        if source_data["file_name"] not in self._sources:
            return False
        
        if source_data["content_hash"] == self._sources[source_data["file_name"]]["content_hash"]:
            return True

        return False

    # results related db operations
    def retrieve_results(self) -> list[PLStatement]:
        return list(self._results.values())

    def add_results(self, results_data: PLStatement) -> PLStatement:
        self._sources[results_data["file_name"]] = results_data
        return results_data

    def result_exists(self, result_data: PLStatement) -> bool:
        if result_data["file_name"] in self._results:
            return True

        return False

    # def retrieve_result(self, file_name: str) -> PLStatement:
    #     result = self._results.get(file_name, None)
    #     if not result:
    #         raise Exception(f"Result for {file_name} was not found")
    #
    #     return result
