# AegisLift 油田吊装作业安全视频智能分析系统 — API 契约 (v1)

> 本文件是前后端对齐的**唯一事实来源**。后端按此实现，前端按此消费。任何一方需要变更，必须先改本文件。
> 后端：FastAPI + 死数据（无数据库，内存/JSON 静态数据）。鉴权：JWT。AI 识别：预置静态结果。

---

## 0. 全局约定

- **Base URL**：`http://127.0.0.1:8000`
- **API 前缀**：所有接口以 `/api` 开头。
- **静态资源**：样例图片通过 `/static/...` 提供（FastAPI StaticFiles 挂载）。
- **CORS**：后端允许来源 `http://localhost:5173` 与 `http://127.0.0.1:5173`（Vite 默认端口），允许所有方法与 header。
- **内容类型**：请求与响应均为 `application/json`（文件/图片除外）。
- **时间格式**：ISO8601 字符串，例 `"2026-02-06T15:34:42"`。
- **鉴权**：除 `/api/auth/login` 外，所有接口需在 Header 携带 `Authorization: Bearer <token>`。

### 统一响应包裹

所有业务接口返回统一结构：

```json
{ "code": 0, "message": "ok", "data": <payload> }
```

- `code`：0 = 成功；非 0 = 业务错误。
- `message`：人类可读信息。
- `data`：见各接口定义；出错时为 `null`。

### 统一错误码

| HTTP | code | 含义 |
|------|------|------|
| 200  | 0    | 成功 |
| 401  | 1001 | 未登录 / token 无效或过期 |
| 403  | 1003 | 无权限 |
| 404  | 1004 | 资源不存在 |
| 422  | 1002 | 参数校验失败 |
| 400  | 1000 | 通用业务错误 |

> 注：鉴权失败时 HTTP 状态码用 401，body 仍为统一结构 `{code:1001,...}`。

### 分页约定

列表接口入参：`page`（从 1 开始，默认 1）、`pageSize`（默认 10）。
列表返回：

```json
{ "items": [ ... ], "total": 123, "page": 1, "pageSize": 10 }
```

---

## 1. 鉴权 Auth

### POST `/api/auth/login`
登录，无需 token。

请求：
```json
{ "username": "admin", "password": "admin123" }
```

成功 `data`：
```json
{
  "token": "<jwt>",
  "tokenType": "Bearer",
  "expiresIn": 86400,
  "user": { "id": "u1", "username": "admin", "displayName": "系统管理员", "role": "admin", "avatar": null }
}
```

失败：`code=1000`，message "用户名或密码错误"。

**预置账号（死数据）**：
- `admin` / `admin123`（role: admin）
- `auditor` / `123456`（role: auditor，审核员）

### GET `/api/auth/me`
获取当前登录用户。返回 `data` 为上面的 `user` 对象。

### POST `/api/auth/logout`
登出（前端清 token 即可，后端返回 `data:null`）。

---

## 2. 首页看板 Dashboard

### GET `/api/dashboard/stats`
顶部统计卡片。`data`：
```json
{
  "totalViolations": 3155,
  "todayAlerts": 42,
  "pendingReview": 18,
  "onlineCameras": 12,
  "totalCameras": 15,
  "handledRate": 0.86
}
```

### GET `/api/dashboard/trend`
近 7 天违章趋势（折线图）。`data`：
```json
{
  "dates": ["02-01","02-02","02-03","02-04","02-05","02-06","02-07"],
  "series": [
    { "name": "违章总数", "data": [120,98,145,160,132,180,155] },
    { "name": "已处理",   "data": [100,80,120,140,110,150,130] }
  ]
}
```

### GET `/api/dashboard/category-distribution`
违章类别分布（饼图/柱图）。`data`：数组
```json
[ { "name": "作业人员进入吊物下方", "value": 860 },
  { "name": "作业人员进入机械旋转半径内", "value": 642 },
  { "name": "未佩戴安全帽", "value": 410 } ]
```

