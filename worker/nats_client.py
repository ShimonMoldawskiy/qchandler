import logging
from nats.aio.client import Client as NATS
from shared.config import get_nats_config


class NATSWorkerClient:
    def __init__(self, subject: str, message_handler):
        self.nc = NATS()
        self.subject = subject
        self.message_handler = message_handler
        self.connected = False

    async def connect_and_subscribe(self):
        try:
            config = get_nats_config()
            await self.nc.connect(servers=[config["url"]])
            await self.nc.subscribe(self.subject, cb=self.message_handler, queue="workers")
            self.connected = True
            logging.info(f"Subscribed to NATS subject '{self.subject}'")
        except Exception as e:
            logging.exception(f"Failed to connect/subscribe to NATS: {e}")

    async def close(self):
        if self.connected:
            await self.nc.drain()
            await self.nc.close()
