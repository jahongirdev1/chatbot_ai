from __future__ import annotations

from typing import Any

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pymongo import ReturnDocument

from core.auth import verify_admin
from core.database import db, serialize_document
from core.logger import logger
from models.knowledge import KnowledgeItem, KnowledgeListResponse, KnowledgeResponse


router = APIRouter(prefix="/api", tags=["Knowledge"])


def _parse_object_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid knowledge id")
    return ObjectId(value)


@router.post("/knowledge", response_model=KnowledgeResponse, dependencies=[Depends(verify_admin)])
async def add_knowledge(item: KnowledgeItem) -> KnowledgeResponse:
    document = item.model_dump()
    result = await db.knowledge.insert_one(document)
    saved = await db.knowledge.find_one({"_id": result.inserted_id})
    if not saved:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to persist knowledge item")
    logger.info("knowledge_created", extra={"id": str(result.inserted_id)})
    return KnowledgeResponse(**serialize_document(saved))


@router.get("/knowledge", response_model=KnowledgeListResponse, dependencies=[Depends(verify_admin)])
async def list_knowledge(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=200),
    search: str | None = Query(default=None, min_length=1, max_length=256),
) -> KnowledgeListResponse:
    filters: dict[str, Any] = {}
    if search:
        filters["$text"] = {"$search": search}

    cursor = db.knowledge.find(filters).sort("question_uz")
    items = await cursor.skip(skip).limit(limit).to_list(length=limit)
    total = await db.knowledge.count_documents(filters)

    return KnowledgeListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[KnowledgeResponse(**serialize_document(item)) for item in items],
    )


@router.get(
    "/knowledge/{knowledge_id}",
    response_model=KnowledgeResponse,
    dependencies=[Depends(verify_admin)],
)
async def get_knowledge(knowledge_id: str) -> KnowledgeResponse:
    document = await db.knowledge.find_one({"_id": _parse_object_id(knowledge_id)})
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found")
    return KnowledgeResponse(**serialize_document(document))


@router.put(
    "/knowledge/{knowledge_id}",
    response_model=KnowledgeResponse,
    dependencies=[Depends(verify_admin)],
)
async def update_knowledge(knowledge_id: str, item: KnowledgeItem) -> KnowledgeResponse:
    object_id = _parse_object_id(knowledge_id)
    updated = await db.knowledge.find_one_and_update(
        {"_id": object_id},
        {"$set": item.model_dump()},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found")
    logger.info("knowledge_updated", extra={"id": knowledge_id})
    return KnowledgeResponse(**serialize_document(updated))


@router.delete(
    "/knowledge/{knowledge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin)],
)
async def delete_knowledge(knowledge_id: str) -> Response:
    object_id = _parse_object_id(knowledge_id)
    result = await db.knowledge.delete_one({"_id": object_id})
    if not result.deleted_count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found")
    logger.info("knowledge_deleted", extra={"id": knowledge_id})
    return Response(status_code=status.HTTP_204_NO_CONTENT)
