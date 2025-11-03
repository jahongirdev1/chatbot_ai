from .factory import get_ai_provider

ai = get_ai_provider()

async def ask_ai(question: str, context: str | None = None, lang: str = "uz") -> str:
    return await ai.generate_answer(question, context, lang)