### GET `/api/dashboard/status-distribution`
处理状态分布。`data`：数组 `[ {"name":"待初审","value":120}, ... ]`
状态取值见第 5 节 `processStatus` 字典。

### GET `/api/dashboard/recent-alarms`
最新告警列表（看板右侧滚动）。`data`：违章记录精简数组（取最近 8 条，字段同列表项 RecordListItem）。

---

## 3. 元数据 / 字典 Meta（用于筛选下拉框）

### GET `/api/meta/categories` — 违章类别
`data`：`[ { "code": "person_under_load", "name": "作业人员进入吊物下方" }, ... ]`

### GET `/api/meta/scenes` — 场景
`data`：`[ { "code": "jingchang", "name": "井场" }, ... ]`

### GET `/api/meta/teams` — 作业队/井队
`data`：`[ { "code": "team_a", "name": "鲁EK8569" }, ... ]`

### GET `/api/meta/versions` — 运行版本
`data`：`[ "V20250917", "V20250801" ]`（字符串数组）

### GET `/api/meta/units` — 二级单位
`data`：`[ { "code": "unit1", "name": "第一作业区" }, ... ]`

> 字典内容由后端死数据决定，前端不得硬编码，必须调用接口获取。

---

## 4. 违章类别字典（业务约定，吊装场景）

后端 `categories` 至少包含以下项（code 固定，name 可调整）：

| code | name | 默认违章等级 |
|------|------|------|
| person_under_load | 作业人员进入吊物下方 | 高 |
| person_in_rotation_radius | 作业人员进入机械旋转半径内 | 高 |
| no_helmet | 未佩戴安全帽 | 中 |
| cross_fence | 人员越过电子围栏 | 高 |
| illegal_command | 违规指挥吊装 | 中 |
| improper_rigging | 吊物捆绑/索具不规范 | 中 |
| no_workwear | 未穿戴工装 | 低 |

场景 scenes：`井场(jingchang)`、`钻井平台(platform)`、`管材堆场(pipe_yard)`、`设备吊装区(equip_zone)`。

---

## 5. 监控记录 / 违章管理 Records

### 数据实体

**RecordListItem（列表项）**：
```json
{
  "id": "v100001",
  "category": "作业人员进入机械旋转半径内",
  "categoryCode": "person_in_rotation_radius",
  "team": "鲁EK8569",
  "workCondition": "吊装作业",
  "scene": "井场",
  "sceneCode": "jingchang",
  "thumbnailUrl": "/static/samples/sample_01.jpg",
  "imageUrl": "/static/samples/sample_01.jpg",
  "createdAt": "2026-02-06T15:34:42",
  "processStatus": "pending_review",
  "processStatusText": "待初审",
  "violationLevel": "高",
  "alarmType": "实时告警",
  "version": "V20250917",
  "unit": "第一作业区",
  "confidence": 0.86
}
```

**processStatus 字典**（前端按 text 显示，按 status 上色）：
| status | text | 建议颜色 |
|--------|------|------|
| pending_review | 待初审 | 橙 |
| unprocessed | 未处理 | 灰 |
| approved | 初审通过 | 绿 |
| rejected | 初审未通过 | 红 |

**RecordDetail（详情，继承列表项全部字段 + 以下）**：
```json
{
  "...": "RecordListItem 全部字段",
  "videoFrameUrl": "/static/samples/sample_01.jpg",
  "imageWidth": 1280,
  "imageHeight": 720,
  "detections": [
    { "id": "d1", "label": "person", "labelText": "人员", "bbox": [330,300,60,110], "confidence": 0.91, "color": "#ff4d4f" },
    { "id": "d2", "label": "load", "labelText": "吊物", "bbox": [760,320,70,70], "confidence": 0.86, "color": "#52c41a" }
  ],
  "fences": [
    { "id": "f1", "name": "电子围栏-上", "points": [[200,175],[1130,175]], "color": "#ff00ff" },
    { "id": "f2", "name": "电子围栏-下", "points": [[200,540],[1130,540]], "color": "#ff00ff" }
  ],
  "reviewResult": null,
  "reviewResultText": null,
  "reviewHistory": [
    { "time": "2026-02-06T15:40:00", "operator": "admin", "action": "approved", "actionText": "识别正确", "remark": "" }
  ]
}
```

