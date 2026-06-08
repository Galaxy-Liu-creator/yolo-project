"""死数据：用户、字典、违章记录、看板统计。

全部为内存静态数据，进程内可被审核/删除接口修改。
所有实体形状严格对齐 API-CONTRACT.md。
"""
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image

# ---------------------------------------------------------------------------
# 1. 预置用户（死数据）
# ---------------------------------------------------------------------------
USERS: List[dict] = [
    {
        "id": "u1",
        "username": "admin",
        "password": "admin123",
        "displayName": "系统管理员",
        "role": "admin",
        "avatar": None,
        "email": "admin@hoistguard.cn",
        "phone": "13800000001",
        "dept": "安全监督部",
    },
    {
        "id": "u2",
        "username": "auditor",
        "password": "123456",
        "displayName": "安全审核员",
        "role": "auditor",
        "avatar": None,
        "email": "auditor@hoistguard.cn",
        "phone": "13800000002",
        "dept": "作业一区",
    },
]


def find_user_by_username(username: str) -> Optional[dict]:
    return next((u for u in USERS if u["username"] == username), None)


def find_user_by_id(user_id: str) -> Optional[dict]:
    return next((u for u in USERS if u["id"] == user_id), None)


def public_user(user: dict) -> dict:
    """剥离密码后的对外用户对象（对齐契约 user 形状）。"""
    return {
        "id": user["id"],
        "username": user["username"],
        "displayName": user["displayName"],
        "role": user["role"],
        "avatar": user.get("avatar"),
        "email": user.get("email"),
        "phone": user.get("phone"),
        "dept": user.get("dept"),
    }


# ---------------------------------------------------------------------------
# 2. 字典 / 元数据
# ---------------------------------------------------------------------------
# 违章类别（code 固定，含默认违章等级）
CATEGORIES: List[dict] = [
    {"code": "person_under_load", "name": "作业人员进入吊物下方", "level": "高"},
    {"code": "person_in_rotation_radius", "name": "作业人员进入机械旋转半径内", "level": "高"},
    {"code": "no_helmet", "name": "未佩戴安全帽", "level": "中"},
    {"code": "no_safety_harness", "name": "高处作业未系安全带", "level": "高"},
    {"code": "cross_fence", "name": "人员越过电子围栏", "level": "高"},
    {"code": "illegal_command", "name": "违规指挥吊装", "level": "中"},
    {"code": "improper_rigging", "name": "吊物捆绑/索具不规范", "level": "中"},
    {"code": "no_workwear", "name": "未穿戴反光背心", "level": "低"},
]

# 场景
SCENES: List[dict] = [
    {"code": "jingchang", "name": "井场"},
    {"code": "platform", "name": "作业平台"},
    {"code": "pipe_yard", "name": "管材堆场"},
    {"code": "equip_zone", "name": "设备吊装区"},
]

# 作业队 / 井队（虚构车牌式代号，不含公司全称）
TEAMS: List[dict] = [
    {"code": "team_a", "name": "鲁EK8569"},
    {"code": "team_b", "name": "鲁HG2317"},
    {"code": "team_c", "name": "鲁QD7042"},
    {"code": "team_d", "name": "鲁BZ1985"},
]

# 运行版本
VERSIONS: List[str] = ["V20250917", "V20250801"]

# 二级单位
UNITS: List[dict] = [
    {"code": "unit1", "name": "第一作业区"},
    {"code": "unit2", "name": "第二作业区"},
    {"code": "unit3", "name": "第三作业区"},
]

# 处理状态字典
PROCESS_STATUS: List[dict] = [
    {"status": "pending_review", "text": "待初审"},
    {"status": "unprocessed", "text": "未处理"},
    {"status": "approved", "text": "初审通过"},
    {"status": "rejected", "text": "初审未通过"},
]
PROCESS_STATUS_TEXT: Dict[str, str] = {s["status"]: s["text"] for s in PROCESS_STATUS}

# 告警类型
ALARM_TYPES = ["实时告警", "离线分析"]

# 审核结果文案
REVIEW_RESULT_TEXT: Dict[str, str] = {
    "correct": "识别正确",
    "wrong": "识别错误",
    "experiment_correct": "实验正确",
}

