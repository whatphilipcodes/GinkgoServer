from typing import Any

from ginkgo.models.prompt import PromptRead
from ginkgo.services.database import db_service
from ginkgo.ws.commands import (
    AddPromptCommand,
    DeletePromptCommand,
    QueryPromptCommand,
    UpdatePromptCommand,
)


async def handle_add_prompt(cmd: AddPromptCommand) -> dict[str, Any]:
    record: PromptRead = db_service.add_prompt(
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
    from ginkgo.ws.commands import AllFilter, ByIdFilter, RecentFilter

    if isinstance(cmd.filters, AllFilter):
        records: list[PromptRead] = db_service.get_all_prompts(
            limit=cmd.filters.limit,
            offset=cmd.filters.offset,
        )
    elif isinstance(cmd.filters, RecentFilter):
        records: list[PromptRead] = db_service.get_recent_prompts(
            hours=cmd.filters.hours,
        )
    elif isinstance(cmd.filters, ByIdFilter):
        record: PromptRead | None = db_service.get_prompt_by_id(cmd.filters.record_id)
        records = [record] if record else []
    else:
        return {
            "status": "error",
            "error": "Unknown filter type",
        }

    return {
        "status": "success",
        "action": "query",
        "type": "prompt",
        "query_type": cmd.filters.query_type,
        "count": len(records),
        "records": [serialize_prompt(r) for r in records],
    }


async def handle_update_prompt(cmd: UpdatePromptCommand) -> dict[str, Any]:
    record: PromptRead | None = db_service.update_prompt(
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
    success: bool = db_service.delete_prompt(cmd.record_id)
    return {
        "status": "success" if success else "error",
        "action": "delete",
        "type": "prompt",
        "record_id": cmd.record_id,
        "deleted": success,
    }


def serialize_prompt(record: PromptRead) -> dict[str, Any]:
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
