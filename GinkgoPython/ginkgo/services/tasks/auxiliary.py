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

    def infer(self, input_text: str):
        self.ensure_inspector_initialized()
        prompt = self.create_prompt()
        raw_output = self.inspector.generate(prompt)
        logger.debug("Auxiliary output:\n%s", raw_output)
