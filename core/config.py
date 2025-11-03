import os
from dotenv import load_dotenv


load_dotenv()

class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "chatbot_ai")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
    GREEN_API_INSTANCE_ID: str | None = os.getenv("GREEN_API_INSTANCE_ID")
    GREEN_API_TOKEN: str | None = os.getenv("GREEN_API_TOKEN")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "changeme")


# Bitta global obyekt
settings = Settings()
