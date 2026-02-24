import asyncio
from typing import Any

from ginkgo.models.enums import GinkgoMessageType, GSODAttribute, GSODTrait
from ginkgo.models.thought import ThoughtRead
from ginkgo.schemas.unreal import GinkgoInput, GinkgoMessage
from ginkgo.services.database import db_service
from ginkgo.services.tasks.gsod import gsod_task
from ginkgo.ws.commands import (
    AddThoughtCommand,
    DeleteThoughtCommand,
    QueryAllThoughts,
    QueryRecentThoughts,
    QueryThoughtCommand,
    QueryThoughtsById,
    UpdateThoughtCommand,
)
from ginkgo.ws.connection_manager import manager


async def handle_add_thought(cmd: AddThoughtCommand) -> dict[str, Any]:
    trait_str, attribute_class_str = await asyncio.to_thread(
        gsod_task.infer, cmd.text
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

    record: ThoughtRead = db_service.add_thought(
        text=cmd.text,
        lang=cmd.lang,
        source=cmd.source,
        attribute_class=attribute_class,
        trait=trait,
    )

    if "unreal" in manager.active_connections:
        input_payload = GinkgoInput(
            id=record.id,
            text=record.text,
            attribute=record.attribute_class or GSODAttribute.REPRESENTATION,
            traitOffset=record.trait_offset,
            traitEntailment=record.trait_entailment,
            scoreHealth=record.score_health,
            scoreSplit=record.score_split,
            scoreImpact=record.score_impact,
        )
        message = GinkgoMessage(
            messageType=GinkgoMessageType.INPUT,
            payloadJson=input_payload,
        )
        await manager.send_to(message.model_dump_json(), "unreal")

    return {
        "status": "success",
        "action": "add",
        "type": "thought",
        "record": serialize_thought(record),
    }


async def handle_query_thought(cmd: QueryThoughtCommand) -> dict[str, Any]:
    if isinstance(cmd, QueryAllThoughts):
        records: list[ThoughtRead] = db_service.get_all_thoughts(
            limit=cmd.filters.limit,
            offset=cmd.filters.offset,
        )
    elif isinstance(cmd, QueryRecentThoughts):
        records: list[ThoughtRead] = db_service.get_recent_thoughts(
            hours=cmd.filters.hours,
        )
    elif isinstance(cmd, QueryThoughtsById):
        record: ThoughtRead | None = db_service.get_thought_by_id(cmd.filters.record_id)
        records = [record] if record else []
    else:
        return {
            "status": "error",
            "error": "Unknown query type",
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
        gsod_task.infer, cmd.text
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

    record: ThoughtRead | None = db_service.update_thought(
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
    success: bool = db_service.delete_thought(cmd.record_id)
    return {
        "status": "success" if success else "error",
        "action": "delete",
        "type": "thought",
        "record_id": cmd.record_id,
        "deleted": success,
    }


def serialize_thought(record: ThoughtRead) -> dict[str, Any]:
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
