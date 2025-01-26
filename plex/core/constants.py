import os

# package configs
PACKAGE_NAME = "plex_api"
HOST = os.environ.get("PLEX_ROUTER_HOST", "0.0.0.0")
PORT = int(os.environ.get("PLEX_ROUTER_PORT", 8000))
WORKERS = max(1, min(4, int(os.environ.get("PLEX_ROUTER_WORKERS", 2))))
ACCESS_LOG = str(os.environ.get("PLEX_ROUTER_ACCESS_LOG", "true")).lower() == "true"
DEBUG_MODE = str(os.environ.get("PLEX_ROUTER_DEBUG_MODE", "true")).lower() == "true"
CORS_ORIGIN_STR = str(os.environ.get("PLEX_ROUTER_CORS_ORIGIN", "*")).strip()

# mongo configs
MONGO_URI = os.environ.get("PLEX_MONGO_URI", "")
MONGO_DB = os.environ.get("PLEX_MONGO_DB", "arcadea_test")
SOURCE_COLLECTION = os.environ.get("PLEX_SOURCE_COLLECTION", "sources")

# llm configs
LLM_TEMPERATURE = max(0.0, min(1.9, float(os.environ.get("PLEX_LLM_MAX_TOKENS", 0.1))))
LLM_MAX_TOKENS = max(0, min(1000, int(os.environ.get("PLEX_LLM_MAX_TOKENS", 500))))
PLEX_DEEPSEEK_BASE_URL = os.environ.get("PLEX_DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_API_KEY = os.environ.get("PLEX_DEEPSEEK_API_KEY", "")
DEEPSEEK_LLM_MODEL = os.environ.get("PLEX_DEEPSEEK_LLM_MODEL", "deepseek-chat")

# analyzer configs
LATEST_AVAILABLE_QUARTER = "Latest Available Quarter"
EXTRACTOR_PROMPT = """Extract the Profit and Loss Statement for the {quarter} of the latest year from the provided financial statement.

Instructions:
1. Analyze the financial statement to find the consolidated Profit and Loss statement for {quarter}.
2. If both consolidated and company-specific statements exist, extract ONLY the consolidated statement.
3. In most financial statements, the quarters are given as follows:
    - 3 months to March 31st (Q1)
    - 3 months to June 30th (Q2)
    - 3 months to Sep 30th (Q3)
    - 3 months to Dec 31st (Q4)
    you must correctly identify the {quarter} and its profit and loss/income statements.
4. Provide each row as a list of elements. Always put headers in the first list.
5. Prefer returning an empty list over making incorrect extractions.

Required Output:
- First sub list is headers. Usual headers: ["Line Item", "3 Months to 30th Sep <year>", "3 Months to 30th Sep <prev_year>", "Change %"]
- Include original column/line item names. {line_items}
- Output must be a list of list elements, each sub list representing a extracted row.
- Preserve financial values with exact precision

<financial_statement>
{content}
</financial_statement>

Quarter to strictly extract profit and loss from: {quarter}"""  # noqa: E501