# 样例图片文件名（真实公开施工安全数据集图片）。
# 实际文件存放于工作区 project/dataset/images/，由后端挂载到 /static/datasets/。
# 见 project/dataset/DATASET-LICENSE.md；若缺失则回退到 PIL 生成的占位图 samples/）。
# 路径相对 /static，前端通过 /static/<path> 访问。
_REAL_IMAGES = [
    "datasets/aswin_hoist_1083.jpg",
    "datasets/aswin_hoist_3072.jpg",
    "datasets/aswin_hoist_3008.jpg",
    "datasets/aswin_hoist_3068.jpg",
    "datasets/aswin_hoist_46.jpg",
]
_PLACEHOLDER_IMAGES = [
    "samples/sample_01.jpg",
    "samples/sample_02.jpg",
    "samples/sample_03.jpg",
    "samples/sample_04.jpg",
    "samples/sample_05.jpg",
    "samples/sample_06.jpg",
]


def _resolve_sample_images() -> List[str]:
    """优先使用工作区真实数据集图片，缺失则回退占位图。"""
    from app.core.config import settings

    dataset_dir = settings.dataset_path
    real = [p for p in _REAL_IMAGES if (dataset_dir / Path(p).name).exists()]
    if len(real) == len(_REAL_IMAGES):
        return real
    if real:
        # 部分存在：用已存在的真实图，避免 404
        return real
    return _PLACEHOLDER_IMAGES


SAMPLE_IMAGES = _resolve_sample_images()

IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720

_PPE_CLASS_MAP = {
    0: ("helmet", "安全帽", "#faad14"),
    1: ("no_helmet", "未佩戴安全帽", "#ff4d4f"),
    2: ("no_vest", "未穿戴反光背心", "#ff7a45"),
    3: ("person", "人员", "#1890ff"),
    4: ("vest", "反光背心", "#52c41a"),
    # Aswin ConstructionSiteCleanedDataSet rule-level violation classes.
    10: ("no_helmet", "未佩戴安全帽", "#ff4d4f"),
    11: ("no_safety_harness", "未系安全带", "#ff4d4f"),
    13: ("person_in_rotation_radius", "机械作业半径内人员", "#ff4d4f"),
}
_VIOLATION_LABEL_CLASSES = {1, 2, 10, 11, 13}
_PPE_CATEGORY_BY_CLASS = {
    1: "no_helmet",
    2: "no_workwear",
    10: "no_helmet",
    11: "no_safety_harness",
    13: "person_in_rotation_radius",
}


# ---------------------------------------------------------------------------
# 3. 生成检测框 / 电子围栏（像素坐标，基于 1280x720）
# ---------------------------------------------------------------------------
_LABEL_MAP = {
    "person": "人员",
    "load": "吊物",
    "boom": "吊臂",
    "helmet": "安全帽",
    "rigging": "索具",
}
_COLOR_PERSON = "#ff4d4f"
_COLOR_LOAD = "#52c41a"
_COLOR_BOOM = "#1890ff"
_COLOR_HELMET = "#faad14"


def _category_by_code(code: str) -> dict:
    return next((c for c in CATEGORIES if c["code"] == code), CATEGORIES[0])


def _dataset_image_path(sample: str) -> Optional[Path]:
    if not sample.startswith("datasets/"):
        return None
    from app.core.config import settings

    return settings.dataset_path / Path(sample).name


def _dataset_label_path(sample: str) -> Optional[Path]:
    image_path = _dataset_image_path(sample)
    if not image_path:
        return None
    return image_path.parent.parent / "labels" / f"{image_path.stem}.txt"


def _image_size(sample: str) -> tuple[int, int]:
    image_path = _dataset_image_path(sample)
    if image_path and image_path.exists():
        with Image.open(image_path) as img:
            return img.size
    return IMAGE_WIDTH, IMAGE_HEIGHT


def _read_yolo_rows(sample: str) -> List[tuple[int, float, float, float, float]]:
    label_path = _dataset_label_path(sample)
    if not label_path or not label_path.exists():
        return []

    rows: List[tuple[int, float, float, float, float]] = []
    for raw in label_path.read_text(encoding="utf-8-sig").splitlines():
        parts = raw.strip().split()
        if len(parts) != 5:
            continue
        try:
            cls = int(parts[0])
            x, y, w, h = [float(v) for v in parts[1:]]
        except ValueError:
            continue
        rows.append((cls, x, y, w, h))
    return rows


def _category_for_sample(sample: str) -> dict:
    classes = [row[0] for row in _read_yolo_rows(sample)]
    for cls in (11, 13, 10, 1, 2):
        if cls in classes:
            return _category_by_code(_PPE_CATEGORY_BY_CLASS[cls])
    return _category_by_code("person_under_load")


