from __future__ import annotations

from fastapi import Header, HTTPException, Request, status
from itsdangerous import BadSignature, BadTimeSignature, SignatureExpired, TimestampSigner

from core.config import settings

signer = TimestampSigner(settings.admin_api_key)

COOKIE_NAME = settings.admin_session_cookie_name


def create_session_token(username: str) -> str:
    """Generate a signed session token for the provided username."""

    return signer.sign(username).decode()


def verify_session_token(token: str) -> str | None:
    """Return the username encoded in the token or ``None`` if invalid/expired."""

    try:
        username = signer.unsign(token, max_age=settings.session_max_age_seconds).decode()
        return username
    except (BadSignature, BadTimeSignature, SignatureExpired):
        return None


async def verify_admin(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")) -> str:
    """Dependency that validates the admin API key header."""

    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key.",
        )
    return "admin"


async def require_admin(request: Request) -> str:
    """Ensure the request originates from an authenticated admin session."""

    token = request.cookies.get(COOKIE_NAME)
    username = verify_session_token(token) if token else None
    if not username:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Authentication required",
            headers={"Location": "/admin/login"},
        )
    return username
