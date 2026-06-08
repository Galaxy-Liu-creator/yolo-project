"""监控记录 / 违章管理接口 /api/records/*。"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.response import ok, err_not_found
from app.core.security import get_current_user
from app.data import mock_data as md
from app.schemas.models import BatchDeleteRequest, ReviewRequest

router = APIRouter(prefix="/api/records", tags=["Records 监控记录"])


def _parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@router.get("", summary="分页查询违章记录")
def list_records(
    current=Depends(get_current_user),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=200),
    categoryCode: Optional[str] = None,
    processStatus: Optional[str] = None,
    version: Optional[str] = None,
    unit: Optional[str] = None,
    team: Optional[str] = None,
    sceneCode: Optional[str] = None,
    keyword: Optional[str] = None,
    startTime: Optional[str] = None,
    endTime: Optional[str] = None,
):
    items = md.RECORDS

    def match(r: dict) -> bool:
        if categoryCode and r["categoryCode"] != categoryCode:
            return False
        if processStatus and r["processStatus"] != processStatus:
            return False
        if version and r["version"] != version:
            return False
        if unit and r.get("unitCode") != unit:
            return False
        if team and r.get("teamCode") != team:
            return False
        if sceneCode and r["sceneCode"] != sceneCode:
            return False
        if keyword:
            kw = keyword.lower()
            haystack = f"{r['id']} {r['category']} {r['team']} {r['scene']}".lower()
            if kw not in haystack:
                return False
        st = _parse_time(startTime)
        et = _parse_time(endTime)
        created = datetime.fromisoformat(r["createdAt"])
        if st and created < st:
            return False
        if et and created > et:
            return False
        return True

    filtered = [r for r in items if match(r)]
    total = len(filtered)
    start = (page - 1) * pageSize
    end = start + pageSize
    page_items = [md.to_list_item(r) for r in filtered[start:end]]

    return ok({
        "items": page_items,
        "total": total,
        "page": page,
        "pageSize": pageSize,
    })


@router.get("/{record_id}", summary="违章详情")
def get_record(record_id: str, current=Depends(get_current_user)):
    record = md.find_record(record_id)
    if not record:
        raise err_not_found("记录不存在")
    return ok(record)


@router.post("/batch-delete", summary="批量删除")
def batch_delete(body: BatchDeleteRequest, current=Depends(get_current_user)):
    id_set = set(body.ids)
    before = len(md.RECORDS)
    md.RECORDS[:] = [r for r in md.RECORDS if r["id"] not in id_set]
    deleted = before - len(md.RECORDS)
    return ok({"deleted": deleted})


@router.post("/{record_id}/review", summary="提交审核结果")
def review_record(record_id: str, body: ReviewRequest, current=Depends(get_current_user)):
    record = md.find_record(record_id)
    if not record:
        raise err_not_found("记录不存在")

    result = body.result
    # correct / experiment_correct -> approved；wrong -> rejected
    new_status = "rejected" if result == "wrong" else "approved"
    action = new_status
    action_text = md.REVIEW_RESULT_TEXT[result]

    record["reviewResult"] = result
    record["reviewResultText"] = action_text
    record["processStatus"] = new_status
    record["processStatusText"] = md.PROCESS_STATUS_TEXT[new_status]
    record["reviewHistory"].append({
        "time": datetime.now().replace(microsecond=0).isoformat(),
        "operator": current["username"],
        "action": action,
        "actionText": action_text,
        "remark": body.remark or "",
    })
    return ok(record)


@router.delete("/{record_id}", summary="删除一条记录")
def delete_record(record_id: str, current=Depends(get_current_user)):
    record = md.find_record(record_id)
    if not record:
        raise err_not_found("记录不存在")
    md.RECORDS[:] = [r for r in md.RECORDS if r["id"] != record_id]
    return ok({"id": record_id})
