"""请求/响应 pydantic 模型（主要用于请求体校验与 OpenAPI 文档）。"""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ---------------- Auth ----------------
class LoginRequest(BaseModel):
    username: str = Field(..., examples=["admin"])
    password: str = Field(..., examples=["admin123"])


class UserOut(BaseModel):
    id: str
    username: str
    displayName: str
    role: str
    avatar: Optional[str] = None


class LoginData(BaseModel):
    token: str
    tokenType: str = "Bearer"
    expiresIn: int
    user: UserOut


class ProfileUpdateRequest(BaseModel):
    displayName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dept: Optional[str] = None
    avatar: Optional[str] = None


class PasswordUpdateRequest(BaseModel):
    oldPassword: str
    newPassword: str


# ---------------- Records ----------------
class ReviewRequest(BaseModel):
    result: Literal["correct", "wrong", "experiment_correct"]
    remark: Optional[str] = ""


class BatchDeleteRequest(BaseModel):
    ids: List[str]


# ---------------- Violation 违章管理 ----------------
class CategoryUpdateRequest(BaseModel):
    enabled: Optional[bool] = None


class RecognitionUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    threshold: Optional[float] = None
