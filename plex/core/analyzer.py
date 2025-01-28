from datetime import datetime
from datetime import UTC
from typing import Annotated
from typing import Any

from langchain_core.globals import set_debug
from langchain_core.globals import set_verbose
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from plex.core.constants import DEBUG_MODE
from plex.core.constants import DEEPSEEK_API_KEY
from plex.core.constants import DEEPSEEK_LLM_MODEL
from plex.core.constants import EXTRACTOR_PROMPT
from plex.core.constants import LLM_MAX_TOKENS
from plex.core.constants import LLM_TEMPERATURE
from plex.core.constants import PLEX_DEEPSEEK_BASE_URL
from plex.core.langchain.llm import get_llm
from plex.core.types import ResultFile
from plex.core.types import SourceFile
from plex.core.utils import convert_to_mappable


# noinspection PyUnusedLocal
@tool
def save_profit_and_loss_statement(
    extracted_items: Annotated[list[list[Any]], "Extracted profit and loss statement items for the requested quarter."],
) -> None:
    """Saves the extracted profit and loss statement CSV."""
    return None


class ReportAnalyzer:
    """Given a source financial document, attempts to extract the Profit and Loss statement using forced tool
    calling."""

    def __init__(self) -> None:
        set_verbose(DEBUG_MODE)
        set_debug(DEBUG_MODE)

        self._llm = get_llm(
            llm_model=DEEPSEEK_LLM_MODEL,
            api_key=DEEPSEEK_API_KEY,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            base_url=PLEX_DEEPSEEK_BASE_URL,
        )

    async def _extract_profit_and_loss(
        self,
        source: SourceFile,
        quarter: str,
        selected_extraction: bool,
    ) -> list[list[Any]]:
        """Attempts to extract the Profit and Loss statement from the source document using forced tool-calling using a
        langchain based tool.

        Args:
            source (dict): source document metadata, including its content
            quarter (str): quarter which the P&L should be extracted from
            selected_extraction (bool): whether to perform a selective extraction or not

        Returns:
            list[list[Any]]: A list of lists representing the extracted P&L statement.
                            Each inner list corresponds to a row in the P&L statement.
        """

        llm_with_tools = self._llm.bind_tools(
            [save_profit_and_loss_statement],
            tool_choice="save_profit_and_loss_statement",
        )
        extraction_chain = ChatPromptTemplate.from_template(EXTRACTOR_PROMPT) | llm_with_tools
        line_items = (
            'ONLY extract these line items for the {quarter}: "Gross '
            'Profit", "Profit Before Tax", "Profit for the Period".'
        )
        result = await extraction_chain.ainvoke(
            input={
                "content": source["content"],
                "quarter": quarter,
                "line_items": line_items if selected_extraction else "",
            },
        )

        if result.tool_calls:
            extracted_items: list[list[Any]] = result.tool_calls[0].get("args", {}).get("extracted_items", [])
            if extracted_items:
                return extracted_items

        return []

    async def run(self, source: SourceFile, quarter: str, selected_extraction: bool = False) -> ResultFile:
        extracted_items = await self._extract_profit_and_loss(
            source=source,
            quarter=quarter,
            selected_extraction=selected_extraction,
        )

        return {
            "file_name": source["file_name"],
            "content": convert_to_mappable(elements=extracted_items),
            "timestamp": datetime.now(UTC).isoformat(),
        }
