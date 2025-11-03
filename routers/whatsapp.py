from fastapi import APIRouter, Request
from core.config import settings
from ai_module import ask_ai
import httpx

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

GREEN_API_URL = f"https://api.green-api.com/waInstance{settings.GREEN_API_INSTANCE_ID}"

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Green API webhook qabul qiluvchi endpoint.
    """
    data = await request.json()
    try:
        msg = data.get("messageData", {}).get("textMessageData", {}).get("textMessage")
        sender = data.get("senderData", {}).get("chatId")
        user_id = sender or "unknown"

        if not msg or not sender:
            return {"status": "ignored"}

        # AI dan javob olish
        answer = await ask_ai(msg)

        # Javobni foydalanuvchiga qaytarish
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{GREEN_API_URL}/sendMessage/{settings.GREEN_API_TOKEN}",
                json={"chatId": sender, "message": answer},
            )

        return {"status": "ok", "message": "sent"}

    except Exception as e:
        print("Webhook error:", e)
        return {"status": "error", "message": str(e)}
