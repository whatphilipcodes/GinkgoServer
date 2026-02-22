from typing import Any

from ginkgo.services.database_service import db_service
from ginkgo.ws.commands import (
    AddPromptCommand,
    DeletePromptCommand,
    QueryPromptCommand,
    UpdatePromptCommand,
)


async def handle_add_prompt(cmd: AddPromptCommand) -> dict[str, Any]:
    record = db_service.add_prompt(
        text=cmd.text,
        lang=cmd.lang,
        source=cmd.source,
    )

    return {
        "status": "success",
        "action": "add",
        "type": "prompt",
        "record": serialize_prompt(record),
    }


async def handle_query_prompt(cmd: QueryPromptCommand) -> dict[str, Any]:
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
            return {
                "status": "error",
                "error": "record_id must be a positive integer",
            }
        record = db_service.get_prompt_by_id(record_id)
        records = [record] if record else []
    else:
        return {
            "status": "error",
            "error": f"Unknown query_type: {cmd.query_type}",
        }

    return {
        "status": "success",
        "action": "query",
        "type": "prompt",
        "query_type": cmd.query_type,
        "count": len(records),
        "records": [serialize_prompt(r) for r in records],
    }


async def handle_update_prompt(cmd: UpdatePromptCommand) -> dict[str, Any]:
    record = db_service.update_prompt(
        cmd.record_id,
        cmd.text,
    )

    if record:
        return {
            "status": "success",
            "action": "update",
            "type": "prompt",
            "record": serialize_prompt(record),
        }
    else:
        return {
            "status": "error",
            "action": "update",
            "type": "prompt",
            "error": f"Prompt {cmd.record_id} not found",
        }


async def handle_delete_prompt(cmd: DeletePromptCommand) -> dict[str, Any]:
    success = db_service.delete_prompt(cmd.record_id)
    return {
        "status": "success" if success else "error",
        "action": "delete",
        "type": "prompt",
        "record_id": cmd.record_id,
        "deleted": success,
    }


def serialize_prompt(record) -> dict[str, Any]:
    return {
        "id": record.id,
        "text": record.text,
        "type": "prompt",
        "valid": record.valid,
        "lang": record.lang.value,
        "source": record.source.value,
        "created_at": record.created_at.isoformat(),
        "modified_at": record.modified_at.isoformat(),
    }
