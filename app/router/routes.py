import os
import httpx
from pathlib import Path
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

from app.lib.connection_manager import ConnectionManager

class RelayMessage(BaseModel):
    message: str

router = APIRouter()
manager = ConnectionManager()
templates = Jinja2Templates(f"{Path(__file__).parent.parent.absolute()}/templates")

PEER_URL = os.getenv("PEER_URL")

@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    service_name = os.getenv("SERVICE_NAME", "SVC")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "service_name": service_name},
    )

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        join_msg = f"Client #{client_id} joined the chat"
        await manager.broadcast(join_msg)
        await forward_to_peer(join_msg)

        while True:
            data = await websocket.receive_text()
            msg = f"Client #{client_id}: {data}"

            await manager.broadcast(msg, skip=websocket)
            await forward_to_peer(msg)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        leave_msg = f"Client #{client_id} left the chat"
        await manager.broadcast(leave_msg)
        await forward_to_peer(leave_msg)

@router.post("/relay")
async def relay(msg: RelayMessage):
    await manager.broadcast(msg.message)
    return {"status": "ok"}


async def forward_to_peer(message: str):
    if not PEER_URL:
        print("PEER_URL não configurado, não enviando mensagem para peer.")
        return

    try:
        async with httpx.AsyncClient() as client:
            await client.post(PEER_URL, json={"message": message})
    except Exception as e:
        print(f"Erro ao encaminhar mensagem para o peer ({PEER_URL}): {e}")