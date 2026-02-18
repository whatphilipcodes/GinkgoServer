import asyncio
import random

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ginkgo.schemas.unreal import UEDataPayload
from ginkgo.ws.connection_manager import manager

router = APIRouter()


async def mock_unreal_data_loop(websocket: WebSocket):
    counter = 0
    try:
        while True:
            await asyncio.sleep(4)

            payload = UEDataPayload(
                ID=counter,
                PillarID=random.randint(0, 3),
                PositionAlongsidePillar=random.uniform(0.0, 1.0),
                DistanceFromPillar=random.uniform(0.0, 1.0),
                InnerColour=random.uniform(0.0, 1.0),
                OuterColour=random.uniform(0.0, 1.0),
                SplitSize=random.uniform(0.0, 1.0),
                LeafSize=random.uniform(0.0, 1.0),
                RotationOffset=random.uniform(0.0, 1.0),
                V5=random.uniform(0.0, 1.0),
            )

            await websocket.send_text(payload.model_dump_json())
            counter += 1

    except asyncio.CancelledError:
        pass


@router.websocket("/ws/unreal")
async def unreal_endpoint(websocket: WebSocket):
    await manager.connect("unreal", websocket)

    mock_task = asyncio.create_task(mock_unreal_data_loop(websocket))

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        mock_task.cancel()
        manager.disconnect("unreal")
