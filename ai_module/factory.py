from core.config import settings
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

def get_ai_provider():
    provider = settings.AI_PROVIDER.lower()

    if provider == "openai":
        return OpenAIProvider()
    elif provider == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown AI provider: {provider}")
