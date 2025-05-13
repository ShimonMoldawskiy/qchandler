import time
import logging

BASE_DELAY = 2  # seconds
MAX_DELAY = 60  # seconds

def calculate_backoff(retry_count, base_delay=BASE_DELAY, max_delay=MAX_DELAY):
    """
    Calculate exponential backoff with an upper bound.
    """
    delay = min(max_delay, base_delay * (2 ** retry_count))
    logging.info(f"Backoff for retry #{retry_count}: {delay} seconds")
    return delay

def should_retry(task, timeout_seconds, current_time=None):
    """
    Check if a task is overdue for retry based on the last update time.
    """
    current_time = current_time or int(time.time())
    last_updated = task.get("updated_at", 0)
    return current_time >= (last_updated + timeout_seconds)
