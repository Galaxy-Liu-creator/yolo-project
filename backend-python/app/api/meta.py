"""元数据 / 字典接口 /api/meta/*（筛选下拉框）。"""
from fastapi import APIRouter, Depends

from app.core.response import ok
from app.core.security import get_current_user
from app.data import mock_data as md

router = APIRouter(prefix="/api/meta", tags=["Meta 字典"])


@router.get("/categories", summary="违章类别")
def categories(current=Depends(get_current_user)):
    return ok([{"code": c["code"], "name": c["name"]} for c in md.CATEGORIES])


@router.get("/scenes", summary="场景")
def scenes(current=Depends(get_current_user)):
    return ok(md.SCENES)


@router.get("/teams", summary="作业队 / 井队")
def teams(current=Depends(get_current_user)):
    return ok(md.TEAMS)


@router.get("/versions", summary="运行版本")
def versions(current=Depends(get_current_user)):
    return ok(md.VERSIONS)


@router.get("/units", summary="二级单位")
def units(current=Depends(get_current_user)):
    return ok(md.UNITS)
