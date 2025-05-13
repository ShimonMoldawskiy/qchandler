import psycopg2
import psycopg2.extras
import json
import logging
import time
from shared.config import get_db_config

def get_connection():
    cfg = get_db_config()
    return psycopg2.connect(
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=cfg["port"]
    )

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id UUID PRIMARY KEY,
                    status TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    result JSONB,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    created_at BIGINT NOT NULL,
                    updated_at BIGINT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_status_updated_at ON tasks (status, updated_at);
            """)
            conn.commit()
            logging.info("Database initialized and ensured table/indexes exist.")

def save_task_to_db(task: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (id, status, payload, retry_count, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                task["id"], task["status"], json.dumps(task["payload"]),
                task["retry_count"], task["created_at"], task["updated_at"]
            ))
            conn.commit()

def get_task_by_id(task_id: str):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT status, result FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
            return dict(task) if task else None

def update_task_status_and_result(task_id: str, status: str, result: dict = None):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE tasks
                    SET status = %s,
                        updated_at = %s,
                        result = %s
                    WHERE id = %s
                """, (
                    status,
                    int(time.time()),
                    json.dumps(result) if result else None,
                    task_id
                ))
                conn.commit()
    except Exception as e:
        logging.exception(f"[{task_id}] Failed to update task status/result: {e}")
