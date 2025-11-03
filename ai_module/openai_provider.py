import openai
from .base_ai import BaseAIProvider
from core.config import settings

LANG_PROMPTS = {
    "uz": "Javobni o‘zbek tilida yoz.",
    "ru": "Ответь на русском языке.",
    "kz": "Жауапты қазақ тілінде жаз.",
}

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"

    async def generate_answer(self, question: str, context: str | None = None, lang: str = "uz") -> str:
        prompt_lang = LANG_PROMPTS.get(lang, LANG_PROMPTS["uz"])

        completion = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are a helpful assistant. {prompt_lang}"},
                {"role": "user", "content": f"{context or ''}\n{question}"}
            ]
        )
        return completion.choices[0].message["content"].strip()
