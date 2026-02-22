import asyncio
import json
import random

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ginkgo.schemas.unreal import UEDataPayload
from ginkgo.services import db_service
from ginkgo.services.llm_service import llm_service
from ginkgo.ws.commands import (
    AddDecreeCommand,
    AddPromptCommand,
    AddThoughtCommand,
    DeleteDecreeCommand,
    DeletePromptCommand,
    DeleteThoughtCommand,
    QueryDecreeCommand,
    QueryPromptCommand,
    QueryThoughtCommand,
    UpdateDecreeCommand,
    UpdatePromptCommand,
    UpdateThoughtCommand,
)
from ginkgo.ws.connection_manager import manager

router = APIRouter()


def serialize_record(record, record_type: str) -> dict:
    """Serialize a record to JSON response format"""
    return {
        "id": record.id,
        "text": record.text,
        "type": record_type,
        "lang": record.lang.value,
        "source": record.source.value,
        "attribute_class": record.attribute_class,
        "trait": record.trait,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
    }


@router.websocket("/ws/frontend")
async def frontend_endpoint(websocket: WebSocket):
    await manager.connect("frontend", websocket)
    try:
        while True:
            raw_json = await websocket.receive_text()

            try:
                data = json.loads(raw_json)
                action = data.get("action")
                record_type = data.get("type")

                # —— Thought operations ——————————————————————————————————
                if record_type == "thought":
                    if action == "add":
                        cmd = AddThoughtCommand.model_validate_json(raw_json)

                        # Run LLM inference in a separate thread
                        trait, attribute_class = await asyncio.to_thread(
                            llm_service.infer_gsod, cmd.text
                        )

                        record = db_service.add_thought(
                            text=cmd.text,
                            lang=cmd.lang,
                            source=cmd.source,
                            attribute_class=attribute_class,
                            trait=trait,
                        )

                        # Send to Unreal for visualization
                        if "unreal" in manager.active_connections:
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
                                "type": "thought",
                                "record": serialize_record(record, "thought"),
                            }
                        )

                    elif action == "query":
                        cmd = QueryThoughtCommand.model_validate_json(raw_json)

                        if cmd.query_type == "all":
                            records = db_service.get_all_thoughts(
                                limit=cmd.filters.get("limit", 100),
                                offset=cmd.filters.get("offset", 0),
                            )
                        elif cmd.query_type == "recent":
                            records = db_service.get_recent_thoughts(
                                hours=cmd.filters.get("hours", 24),
                            )
                        elif cmd.query_type == "by_id":
                            record_id = cmd.filters.get("record_id")
                            if not isinstance(record_id, int) or record_id <= 0:
                                await websocket.send_json(
                                    {
                                        "status": "error",
                                        "error": "record_id must be a positive integer",
                                    }
                                )
                                continue
                            record = db_service.get_thought_by_id(record_id)
                            records = [record] if record else []
                        else:
                            await websocket.send_json(
                                {
                                    "status": "error",
                                    "error": f"Unknown query_type: {cmd.query_type}",
                                }
                            )
                            continue

                        await websocket.send_json(
                            {
                                "status": "success",
                                "action": "query",
                                "type": "thought",
                                "query_type": cmd.query_type,
                                "count": len(records),
                                "records": [
                                    serialize_record(r, "thought") for r in records
                                ],
                            }
                        )

                    elif action == "delete":
                        cmd = DeleteThoughtCommand.model_validate_json(raw_json)
                        success = db_service.delete_thought(cmd.record_id)
                        await websocket.send_json(
                            {
                                "status": "success" if success else "error",
                                "action": "delete",
                                "type": "thought",
                                "record_id": cmd.record_id,
                                "deleted": success,
                            }
                        )

                    elif action == "update":
                        cmd = UpdateThoughtCommand.model_validate_json(raw_json)

                        # Run LLM inference in a separate thread
                        trait, attribute_class = await asyncio.to_thread(
                            llm_service.infer_gsod, cmd.text
                        )

                        record = db_service.update_thought(
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
                                    "type": "thought",
                                    "record": serialize_record(record, "thought"),
                                }
                            )
                        else:
                            await websocket.send_json(
                                {
                                    "status": "error",
                                    "action": "update",
                                    "type": "thought",
                                    "error": f"Thought {cmd.record_id} not found",
                                }
                            )

                # —— Prompt operations ———————————————————————————————————
                elif record_type == "prompt":
                    if action == "add":
                        cmd = AddPromptCommand.model_validate_json(raw_json)

                        # Run LLM inference in a separate thread
                        trait, attribute_class = await asyncio.to_thread(
                            llm_service.infer_gsod, cmd.text
                        )

                        record = db_service.add_prompt(
                            text=cmd.text,
                            lang=cmd.lang,
                            source=cmd.source,
                            attribute_class=attribute_class,
                            trait=trait,
                        )

                        await websocket.send_json(
                            {
                                "status": "success",
                                "action": "add",
                                "type": "prompt",
                                "record": serialize_record(record, "prompt"),
                            }
                        )

                    elif action == "query":
                        cmd = QueryPromptCommand.model_validate_json(raw_json)

                        if cmd.query_type == "all":
                            records = db_service.get_all_prompts(
                                limit=cmd.filters.get("limit", 100),
                                offset=cmd.filters.get("offset", 0),
                            )
                        elif cmd.query_type == "recent":
                            records = db_service.get_recent_prompts(
                                hours=cmd.filters.get("hours", 24),
                            )
                        elif cmd.query_type == "by_id":
                            record_id = cmd.filters.get("record_id")
                            if not isinstance(record_id, int) or record_id <= 0:
                                await websocket.send_json(
                                    {
                                        "status": "error",
                                        "error": "record_id must be a positive integer",
                                    }
                                )
                                continue
                            record = db_service.get_prompt_by_id(record_id)
                            records = [record] if record else []
                        else:
                            await websocket.send_json(
                                {
                                    "status": "error",
                                    "error": f"Unknown query_type: {cmd.query_type}",
                                }
                            )
                            continue

                        await websocket.send_json(
                            {
                                "status": "success",
                                "action": "query",
                                "type": "prompt",
                                "query_type": cmd.query_type,
                                "count": len(records),
                                "records": [
                                    serialize_record(r, "prompt") for r in records
                                ],
                            }
                        )

                    elif action == "delete":
                        cmd = DeletePromptCommand.model_validate_json(raw_json)
                        success = db_service.delete_prompt(cmd.record_id)
                        await websocket.send_json(
                            {
                                "status": "success" if success else "error",
                                "action": "delete",
                                "type": "prompt",
                                "record_id": cmd.record_id,
                                "deleted": success,
                            }
                        )

                    elif action == "update":
                        cmd = UpdatePromptCommand.model_validate_json(raw_json)

                        # Run LLM inference in a separate thread
                        trait, attribute_class = await asyncio.to_thread(
                            llm_service.infer_gsod, cmd.text
                        )

                        record = db_service.update_prompt(
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
                                    "type": "prompt",
                                    "record": serialize_record(record, "prompt"),
                                }
                            )
                        else:
                            await websocket.send_json(
                                {
                                    "status": "error",
                                    "action": "update",
                                    "type": "prompt",
                                    "error": f"Prompt {cmd.record_id} not found",
                                }
                            )

                # —— Decree operations ────────────────────────────────────
                elif record_type == "decree":
                    if action == "add":
                        cmd = AddDecreeCommand.model_validate_json(raw_json)

                        # Run LLM inference in a separate thread
                        trait, attribute_class = await asyncio.to_thread(
                            llm_service.infer_gsod, cmd.text
                        )

                        record = db_service.add_decree(
                            text=cmd.text,
                            lang=cmd.lang,
                            source=cmd.source,
                            attribute_class=attribute_class,
                            trait=trait,
                        )

                        await websocket.send_json(
                            {
                                "status": "success",
                                "action": "add",
                                "type": "decree",
                                "record": serialize_record(record, "decree"),
                            }
                        )

                    elif action == "query":
                        cmd = QueryDecreeCommand.model_validate_json(raw_json)

                        if cmd.query_type == "all":
                            records = db_service.get_all_decrees(
                                limit=cmd.filters.get("limit", 100),
                                offset=cmd.filters.get("offset", 0),
                            )
                        elif cmd.query_type == "recent":
                            records = db_service.get_recent_decrees(
                                hours=cmd.filters.get("hours", 24),
                            )
                        elif cmd.query_type == "by_id":
                            record_id = cmd.filters.get("record_id")
                            if not isinstance(record_id, int) or record_id <= 0:
                                await websocket.send_json(
                                    {
                                        "status": "error",
                                        "error": "record_id must be a positive integer",
                                    }
                                )
                                continue
                            record = db_service.get_decree_by_id(record_id)
                            records = [record] if record else []
                        else:
                            await websocket.send_json(
                                {
                                    "status": "error",
                                    "error": f"Unknown query_type: {cmd.query_type}",
                                }
                            )
                            continue

                        await websocket.send_json(
                            {
                                "status": "success",
                                "action": "query",
                                "type": "decree",
                                "query_type": cmd.query_type,
                                "count": len(records),
                                "records": [
                                    serialize_record(r, "decree") for r in records
                                ],
                            }
                        )

                    elif action == "delete":
                        cmd = DeleteDecreeCommand.model_validate_json(raw_json)
                        success = db_service.delete_decree(cmd.record_id)
                        await websocket.send_json(
                            {
                                "status": "success" if success else "error",
                                "action": "delete",
                                "type": "decree",
                                "record_id": cmd.record_id,
                                "deleted": success,
                            }
                        )

                    elif action == "update":
                        cmd = UpdateDecreeCommand.model_validate_json(raw_json)

                        # Run LLM inference in a separate thread
                        trait, attribute_class = await asyncio.to_thread(
                            llm_service.infer_gsod, cmd.text
                        )

                        record = db_service.update_decree(
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
                                    "type": "decree",
                                    "record": serialize_record(record, "decree"),
                                }
                            )
                        else:
                            await websocket.send_json(
                                {
                                    "status": "error",
                                    "action": "update",
                                    "type": "decree",
                                    "error": f"Decree {cmd.record_id} not found",
                                }
                            )

                else:
                    await websocket.send_json(
                        {
                            "status": "error",
                            "error": f"Unknown record type: {record_type}",
                        }
                    )

            except ValidationError as e:
                await websocket.send_json(
                    {"status": "error", "error": f"Invalid payload format. {str(e)}"}
                )
            except json.JSONDecodeError:
                await websocket.send_json({"status": "error", "error": "Invalid JSON"})
            except Exception as e:
                await websocket.send_json(
                    {"status": "error", "error": f"Internal error: {str(e)}"}
                )

    except WebSocketDisconnect:
        manager.disconnect("frontend")
