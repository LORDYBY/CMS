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