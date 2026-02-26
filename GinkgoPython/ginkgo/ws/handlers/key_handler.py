from typing import Any

from ginkgo.core.config import settings
from ginkgo.models.enums import GinkgoMessageType
from ginkgo.schemas.unreal import GinkgoKeystroke, GinkgoMessage
from ginkgo.utils.logger import get_logger
from ginkgo.ws.commands import SendKeystrokeCommand
from ginkgo.ws.connection_manager import manager

logger = get_logger(__name__)


async def handle_keystroke(cmd: SendKeystrokeCommand) -> dict[str, Any]:
    """Forward keystrokes to Unreal when enabled."""

    keystroke = GinkgoKeystroke(key=cmd.key, context=cmd.context)
    forwarded = False

    if settings.send_keystrokes and "unreal" in manager.active_connections:
        message = GinkgoMessage(
            messageType=GinkgoMessageType.KEYSTROKE,
            payloadJson=keystroke,
        )
        await manager.send_to(message.model_dump_json(), "unreal")
        forwarded = True
    else:
        if not settings.send_keystrokes:
            logger.info("Keystroke forwarding disabled via settings.send_keystrokes")
        elif "unreal" not in manager.active_connections:
            logger.info("Keystroke not forwarded; no active 'unreal' websocket")

    return {
        "status": "success",
        "action": "send",
        "type": "keystroke",
        "forwarded": forwarded,
    }
