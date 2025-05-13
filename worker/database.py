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

def fetch_task_by_id(task_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                return dict(cur.fetchone()) if cur.rowcount else None
    except Exception as e:
        logging.exception(f"[{task_id}] Failed to fetch task: {e}")
        return None

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
