import psycopg2
import psycopg2.extras
import json
import logging
import time
from shared.config import get_db_config
from shared.models import TaskStatus


def get_connection():
    cfg = get_db_config()
    return psycopg2.connect(
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=cfg["port"]
    )

def get_retryable_tasks(timeout_seconds: int):
    """
    Fetch tasks that are either:
    - still 'queued' and have not been picked up
    - stuck in 'running' status beyond their retry timeout
    """
    now = int(time.time())
    threshold = now - timeout_seconds

    query = """
        SELECT * FROM tasks
        WHERE (status = %s OR status = %s)
        AND updated_at < %s
        ORDER BY updated_at ASC
        LIMIT 50;
    """

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (TaskStatus.QUEUED, TaskStatus.RUNNING, threshold))
                return cur.fetchall()
    except Exception as e:
        logging.exception(f"Failed to fetch retryable tasks: {e}")
        return []

def increment_retry_count(task_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE tasks
                    SET retry_count = retry_count + 1,
                        status = %s,
                        updated_at = %s
                    WHERE id = %s
                """, (TaskStatus.QUEUED, int(time.time()), task_id))
                conn.commit()
    except Exception as e:
        logging.exception(f"[{task_id}] Failed to increment retry count: {e}")

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