> **bbox 坐标系**：`[x, y, w, h]`，单位为像素，基于 `imageWidth × imageHeight`（1280×720）。前端按图片实际渲染尺寸做等比缩放绘制。
> **fences.points**：折线点数组，同一坐标系（像素，基于 imageWidth×imageHeight）。

### GET `/api/records`
分页查询违章记录。Query 参数（全部可选）：

| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码，默认 1 |
| pageSize | int | 每页条数，默认 10 |
| categoryCode | string | 违章类别 code |
| processStatus | string | 处理状态 |
| version | string | 运行版本 |
| unit | string | 二级单位 code |
| team | string | 井队 code |
| sceneCode | string | 场景 code |
| keyword | string | 关键字（检测ID/类别模糊匹配） |
| startTime | string | 创建时间起 ISO8601 |
| endTime | string | 创建时间止 ISO8601 |

`data`：分页结构，`items` 为 RecordListItem 数组。

### GET `/api/records/{id}`
违章详情。`data` 为 RecordDetail；不存在返回 404 / code 1004。

### POST `/api/records/{id}/review`
提交审核结果（对应详情页"识别正确/识别错误/实验正确"按钮）。

请求：
```json
{ "result": "correct", "remark": "" }
```
`result` 取值：`correct`(识别正确) | `wrong`(识别错误) | `experiment_correct`(实验正确)。

行为：更新该记录 `reviewResult`，并据此更新 `processStatus`（correct→approved，wrong→rejected，experiment_correct→approved），追加一条 `reviewHistory`。
`data`：更新后的 RecordDetail。

### DELETE `/api/records/{id}`
删除一条记录。`data`：`{ "id": "v100001" }`。

### POST `/api/records/batch-delete`
批量删除（列表多选）。请求 `{ "ids": ["v1","v2"] }`，`data`：`{ "deleted": 2 }`。

---

## 6. 样例图片资源

后端在 `backend-python/static/samples/` 放置若干吊装/作业现场样例图（可用纯色占位图或现场图），通过 `/static/samples/xxx.jpg` 暴露。死数据记录的 `imageUrl/thumbnailUrl/videoFrameUrl` 指向这些路径。前端通过 `Base URL + imageUrl` 拼接访问。

---

## 7. 前端路由约定（供后端了解，前端实现）

| 路径 | 页面 |
|------|------|
| /login | 登录页 |
| / 或 /dashboard | 首页数据看板 |
| /records | 监控记录列表 |
| /records/:id | 监控详情 + 审核 |

未登录访问受保护路由 → 跳转 /login。

---

## 8. 命名与文案约束（重要）

- 系统标题统一为：**油田吊装作业安全视频智能分析系统**（页面/标题栏）。
- **禁止**出现任何真实公司字样（如"胜利钻井"等）。井队名用虚构代号（如"鲁EK8569"作为车牌式代号可保留，但不得带公司全称）。
- 场景为**吊装作业**，文案围绕吊装安全（吊物、吊臂、旋转半径、索具等），不要写"钻井"。

---

## 9. 个人设置（Auth 扩展）

> 以下接口均需登录（Bearer token）。`user` 对象在原有 `id/username/displayName/role/avatar` 基础上新增 `email/phone/dept` 三个字段（登录、`/api/auth/me`、本节接口均返回）。

**user 对象（扩展后）**：
```json
{
  "id": "u1",
  "username": "admin",
  "displayName": "系统管理员",
  "role": "admin",
  "avatar": null,
  "email": "admin@aegislift.cn",
  "phone": "13800000001",
  "dept": "安全监督部"
}
```

