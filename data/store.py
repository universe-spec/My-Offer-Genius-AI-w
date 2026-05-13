# data/store.py
"""数据持久层：SQLite 数据库（替代原 JSON 文件）"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

# 数据存放目录和数据库文件路径
DATA_DIR = Path("./offergenius_data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "offergenius.db"


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接，设置行工厂为字典行"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row   # 让查询结果可以用 dict(row) 转成字典
    return conn


def init_db() -> None:
    """初始化数据库表（自动创建，不会重复创建）"""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            user_name TEXT DEFAULT '',
            target_job TEXT DEFAULT '',
            target_company TEXT DEFAULT '',
            resume_text TEXT DEFAULT '',
            diagnosis TEXT DEFAULT '{}',
            questions TEXT DEFAULT '[]',
            feedbacks TEXT DEFAULT '[]',
            final_report TEXT DEFAULT '{}'
        )
    """)
    conn.commit()
    conn.close()


def load_all_sessions() -> List[Dict]:
    """查询所有历史会话，最新排在前面"""
    init_db()
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    sessions = []
    for row in rows:
        session = dict(row)
        # 把 JSON 字符串转回 Python 对象
        for field in ["diagnosis", "questions", "feedbacks", "final_report"]:
            try:
                session[field] = json.loads(session[field])
            except (json.JSONDecodeError, TypeError):
                session[field] = {} if field in ["diagnosis", "final_report"] else []
        sessions.append(session)
    return sessions


def save_session(session_dict: Dict) -> None:
    """新增或更新一条会话记录"""
    init_db()

    # 深拷贝一份，因为我们要把复杂字段转成 JSON 字符串
    data = session_dict.copy()
    for field in ["diagnosis", "questions", "feedbacks", "final_report"]:
        if field in data:
            data[field] = json.dumps(data[field], ensure_ascii=False)

    conn = _get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO sessions
            (session_id, created_at, user_name, target_job, target_company,
             resume_text, diagnosis, questions, feedbacks, final_report)
        VALUES
            (:session_id, :created_at, :user_name, :target_job, :target_company,
             :resume_text, :diagnosis, :questions, :feedbacks, :final_report)
    """, data)
    conn.commit()
    conn.close()


def get_session_by_id(session_id: str) -> Optional[Dict]:
    """根据 session_id 查询单条会话"""
    init_db()
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        (session_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return None

    session = dict(row)
    for field in ["diagnosis", "questions", "feedbacks", "final_report"]:
        try:
            session[field] = json.loads(session[field])
        except (json.JSONDecodeError, TypeError):
            session[field] = {} if field in ["diagnosis", "final_report"] else []
    return session