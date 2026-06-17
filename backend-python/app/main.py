"""FastAPI 入口：路由挂载、CORS、StaticFiles、全局异常处理。"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import auth, dashboard, meta, records, violation
from app.core.config import settings
from app.core.response import BizError, fail, ok

app = FastAPI(
    title="油田吊装作业安全视频智能分析系统 API",
    description="AegisLift 演示后端：FastAPI + 死数据 + JWT。统一响应 {code,message,data}。",
    version="1.0.0",
)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- 全局异常处理（统一响应结构） ----------------
@app.exception_handler(BizError)
async def biz_error_handler(request: Request, exc: BizError):
    return JSONResponse(
        status_code=exc.http_status,
        content=fail(exc.code, exc.message),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # 422 参数校验失败 -> code 1002
    first = exc.errors()[0] if exc.errors() else {}
    loc = ".".join(str(x) for x in first.get("loc", []) if x != "body")
    msg = first.get("msg", "参数校验失败")
    detail = f"{loc}: {msg}" if loc else msg
    return JSONResponse(status_code=422, content=fail(1002, f"参数校验失败 ({detail})"))


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # 将默认 HTTP 异常映射到统一错误码
    code_map = {401: 1001, 403: 1003, 404: 1004, 422: 1002}
    code = code_map.get(exc.status_code, 1000)
    message = exc.detail if isinstance(exc.detail, str) else "请求错误"
    return JSONResponse(status_code=exc.status_code, content=fail(code, message))


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=fail(1000, f"服务器内部错误: {exc}"))


# ---------------- 静态资源 ----------------
settings.static_path.mkdir(parents=True, exist_ok=True)
# 工作区级数据集目录优先挂载到 /static/datasets（真实吊装/起重机现场图）
if settings.dataset_path.exists():
    app.mount(
        "/static/datasets",
        StaticFiles(directory=str(settings.dataset_path)),
        name="datasets",
    )
app.mount("/static", StaticFiles(directory=str(settings.static_path)), name="static")

# ---------------- 路由 ----------------
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(meta.router)
app.include_router(records.router)
app.include_router(violation.router)


@app.get("/", tags=["Root"], summary="健康检查")
def root():
    return ok({"name": settings.APP_NAME, "status": "running", "docs": "/docs"})
