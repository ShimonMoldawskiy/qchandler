import logging
from nats.aio.client import Client as NATS
from shared.config import get_nats_config

async def publish_task(task_id: str):
    nc = NATS()
    try:
        await nc.connect(servers=[get_nats_config()["url"]])
        await nc.publish("tasks", task_id.encode())
        await nc.drain()
        logging.info(f"[{task_id}] Republished to NATS topic 'tasks'")
    except Exception as e:
        logging.exception(f"[{task_id}] Failed to republish to NATS: {e}")
    finally:
        if nc.is_connected:
            await nc.close()
