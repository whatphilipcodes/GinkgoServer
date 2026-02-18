from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ginkgo.schemas.frontend import UserInput
from ginkgo.ws.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/frontend")
async def frontend_endpoint(websocket: WebSocket):
    await manager.connect("frontend", websocket)
    try:
        while True:
            raw_json = await websocket.receive_text()

            try:
                validated_input = UserInput.model_validate_json(raw_json)
                # asyncio.create_task(process_user_input(validated_input)) # to-do
                print(validated_input)

            except ValidationError as e:
                await websocket.send_text(f"Error: Invalid payload format. {e}")

    except WebSocketDisconnect:
        manager.disconnect("frontend")
