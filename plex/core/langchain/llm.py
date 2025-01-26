from langchain_core.language_models import BaseChatModel
from langchain_openai.chat_models.base import BaseChatOpenAI
from sanic.log import logger

from plex.shared.exceptions.analyzer import AnalyzerInitializationError


def get_llm(llm_model: str, api_key: str, temperature: float, max_tokens: int) -> BaseChatModel:
    """Returns a Langchain LLM wrapper for the Deepseek model based on the specified configurations.

    Args:
        llm_model (str): The name of the Deepseek model to use (e.g., "deepseek-chat").
        api_key (str): The API key for authenticating requests to the Deepseek API.
        temperature (float): The sampling temperature for the model.
        max_tokens (int): The maximum number of tokens the model is allowed to generate.

    Returns:
        BaseChatModel: A Langchain `BaseChatOpenAI` instance configured with the specified
                      Deepseek model and parameters.

    Raises:
        AnalyzerInitializationError: If the LLM cannot be constructed due to invalid configurations
                                    or other errors during initialization.
    """

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
