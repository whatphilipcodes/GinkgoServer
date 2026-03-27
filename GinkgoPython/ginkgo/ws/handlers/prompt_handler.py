import asyncio
from typing import Any

from ginkgo.models.enums import InputSource
from ginkgo.models.prompt import PromptRead
from ginkgo.services.database import db_service
from ginkgo.services.tasks.augment import augment_task
from ginkgo.services.tasks.filter import filter_task
from ginkgo.utils.logger import get_logger
from ginkgo.ws.commands import (
    AddPromptCommand,
    DeleteCommand,
    QueryAll,
    QueryById,
    QueryCommand,
    QueryRecent,
    UpdatePromptCommand,
)

logger = get_logger(__name__)


async def handle_add_prompt(cmd: AddPromptCommand) -> dict[str, Any]:
    logger.info("Inferring user input: Prompt: %s", cmd.text)
    filter_result = await asyncio.to_thread(filter_task.infer, cmd.text)
    if not filter_result.valid:
        return {
            "status": "error",
            "action": "add",
            "type": "prompt",
            "error": "Input rejected by content filter",
        }

    augment = await asyncio.to_thread(augment_task.infer, cmd.text)

    record: PromptRead = db_service.add_prompt(
        text=cmd.text,
        lang=augment.language,
        source=InputSource.AUDIENCE,
    )

    return {
        "status": "success",
        "action": "add",
        "type": "prompt",
        "record": record,
    }


async def handle_query_prompt(cmd: QueryCommand) -> dict[str, Any]:
    if isinstance(cmd, QueryAll):
        records: list[PromptRead] = db_service.get_all_prompts(
            limit=cmd.filters.limit,
            offset=cmd.filters.offset,
            recent=cmd.filters.recent,
        )
    elif isinstance(cmd, QueryRecent):
        records: list[PromptRead] = db_service.get_recent_prompts(
            hours=cmd.filters.hours,
        )
    elif isinstance(cmd, QueryById):
        record: PromptRead | None = db_service.get_prompt_by_id(cmd.filters.record_id)
        records = [record] if record else []
    else:
        return {
            "status": "error",
            "error": "Unknown query type",
        }

    return {
        "status": "success",
        "action": "query",
        "type": "prompt",
        "query_type": cmd.query_type,
        "count": len(records),
        "records": [r for r in records],
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
            "record": record,
        }
    else:
        return {
            "status": "error",
            "action": "update",
            "type": "prompt",
            "error": f"Prompt {cmd.record_id} not found",
        }


async def handle_delete_prompt(cmd: DeleteCommand) -> dict[str, Any]:
    success: bool = db_service.delete_prompt(cmd.record_id)
    return {
        "status": "success" if success else "error",
        "action": "delete",
        "type": "prompt",
        "record_id": cmd.record_id,
        "deleted": success,
    }