def _yolo_bbox_to_pixels(
    x: float,
    y: float,
    w: float,
    h: float,
    image_width: int,
    image_height: int,
) -> List[int]:
    left = max(0, int(round((x - w / 2) * image_width)))
    top = max(0, int(round((y - h / 2) * image_height)))
    width = min(image_width - left, int(round(w * image_width)))
    height = min(image_height - top, int(round(h * image_height)))
    return [left, top, max(1, width), max(1, height)]


def _gen_dataset_detections(sample: str, rng: random.Random) -> List[dict]:
    image_width, image_height = _image_size(sample)
    dets: List[dict] = []
    for cls, x, y, w, h in _read_yolo_rows(sample):
        if cls not in _VIOLATION_LABEL_CLASSES:
            continue
        label, label_text, color = _PPE_CLASS_MAP[cls]
        dets.append({
            "id": f"d{len(dets) + 1}",
            "label": label,
            "labelText": label_text,
            "bbox": _yolo_bbox_to_pixels(x, y, w, h, image_width, image_height),
            "confidence": round(rng.uniform(0.84, 0.97), 2),
            "color": color,
        })
    return dets


def _gen_detections(rng: random.Random) -> List[dict]:
    """生成 2~4 个检测框，坐标均落在画面内。"""
    dets: List[dict] = []
    # 人员
    px = rng.randint(120, 760)
    py = rng.randint(260, 480)
    dets.append({
        "id": "d1",
        "label": "person",
        "labelText": _LABEL_MAP["person"],
        "bbox": [px, py, rng.randint(48, 72), rng.randint(100, 140)],
        "confidence": round(rng.uniform(0.82, 0.97), 2),
        "color": _COLOR_PERSON,
    })
    # 吊物
    lx = rng.randint(640, 980)
    ly = rng.randint(220, 420)
    dets.append({
        "id": "d2",
        "label": "load",
        "labelText": _LABEL_MAP["load"],
        "bbox": [lx, ly, rng.randint(70, 130), rng.randint(60, 110)],
        "confidence": round(rng.uniform(0.80, 0.95), 2),
        "color": _COLOR_LOAD,
    })
    # 吊臂（部分记录）
    if rng.random() < 0.6:
        dets.append({
            "id": "d3",
            "label": "boom",
            "labelText": _LABEL_MAP["boom"],
            "bbox": [rng.randint(700, 1000), rng.randint(60, 160), rng.randint(160, 260), rng.randint(28, 50)],
            "confidence": round(rng.uniform(0.78, 0.93), 2),
            "color": _COLOR_BOOM,
        })
    # 安全帽（部分记录）
    if rng.random() < 0.5:
        dets.append({
            "id": "d4",
            "label": "helmet",
            "labelText": _LABEL_MAP["helmet"],
            "bbox": [px + 6, max(py - 34, 10), 36, 30],
            "confidence": round(rng.uniform(0.75, 0.92), 2),
            "color": _COLOR_HELMET,
        })
    return dets


def _gen_fences(rng: random.Random) -> List[dict]:
    """监控记录详情不叠加电子围栏，避免与真实图片视角不匹配。"""
    return []


# ---------------------------------------------------------------------------
# 4. 生成违章记录（30~60 条）
# ---------------------------------------------------------------------------
# processStatus 分布（让四种状态都出现且合理）
_STATUS_POOL = (
    ["pending_review"] * 9
    + ["unprocessed"] * 6
    + ["approved"] * 9
    + ["rejected"] * 6
)


