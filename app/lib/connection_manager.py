from typing import List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, skip: WebSocket | None = None):
        """
        Envia a mensagem para todos os clientes conectados,
        exceto (opcionalmente) o WebSocket indicado em 'skip'.
        """
        to_remove = []
        for connection in self.active_connections:
            if skip is not None and connection is skip:
                continue
            try:
                await connection.send_text(message)
            except Exception:
                to_remove.append(connection)

        for ws in to_remove:
            self.disconnect(ws)
