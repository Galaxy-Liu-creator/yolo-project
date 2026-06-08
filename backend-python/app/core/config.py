"""应用配置：使用 pydantic-settings 从 .env 读取。"""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# app 包所在目录
APP_DIR = Path(__file__).resolve().parent.parent
# 项目根目录（backend-python）
PROJECT_ROOT = APP_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "HoistGuard"
    SECRET_KEY: str = "hoistguard-demo-secret-key-change-me-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 86400

    # 逗号分隔的来源字符串（避免 pydantic-settings 对 List 字段做 JSON 解析）
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    STATIC_DIR: str = "static"

    # 工作区级数据集目录（相对 project 工作区根，即 backend-python 的上一级）
    DATASET_DIR: str = "dataset/images"

    @property
    def cors_origins(self) -> List[str]:
        return [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]

    @property
    def static_path(self) -> Path:
        """静态资源绝对路径。"""
        return APP_DIR / self.STATIC_DIR

    @property
    def dataset_path(self) -> Path:
        """工作区级数据集图片目录（project/dataset/images）。"""
        return PROJECT_ROOT.parent / self.DATASET_DIR


settings = Settings()
