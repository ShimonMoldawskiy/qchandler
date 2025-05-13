import asyncio
import logging
import signal
import uuid

from shared.logging_config import setup_logging
from shared.exceptions import UnrecoverableTaskError
from database import update_task_status_and_result, fetch_task_by_id
from nats_client import NATSWorkerClient
from executor import QuantumCircuitExecutor
from shared.models import TaskStatus

setup_logging()
worker_id = str(uuid.uuid4())
logger = logging.getLogger(__name__)

async def handle_task(msg):
    task_id = msg.data.decode()
    logger.info(f"[{worker_id}][{task_id}] Received task from broker")
    task = fetch_task_by_id(task_id)
    if not task:
        logger.warning(f"[{worker_id}][{task_id}] Task not found in DB")
        return
    try:
        update_task_status_and_result(task_id, status=TaskStatus.RUNNING)
        qc_data = task["payload"]
        ce = QuantumCircuitExecutor(qc_data)
        result = ce.execute()
        update_task_status_and_result(task_id, status=TaskStatus.COMPLETED, result={"counts": result})
        logger.info(f"[{worker_id}][{task_id}] Execution completed")
    except UnrecoverableTaskError as e:
        update_task_status_and_result(task_id, status=TaskStatus.FAILED, result={"error": str(e)})
    except Exception as e:
        logger.exception(f"[{worker_id}][{task_id}] Task execution failed: {e}")
        update_task_status_and_result(task_id, status=TaskStatus.RUNNING, result={"error": "Task execution failed"})

async def run():
    broker_client = NATSWorkerClient(subject="tasks", message_handler=handle_task)
    await broker_client.connect_and_subscribe()
    logger.info(f"[{worker_id}] Subscribed to broker 'tasks' topic")

    stop_event = asyncio.Event()
    for sig_name in ("SIGINT", "SIGTERM"):
        asyncio.get_running_loop().add_signal_handler(getattr(signal, sig_name), stop_event.set)

    await stop_event.wait()
    await broker_client.close()

if __name__ == "__main__":
    asyncio.run(run())