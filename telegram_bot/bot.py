import logging
import httpx
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from core.config import settings

# === Logging ===
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# === Config ===
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
API_BASE = "http://127.0.0.1:8000/api"

# === User language state ===
user_lang = {}  # {chat_id: "uz"|"ru"|"kz"}

# === Til tanlash keyboard ===
def language_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang_kz"),
        ]
    ])

# === /start komandasi ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_lang[chat_id] = "uz"  # default
    await update.message.reply_text(
        "Assalomu alaykum! Tilni tanlang:",
        reply_markup=language_menu()
    )

# === Til tanlanganda ===
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    lang_code = query.data.split("_")[1]
    user_lang[chat_id] = lang_code

    langs = {"uz": "🇺🇿 O‘zbek tili", "ru": "🇷🇺 Русский язык", "kz": "🇰🇿 Қазақ тілі"}
    await query.edit_message_text(f"✅ Siz {langs[lang_code]} tilini tanladingiz.\nEndi savolingizni yozing.")

# === Asosiy chat handler ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    lang = user_lang.get(chat_id, "uz")  # default = uz

    await update.message.chat.send_action("typing")

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{API_BASE}/ask?lang={lang}",
                json={"user_id": str(chat_id), "question": text},
                timeout=60.0
            )
            data = r.json()
            answer = data.get("answer", "Javob topilmadi.")
    except Exception as e:
        logging.error(e)
        answer = "❌ Server bilan aloqa yo‘q."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Tilni o‘zgartirish", callback_data="change_lang")],
        [
            InlineKeyboardButton("✅ To‘g‘ri", callback_data=f"fb_good"),
            InlineKeyboardButton("❌ Noto‘g‘ri", callback_data=f"fb_bad")
        ]
    ])

    await update.message.reply_text(answer, reply_markup=keyboard)

# === Tilni qayta tanlash ===
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🌐 Tilni tanlang:", reply_markup=language_menu())

# === Feedback handler ===
async def feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    feedback_type = query.data.replace("fb_", "")

    await query.edit_message_reply_markup(reply_markup=None)
    if feedback_type == "good":
        await query.message.reply_text("🙏 Rahmat! Fikringiz muhim.")
    else:
        await query.message.reply_text("😔 Keyingi safar yaxshiroq bo‘lamiz!")

# === Botni ishga tushirish ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(change_language, pattern="^change_lang$"))
    app.add_handler(CallbackQueryHandler(feedback_callback, pattern="^fb_"))

    print("🤖 Telegram bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
