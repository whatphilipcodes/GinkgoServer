from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class HealthResult(BaseModel):
    trait: float


class HealthTask(BaseTask):
    def __init__(self):
        super().__init__("health.md")

    def infer(self, input_text: str):
        self.ensure_inspector_initialized()
        prompt = self.create_prompt()
        raw_output = self.inspector.generate(prompt)
        logger.debug("Health output:\n%s", raw_output)
