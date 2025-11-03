from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from core.database import db
from core.auth import create_session_token, verify_session_token, require_admin, COOKIE_NAME
from core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")


# =========================
# 🔐 LOGIN & LOGOUT
# =========================

@router.get("/login")
async def login_page(request: Request):
    """
    Admin login sahifasi (GET)
    """
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def login_post(request: Request, password: str = Form(...)):
    """
    Admin login (POST) — parol tekshirish va cookie yozish
    """
    if password == settings.ADMIN_API_KEY:
        token = create_session_token("admin")
        response = RedirectResponse(url="/admin/knowledge", status_code=303)
        response.set_cookie(COOKIE_NAME, token, max_age=60 * 60 * 12)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "❌ Noto‘g‘ri parol!"})


@router.get("/logout")
async def logout(request: Request):
    """
    Admin chiqish (logout)
    """
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


# =========================
# 📚 KNOWLEDGE CRUD
# =========================

@router.get("/knowledge")
async def list_knowledge(request: Request, user=Depends(require_admin)):
    """
    Barcha knowledge yozuvlarini ko‘rsatish
    """
    items = await db.knowledge.find().to_list(100)
    return templates.TemplateResponse(
        "knowledge/list.html",
        {"request": request, "items": items}
    )


@router.get("/knowledge/add")
async def add_form(request: Request, user=Depends(require_admin)):
    """
    Qo‘shish formasi
    """
    return templates.TemplateResponse(
        "knowledge/form.html",
        {"request": request, "item": None}
    )


@router.post("/knowledge/add")
async def add_item(
    request: Request,
    question_uz: str = Form(...),
    answer_uz: str = Form(...),
    question_ru: str = Form(...),
    answer_ru: str = Form(...),
    question_kz: str = Form(...),
    answer_kz: str = Form(...),
    category: str = Form(None),
    user=Depends(require_admin)
):
    """
    Yangi knowledge qo‘shish (POST)
    """
    await db.knowledge.insert_one({
        "question_uz": question_uz,
        "answer_uz": answer_uz,
        "question_ru": question_ru,
        "answer_ru": answer_ru,
        "question_kz": question_kz,
        "answer_kz": answer_kz,
        "category": category
    })
    return RedirectResponse(url="/admin/knowledge", status_code=303)


@router.get("/knowledge/edit/{id}")
async def edit_form(request: Request, id: str, user=Depends(require_admin)):
    """
    Tahrirlash formasi
    """
    item = await db.knowledge.find_one({"_id": ObjectId(id)})
    return templates.TemplateResponse(
        "knowledge/form.html",
        {"request": request, "item": item}
    )


@router.post("/knowledge/edit/{id}")
async def edit_item(
    id: str,
    question_uz: str = Form(...),
    answer_uz: str = Form(...),
    question_ru: str = Form(...),
    answer_ru: str = Form(...),
    question_kz: str = Form(...),
    answer_kz: str = Form(...),
    category: str = Form(None),
    user=Depends(require_admin)
):
    """
    Knowledge yozuvini yangilash
    """
    await db.knowledge.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "question_uz": question_uz,
            "answer_uz": answer_uz,
            "question_ru": question_ru,
            "answer_ru": answer_ru,
            "question_kz": question_kz,
            "answer_kz": answer_kz,
            "category": category
        }}
    )
    return RedirectResponse(url="/admin/knowledge", status_code=303)


@router.get("/knowledge/delete/{id}")
async def delete_item(id: str, user=Depends(require_admin)):
    """
    Knowledge yozuvini o‘chirish
    """
    await db.knowledge.delete_one({"_id": ObjectId(id)})
    return RedirectResponse(url="/admin/knowledge", status_code=303)