def _build_record(idx: int, rng: random.Random) -> dict:
    img = SAMPLE_IMAGES[idx % len(SAMPLE_IMAGES)]
    cat = _category_for_sample(img)
    scene = rng.choice(SCENES)
    team = rng.choice(TEAMS)
    unit = rng.choice(UNITS)
    version = rng.choice(VERSIONS)
    status = _STATUS_POOL[idx % len(_STATUS_POOL)]
    img_url = f"/static/{img}"
    image_width, image_height = _image_size(img)

    # createdAt 分散在近 7 天内
    days_ago = rng.randint(0, 6)
    base = datetime.now().replace(microsecond=0) - timedelta(days=days_ago)
    created = base - timedelta(
        hours=rng.randint(0, 12), minutes=rng.randint(0, 59), seconds=rng.randint(0, 59)
    )

    rid = f"v{100001 + idx}"
    detections = _gen_dataset_detections(img, rng) or _gen_detections(rng)
    fences = _gen_fences(rng)

    # 审核结果与状态联动
    review_result = None
    review_result_text = None
    review_history: List[dict] = []
    if status == "approved":
        review_result = rng.choice(["correct", "experiment_correct"])
        review_result_text = REVIEW_RESULT_TEXT[review_result]
        review_history.append({
            "time": (created + timedelta(minutes=rng.randint(5, 120))).isoformat(),
            "operator": rng.choice(["admin", "auditor"]),
            "action": "approved",
            "actionText": review_result_text,
            "remark": "",
        })
    elif status == "rejected":
        review_result = "wrong"
        review_result_text = REVIEW_RESULT_TEXT["wrong"]
        review_history.append({
            "time": (created + timedelta(minutes=rng.randint(5, 120))).isoformat(),
            "operator": rng.choice(["admin", "auditor"]),
            "action": "rejected",
            "actionText": review_result_text,
            "remark": rng.choice(["误检，画面无人员越界", "光照导致误判", ""]),
        })

    record = {
        # —— RecordListItem 字段 ——
        "id": rid,
        "category": cat["name"],
        "categoryCode": cat["code"],
        "team": team["name"],
        "teamCode": team["code"],
        "workCondition": "吊装作业",
        "scene": scene["name"],
        "sceneCode": scene["code"],
        "thumbnailUrl": img_url,
        "imageUrl": img_url,
        "createdAt": created.isoformat(),
        "processStatus": status,
        "processStatusText": PROCESS_STATUS_TEXT[status],
        "violationLevel": cat["level"],
        "alarmType": rng.choice(ALARM_TYPES),
        "version": version,
        "unit": unit["name"],
        "unitCode": unit["code"],
        "confidence": round(rng.uniform(0.78, 0.97), 2),
        # —— RecordDetail 扩展字段 ——
        "videoFrameUrl": img_url,
        "imageWidth": image_width,
        "imageHeight": image_height,
        "detections": detections,
        "fences": fences,
        "reviewResult": review_result,
        "reviewResultText": review_result_text,
        "reviewHistory": review_history,
    }
    return record


def _generate_records() -> List[dict]:
    rng = random.Random(20260601)  # 固定种子，演示可复现
    count = 48  # 落在 30~60 区间
    records = [_build_record(i, rng) for i in range(count)]
    # 按创建时间倒序（最新在前）
    records.sort(key=lambda r: r["createdAt"], reverse=True)
    return records


# 进程内可变数据集
RECORDS: List[dict] = _generate_records()

# RecordListItem 包含的字段集（详情比列表项多出的字段在此基础上扩展）
_LIST_FIELDS = [
    "id", "category", "categoryCode", "team", "teamCode", "workCondition",
    "scene", "sceneCode", "thumbnailUrl", "imageUrl", "createdAt",
    "processStatus", "processStatusText", "violationLevel", "alarmType",
    "version", "unit", "unitCode", "confidence",
]


def to_list_item(record: dict) -> dict:
    """从完整记录裁剪为 RecordListItem。"""
    return {k: record[k] for k in _LIST_FIELDS}


def find_record(record_id: str) -> Optional[dict]:
    return next((r for r in RECORDS if r["id"] == record_id), None)


# ---------------------------------------------------------------------------
# 5. 看板统计（部分预置、部分从记录派生）
# ---------------------------------------------------------------------------
def dashboard_stats() -> dict:
    pending = sum(1 for r in RECORDS if r["processStatus"] == "pending_review")
    handled = sum(1 for r in RECORDS if r["processStatus"] in ("approved", "rejected"))
    total_in_mem = len(RECORDS)
    handled_rate = round(handled / total_in_mem, 2) if total_in_mem else 0.0
    return {
        "totalViolations": 3155,  # 平台累计（预置大数）
        "todayAlerts": 42,
        "pendingReview": pending,
        "onlineCameras": 12,
        "totalCameras": 15,
        "handledRate": handled_rate,
    }


