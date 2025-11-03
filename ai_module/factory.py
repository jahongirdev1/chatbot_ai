from core.config import settings
from core.logger import logger

from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider


def get_ai_provider():
    provider = settings.ai_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
        logger.info("ai_provider_selected", extra={"provider": "openai"})
        return OpenAIProvider()
    if provider == "ollama":
        logger.info("ai_provider_selected", extra={"provider": "ollama"})
        return OllamaProvider()
    raise ValueError(f"Unknown AI provider: {provider}")
