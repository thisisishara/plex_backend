from langchain_core.language_models import BaseChatModel
from langchain_openai.chat_models.base import BaseChatOpenAI
from sanic.log import logger

from plex.shared.exceptions.analyzer import AnalyzerInitializationError


def get_llm(llm_model: str, api_key: str, temperature: float, max_tokens: int) -> BaseChatModel:
    try:
        return BaseChatOpenAI(
            model=llm_model,
            temperature=temperature,
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com",
            max_tokens=max_tokens,
            n=1,
        )

    except Exception as e:
        logger.exception(e)
        raise AnalyzerInitializationError("Failed to construct the LLM from the provided configs.")
