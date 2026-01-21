from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections = set()

    async def connect(self, websocket):
        self.active_connections.add(websocket)

    async def disconnect(self, websocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: str):
        for ws in self.active_connections:
            await ws.send_text(message)


manager = ConnectionManager()

class DeviceConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[device_id] = websocket

    def disconnect(self, device_id: str):
        if device_id in self.active:
            del self.active[device_id]

    async def send_to_device(self, device_id: str, message: dict):
        if device_id in self.active:
            await self.active[device_id].send_json(message)

manager = DeviceConnectionManager()