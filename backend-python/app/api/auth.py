"""鉴权接口 /api/auth/*。"""
from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.response import ok, err_business, err_validation
from app.core.security import authenticate_user, create_access_token, get_current_user
from app.data.mock_data import public_user, find_user_by_id
from app.schemas.models import LoginRequest, ProfileUpdateRequest, PasswordUpdateRequest

router = APIRouter(prefix="/api/auth", tags=["Auth 鉴权"])


@router.post("/login", summary="登录")
def login(body: LoginRequest):
    user = authenticate_user(body.username, body.password)
    if not user:
        raise err_business("用户名或密码错误")
    token = create_access_token(user)
    return ok({
        "token": token,
        "tokenType": "Bearer",
        "expiresIn": settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        "user": public_user(user),
    })


@router.get("/me", summary="获取当前登录用户")
def me(current=Depends(get_current_user)):
    return ok(public_user(current))


@router.post("/logout", summary="登出")
def logout(current=Depends(get_current_user)):
    return ok(None, message="已登出")


@router.put("/profile", summary="更新个人资料")
def update_profile(body: ProfileUpdateRequest, current=Depends(get_current_user)):
    user = find_user_by_id(current["id"])
    if not user:
        raise err_business("用户不存在")
    for field in ("displayName", "email", "phone", "dept", "avatar"):
        value = getattr(body, field)
        if value is not None:
            user[field] = value
    return ok(public_user(user))


@router.put("/password", summary="修改密码")
def update_password(body: PasswordUpdateRequest, current=Depends(get_current_user)):
    if body.oldPassword != current["password"]:
        raise err_business("原密码错误")
    if len(body.newPassword) < 6:
        raise err_validation("新密码至少6位")
    user = find_user_by_id(current["id"])
    if not user:
        raise err_business("用户不存在")
    user["password"] = body.newPassword
    return ok(None, message="密码修改成功")
