import asyncio
from typing import Any

from ginkgo.models.thought import ThoughtRead
from ginkgo.schemas.unreal import GinkgoInput, GinkgoMessage, GinkgoMessageType
from ginkgo.services.database import db_service
from ginkgo.services.tasks.auxiliary import aux_task
from ginkgo.services.tasks.decree import decree_task
from ginkgo.services.tasks.gsod import gsod_task
from ginkgo.services.tasks.validate import validate_task
from ginkgo.utils.logger import get_logger
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

logger = get_logger(__name__)


async def handle_add_thought(cmd: AddThoughtCommand) -> dict[str, Any]:
    validate_result = await asyncio.to_thread(validate_task.infer, cmd.text)

    if not validate_result.valid:
        logger.info("Invalid Input. Discarding...")
        record: ThoughtRead = db_service.add_thought(
            text=cmd.text,
            lang=validate_result.language,
            source=cmd.source,
            valid=False,
        )
    else:
        gsod_future = asyncio.to_thread(gsod_task.infer, cmd.text)
        health_future = asyncio.to_thread(decree_task.infer, cmd.text)
        aux_future = asyncio.to_thread(aux_task.infer, cmd.text)
        gsod_result, decree_result, aux_result = await asyncio.gather(
            gsod_future,
            health_future,
            aux_future,
        )

        record: ThoughtRead = db_service.add_thought(
            text=cmd.text,
            lang=validate_result.language,
            source=cmd.source,
            valid=True,
            attribute_class=gsod_result.attribute,
            trait=gsod_result.trait,
            trait_entailment=gsod_result.entailment,
            score_health=decree_result.alignment,
            score_split=aux_result.split,
            score_impact=aux_result.impact,
        )

    # to-do: better separation between valid and invalid
    if (
        "unreal" in manager.active_connections
        and record.valid
        and record.attribute_class
    ):
        input_payload = GinkgoInput(
            id=record.id,
            text=record.text,
            attribute=record.attribute_class,
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
    validate_result = await asyncio.to_thread(validate_task.infer, cmd.text)

    if not validate_result.valid:
        logger.info("Invalid Input. Disgarded...")
        record: ThoughtRead | None = db_service.update_thought(
            cmd.record_id,
            cmd.text,
            valid=False,
            trait_entailment=0.0,
            score_health=0.0,
            score_split=0.0,
            score_impact=0.0,
        )
    else:
        gsod_future = asyncio.to_thread(gsod_task.infer, cmd.text)
        health_future = asyncio.to_thread(decree_task.infer, cmd.text)
        aux_future = asyncio.to_thread(aux_task.infer, cmd.text)
        gsod_result, decree_result, aux_result = await asyncio.gather(
            gsod_future,
            health_future,
            aux_future,
        )

        record: ThoughtRead | None = db_service.update_thought(
            cmd.record_id,
            cmd.text,
            valid=validate_result.valid,
            attribute_class=gsod_result.attribute,
            trait=gsod_result.trait,
            trait_entailment=gsod_result.entailment,
            score_health=decree_result.alignment,
            score_split=aux_result.split,
            score_impact=aux_result.impact,
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
        "lang": record.lang if record.lang else None,
        "source": record.source.value,
        "created_at": record.created_at.isoformat(),
        "modified_at": record.modified_at.isoformat(),
        "attribute_class": record.attribute_class.value
        if record.attribute_class
        else None,
        "trait": record.trait.value if record.trait else None,
        "trait_offset": record.trait_offset,
        "trait_entailment": record.trait_entailment,
        "score_health": record.score_health,
        "score_split": record.score_split,
        "score_impact": record.score_impact,
    }
