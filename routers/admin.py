from __future__ import annotations

import math
from typing import Any

from bson import ObjectId
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from core.auth import COOKIE_NAME, create_session_token, require_admin
from core.config import settings
from core.database import db, serialize_document
from core.logger import logger
from models.knowledge import KnowledgeItem


router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")

PAGE_SIZE = 20


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def login_post(request: Request, password: str = Form(...)):
    if password == settings.admin_api_key:
        token = create_session_token("admin")
        response = RedirectResponse(url="/admin/knowledge", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            COOKIE_NAME,
            token,
            max_age=settings.session_max_age_seconds,
            httponly=True,
            samesite="lax",
            secure=False,
        )
        logger.info("admin_logged_in")
        return response
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "❌ Noto‘g‘ri parol!"},
    )


@router.get("/logout")
async def logout(_: Request):
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(COOKIE_NAME)
    logger.info("admin_logged_out")
    return response


@router.get("/knowledge")
async def list_knowledge(
    request: Request,
    user: str = Depends(require_admin),
    page: int = Query(default=1, ge=1),
    search: str | None = Query(default=None, min_length=1, max_length=256),
):
    filters: dict[str, Any] = {}
    if search:
        filters["$text"] = {"$search": search}

    skip = (page - 1) * PAGE_SIZE
    cursor = db.knowledge.find(filters).sort("question_uz")
    items = await cursor.skip(skip).limit(PAGE_SIZE).to_list(length=PAGE_SIZE)
    total = await db.knowledge.count_documents(filters)
    pages = max(1, math.ceil(total / PAGE_SIZE))

    context = {
        "request": request,
        "items": [serialize_document(item) for item in items],
        "page": page,
        "pages": pages,
        "search": search or "",
        "total": total,
    }
    return templates.TemplateResponse("knowledge/list.html", context)


@router.get("/knowledge/add")
async def add_form(request: Request, user: str = Depends(require_admin)):
    return templates.TemplateResponse("knowledge/form.html", {"request": request, "item": None})


def _clean_form_value(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


@router.post("/knowledge/add")
async def add_item(
    request: Request,
    question_uz: str = Form(...),
    answer_uz: str = Form(...),
    question_ru: str = Form(...),
    answer_ru: str = Form(...),
    question_kz: str = Form(...),
    answer_kz: str = Form(...),
    category: str | None = Form(default=None),
    user: str = Depends(require_admin),
):
    item = KnowledgeItem(
        question_uz=question_uz.strip(),
        answer_uz=answer_uz.strip(),
        question_ru=question_ru.strip(),
        answer_ru=answer_ru.strip(),
        question_kz=question_kz.strip(),
        answer_kz=answer_kz.strip(),
        category=_clean_form_value(category),
    )
    await db.knowledge.insert_one(item.model_dump())
    logger.info("knowledge_created", extra={"source": "admin"})
    return RedirectResponse(url="/admin/knowledge", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/knowledge/edit/{item_id}")
async def edit_form(request: Request, item_id: str, user: str = Depends(require_admin)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    item = await db.knowledge.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse(
        "knowledge/form.html",
        {"request": request, "item": serialize_document(item)},
    )


@router.post("/knowledge/edit/{item_id}")
async def edit_item(
    item_id: str,
    question_uz: str = Form(...),
    answer_uz: str = Form(...),
    question_ru: str = Form(...),
    answer_ru: str = Form(...),
    question_kz: str = Form(...),
    answer_kz: str = Form(...),
    category: str | None = Form(default=None),
    user: str = Depends(require_admin),
):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    item = KnowledgeItem(
        question_uz=question_uz.strip(),
        answer_uz=answer_uz.strip(),
        question_ru=question_ru.strip(),
        answer_ru=answer_ru.strip(),
        question_kz=question_kz.strip(),
        answer_kz=answer_kz.strip(),
        category=_clean_form_value(category),
    )
    result = await db.knowledge.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": item.model_dump()},
    )
    if not result.matched_count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    logger.info("knowledge_updated", extra={"id": item_id, "source": "admin"})
    return RedirectResponse(url="/admin/knowledge", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/knowledge/delete/{item_id}")
async def delete_item(item_id: str, user: str = Depends(require_admin)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    result = await db.knowledge.delete_one({"_id": ObjectId(item_id)})
    if not result.deleted_count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    logger.info("knowledge_deleted", extra={"id": item_id, "source": "admin"})
    return RedirectResponse(url="/admin/knowledge", status_code=status.HTTP_303_SEE_OTHER)
