import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

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
from ginkgo.ws.handlers import decree_handler, prompt_handler, thought_handler

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

                response = await dispatch_message(record_type, action, raw_json)

                if response:
                    await websocket.send_json(response)

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


async def dispatch_message(record_type: str, action: str, raw_json: str):
    if record_type == "thought":
        if action == "add":
            cmd = AddThoughtCommand.model_validate_json(raw_json)
            return await thought_handler.handle_add_thought(cmd)
        elif action == "query":
            cmd = QueryThoughtCommand.model_validate_json(raw_json)
            return await thought_handler.handle_query_thought(cmd)
        elif action == "update":
            cmd = UpdateThoughtCommand.model_validate_json(raw_json)
            return await thought_handler.handle_update_thought(cmd)
        elif action == "delete":
            cmd = DeleteThoughtCommand.model_validate_json(raw_json)
            return await thought_handler.handle_delete_thought(cmd)

    elif record_type == "prompt":
        if action == "add":
            cmd = AddPromptCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_add_prompt(cmd)
        elif action == "query":
            cmd = QueryPromptCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_query_prompt(cmd)
        elif action == "update":
            cmd = UpdatePromptCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_update_prompt(cmd)
        elif action == "delete":
            cmd = DeletePromptCommand.model_validate_json(raw_json)
            return await prompt_handler.handle_delete_prompt(cmd)

    elif record_type == "decree":
        if action == "add":
            cmd = AddDecreeCommand.model_validate_json(raw_json)
            return await decree_handler.handle_add_decree(cmd)
        elif action == "query":
            cmd = QueryDecreeCommand.model_validate_json(raw_json)
            return await decree_handler.handle_query_decree(cmd)
        elif action == "update":
            cmd = UpdateDecreeCommand.model_validate_json(raw_json)
            return await decree_handler.handle_update_decree(cmd)
        elif action == "delete":
            cmd = DeleteDecreeCommand.model_validate_json(raw_json)
            return await decree_handler.handle_delete_decree(cmd)

    else:
        return {
            "status": "error",
            "error": f"Unknown record type: {record_type}",
        }

    return None
