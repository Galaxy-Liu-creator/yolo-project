# AegisLift 后端（油田吊装作业安全视频智能分析系统 · 演示后端）

FastAPI + 死数据（无数据库，内存/静态数据）+ JWT 鉴权。AI 识别结果全部为预置静态数据。
本服务严格按 `../API-CONTRACT.md` 实现，统一响应结构 `{code, message, data}`。

## 技术栈

- FastAPI 0.115 / Uvicorn
- pydantic 2 + pydantic-settings（从 `.env` 读取配置）
- PyJWT（JWT 签发与校验）
- Pillow（生成样例占位图）

## 目录结构

```
backend-python/
  app/
    main.py              # FastAPI 入口：路由、CORS、StaticFiles、全局异常处理
    core/
      config.py          # 配置（pydantic-settings）
      security.py        # JWT 生成/校验、get_current_user 依赖
      response.py        # 统一响应包裹 ok()/fail() + 业务异常 BizError
    api/
      auth.py            # /api/auth/*
      dashboard.py       # /api/dashboard/*
      meta.py            # /api/meta/*
      records.py         # /api/records/*
    schemas/
      models.py          # 请求体 pydantic 模型
    data/
      mock_data.py       # 死数据：用户、字典、48 条违章记录、看板统计
    static/samples/      # 样例占位图 sample_01.jpg ... sample_06.jpg（1280×720）
  tools/
    gen_samples.py       # 重新生成样例图脚本
  requirements.txt
  .env.example
  .env                   # 演示用配置（可提交）
  run.py                 # 启动脚本
  README.md
```

## 安装

```bash
# 建议使用虚拟环境（可选）
python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt
```

## 启动

方式一（推荐）：

```bash
uvicorn app.main:app --reload --port 8000
```

方式二：

```bash
python run.py
```

- 服务地址：`http://127.0.0.1:8000`
- Swagger 接口文档：`http://127.0.0.1:8000/docs`
- 样例图片：`http://127.0.0.1:8000/static/samples/sample_01.jpg`

> 注意：请在 `backend-python` 目录下启动，确保 `app` 包可被导入。

## 预置账号（死数据）

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 admin |
| auditor | 123456 | 审核员 auditor |

## 鉴权说明

- 除 `POST /api/auth/login` 外，所有接口需携带 `Authorization: Bearer <token>`。
- token 失效 / 缺失返回 HTTP 401，body 为 `{code:1001, message:..., data:null}`。
- token 有效期默认 86400 秒（24 小时），可在 `.env` 调整 `ACCESS_TOKEN_EXPIRE_SECONDS`。

## 接口清单

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 登录，返回 token + user |
| GET | /api/auth/me | 当前登录用户 |
| POST | /api/auth/logout | 登出 |
| GET | /api/dashboard/stats | 顶部统计卡片 |
| GET | /api/dashboard/trend | 近 7 天违章趋势 |
| GET | /api/dashboard/category-distribution | 违章类别分布 |
| GET | /api/dashboard/status-distribution | 处理状态分布 |
| GET | /api/dashboard/recent-alarms | 最新告警（最近 8 条） |
| GET | /api/meta/categories | 违章类别字典 |
| GET | /api/meta/scenes | 场景字典 |
| GET | /api/meta/teams | 作业队/井队字典 |
| GET | /api/meta/versions | 运行版本字典 |
| GET | /api/meta/units | 二级单位字典 |
| GET | /api/records | 分页查询违章记录（支持全部筛选参数） |
| GET | /api/records/{id} | 违章详情（含 detections / fences） |
| POST | /api/records/{id}/review | 提交审核结果，更新状态并追加 reviewHistory |
| DELETE | /api/records/{id} | 删除一条记录 |
| POST | /api/records/batch-delete | 批量删除 |

## 快速验证（PowerShell / curl）

```bash
# 1. 登录拿 token
curl -X POST http://127.0.0.1:8000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# 2. 带 token 调用（将 <token> 替换为上一步返回值）
curl http://127.0.0.1:8000/api/records?page=1&pageSize=5 -H "Authorization: Bearer <token>"
curl http://127.0.0.1:8000/api/dashboard/stats -H "Authorization: Bearer <token>"
```

## 文案与合规

- 系统标题统一为「油田吊装作业安全视频智能分析系统」。
- 不包含任何真实公司名称；井队名为虚构车牌式代号（如「鲁EK8569」）。
- 场景围绕吊装作业（吊物、吊臂、旋转半径、索具、电子围栏）。
- 样例图均为程序生成的占位图，标注「DEMO 占位图 · 仅供演示」。
