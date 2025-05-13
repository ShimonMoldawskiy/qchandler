import asyncio
import logging
from nats.aio.client import Client as NATS
from shared.config import get_nats_config

# NATS publishing must happen in an event loop
def publish_task(task_id: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_publish(task_id))
    loop.close()

async def _publish(task_id: str):
    nc = NATS()
    config = get_nats_config()

    try:
        await nc.connect(servers=[config["url"]])
        await nc.publish("tasks", task_id.encode())
        logging.info(f"[{task_id}] Published to NATS topic 'tasks'")
        await nc.drain()
    except Exception as e:
        logging.exception(f"[{task_id}] Failed to publish to NATS: {e}")
    finally:
        if nc.is_connected:
            await nc.close()
