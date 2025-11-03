from fastapi import Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from itsdangerous import TimestampSigner, BadSignature
from core.config import settings

signer = TimestampSigner(settings.ADMIN_API_KEY)  # secret key sifatida ishlatamiz

COOKIE_NAME = "admin_session"

# === Session yaratish ===
def create_session_token(username: str):
    return signer.sign(username).decode()

# === Sessionni tekshirish ===
def verify_session_token(token: str) -> str | None:
    try:
        username = signer.unsign(token, max_age=60 * 60 * 12).decode()  # 12 soat amal qiladi
        return username
    except BadSignature:
        return None

# === Request orqali adminni tekshirish ===
async def require_admin(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if not token or not verify_session_token(token):
        return RedirectResponse(url="/admin/login", status_code=303)
