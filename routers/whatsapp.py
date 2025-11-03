from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Request, status

from ai_module import ask_ai
from core.config import settings
from core.logger import logger


router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])


def _build_green_api_url() -> str:
    if not settings.green_api_instance_id or not settings.green_api_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Green API credentials are not configured.",
        )
    return f"https://api.green-api.com/waInstance{settings.green_api_instance_id}"


@router.post("/webhook")
async def whatsapp_webhook(request: Request) -> dict[str, str]:
    """Handle incoming WhatsApp webhooks sent by Green API."""

    try:
        payload = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload") from exc
    message = payload.get("messageData", {}).get("textMessageData", {}).get("textMessage")
    sender = payload.get("senderData", {}).get("chatId")

    if not message or not sender:
        logger.info("whatsapp_webhook_ignored", extra={"reason": "missing_message"})
        return {"status": "ignored", "message": "Event did not contain a text message."}

    logger.info("whatsapp_message_received", extra={"sender": sender})

    try:
        answer = await ask_ai(message)
    except Exception as exc:
        logger.exception("whatsapp_ai_failed", extra={"sender": sender})
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider error") from exc

    base_url = _build_green_api_url()
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/sendMessage/{settings.green_api_token}",
            json={"chatId": sender, "message": answer},
        )
        response.raise_for_status()

    logger.info("whatsapp_message_sent", extra={"sender": sender})
    return {"status": "ok", "message": "sent"}
