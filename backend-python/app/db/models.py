"""ORM 数据模型：与 app/data/mock_data.py 的实体一一对应。

每个类即一张表。列名采用 snake_case，并在注释中标注契约里的原始驼峰字段名，
便于与 API-CONTRACT.md / 前端字段对照。时间统一以 ISO 字符串存储，保持与死数据完全一致。
"""
from typing import List, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# ---------------------------------------------------------------------------
# 字典 / 元数据
# ---------------------------------------------------------------------------
class Category(Base):
    """违章类别字典。"""

    __tablename__ = "categories"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[str] = mapped_column(String, nullable=False)  # 违章等级 高/中/低


class Scene(Base):
    """场景字典。"""

    __tablename__ = "scenes"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Team(Base):
    """作业队 / 井队字典。"""

    __tablename__ = "teams"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Unit(Base):
    """二级单位字典。"""

    __tablename__ = "units"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Version(Base):
    """运行版本字典。"""

    __tablename__ = "versions"

    version: Mapped[str] = mapped_column(String, primary_key=True)


class ProcessStatus(Base):
    """处理状态字典。"""

    __tablename__ = "process_status"

    status: Mapped[str] = mapped_column(String, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)


# ---------------------------------------------------------------------------
# 用户
# ---------------------------------------------------------------------------
class User(Base):
    """系统用户（含明文密码，仅演示用）。"""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)  # displayName
    role: Mapped[str] = mapped_column(String, nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    dept: Mapped[Optional[str]] = mapped_column(String, nullable=True)


# ---------------------------------------------------------------------------
# 违章记录 + 子表（检测框 / 审核流水）
# ---------------------------------------------------------------------------
class ViolationRecord(Base):
    """违章记录主表（对应契约 RecordDetail，列表项为其字段子集）。"""

    __tablename__ = "violation_records"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    category_code: Mapped[str] = mapped_column(String, index=True)        # categoryCode
    team: Mapped[str] = mapped_column(String, nullable=False)
    team_code: Mapped[str] = mapped_column(String, index=True)            # teamCode
    work_condition: Mapped[str] = mapped_column(String)                   # workCondition
    scene: Mapped[str] = mapped_column(String)
    scene_code: Mapped[str] = mapped_column(String, index=True)           # sceneCode
    thumbnail_url: Mapped[str] = mapped_column(String)                    # thumbnailUrl
    image_url: Mapped[str] = mapped_column(String)                        # imageUrl
    created_at: Mapped[str] = mapped_column(String, index=True)           # createdAt (ISO8601)
    process_status: Mapped[str] = mapped_column(String, index=True)       # processStatus
    process_status_text: Mapped[str] = mapped_column(String)              # processStatusText
    violation_level: Mapped[str] = mapped_column(String)                  # violationLevel
    alarm_type: Mapped[str] = mapped_column(String)                       # alarmType
    version: Mapped[str] = mapped_column(String)
    unit: Mapped[str] = mapped_column(String)
    unit_code: Mapped[str] = mapped_column(String, index=True)            # unitCode
    confidence: Mapped[float] = mapped_column(Float)
    video_frame_url: Mapped[str] = mapped_column(String)                  # videoFrameUrl
    image_width: Mapped[int] = mapped_column(Integer)                     # imageWidth
    image_height: Mapped[int] = mapped_column(Integer)                    # imageHeight
    review_result: Mapped[Optional[str]] = mapped_column(String, nullable=True)        # reviewResult
    review_result_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)   # reviewResultText

    detections: Mapped[List["Detection"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )
    review_history: Mapped[List["ReviewHistory"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )


class Detection(Base):
    """检测框（违章记录的 detections 子项）。bbox 拆为 x/y/w/h 四列。"""

    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[str] = mapped_column(ForeignKey("violation_records.id"), index=True)
    det_key: Mapped[str] = mapped_column(String)        # 原始 detection id，如 "d1"
    label: Mapped[str] = mapped_column(String)
    label_text: Mapped[str] = mapped_column(String)     # labelText
    bbox_x: Mapped[int] = mapped_column(Integer)        # bbox[0] left
    bbox_y: Mapped[int] = mapped_column(Integer)        # bbox[1] top
    bbox_w: Mapped[int] = mapped_column(Integer)        # bbox[2] width
    bbox_h: Mapped[int] = mapped_column(Integer)        # bbox[3] height
    confidence: Mapped[float] = mapped_column(Float)
    color: Mapped[str] = mapped_column(String)

    record: Mapped["ViolationRecord"] = relationship(back_populates="detections")


class ReviewHistory(Base):
    """审核流水（违章记录的 reviewHistory 子项）。"""

    __tablename__ = "review_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[str] = mapped_column(ForeignKey("violation_records.id"), index=True)
    time: Mapped[str] = mapped_column(String)           # ISO8601
    operator: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    action_text: Mapped[str] = mapped_column(String)    # actionText
    remark: Mapped[str] = mapped_column(String, default="")

    record: Mapped["ViolationRecord"] = relationship(back_populates="review_history")


# ---------------------------------------------------------------------------
# 违章管理（类别管理 / 审核记录 / 电子围栏 / 识别项）
# ---------------------------------------------------------------------------
class CategoryAdmin(Base):
    """类别管理（含启用状态、计数、描述、关联场景）。"""

    __tablename__ = "category_admin"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    count: Mapped[int] = mapped_column(Integer)
    desc: Mapped[str] = mapped_column("desc", Text)              # 描述（列名 desc 已显式指定并自动转义）
    related_scene: Mapped[str] = mapped_column(String)          # relatedScene


class ReviewLog(Base):
    """审核记录流水。"""

    __tablename__ = "review_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    record_id: Mapped[str] = mapped_column(String, index=True)  # recordId
    category: Mapped[str] = mapped_column(String)
    operator: Mapped[str] = mapped_column(String)
    result: Mapped[str] = mapped_column(String)
    result_text: Mapped[str] = mapped_column(String)            # resultText
    from_status: Mapped[str] = mapped_column(String)            # fromStatus
    from_status_text: Mapped[str] = mapped_column(String)       # fromStatusText
    to_status: Mapped[str] = mapped_column(String)              # toStatus
    to_status_text: Mapped[str] = mapped_column(String)         # toStatusText
    time: Mapped[str] = mapped_column(String, index=True)       # ISO8601
    remark: Mapped[str] = mapped_column(String, default="")


class FenceConfig(Base):
    """电子围栏配置。points 多边形坐标以 JSON 字符串存储。"""

    __tablename__ = "fences_config"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    scene: Mapped[str] = mapped_column(String)
    scene_code: Mapped[str] = mapped_column(String)             # sceneCode
    camera: Mapped[str] = mapped_column(String)
    fence_type: Mapped[str] = mapped_column("type", String)     # type: line/area
    type_text: Mapped[str] = mapped_column(String)              # typeText
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    points: Mapped[str] = mapped_column(Text)                   # JSON: [[x,y], ...]
    color: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String)             # createdAt (ISO8601)


class RecognitionItem(Base):
    """识别项配置。"""

    __tablename__ = "recognition_items"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category_code: Mapped[str] = mapped_column(String)          # categoryCode
    model_version: Mapped[str] = mapped_column(String)          # modelVersion
    threshold: Mapped[float] = mapped_column(Float)
    sensitivity: Mapped[str] = mapped_column(String)
    sensitivity_text: Mapped[str] = mapped_column(String)       # sensitivityText
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
