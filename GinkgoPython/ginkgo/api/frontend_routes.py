from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ginkgo.schemas.frontend import InputType, UserInput
from ginkgo.services import db_service
from ginkgo.ws.commands import (
    AddInputCommand,
    DeleteInputCommand,
    QueryInputCommand,
    UpdateInputCommand,
)
from ginkgo.ws.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/frontend")
async def frontend_endpoint(websocket: WebSocket):
    await manager.connect("frontend", websocket)
    try:
        while True:
            raw_json = await websocket.receive_text()

            try:
                import json

                data = json.loads(raw_json)
                action = data.get("action")

                if action == "add":
                    cmd = AddInputCommand.model_validate_json(raw_json)
                    record = db_service.add_input(text=cmd.text, input_type=cmd.type)
                    await websocket.send_json(
                        {
                            "status": "success",
                            "action": "add",
                            "record": {
                                "id": record.id,
                                "text": record.text,
                                "type": record.type.value,
                                "created_at": record.created_at.isoformat(),
                                "updated_at": record.updated_at.isoformat(),
                            },
                        }
                    )

                elif action == "query":
                    cmd = QueryInputCommand.model_validate_json(raw_json)

                    if cmd.query_type == "all":
                        records = db_service.get_all(
                            limit=cmd.filters.get("limit", 100),
                            offset=cmd.filters.get("offset", 0),
                        )
                    elif cmd.query_type == "by_type":
                        input_type_str = cmd.filters.get("input_type", "thought")
                        try:
                            input_type = InputType(input_type_str)
                            records = db_service.get_by_type(
                                input_type,
                                limit=cmd.filters.get("limit"),
                            )
                        except ValueError:
                            await websocket.send_json(
                                {
                                    "status": "error",
                                    "error": f"Invalid input_type: {input_type_str}",
                                }
                            )
                            continue

                    elif cmd.query_type == "recent":
                        input_type_str = cmd.filters.get("input_type")
                        input_type = (
                            InputType(input_type_str) if input_type_str else None
                        )

                        records = db_service.get_recent(
                            hours=cmd.filters.get("hours", 24),
                            input_type=input_type,
                        )
                    elif cmd.query_type == "by_id":
                        record = db_service.get_by_id(cmd.filters.get("record_id"))
                        records = [record] if record else []
                    else:
                        await websocket.send_json(
                            {
                                "status": "error",
                                "error": f"Unknown query type: {cmd.query_type}",
                            }
                        )
                        continue

                    await websocket.send_json(
                        {
                            "status": "success",
                            "action": "query",
                            "query_type": cmd.query_type,
                            "count": len(records),
                            "records": [
                                {
                                    "id": r.id,
                                    "text": r.text,
                                    "type": r.type.value,
                                    "created_at": r.created_at.isoformat(),
                                    "updated_at": r.updated_at.isoformat(),
                                }
                                for r in records
                            ],
                        }
                    )

                elif action == "delete":
                    cmd = DeleteInputCommand.model_validate_json(raw_json)
                    success = db_service.delete(cmd.record_id)
                    await websocket.send_json(
                        {
                            "status": "success" if success else "error",
                            "action": "delete",
                            "record_id": cmd.record_id,
                            "deleted": success,
                        }
                    )

                elif action == "update":
                    cmd = UpdateInputCommand.model_vali.valuedate_json(raw_json)
                    record = db_service.update_text(cmd.record_id, cmd.text)
                    if record:
                        await websocket.send_json(
                            {
                                "status": "success",
                                "action": "update",
                                "record": {
                                    "id": record.id,
                                    "text": record.text,
                                    "type": record.type,
                                    "created_at": record.created_at.isoformat(),
                                    "updated_at": record.updated_at.isoformat(),
                                },
                            }
                        )
                    else:
                        await websocket.send_json(
                            {
                                "status": "error",
                                "action": "update",
                                "error": f"Record {cmd.record_id} not found",
                            }
                        )

                elif action is None:
                    validated_input = UserInput.model_validate_json(raw_json)
                    record = db_service.add_input(
                        text=validated_input.text,
                        input_type=validated_input.type,
                    )
                    await websocket.send_json(
                        {
                            "status": "success",
                            "action": "add",
                            "record": {
                                "id": record.id,
                                "text": record.text,
                                "type": record.type.value,
                                "created_at": record.created_at.isoformat(),
                                "updated_at": record.updated_at.isoformat(),
                            },
                        }
                    )

                else:
                    await websocket.send_json(
                        {"status": "error", "error": f"Unknown action: {action}"}
                    )

            except ValidationError as e:
                await websocket.send_json(
                    {"status": "error", "error": f"Invalid payload format. {str(e)}"}
                )
            except json.JSONDecodeError:
                await websocket.send_json({"status": "error", "error": "Invalid JSON"})

    except WebSocketDisconnect:
        manager.disconnect("frontend")
