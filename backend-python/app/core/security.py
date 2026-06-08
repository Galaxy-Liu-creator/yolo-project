"""JWT 生成/校验、用户校验与 get_current_user 依赖。"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.response import err_unauthorized
from app.data.mock_data import find_user_by_username, find_user_by_id

# auto_error=False：自身处理缺失 token，返回统一 401 结构而非 FastAPI 默认 403
_bearer = HTTPBearer(auto_error=False)


def verify_password(plain: str, stored: str) -> bool:
    """演示用明文比对（死数据账号）。"""
    return plain == stored


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """校验用户名密码，成功返回用户 dict，失败返回 None。"""
    user = find_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


def create_access_token(user: dict) -> str:
    """生成 JWT。sub = 用户 id。"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    payload = {
        "sub": user["id"],
        "username": user["username"],
        "role": user["role"],
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """解析 JWT，失败抛 BizError(1001)。"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise err_unauthorized("登录已过期，请重新登录")
    except jwt.PyJWTError:
        raise err_unauthorized("token 无效")
    return payload


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> dict:
    """依赖：从 Bearer token 解析当前用户。失败抛 401 / code 1001。"""
    if credentials is None or not credentials.credentials:
        raise err_unauthorized("缺少认证信息")
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    user = find_user_by_id(user_id) if user_id else None
    if not user:
        raise err_unauthorized("用户不存在或 token 无效")
    return user
