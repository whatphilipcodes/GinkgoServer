from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ginkgo.schemas.frontend import UserInput
from ginkgo.services import db_service
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

                # Store in database with automatic timestamp
                record = db_service.add_input(
                    text=validated_input.text,
                    input_type=validated_input.type,
                )
                print(f"Stored: {record}")

                # asyncio.create_task(process_user_input(validated_input)) # to-do

            except ValidationError as e:
                await websocket.send_text(f"Error: Invalid payload format. {e}")

    except WebSocketDisconnect:
        manager.disconnect("frontend")


# REST endpoints for querying stored data
@router.get("/api/inputs")
async def get_all_inputs(limit: int = 100, offset: int = 0):
    """Get all user inputs with pagination"""
    records = db_service.get_all(limit=limit, offset=offset)
    return {
        "count": len(records),
        "records": [
            {
                "id": r.id,
                "text": r.text,
                "type": r.type,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat(),
            }
            for r in records
        ],
    }


@router.get("/api/inputs/type/{input_type}")
async def get_inputs_by_type(input_type: str, limit: int = 100):
    """Get user inputs filtered by type (thought/prompt/decree)"""
    records = db_service.get_by_type(input_type, limit=limit)
    return {
        "count": len(records),
        "type": input_type,
        "records": [
            {
                "id": r.id,
                "text": r.text,
                "type": r.type,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat(),
            }
            for r in records
        ],
    }


@router.get("/api/inputs/recent")
async def get_recent_inputs(hours: int = 24, input_type: str | None = None):
    """Get recent inputs within the specified hours, optionally filtered by type"""
    records = db_service.get_recent(hours=hours, input_type=input_type)
    return {
        "count": len(records),
        "hours": hours,
        "type": input_type,
        "records": [
            {
                "id": r.id,
                "text": r.text,
                "type": r.type,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat(),
            }
            for r in records
        ],
    }


@router.get("/api/inputs/{record_id}")
async def get_input_by_id(record_id: int):
    """Get a specific input by ID"""
    record = db_service.get_by_id(record_id)
    if not record:
        return {"error": "Record not found"}, 404
    return {
        "id": record.id,
        "text": record.text,
        "type": record.type,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
    }
