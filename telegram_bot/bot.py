from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Dict

import httpx
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Ensure project root is on sys.path when running this script directly.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from core.config import settings


logger = logging.getLogger(__name__)

BOT_TOKEN = settings.telegram_bot_token
API_BASE = settings.api_base_url.rstrip("/")

user_lang: Dict[int, str] = {}
LANGUAGE_BUTTON_TEXT = "🌐 Tilni o‘zgartirish"


def persistent_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(LANGUAGE_BUTTON_TEXT)]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def language_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz"),
                InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
                InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang_kz"),
            ]
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_lang[chat_id] = "uz"
    await update.message.reply_text("Assalomu alaykum! Tilni tanlang:", reply_markup=language_menu())
    await update.message.reply_text(
        "Tilni qayta tanlash uchun qulay tugmadan foydalaning.",
        reply_markup=persistent_menu(),
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    lang_code = query.data.split("_")[1]
    user_lang[chat_id] = lang_code

    langs = {"uz": "🇺🇿 O‘zbek tili", "ru": "🇷🇺 Русский язык", "kz": "🇰🇿 Қазақ тілі"}
    await query.edit_message_text(f"✅ Siz {langs[lang_code]} tilini tanladingiz.\nEndi savolingizni yozing.")
    await query.message.reply_text("Tilni o‘zgartirish uchun tugmadan foydalanishingiz mumkin.", reply_markup=persistent_menu())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    text = update.message.text
    lang = user_lang.get(chat_id, "uz")

    if text == LANGUAGE_BUTTON_TEXT:
        await update.message.reply_text("🌐 Tilni tanlang:", reply_markup=language_menu())
        return

    await update.message.chat.send_action("typing")

    client: httpx.AsyncClient = context.application.bot_data["http_client"]
    try:
        response = await client.post(
            "/ask",
            params={"lang": lang},
            json={"user_id": str(chat_id), "question": text},
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "Javob topilmadi.")
        context.user_data["last_message_id"] = data.get("message_id")
    except httpx.HTTPStatusError as exc:
        logger.error("ask_endpoint_failed", exc_info=exc)
        answer = "❌ Server bilan aloqa yo‘q."
    except httpx.TimeoutException as exc:
        logger.warning("ask_endpoint_timeout", exc_info=exc)
        answer = (
            "⌛ Server javobi juda kechikdi. Biroz kutib, qayta yuboring."
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("ask_endpoint_unexpected_error", exc_info=exc)
        answer = "❌ Server bilan aloqa yo‘q."

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🌐 Tilni o‘zgartirish", callback_data="change_lang")],
            [
                InlineKeyboardButton("✅ To‘g‘ri", callback_data="fb_good"),
                InlineKeyboardButton("❌ Noto‘g‘ri", callback_data="fb_bad"),
            ],
        ]
    )

    await update.message.reply_text(answer, reply_markup=keyboard)


async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🌐 Tilni tanlang:", reply_markup=language_menu())
    await query.message.reply_text("Tilni o‘zgartirish uchun tugmadan foydalanishingiz mumkin.", reply_markup=persistent_menu())


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in user_lang:
        user_lang[chat_id] = "uz"
    await update.message.reply_text("🌐 Tilni tanlang:", reply_markup=language_menu())
    await update.message.reply_text("Tilni o‘zgartirish uchun tugmadan foydalanishingiz mumkin.", reply_markup=persistent_menu())


async def feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    feedback_type = query.data.replace("fb_", "")

    await query.edit_message_reply_markup(reply_markup=None)

    message_id = context.user_data.get("last_message_id")
    if message_id:
        client: httpx.AsyncClient = context.application.bot_data["http_client"]
        try:
            await client.post(
                "/feedback",
                json={"message_id": message_id, "rating": feedback_type},
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("feedback_send_failed", exc_info=exc)

    if feedback_type == "good":
        await query.message.reply_text("🙏 Rahmat! Fikringiz muhim.")
    else:
        await query.message.reply_text("😔 Keyingi safar yaxshiroq bo‘lamiz!")


async def _post_init(application: Application) -> None:
    timeout = httpx.Timeout(read=120.0, connect=10.0, write=30.0, pool=None)
    application.bot_data["http_client"] = httpx.AsyncClient(base_url=API_BASE, timeout=timeout)


async def _post_shutdown(application: Application) -> None:
    client: httpx.AsyncClient | None = application.bot_data.pop("http_client", None)
    if client:
        await client.aclose()


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    app = Application.builder().token(BOT_TOKEN).build()
    app.post_init = _post_init
    app.post_shutdown = _post_shutdown

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(change_language, pattern="^change_lang$"))
    app.add_handler(CallbackQueryHandler(feedback_callback, pattern="^fb_"))

    logger.info("telegram_bot_started")
    app.run_polling()


if __name__ == "__main__":
    main()
