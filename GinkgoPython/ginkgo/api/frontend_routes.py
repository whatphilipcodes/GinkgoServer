import asyncio
import json
import random

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ginkgo.schemas.frontend import Input, InputType
from ginkgo.schemas.unreal import UEDataPayload
from ginkgo.services import db_service
from ginkgo.services.llm_service import llm_service
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
                data = json.loads(raw_json)
                action = data.get("action")

                if action == "add":
                    cmd = AddInputCommand.model_validate_json(raw_json)

                    # Run LLM inference in a separate thread to avoid blocking the event loop
                    trait, attribute_class = await asyncio.to_thread(
                        llm_service.infer_gsod, cmd.text
                    )

                    record = db_service.add_input(
                        text=cmd.text,
                        input_type=cmd.type,
                        lang=cmd.lang,
                        source=cmd.source,
                        attribute_class=attribute_class,
                        trait=trait,
                    )

                    # Send to Unreal if this is a thought
                    if (
                        cmd.type == InputType.THOUGHT
                        and "unreal" in manager.active_connections
                    ):
                        payload = UEDataPayload(
                            ID=record.id,
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
                        await manager.send_to(payload.model_dump_json(), "unreal")

                    await websocket.send_json(
                        {
                            "status": "success",
                            "action": "add",
                            "record": {
                                "id": record.id,
                                "text": record.text,
                                "type": record.type.value,
                                "lang": record.lang.value,
                                "source": record.source.value,
                                "attribute_class": record.attribute_class,
                                "trait": record.trait,
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
                        try:
                            input_type = (
                                InputType(input_type_str) if input_type_str else None
                            )
                        except ValueError:
                            await websocket.send_json(
                                {
                                    "status": "error",
                                    "error": f"Invalid input_type: {input_type_str}",
                                }
                            )
                            continue

                        records = db_service.get_recent(
                            hours=cmd.filters.get("hours", 24),
                            input_type=input_type,
                        )
                    elif cmd.query_type == "by_id":
                        record_id = cmd.filters.get("record_id")
                        if not isinstance(record_id, int) or record_id <= 0:
                            await websocket.send_json(
                                {
                                    "status": "error",
                                    "error": "record_id filter must be a positive integer",
                                }
                            )
                            continue
                        record = db_service.get_by_id(record_id)
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
                                    "lang": r.lang.value,
                                    "source": r.source.value,
                                    "attribute_class": r.attribute_class,
                                    "trait": r.trait,
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
                    cmd = UpdateInputCommand.model_validate_json(raw_json)

                    # Run LLM inference in a separate thread to avoid blocking the event loop
                    trait, attribute_class = await asyncio.to_thread(
                        llm_service.infer_gsod, cmd.text
                    )

                    record = db_service.update_text(
                        cmd.record_id,
                        cmd.text,
                        attribute_class=attribute_class,
                        trait=trait,
                    )
                    if record:
                        await websocket.send_json(
                            {
                                "status": "success",
                                "action": "update",
                                "record": {
                                    "id": record.id,
                                    "text": record.text,
                                    "type": record.type.value,
                                    "lang": record.lang.value,
                                    "source": record.source.value,
                                    "attribute_class": record.attribute_class,
                                    "trait": record.trait,
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
                    validated_input = Input.model_validate_json(raw_json)

                    # Run LLM inference in a separate thread to avoid blocking the event loop
                    trait, attribute_class = await asyncio.to_thread(
                        llm_service.infer_gsod, validated_input.text
                    )

                    record = db_service.add_input(
                        text=validated_input.text,
                        input_type=validated_input.type,
                        lang=validated_input.lang,
                        source=validated_input.source,
                        attribute_class=attribute_class,
                        trait=trait,
                    )
                    await websocket.send_json(
                        {
                            "status": "success",
                            "action": "add",
                            "record": {
                                "id": record.id,
                                "text": record.text,
                                "type": record.type.value,
                                "lang": record.lang.value,
                                "source": record.source.value,
                                "attribute_class": record.attribute_class,
                                "trait": record.trait,
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