### PUT `/api/auth/profile`
更新当前登录用户个人资料。请求体所有字段可选，仅更新传入的非空字段：
```json
{ "displayName": "新名称", "email": "a@b.cn", "phone": "139...", "dept": "作业一区", "avatar": "/static/xxx.png" }
```
`data`：更新后的 user 对象（同上形状）。

### PUT `/api/auth/password`
修改当前登录用户密码。请求体：
```json
{ "oldPassword": "admin123", "newPassword": "newpass1" }
```
行为：
- `oldPassword` 与当前密码不符 → 400 / code 1000，message "原密码错误"。
- `newPassword` 长度 < 6 → 422 / code 1002，message "新密码至少6位"。
- 通过则更新密码，`data` 为 `null`，message "密码修改成功"。

---

## 10. 违章管理（Violation）

> 以下接口均需登录（Bearer token），统一响应 `{code,message,data}`。

### GET `/api/violation/categories`
违章类别管理列表（基于违章类别派生，含启用状态与统计）。`data` 为数组，元素：

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 类别 code |
| name | string | 类别名称 |
| level | string | 违章等级（高/中/低） |
| enabled | bool | 是否启用 |
| count | int | 累计触发次数 |
| desc | string | 类别中文描述 |
| relatedScene | string | 关联场景名 |

### PUT `/api/violation/categories/{code}`
更新某违章类别（当前支持启用/停用）。请求体：
```json
{ "enabled": false }
```
`enabled` 可选。`data` 为更新后的类别项（同上形状）。类别不存在 → 404 / code 1004。

### GET `/api/violation/review-logs`
分页查询审核记录。Query 参数（全部可选）：

| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码，默认 1 |
| pageSize | int | 每页条数，默认 10 |
| result | string | 审核结果过滤：correct/wrong/experiment_correct |

`data` 为分页结构 `{ items, total, page, pageSize }`，`items` 元素：
```json
{
  "id": "rl1001",
  "recordId": "v100012",
  "category": "未佩戴安全帽",
  "operator": "系统管理员",
  "result": "correct",
  "resultText": "识别正确",
  "fromStatus": "pending_review",
  "fromStatusText": "待初审",
  "toStatus": "approved",
  "toStatusText": "初审通过",
  "time": "2026-06-01T10:22:31",
  "remark": "复核无误"
}
```

### GET `/api/violation/fences`
电子围栏配置列表。`data` 为数组，元素：
```json
{
  "id": "fc101",
  "name": "1号井场-警戒线",
  "scene": "井场",
  "sceneCode": "jingchang",
  "camera": "CAM-01",
  "type": "line",
  "typeText": "警戒线",
  "enabled": true,
  "points": [[200,175],[1080,175]],
  "color": "#ff00ff",
  "createdAt": "2026-05-24T..."
}
```
`type` 取值：`line`(警戒线) | `area`(区域)。`points` 为像素坐标点数组（基于 1280×720）。

### GET `/api/violation/recognition-items`
识别项配置列表。`data` 为数组，元素：
```json
{
  "id": "ri201",
  "name": "安全帽检测",
  "categoryCode": "no_helmet",
  "modelVersion": "V20250917",
  "threshold": 0.78,
  "sensitivity": "high",
  "sensitivityText": "高",
  "enabled": true
}
```
`threshold` 为置信度阈值（0.5~0.95）。`sensitivity` 取值：`low/medium/high`。

### PUT `/api/violation/recognition-items/{id}`
更新识别项配置。请求体（字段均可选）：
```json
{ "enabled": true, "threshold": 0.85 }
```
`data` 为更新后的识别项（同上形状）。识别项不存在 → 404 / code 1004。
- 页脚版权写通用文案，例："© 2026 油田吊装作业安全视频智能分析系统 · V2025.01"。
