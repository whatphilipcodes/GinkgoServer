import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import TypeAdapter, ValidationError

from ginkgo.ws.commands import (
    AddDecreeCommand,
    AddPromptCommand,
    AddThoughtCommand,
    DeleteDecreeCommand,
    DeletePromptCommand,
    DeleteThoughtCommand,
    QueryAllThoughts,
    QueryDecreeCommand,
    QueryPromptCommand,
    QueryRecentThoughts,
    QueryThoughtCommand,
    QueryThoughtsById,
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


async def dispatch_message(
    record_type: str, action: str, raw_json: str
) -> dict[str, Any] | None:

    thought_query_adapter: TypeAdapter[QueryThoughtCommand] = TypeAdapter(
        QueryThoughtCommand
    )
    prompt_query_adapter: TypeAdapter[QueryPromptCommand] = TypeAdapter(
        QueryPromptCommand
    )
    decree_query_adapter: TypeAdapter[QueryDecreeCommand] = TypeAdapter(
        QueryDecreeCommand
    )

    if record_type == "thought":
        if action == "add":
            cmd: AddThoughtCommand = AddThoughtCommand.model_validate_json(raw_json)
            return await thought_handler.handle_add_thought(cmd)
        elif action == "query":
            cmd: QueryAllThoughts | QueryRecentThoughts | QueryThoughtsById = (
                thought_query_adapter.validate_json(raw_json)
            )
            return await thought_handler.handle_query_thought(cmd)
        elif action == "update":
            cmd: UpdateThoughtCommand = UpdateThoughtCommand.model_validate_json(
                raw_json
            )
            return await thought_handler.handle_update_thought(cmd)
        elif action == "delete":
            cmd: DeleteThoughtCommand = DeleteThoughtCommand.model_validate_json(
                raw_json
            )
            return await thought_handler.handle_delete_thought(cmd)

    elif record_type == "prompt":
        if action == "add":
            cmd: AddPromptCommand = AddPromptCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_add_prompt(cmd)
        elif action == "query":
            cmd: QueryPromptCommand = prompt_query_adapter.validate_json(raw_json)
            return await prompt_handler.handle_query_prompt(cmd)
        elif action == "update":
            cmd: UpdatePromptCommand = UpdatePromptCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_update_prompt(cmd)
        elif action == "delete":
            cmd: DeletePromptCommand = DeletePromptCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_delete_prompt(cmd)

    elif record_type == "decree":
        if action == "add":
            cmd: AddDecreeCommand = AddDecreeCommand.model_validate_json(raw_json)
            return await decree_handler.handle_add_decree(cmd)
        elif action == "query":
            cmd: QueryDecreeCommand = decree_query_adapter.validate_json(raw_json)
            return await decree_handler.handle_query_decree(cmd)
        elif action == "update":
            cmd: UpdateDecreeCommand = UpdateDecreeCommand.model_validate_json(raw_json)
            return await decree_handler.handle_update_decree(cmd)
        elif action == "delete":
            cmd: DeleteDecreeCommand = DeleteDecreeCommand.model_validate_json(raw_json)
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