def dashboard_trend() -> dict:
    """近 7 天趋势：从记录按天聚合，并补充预置基数使曲线饱满。"""
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    dates = [d.strftime("%m-%d") for d in days]

    total_series: List[int] = []
    handled_series: List[int] = []
    base_total = [120, 98, 145, 160, 132, 180, 155]
    base_handled = [100, 80, 120, 140, 110, 150, 130]
    for i, d in enumerate(days):
        day_records = [r for r in RECORDS if r["createdAt"][:10] == d.isoformat()]
        day_handled = [r for r in day_records if r["processStatus"] in ("approved", "rejected")]
        total_series.append(base_total[i] + len(day_records))
        handled_series.append(base_handled[i] + len(day_handled))

    return {
        "dates": dates,
        "series": [
            {"name": "违章总数", "data": total_series},
            {"name": "已处理", "data": handled_series},
        ],
    }


def dashboard_category_distribution() -> List[dict]:
    """违章类别分布：记录计数 + 预置基数。"""
    base = {
        "person_under_load": 860,
        "person_in_rotation_radius": 642,
        "no_helmet": 410,
        "no_safety_harness": 386,
        "cross_fence": 388,
        "illegal_command": 295,
        "improper_rigging": 360,
        "no_workwear": 200,
    }
    counts = {c["code"]: 0 for c in CATEGORIES}
    for r in RECORDS:
        counts[r["categoryCode"]] = counts.get(r["categoryCode"], 0) + 1
    result = []
    for c in CATEGORIES:
        result.append({
            "name": c["name"],
            "value": base.get(c["code"], 0) + counts.get(c["code"], 0),
        })
    result.sort(key=lambda x: x["value"], reverse=True)
    return result


def dashboard_status_distribution() -> List[dict]:
    """处理状态分布（从内存记录派生）。"""
    counts = {s["status"]: 0 for s in PROCESS_STATUS}
    for r in RECORDS:
        counts[r["processStatus"]] = counts.get(r["processStatus"], 0) + 1
    return [{"name": s["text"], "value": counts[s["status"]]} for s in PROCESS_STATUS]


def dashboard_recent_alarms() -> List[dict]:
    """最近 8 条告警（RecordListItem 形状）。"""
    return [to_list_item(r) for r in RECORDS[:8]]


# ---------------------------------------------------------------------------
# 6. 违章管理（类别管理 / 审核记录 / 电子围栏 / 识别项配置）
# ---------------------------------------------------------------------------
# 6.1 类别管理：基于 CATEGORIES 派生（含 enabled / count / desc / relatedScene）
_CATEGORY_DESC: Dict[str, str] = {
    "person_under_load": "作业人员进入吊物正下方危险区域",
    "person_in_rotation_radius": "作业人员进入机械旋转半径内",
    "no_helmet": "作业人员未按规定佩戴安全帽",
    "no_safety_harness": "高处作业人员未按规定系挂安全带",
    "cross_fence": "人员越过电子围栏进入警戒区域",
    "illegal_command": "指挥人员违规指挥吊装作业",
    "improper_rigging": "吊物捆绑或索具使用不规范",
    "no_workwear": "作业人员未按规定穿戴反光背心",
}
_CATEGORY_SCENE: Dict[str, str] = {
    "person_under_load": "设备吊装区",
    "person_in_rotation_radius": "设备吊装区",
    "no_helmet": "井场",
    "no_safety_harness": "设备吊装区",
    "cross_fence": "作业平台",
    "illegal_command": "作业平台",
    "improper_rigging": "管材堆场",
    "no_workwear": "井场",
}


def _build_category_admin() -> List[dict]:
    rng = random.Random(20260602)  # 固定种子，演示可复现
    items: List[dict] = []
    for i, c in enumerate(CATEGORIES):
        items.append({
            "code": c["code"],
            "name": c["name"],
            "level": c["level"],
            # 末项默认停用，其余启用
            "enabled": False if i == len(CATEGORIES) - 1 else True,
            "count": rng.randint(200, 900),
            "desc": _CATEGORY_DESC.get(c["code"], c["name"]),
            "relatedScene": _CATEGORY_SCENE.get(c["code"], SCENES[i % len(SCENES)]["name"]),
        })
    return items


# 进程内可变（PUT 接口修改 enabled）
CATEGORY_ADMIN: List[dict] = _build_category_admin()


def list_category_admin() -> List[dict]:
    return CATEGORY_ADMIN


def find_category_admin(code: str) -> Optional[dict]:
    return next((c for c in CATEGORY_ADMIN if c["code"] == code), None)


