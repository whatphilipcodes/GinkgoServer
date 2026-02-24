from ginkgo.core.config import settings
from ginkgo.services.inspector import inspector_service
from ginkgo.services.tasks.base import BaseClassificationTask
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


class ValidateTask(BaseClassificationTask):
    """Used to validate inputs
    """

    def __init__(self):
        super().__init__()

    def build_system_instruction(self) -> str:
        return ""

    def infer(self, input_text: str) -> bool:
        return False


Validate_task = ValidateTask()
