import asyncio
import random
from typing import Any

from ginkgo.models.base import GSODAttribute, GSODTrait
from ginkgo.schemas.unreal import UEDataPayload
from ginkgo.services.database_service import db_service
from ginkgo.services.llm_service import llm_service
from ginkgo.ws.commands import (
    AddThoughtCommand,
    DeleteThoughtCommand,
    QueryThoughtCommand,
    UpdateThoughtCommand,
)
from ginkgo.ws.connection_manager import manager


async def handle_add_thought(cmd: AddThoughtCommand) -> dict[str, Any]:
    trait_str, attribute_class_str = await asyncio.to_thread(
        llm_service.infer_gsod, cmd.text
    )

    attribute_class = None
    trait = None
    if attribute_class_str:
        try:
            attribute_class = GSODAttribute(attribute_class_str)
        except ValueError:
            pass
    if trait_str:
        try:
            trait = GSODTrait(trait_str)
        except ValueError:
            pass

    record = db_service.add_thought(
        text=cmd.text,
        lang=cmd.lang,
        source=cmd.source,
        attribute_class=attribute_class,
        trait=trait,
    )

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

    return {
        "status": "success",
        "action": "add",
        "type": "thought",
        "record": serialize_thought(record),
    }


async def handle_query_thought(cmd: QueryThoughtCommand) -> dict[str, Any]:
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
            return {
                "status": "error",
                "error": "record_id must be a positive integer",
            }
        record = db_service.get_thought_by_id(record_id)
        records = [record] if record else []
    else:
        return {
            "status": "error",
            "error": f"Unknown query_type: {cmd.query_type}",
        }

    return {
        "status": "success",
        "action": "query",
        "type": "thought",
        "query_type": cmd.query_type,
        "count": len(records),
        "records": [serialize_thought(r) for r in records],
    }


async def handle_update_thought(cmd: UpdateThoughtCommand) -> dict[str, Any]:
    trait_str, attribute_class_str = await asyncio.to_thread(
        llm_service.infer_gsod, cmd.text
    )

    attribute_class = None
    trait = None
    if attribute_class_str:
        try:
            attribute_class = GSODAttribute(attribute_class_str)
        except ValueError:
            pass
    if trait_str:
        try:
            trait = GSODTrait(trait_str)
        except ValueError:
            pass

    record = db_service.update_thought(
        cmd.record_id,
        cmd.text,
        attribute_class=attribute_class,
        trait=trait,
    )

    if record:
        return {
            "status": "success",
            "action": "update",
            "type": "thought",
            "record": serialize_thought(record),
        }
    else:
        return {
            "status": "error",
            "action": "update",
            "type": "thought",
            "error": f"Thought {cmd.record_id} not found",
        }


async def handle_delete_thought(cmd: DeleteThoughtCommand) -> dict[str, Any]:
    success = db_service.delete_thought(cmd.record_id)
    return {
        "status": "success" if success else "error",
        "action": "delete",
        "type": "thought",
        "record_id": cmd.record_id,
        "deleted": success,
    }


def serialize_thought(record) -> dict[str, Any]:
    return {
        "id": record.id,
        "text": record.text,
        "type": "thought",
        "valid": record.valid,
        "lang": record.lang.value,
        "source": record.source.value,
        "created_at": record.created_at.isoformat(),
        "modified_at": record.modified_at.isoformat(),
        "attribute_class": (
            record.attribute_class.value if record.attribute_class else None
        ),
        "trait": record.trait.value if record.trait else None,
        "trait_offset": record.trait_offset,
        "trait_entailment": record.trait_entailment,
        "score_health": record.score_health,
        "score_split": record.score_split,
        "score_impact": record.score_impact,
    }
