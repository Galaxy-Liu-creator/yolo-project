"""违章管理接口 /api/violation/*（类别管理 / 审核记录 / 电子围栏 / 识别项配置）。"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.response import ok, err_not_found
from app.core.security import get_current_user
from app.data import mock_data as md
from app.schemas.models import CategoryUpdateRequest, RecognitionUpdateRequest

router = APIRouter(prefix="/api/violation", tags=["Violation 违章管理"])


@router.get("/categories", summary="违章类别管理列表")
def categories(current=Depends(get_current_user)):
    return ok(md.list_category_admin())


@router.put("/categories/{code}", summary="更新违章类别（启用/停用）")
def update_category(code: str, body: CategoryUpdateRequest, current=Depends(get_current_user)):
    item = md.find_category_admin(code)
    if not item:
        raise err_not_found("违章类别不存在")
    if body.enabled is not None:
        item["enabled"] = body.enabled
    return ok(item)


@router.get("/review-logs", summary="分页查询审核记录")
def review_logs(
    current=Depends(get_current_user),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=200),
    result: Optional[str] = None,
):
    items = md.REVIEW_LOGS
    filtered = [r for r in items if not result or r["result"] == result]
    total = len(filtered)
    start = (page - 1) * pageSize
    end = start + pageSize
    return ok({
        "items": filtered[start:end],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    })


@router.get("/fences", summary="电子围栏配置列表")
def fences(current=Depends(get_current_user)):
    return ok(md.FENCES_CONFIG)


@router.get("/recognition-items", summary="识别项配置列表")
def recognition_items(current=Depends(get_current_user)):
    return ok(md.RECOGNITION_ITEMS)


@router.put("/recognition-items/{id}", summary="更新识别项配置")
def update_recognition_item(id: str, body: RecognitionUpdateRequest, current=Depends(get_current_user)):
    item = md.find_recognition_item(id)
    if not item:
        raise err_not_found("识别项不存在")
    if body.enabled is not None:
        item["enabled"] = body.enabled
    if body.threshold is not None:
        item["threshold"] = body.threshold
    return ok(item)
