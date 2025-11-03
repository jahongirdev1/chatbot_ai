import httpx
from .base_ai import BaseAIProvider
from core.config import settings

LANG_PROMPTS = {
    "uz": "Iltimos, javobni o‘zbek tilida yoz.",
    "ru": "Пожалуйста, ответь на русском языке.",
    "kz": "Жауапты қазақ тілінде жаз.",
}


class OllamaProvider(BaseAIProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = "llama3"

    async def generate_answer(self, question: str, context: str | None = None, lang: str = "uz") -> str:
        lang_prompt = LANG_PROMPTS.get(lang, LANG_PROMPTS["uz"])
        full_prompt = f"{lang_prompt}\nKontekst: {context or ''}\nSavol: {question}\nJavob:"

        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt}
            )
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip()
