from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ginkgo.models.enums import GinkgoMessageType
from ginkgo.schemas.unreal import GinkgoMessage
from ginkgo.ws.connection_manager import manager
from ginkgo.ws.handlers.init_handler import handle_init

router = APIRouter()


@router.websocket("/ws/unreal")
async def unreal_endpoint(websocket: WebSocket):
    await manager.connect("unreal", websocket)

    try:
        while True:
            text = await websocket.receive_text()
            msg = GinkgoMessage.model_validate_json(text)
            if msg.messageType == GinkgoMessageType.INIT:
                await handle_init()

    except WebSocketDisconnect:
        manager.disconnect("unreal")
