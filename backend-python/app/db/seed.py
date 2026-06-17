"""把 app/data/mock_data.py 的演示数据写入 SQLite。

- 只读取死数据后落库，不修改任何死数据 / 接口 / 前端。
- 可重复执行：每次先 drop 再建表再插入，保证结果与死数据一致（死数据使用固定随机种子，可复现）。
"""
import json
from typing import Dict

from app.data import mock_data as M
from app.db import models
from app.db.database import Base, SessionLocal, engine


def reset_schema() -> None:
    """重建所有表结构。"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_database() -> Dict[str, int]:
    """把死数据写入数据库，返回各表写入条数。"""
    reset_schema()
    session = SessionLocal()
    try:
        # —— 字典 / 元数据 ——
        session.add_all([models.Category(code=c["code"], name=c["name"], level=c["level"]) for c in M.CATEGORIES])
        session.add_all([models.Scene(code=s["code"], name=s["name"]) for s in M.SCENES])
        session.add_all([models.Team(code=t["code"], name=t["name"]) for t in M.TEAMS])
        session.add_all([models.Unit(code=u["code"], name=u["name"]) for u in M.UNITS])
        session.add_all([models.Version(version=v) for v in M.VERSIONS])
        session.add_all([models.ProcessStatus(status=p["status"], text=p["text"]) for p in M.PROCESS_STATUS])

        # —— 用户 ——
        session.add_all([
            models.User(
                id=u["id"], username=u["username"], password=u["password"],
                display_name=u["displayName"], role=u["role"], avatar=u.get("avatar"),
                email=u.get("email"), phone=u.get("phone"), dept=u.get("dept"),
            )
            for u in M.USERS
        ])

        # —— 违章记录 + 子表（检测框 / 审核流水）——
        det_count = 0
        rh_count = 0
        for r in M.RECORDS:
            rec = models.ViolationRecord(
                id=r["id"], category=r["category"], category_code=r["categoryCode"],
                team=r["team"], team_code=r["teamCode"], work_condition=r["workCondition"],
                scene=r["scene"], scene_code=r["sceneCode"], thumbnail_url=r["thumbnailUrl"],
                image_url=r["imageUrl"], created_at=r["createdAt"], process_status=r["processStatus"],
                process_status_text=r["processStatusText"], violation_level=r["violationLevel"],
                alarm_type=r["alarmType"], version=r["version"], unit=r["unit"], unit_code=r["unitCode"],
                confidence=r["confidence"], video_frame_url=r["videoFrameUrl"],
                image_width=r["imageWidth"], image_height=r["imageHeight"],
                review_result=r.get("reviewResult"), review_result_text=r.get("reviewResultText"),
            )
            for d in r["detections"]:
                bx, by, bw, bh = d["bbox"]
                rec.detections.append(models.Detection(
                    det_key=d["id"], label=d["label"], label_text=d["labelText"],
                    bbox_x=bx, bbox_y=by, bbox_w=bw, bbox_h=bh,
                    confidence=d["confidence"], color=d["color"],
                ))
                det_count += 1
            for h in r.get("reviewHistory", []):
                rec.review_history.append(models.ReviewHistory(
                    time=h["time"], operator=h["operator"], action=h["action"],
                    action_text=h["actionText"], remark=h.get("remark", ""),
                ))
                rh_count += 1
            session.add(rec)

        # —— 类别管理 ——
        session.add_all([
            models.CategoryAdmin(
                code=c["code"], name=c["name"], level=c["level"], enabled=c["enabled"],
                count=c["count"], desc=c["desc"], related_scene=c["relatedScene"],
            )
            for c in M.CATEGORY_ADMIN
        ])

        # —— 审核记录 ——
        session.add_all([
            models.ReviewLog(
                id=l["id"], record_id=l["recordId"], category=l["category"], operator=l["operator"],
                result=l["result"], result_text=l["resultText"], from_status=l["fromStatus"],
                from_status_text=l["fromStatusText"], to_status=l["toStatus"],
                to_status_text=l["toStatusText"], time=l["time"], remark=l.get("remark", ""),
            )
            for l in M.REVIEW_LOGS
        ])

        # —— 电子围栏（points 存 JSON）——
        session.add_all([
            models.FenceConfig(
                id=f["id"], name=f["name"], scene=f["scene"], scene_code=f["sceneCode"],
                camera=f["camera"], fence_type=f["type"], type_text=f["typeText"], enabled=f["enabled"],
                points=json.dumps(f["points"], ensure_ascii=False), color=f["color"], created_at=f["createdAt"],
            )
            for f in M.FENCES_CONFIG
        ])

        # —— 识别项配置 ——
        session.add_all([
            models.RecognitionItem(
                id=ri["id"], name=ri["name"], category_code=ri["categoryCode"],
                model_version=ri["modelVersion"], threshold=ri["threshold"],
                sensitivity=ri["sensitivity"], sensitivity_text=ri["sensitivityText"], enabled=ri["enabled"],
            )
            for ri in M.RECOGNITION_ITEMS
        ])

        session.commit()

        return {
            "categories": len(M.CATEGORIES),
            "scenes": len(M.SCENES),
            "teams": len(M.TEAMS),
            "units": len(M.UNITS),
            "versions": len(M.VERSIONS),
            "process_status": len(M.PROCESS_STATUS),
            "users": len(M.USERS),
            "violation_records": len(M.RECORDS),
            "detections": det_count,
            "review_history": rh_count,
            "category_admin": len(M.CATEGORY_ADMIN),
            "review_logs": len(M.REVIEW_LOGS),
            "fences_config": len(M.FENCES_CONFIG),
            "recognition_items": len(M.RECOGNITION_ITEMS),
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
