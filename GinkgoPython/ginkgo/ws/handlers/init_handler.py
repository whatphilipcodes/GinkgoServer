from ginkgo.core.config import settings
from ginkgo.schemas.unreal import (
    GinkgoInput,
    GinkgoInputList,
    GinkgoMessage,
    GinkgoMessageType,
)
from ginkgo.services.database import db_service
from ginkgo.utils.logger import get_logger
from ginkgo.utils.math import map_trait_offset
from ginkgo.ws.connection_manager import manager

logger = get_logger(__name__)


async def handle_init():
    if "unreal" in manager.active_connections:
        logger.info(
            "Initialization request received. Restoring inputs from database..."
        )
        records = db_service.get_all_thoughts(
            limit=settings.query_init_entry_limit,
            recent=True,
        )
        inputs = []
        for entry in records:
            if not entry.attribute_class:
                continue
            trait_offset = map_trait_offset(entry.trait) if entry.trait else 0.0
            inputs.append(
                GinkgoInput(
                    id=entry.id,
                    text=entry.text,
                    attribute=entry.attribute_class,
                    traitOffset=trait_offset,
                    traitEntailment=entry.trait_entailment,
                    scoreHealth=entry.score_health,
                    scoreSplit=entry.score_split,
                    scoreImpact=entry.score_impact,
                )
            )

        msg = GinkgoMessage(
            messageType=GinkgoMessageType.INIT,
            payloadJson=GinkgoInputList(entries=inputs),
        )
        await manager.send_to(msg.model_dump_json(), "unreal")
