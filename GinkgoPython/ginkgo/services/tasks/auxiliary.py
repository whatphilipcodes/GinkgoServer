from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class AuxiliaryResult(BaseModel):
    split: float
    impact: float


class AuxiliaryTask(BaseTask):
    def __init__(self):
        super().__init__("auxiliary.md")

    def infer(self, input_text: str) -> AuxiliaryResult:
        self.ensure_inspector_initialized()

        prompt = self.create_prompt({"input_text": input_text})
        result = self.parse_result(AuxiliaryResult, self.inspector.generate(prompt))

        if not result:
            raise RuntimeError("Model did not return interpretable result")

        logger.info("AuxiliaryTask successful: %s", result)
        return result


aux_task = AuxiliaryTask()
