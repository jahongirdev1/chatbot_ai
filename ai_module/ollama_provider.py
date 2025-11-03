from __future__ import annotations

import httpx

from .base_ai import BaseAIProvider
from core.config import settings

LANG_PROMPTS = {
    "uz": "Iltimos, javobni o‘zbek tilida yoz.",
    "ru": "Пожалуйста, ответь на русском языке.",
    "kz": "Жауапты қазақ тілінде жаз.",
}


class OllamaProvider(BaseAIProvider):
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = "llama3"
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)

    async def generate_answer(
        self,
        question: str,
        context: str | None = None,
        lang: str = "uz",
    ) -> str:
        lang_prompt = LANG_PROMPTS.get(lang, LANG_PROMPTS["uz"])
        full_prompt = f"{lang_prompt}\nContext: {context or 'Nomaʼlum'}\nQuestion: {question}\nAnswer:"

        response = await self._client.post(
            "/api/generate",
            json={"model": self.model, "prompt": full_prompt},
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "").strip()
        if not answer:
            raise RuntimeError("Ollama returned an empty response")
        return answer

    async def aclose(self) -> None:
        await self._client.aclose()
