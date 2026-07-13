"""
WebSocket Connection Manager
Manages real-time connections for push notifications and live chat.
"""
import json
import logging
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger("basma_api.websocket")


class ConnectionManager:
    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(websocket)
        logger.info(f"WebSocket connected: user={user_id}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                del self._connections[user_id]
        logger.info(f"WebSocket disconnected: user={user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        if user_id not in self._connections:
            return
        dead = set()
        for ws in self._connections[user_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections[user_id].discard(ws)

    async def broadcast(self, message: dict):
        for user_id in list(self._connections.keys()):
            await self.send_to_user(user_id, message)

    @property
    def active_connections(self) -> int:
        return sum(len(ws) for ws in self._connections.values())


manager = ConnectionManager()
