from typing import Any

from ginkgo.services.database import db_service
from ginkgo.ws.commands import (
    AddDecreeCommand,
    DeleteDecreeCommand,
    QueryDecreeCommand,
    UpdateDecreeCommand,
)


async def handle_add_decree(cmd: AddDecreeCommand) -> dict[str, Any]:
    record = db_service.add_decree(
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
            return {
                "status": "error",
                "error": "record_id must be a positive integer",
            }
        record = db_service.get_decree_by_id(record_id)
        records = [record] if record else []
    else:
        return {
            "status": "error",
            "error": f"Unknown query_type: {cmd.query_type}",
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
    record = db_service.update_decree(
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
    success = db_service.delete_decree(cmd.record_id)
    return {
        "status": "success" if success else "error",
        "action": "delete",
        "type": "decree",
        "record_id": cmd.record_id,
        "deleted": success,
    }


def serialize_decree(record) -> dict[str, Any]:
    return {
        "id": record.id,
        "text": record.text,
        "type": "decree",
        "valid": record.valid,
        "lang": record.lang.value,
        "source": record.source.value,
        "created_at": record.created_at.isoformat(),
        "modified_at": record.modified_at.isoformat(),
    }
