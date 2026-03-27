import asyncio
from typing import Any

from ginkgo.models.decree import DecreeRead
from ginkgo.models.enums import InputSource
from ginkgo.services.database import db_service
from ginkgo.services.tasks.augment import augment_task
from ginkgo.services.tasks.filter import filter_task
from ginkgo.utils.logger import get_logger
from ginkgo.ws.commands import (
    AddDecreeCommand,
    DeleteCommand,
    QueryAll,
    QueryById,
    QueryCommand,
    QueryRecent,
    UpdateDecreeCommand,
)

logger = get_logger(__name__)


async def handle_add_decree(cmd: AddDecreeCommand) -> dict[str, Any]:
    logger.info("Inferring user input: Decree: %s", cmd.text)
    filter_result = await asyncio.to_thread(filter_task.infer, cmd.text)
    if not filter_result.valid:
        return {
            "status": "error",
            "action": "add",
            "type": "decree",
            "error": "Input rejected by content filter",
        }

    augment = await asyncio.to_thread(augment_task.infer, cmd.text)

    record: DecreeRead = db_service.add_decree(
        text=cmd.text,
        lang=augment.language,
        source=InputSource.AUDIENCE,
    )

    return {
        "status": "success",
        "action": "add",
        "type": "decree",
        "record": record,
    }


async def handle_query_decree(cmd: QueryCommand) -> dict[str, Any]:
    if isinstance(cmd, QueryAll):
        records: list[DecreeRead] = db_service.get_all_decrees(
            limit=cmd.filters.limit,
            offset=cmd.filters.offset,
            recent=cmd.filters.recent,
        )
    elif isinstance(cmd, QueryRecent):
        records: list[DecreeRead] = db_service.get_recent_decrees(
            hours=cmd.filters.hours,
        )
    elif isinstance(cmd, QueryById):
        record: DecreeRead | None = db_service.get_decree_by_id(cmd.filters.record_id)
        records = [record] if record else []
    else:
        return {
            "status": "error",
            "error": "Unknown query type",
        }

    return {
        "status": "success",
        "action": "query",
        "type": "decree",
        "query_type": cmd.query_type,
        "count": len(records),
        "records": [r for r in records],
    }


async def handle_update_decree(cmd: UpdateDecreeCommand) -> dict[str, Any]:
    record: DecreeRead | None = db_service.update_decree(
        cmd.record_id,
        cmd.text,
    )

    if record:
        return {
            "status": "success",
            "action": "update",
            "type": "decree",
            "record": record,
        }
    else:
        return {
            "status": "error",
            "action": "update",
            "type": "decree",
            "error": f"Decree {cmd.record_id} not found",
        }


async def handle_delete_decree(cmd: DeleteCommand) -> dict[str, Any]:
    success: bool = db_service.delete_decree(cmd.record_id)
    return {
        "status": "success" if success else "error",
        "action": "delete",
        "type": "decree",
        "record_id": cmd.record_id,
        "deleted": success,
    }
