from typing import Any

from ginkgo.models.decree import DecreeRead
from ginkgo.services.database import db_service
from ginkgo.ws.commands import (
    AddDecreeCommand,
    DeleteDecreeCommand,
    QueryAllDecrees,
    QueryDecreeCommand,
    QueryDecreesById,
    QueryRecentDecrees,
    UpdateDecreeCommand,
)


async def handle_add_decree(cmd: AddDecreeCommand) -> dict[str, Any]:
    record: DecreeRead = db_service.add_decree(
        text=cmd.text,
        lang=cmd.lang,
        source=cmd.source,
    )

    return {
        "status": "success",
        "action": "add",
        "type": "decree",
        "record": serialize_decree(record),
    }


async def handle_query_decree(cmd: QueryDecreeCommand) -> dict[str, Any]:
    if isinstance(cmd, QueryAllDecrees):
        records: list[DecreeRead] = db_service.get_all_decrees(
            limit=cmd.filters.limit,
            offset=cmd.filters.offset,
        )
    elif isinstance(cmd, QueryRecentDecrees):
        records: list[DecreeRead] = db_service.get_recent_decrees(
            hours=cmd.filters.hours,
        )
    elif isinstance(cmd, QueryDecreesById):
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
        "records": [serialize_decree(r) for r in records],
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
            "record": serialize_decree(record),
        }
    else:
        return {
            "status": "error",
            "action": "update",
            "type": "decree",
            "error": f"Decree {cmd.record_id} not found",
        }


async def handle_delete_decree(cmd: DeleteDecreeCommand) -> dict[str, Any]:
    success: bool = db_service.delete_decree(cmd.record_id)
    return {
        "status": "success" if success else "error",
        "action": "delete",
        "type": "decree",
        "record_id": cmd.record_id,
        "deleted": success,
    }


def serialize_decree(record: DecreeRead) -> dict[str, Any]:
    return {
        "id": record.id,
        "text": record.text,
        "type": "decree",
        "valid": record.valid,
        "lang": record.lang if record.lang else None,
        "source": record.source.value,
        "created_at": record.created_at.isoformat(),
        "modified_at": record.modified_at.isoformat(),
    }
