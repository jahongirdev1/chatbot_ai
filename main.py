from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from ai_module import shutdown_ai
from core.config import settings
from core.database import init_indexes
from core.middleware import RequestLoggingMiddleware
from routers import admin, chat, feedback, knowledge, whatsapp


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "templates" / "static"

app = FastAPI(title="ChatBot AI Backend with Admin Panel")

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.admin_api_key,
    session_cookie=settings.session_cookie_name,
    max_age=settings.session_max_age_seconds,
    same_site="lax",
    https_only=False,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(chat.router)
app.include_router(feedback.router)
app.include_router(knowledge.router)
app.include_router(whatsapp.router)
app.include_router(admin.router)


@app.on_event("startup")
async def startup_event() -> None:
    await init_indexes()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await shutdown_ai()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "ChatBot AI API is running 🚀"}
