"""数据持久层（SQLite + SQLAlchemy 2.0）。

本包为独立的数据库层：**不被运行中的 FastAPI 应用导入**，
仅用于把 app/data/mock_data.py 的演示数据落库（建库 / 展示 / 代码评审 / 后续接入）。
死数据保持原样，作为种子来源。
"""
