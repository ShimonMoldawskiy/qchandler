import asyncio
import logging
from shared.logging_config import setup_logging
from database import get_retryable_tasks, increment_retry_count, update_task_status_and_result
from nats_client import publish_task
from shared.models import TaskStatus
from utils import calculate_backoff, should_retry

RETRY_TIMEOUT_SECONDS = 60  # time after which a task is considered expired
MAX_RETRIES = 5
SLEEP_TIME = 30  # seconds to wait before checking for expired tasks again

setup_logging()
logger = logging.getLogger(__name__)

async def retry_expired_tasks():
    logger.info("Starting retry job loop...")
    while True:
        try:
            tasks = get_retryable_tasks(RETRY_TIMEOUT_SECONDS)
            logger.info(f"Found {len(tasks)} retryable tasks")
            for task in tasks:
                if task["retry_count"] >= MAX_RETRIES:
                    logger.warning(f"[{task['id']}] Max retries exceeded, skipping")
                    update_task_status_and_result(
                        task["id"], status=TaskStatus.FAILED, result={"error": "Max retries exceeded"})
                    continue

                if should_retry(task, RETRY_TIMEOUT_SECONDS):
                    delay = calculate_backoff(task["retry_count"])
                    await asyncio.sleep(delay)

                    increment_retry_count(task["id"])
                    await publish_task(task["id"])
                    logger.info(f"[{task['id']}] Re-queued with retry #{task['retry_count'] + 1}")
        except Exception as e:
            logger.exception(f"Error in retry job loop: {e}")

        await asyncio.sleep(SLEEP_TIME)  # wait before checking again

if __name__ == "__main__":
    asyncio.run(retry_expired_tasks())
