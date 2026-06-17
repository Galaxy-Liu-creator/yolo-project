"""SQLite 连接与会话管理（SQLAlchemy 2.0）。

- 数据库文件：backend-python/app.db（单文件，无需任何服务进程）。
- engine / SessionLocal / Base 供 models 与 seed 使用。
- 该模块独立存在，不会被 app.main 等运行时代码导入，因此对现有演示零影响。
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# app/db/database.py -> app/db -> app -> backend-python
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

# SQLite 单文件数据库路径
DB_PATH = BACKEND_ROOT / "app.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False 便于多线程（如后续接入 FastAPI）共享连接
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """所有 ORM 模型的声明式基类。"""

    pass
