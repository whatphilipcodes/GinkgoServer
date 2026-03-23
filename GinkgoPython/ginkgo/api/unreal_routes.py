from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ginkgo.ws.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/unreal")
async def unreal_endpoint(websocket: WebSocket):
    await manager.connect("unreal", websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect("unreal")
