from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import chat, feedback, knowledge, whatsapp
from core.auth import verify_admin
from fastapi.middleware.sessions import SessionMiddleware

app = FastAPI(title="ChatBot AI Backend with Admin Panel")



app.add_middleware(SessionMiddleware, secret_key=settings.ADMIN_API_KEY)
# === Static va Templates ===
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routers
app.include_router(chat.router)
app.include_router(feedback.router)
app.include_router(knowledge.router)
app.include_router(whatsapp.router)

@app.get("/")
async def root():
    return {"message": "ChatBot AI API is running 🚀"}
