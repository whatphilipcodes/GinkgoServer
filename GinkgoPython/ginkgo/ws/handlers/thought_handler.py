import asyncio
from typing import Any

from ginkgo.models.enums import InputSource
from ginkgo.models.thought import ThoughtRead
from ginkgo.schemas.unreal import GinkgoInput, GinkgoMessage, GinkgoMessageType
from ginkgo.services.database import db_service
from ginkgo.services.tasks.augment import augment_task
from ginkgo.services.tasks.auxiliary import aux_task
from ginkgo.services.tasks.decree import decree_task
from ginkgo.services.tasks.filter import filter_task
from ginkgo.services.tasks.gsod import gsod_task
from ginkgo.utils.logger import get_logger
from ginkgo.ws.commands import (
    AddThoughtCommand,
    DeleteCommand,
    QueryAll,
    QueryById,
    QueryCommand,
    QueryRecent,
    UpdateThoughtCommand,
)
from ginkgo.ws.connection_manager import manager

logger = get_logger(__name__)


async def handle_add_thought(cmd: AddThoughtCommand) -> dict[str, Any]:

    prompt = db_service.get_prompt_by_id(cmd.prompt_id)

    if not prompt:
        logger.info("Prompt is missing.")
        return {
            "status": "error",
            "action": "add",
            "type": "thought",
            "error": "Input rejected because prompt missing.",
        }

    logger.info("Inferring user input")
    logger.info(f"Prompt: {prompt.text}")
    logger.info(f"Thought: {cmd.text}")

    filter_result = await asyncio.to_thread(filter_task.infer, cmd.text)
    if not filter_result.valid:
        logger.info("Invalid input. Rejected before insert.")
        return {
            "status": "error",
            "action": "add",
            "type": "thought",
            "error": "Input rejected by validation",
        }

    augment_future = asyncio.to_thread(augment_task.infer, cmd.text)
    gsod_future = asyncio.to_thread(gsod_task.infer, cmd.text, prompt.text)
    health_future = asyncio.to_thread(decree_task.infer, cmd.text, prompt.text)
    aux_future = asyncio.to_thread(aux_task.infer, cmd.text, prompt.text)
    augment_result, gsod_result, decree_result, aux_result = await asyncio.gather(
        augment_future,
        gsod_future,
        health_future,
        aux_future,
    )

    if not gsod_result:
        logger.info("Input could not be classified. Rejected before insert.")
        return {
            "status": "error",
            "action": "add",
            "type": "thought",
            "error": "Input rejected because class missing.",
        }

    record: ThoughtRead = db_service.add_thought(
        prompt_id=cmd.prompt_id,
        text=cmd.text,
        lang=augment_result.language,
        source=InputSource.AUDIENCE,
        attribute_class=gsod_result.attribute,
        trait=gsod_result.trait,
        trait_entailment=gsod_result.entailment,
        score_health=decree_result.alignment,
        score_split=aux_result.split,
        score_impact=aux_result.impact,
    )

    if "unreal" in manager.active_connections and record.attribute_class:
        input_payload = GinkgoInput.from_thought(record)
        message = GinkgoMessage(
            messageType=GinkgoMessageType.INPUT,
            payloadJson=input_payload,
        )
        await manager.send_to(message.model_dump_json(), "unreal")

    logger.info("Cycle complete " + "=" * 128 + "\n")

    return {
        "status": "success",
        "action": "add",
        "type": "thought",
        "record": record,
    }


async def handle_query_thought(cmd: QueryCommand) -> dict[str, Any]:
    if isinstance(cmd, QueryAll):
        records: list[ThoughtRead] = db_service.get_all_thoughts(
            limit=cmd.filters.limit,
            offset=cmd.filters.offset,
            recent=cmd.filters.recent,
        )
    elif isinstance(cmd, QueryRecent):
        records: list[ThoughtRead] = db_service.get_recent_thoughts(
            hours=cmd.filters.hours,
        )
    elif isinstance(cmd, QueryById):
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
        "records": [r for r in records],
    }


async def handle_update_thought(cmd: UpdateThoughtCommand) -> dict[str, Any]:
    logger.info("Inferring user input: Thought: %s", cmd.text)

    filter_result = await asyncio.to_thread(filter_task.infer, cmd.text)
    if not filter_result.valid:
        logger.info("Invalid input. Rejected before insert.")
        return {
            "status": "error",
            "action": "add",
            "type": "thought",
            "error": "Input rejected by validation",
        }
    else:
        augment_future = asyncio.to_thread(augment_task.infer, cmd.text)
        gsod_future = asyncio.to_thread(gsod_task.infer, cmd.text, "prompt missing")
        health_future = asyncio.to_thread(decree_task.infer, cmd.text, "prompt missing")
        aux_future = asyncio.to_thread(aux_task.infer, cmd.text, "prompt missing")
        augment_result, gsod_result, decree_result, aux_result = await asyncio.gather(
            augment_future,
            gsod_future,
            health_future,
            aux_future,
        )

        record: ThoughtRead | None = db_service.update_thought(
            cmd.record_id,
            prompt_id=cmd.prompt_id,
            text=cmd.text,
            lang=augment_result.language,
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
            "record": record,
        }
    else:
        return {
            "status": "error",
            "action": "update",
            "type": "thought",
            "error": f"Thought {cmd.record_id} not found",
        }


async def handle_delete_thought(cmd: DeleteCommand) -> dict[str, Any]:
    success: bool = db_service.delete_thought(cmd.record_id)
    return {
        "status": "success" if success else "error",
        "action": "delete",
        "type": "thought",
        "record_id": cmd.record_id,
        "deleted": success,
    }
