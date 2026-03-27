from ginkgo.core.config import settings
from ginkgo.schemas.unreal import (
    GinkgoInput,
    GinkgoInputList,
    GinkgoMessage,
    GinkgoMessageType,
)
from ginkgo.services.database import db_service
from ginkgo.utils.logger import get_logger
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
            inputs.append(GinkgoInput.from_thought(entry))

        msg = GinkgoMessage(
            messageType=GinkgoMessageType.INIT,
            payloadJson=GinkgoInputList(entries=inputs),
        )
        await manager.send_to(msg.model_dump_json(), "unreal")
