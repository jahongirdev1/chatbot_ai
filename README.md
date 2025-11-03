
# 🤖 ChatBot AI — Universal Multilingual Chatbot Backend

### 🧠 Overview
**ChatBot AI** is a universal backend for a multilingual chatbot that works with:
- 🟢 **Telegram Bot**
- 💬 **WhatsApp Bot** (via Green API)
- 📱 **Mobile App** (Flutter client)

It integrates **AI models (Ollama / OpenAI)** and supports **3 languages** — Uzbek 🇺🇿, Russian 🇷🇺, and Kazakh 🇰🇿.  
Built using **FastAPI**, **MongoDB**, and **Jinja2 templates** for the admin panel.

---


## ⚙️ Features

### 🔹 AI-Powered Chat
- `/api/ask` — answers user questions
- Searches knowledge base first; if not found, asks AI
- Supports language parameter `?lang=uz|ru|kz`

### 🔹 Multilingual Knowledge Base
- Each record stored in MongoDB in 3 languages:
  ```json
  {
    "question_uz": "...",
    "answer_uz": "...",
    "question_ru": "...",
    "answer_ru": "...",
    "question_kz": "...",
    "answer_kz": "..."
  }
  ```

### 🔹 Admin Panel (Web UI)
- Built with **Jinja2 templates**
- CRUD interface for multilingual Q&A entries
- Login with password (`ADMIN_API_KEY`)
- Cookie-based 12-hour session (using `itsdangerous`)

### 🔹 Telegram Bot
- Built with **python-telegram-bot v21 (async)**
- Language selection (🇺🇿 / 🇷🇺 / 🇰🇿)
- Feedback buttons: ✅ Correct / ❌ Incorrect
- Language change button 🌐

### 🔹 WhatsApp Bot
- Integrated via **Green API**
- Handles incoming webhooks
- Automatically replies using AI or knowledge base

### 🔹 Logging System
- Middleware logs every request and error
- Logs saved daily in `logs/YYYY-MM-DD.log`

---

## 🧱 Project Structure

```
chatbot_ai/
 ├── main.py
 ├── core/
 ├── ai_module/
 ├── routers/
 ├── telegram_bot/
 ├── whatsapp_bot/
 ├── templates/
 ├── static/
 ├── models/
 ├── logs/
 └── .env
```

---

## 🧩 Environment Configuration

Create a `.env` file in the project root:
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=chatbot_ai

AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=sk-yourkey

ADMIN_API_KEY=super_secret_key

TELEGRAM_BOT_TOKEN=123456:ABC-XYZ
GREEN_API_INSTANCE_ID=1100000000
GREEN_API_TOKEN=your_green_api_token
```

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/chatbot_ai.git
cd chatbot_ai
pipenv install
pipenv shell
```

---

## 🚀 Run Locally

### ▶️ FastAPI Server
```bash
uvicorn main:app --reload
```
Visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 🤖 Telegram Bot
```bash
python telegram_bot/bot.py
```

---

## 🧰 Services (Systemd or Docker)

### systemd example:
```
/etc/systemd/system/chatbot_api.service
/etc/systemd/system/chatbot_tg.service
```

### Docker Compose example:
```yaml
version: "3.9"
services:
  api:
    build: .
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    env_file: .env
  telegram:
    build: .
    command: python telegram_bot/bot.py
    env_file: .env
```

---

## 📋 Libraries Used

```bash
pipenv install fastapi uvicorn[standard] motor httpx python-dotenv \
jinja2 python-multipart itsdangerous python-telegram-bot==21.4
```

---

## 🔒 Security Notes
- `.env` must never be committed to Git.
- Use separate production keys for AI and Green API.
- Restrict admin panel access to trusted IPs if possible.

---

## 🧠 Future Improvements
- Add search and pagination to admin panel.
- Include AI chat history and statistics dashboard.
- Add Celery for background task processing (logging, metrics).
- Dockerize Ollama / OpenAI switch configuration.

---

## 🏁 License
MIT License — free to use, modify, and distribute.

---

## 👤 Author
**BRAT** — developer of the ChatBot AI project.  
Contact: coming soon  
Version: 1.0.0
