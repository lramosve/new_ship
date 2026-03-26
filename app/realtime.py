import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._channels: dict[str, list[asyncio.Queue[dict[str, Any]]]] = defaultdict(list)

    async def connect(self, channel: str, websocket: WebSocket) -> asyncio.Queue[dict[str, Any]]:
        await websocket.accept()
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._channels[channel].append(queue)
        return queue

    def disconnect(self, channel: str, queue: asyncio.Queue[dict[str, Any]]):
        active = self._channels.get(channel)
        if active is None:
            return
        if queue in active:
            active.remove(queue)
        if not active:
            self._channels.pop(channel, None)

    def publish(self, channel: str, message: dict[str, Any]):
        for queue in list(self._channels.get(channel, [])):
            queue.put_nowait(message)


manager = ConnectionManager()
