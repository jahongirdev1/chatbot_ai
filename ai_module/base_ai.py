from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_answer(self, question: str, context: str | None = None, lang: str = "uz") -> str:
        pass
