"""首页看板接口 /api/dashboard/*。"""
from fastapi import APIRouter, Depends

from app.core.response import ok
from app.core.security import get_current_user
from app.data import mock_data as md

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard 看板"])


@router.get("/stats", summary="顶部统计卡片")
def stats(current=Depends(get_current_user)):
    return ok(md.dashboard_stats())


@router.get("/trend", summary="近 7 天违章趋势")
def trend(current=Depends(get_current_user)):
    return ok(md.dashboard_trend())


@router.get("/category-distribution", summary="违章类别分布")
def category_distribution(current=Depends(get_current_user)):
    return ok(md.dashboard_category_distribution())


@router.get("/status-distribution", summary="处理状态分布")
def status_distribution(current=Depends(get_current_user)):
    return ok(md.dashboard_status_distribution())


@router.get("/recent-alarms", summary="最新告警列表")
def recent_alarms(current=Depends(get_current_user)):
    return ok(md.dashboard_recent_alarms())
