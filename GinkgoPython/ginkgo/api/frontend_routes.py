import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import TypeAdapter, ValidationError

from ginkgo.core.config import settings
from ginkgo.ws.commands import (
    AddDecreeCommand,
    AddPromptCommand,
    AddThoughtCommand,
    DeleteCommand,
    QueryCommand,
    SendKeystrokeCommand,
    UpdateDecreeCommand,
    UpdatePromptCommand,
    UpdateThoughtCommand,
)
from ginkgo.ws.connection_manager import manager
from ginkgo.ws.handlers import (
    decree_handler,
    key_handler,
    prompt_handler,
    thought_handler,
)

router = APIRouter()


async def keepalive_task(websocket: WebSocket):
    """Send periodic ping frames to keep WebSocket connection alive.

    This prevents Windows asyncio IOCP proactor timeout (~90 seconds)
    by sending a ping frame every KEEPALIVE_INTERVAL seconds.
    """
    try:
        while True:
            await asyncio.sleep(settings.websocket_keepalive_interval)
            try:
                # Send a ping frame using the underlying websockets connection
                await websocket.send_json({"type": "ping"})
            except Exception:
                # If we can't send, the connection is likely closed
                break
    except asyncio.CancelledError:
        pass


@router.websocket("/ws/frontend")
async def frontend_endpoint(websocket: WebSocket):
    await manager.connect("frontend", websocket)
    keepalive = None
    try:
        # Start the keepalive task
        keepalive = asyncio.create_task(keepalive_task(websocket))

        while True:
            raw_json = await websocket.receive_text()

            try:
                data = json.loads(raw_json)

                # Ignore ping messages from keepalive task
                if data.get("type") == "ping":
                    continue

                action = data.get("action")
                record_type = data.get("type")

                response: dict[str, Any] | None = await dispatch_message(
                    record_type, action, raw_json
                )

                if response:
                    await websocket.send_json(jsonable_encoder(response))

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
    finally:
        # Clean up keepalive task
        if keepalive:
            keepalive.cancel()
            try:
                await keepalive
            except asyncio.CancelledError:
                pass


async def dispatch_message(
    record_type: str, action: str, raw_json: str
) -> dict[str, Any] | None:

    query_adapter: TypeAdapter[QueryCommand] = TypeAdapter(QueryCommand)

    if record_type == "thought":
        if action == "add":
            cmd: AddThoughtCommand = AddThoughtCommand.model_validate_json(raw_json)
            return await thought_handler.handle_add_thought(cmd)
        elif action == "query":
            cmd = query_adapter.validate_json(raw_json)
            return await thought_handler.handle_query_thought(cmd)
        elif action == "update":
            cmd: UpdateThoughtCommand = UpdateThoughtCommand.model_validate_json(
                raw_json
            )
            return await thought_handler.handle_update_thought(cmd)
        elif action == "delete":
            cmd: DeleteCommand = DeleteCommand.model_validate_json(raw_json)
            return await thought_handler.handle_delete_thought(cmd)

    elif record_type == "prompt":
        if action == "add":
            cmd: AddPromptCommand = AddPromptCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_add_prompt(cmd)
        elif action == "query":
            cmd = query_adapter.validate_json(raw_json)
            return await prompt_handler.handle_query_prompt(cmd)
        elif action == "update":
            cmd: UpdatePromptCommand = UpdatePromptCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_update_prompt(cmd)
        elif action == "delete":
            cmd: DeleteCommand = DeleteCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_delete_prompt(cmd)

    elif record_type == "decree":
        if action == "add":
            cmd: AddDecreeCommand = AddDecreeCommand.model_validate_json(raw_json)
            return await decree_handler.handle_add_decree(cmd)
        elif action == "query":
            cmd = query_adapter.validate_json(raw_json)
            return await decree_handler.handle_query_decree(cmd)
        elif action == "update":
            cmd: UpdateDecreeCommand = UpdateDecreeCommand.model_validate_json(raw_json)
            return await decree_handler.handle_update_decree(cmd)
        elif action == "delete":
            cmd: DeleteCommand = DeleteCommand.model_validate_json(raw_json)
            return await decree_handler.handle_delete_decree(cmd)

    elif record_type == "keystroke":
        if action == "send":
            cmd: SendKeystrokeCommand = SendKeystrokeCommand.model_validate_json(
                raw_json
            )
            return await key_handler.handle_keystroke(cmd)

    else:
        return {
            "status": "error",
            "error": f"Unknown record type: {record_type}",
        }

    return None
