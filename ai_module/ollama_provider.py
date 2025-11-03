from __future__ import annotations

import json

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
        self.model = "deepseek-r1:8b"
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    async def generate_answer(
        self,
        question: str,
        context: str | None = None,
        lang: str = "uz",
    ) -> str:
        lang_prompt = LANG_PROMPTS.get(lang, LANG_PROMPTS["uz"])
        full_prompt = f"{lang_prompt}\nContext: {context or 'Nomaʼlum'}\nQuestion: {question}\nAnswer:"

        try:
            async with self._client.stream(
                "POST",
                "/api/generate",
                json={"model": self.model, "prompt": full_prompt},
            ) as response:
                response.raise_for_status()
                chunks: list[str] = []
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    payload = json.loads(line)
                    if error := payload.get("error"):
                        raise RuntimeError(f"Ollama error: {error}")
                    chunk = payload.get("response")
                    if chunk:
                        chunks.append(chunk)
                    if payload.get("done"):
                        break
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Ollama request failed while connecting to {self.base_url}"
            ) from exc
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive logging
            raise RuntimeError("Failed to parse Ollama response stream") from exc

        answer = "".join(chunks).strip()
        if not answer:
            raise RuntimeError("Ollama returned an empty response")
        return answer

    async def aclose(self) -> None:
        await self._client.aclose()
