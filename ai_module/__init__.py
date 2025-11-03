from typing import Any

from .factory import get_ai_provider

ai_provider = get_ai_provider()


async def ask_ai(question: str, context: str | None = None, lang: str = "uz") -> str:
    return await ai_provider.generate_answer(question, context, lang)


async def shutdown_ai() -> None:
    closer: Any = getattr(ai_provider, "aclose", None)
    if callable(closer):
        await closer()
