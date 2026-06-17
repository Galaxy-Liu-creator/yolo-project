"""建库脚本：在 backend-python 目录下执行 `python init_db.py`。

会在 backend-python/app.db 生成 SQLite 数据库，并把 app/data/mock_data.py 的
演示数据写入。可重复执行（每次重建）。不影响运行中的 FastAPI 演示后端。
"""
from app.db.database import DB_PATH
from app.db.seed import seed_database


def main() -> None:
    print(f"[init_db] 目标数据库: {DB_PATH}")
    counts = seed_database()
    print("[init_db] 数据写入完成，各表条数：")
    total = 0
    for table, n in counts.items():
        total += n
        print(f"  - {table:<20} {n}")
    print(f"[init_db] 合计 {total} 行，数据库已就绪。")


if __name__ == "__main__":
    main()