# 6.2 审核记录 REVIEW_LOGS（~30 条）
_RESULT_POOL = (
    ["correct"] * 5 + ["wrong"] * 3 + ["experiment_correct"] * 2
)
_REVIEW_STATUS_PAIR = {
    "correct": ("pending_review", "approved"),
    "experiment_correct": ("pending_review", "approved"),
    "wrong": ("pending_review", "rejected"),
}
_REVIEW_REMARKS = [
    "", "", "复核无误", "误检，画面无人员越界", "光照导致误判",
    "实验环境复现确认", "现场已整改",
]


def _build_review_logs() -> List[dict]:
    rng = random.Random(20260603)  # 固定种子，演示可复现
    logs: List[dict] = []
    for i in range(30):
        result = _RESULT_POOL[i % len(_RESULT_POOL)]
        from_status, to_status = _REVIEW_STATUS_PAIR[result]
        cat = rng.choice(CATEGORIES)
        operator = rng.choice(USERS)["displayName"]
        days_ago = rng.randint(0, 6)
        t = datetime.now().replace(microsecond=0) - timedelta(
            days=days_ago,
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
            seconds=rng.randint(0, 59),
        )
        logs.append({
            "id": f"rl{1001 + i}",
            "recordId": f"v{100001 + rng.randint(0, 47)}",
            "category": cat["name"],
            "operator": operator,
            "result": result,
            "resultText": REVIEW_RESULT_TEXT[result],
            "fromStatus": from_status,
            "fromStatusText": PROCESS_STATUS_TEXT[from_status],
            "toStatus": to_status,
            "toStatusText": PROCESS_STATUS_TEXT[to_status],
            "time": t.isoformat(),
            "remark": rng.choice(_REVIEW_REMARKS),
        })
    logs.sort(key=lambda x: x["time"], reverse=True)
    return logs


REVIEW_LOGS: List[dict] = _build_review_logs()


# 6.3 电子围栏配置 FENCES_CONFIG（~8 条）
def _build_fences_config() -> List[dict]:
    rng = random.Random(20260604)  # 固定种子
    fence_types = [("line", "警戒线"), ("area", "区域")]
    items: List[dict] = []
    for i in range(8):
        ftype, ftext = fence_types[i % 2]
        scene = SCENES[i % len(SCENES)]
        n_points = 2 if ftype == "line" else rng.randint(3, 4)
        points = [
            [rng.randint(100, 1180), rng.randint(80, 640)]
            for _ in range(n_points)
        ]
        items.append({
            "id": f"fc{101 + i}",
            "name": f"{i + 1}号井场-{ftext}",
            "scene": scene["name"],
            "sceneCode": scene["code"],
            "camera": f"CAM-{i + 1:02d}",
            "type": ftype,
            "typeText": ftext,
            "enabled": False if i == 5 else True,
            "points": points,
            "color": "#ff00ff" if ftype == "line" else "#00e5ff",
            "createdAt": (
                datetime.now().replace(microsecond=0) - timedelta(days=10 + i)
            ).isoformat(),
        })
    return items


FENCES_CONFIG: List[dict] = _build_fences_config()


# 6.4 识别项配置 RECOGNITION_ITEMS（~7 条）
_RECOGNITION_DEFS = [
    ("安全帽检测", "no_helmet"),
    ("人员入侵检测", "person_under_load"),
    ("越界检测", "cross_fence"),
    ("安全带识别", "no_safety_harness"),
    ("吊物识别", "improper_rigging"),
    ("违规指挥识别", "illegal_command"),
    ("索具规范检测", "improper_rigging"),
    ("反光背心识别", "no_workwear"),
]
_SENSITIVITY_TEXT = {"low": "低", "medium": "中", "high": "高"}


def _build_recognition_items() -> List[dict]:
    rng = random.Random(20260605)  # 固定种子
    sens_pool = ["high", "medium", "high", "medium", "low", "medium", "high"]
    items: List[dict] = []
    for i, (name, code) in enumerate(_RECOGNITION_DEFS):
        sens = sens_pool[i % len(sens_pool)]
        items.append({
            "id": f"ri{201 + i}",
            "name": name,
            "categoryCode": code,
            "modelVersion": rng.choice(VERSIONS),
            "threshold": round(rng.uniform(0.5, 0.95), 2),
            "sensitivity": sens,
            "sensitivityText": _SENSITIVITY_TEXT[sens],
            "enabled": False if i == 6 else True,
        })
    return items


RECOGNITION_ITEMS: List[dict] = _build_recognition_items()


def find_recognition_item(item_id: str) -> Optional[dict]:
    return next((r for r in RECOGNITION_ITEMS if r["id"] == item_id), None)
