"""统一响应包裹与业务异常。"""
from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一响应结构 {code, message, data}。"""
    code: int = 0
    message: str = "ok"
    data: Any = None


def ok(data: Any = None, message: str = "ok") -> dict:
    """成功响应。"""
    return {"code": 0, "message": message, "data": data}


def fail(code: int, message: str, data: Any = None) -> dict:
    """失败响应。"""
    return {"code": code, "message": message, "data": data}


class BizError(Exception):
    """业务异常：携带 HTTP 状态码 + 业务 code + message。

    与契约统一错误码对齐：
      401 / 1001 未登录或 token 无效
      403 / 1003 无权限
      404 / 1004 资源不存在
      422 / 1002 参数校验失败
      400 / 1000 通用业务错误
    """

    def __init__(self, message: str, code: int = 1000, http_status: int = 400):
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)


# 便捷构造器
def err_unauthorized(message: str = "未登录或登录已过期") -> BizError:
    return BizError(message, code=1001, http_status=401)


def err_forbidden(message: str = "无权限") -> BizError:
    return BizError(message, code=1003, http_status=403)


def err_not_found(message: str = "资源不存在") -> BizError:
    return BizError(message, code=1004, http_status=404)


def err_validation(message: str = "参数校验失败") -> BizError:
    return BizError(message, code=1002, http_status=422)


def err_business(message: str = "业务处理失败") -> BizError:
    return BizError(message, code=1000, http_status=400)
