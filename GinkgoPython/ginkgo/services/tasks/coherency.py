from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class CoherencyResult(BaseModel):
    coherent: bool


class CoherencyTask(BaseTask):
    def __init__(self) -> None:
        super().__init__("coherency.md")

    def infer(self, input_user: str, input_prompt: str) -> CoherencyResult:
        self.ensure_inspector_initialized()

        prompt = self.create_prompt(
            {"input_prompt": input_prompt, "input_user": input_user}
        )
        result = self.parse_result(CoherencyResult, self.inspector.generate(prompt))

        if not result:
            raise RuntimeError("Model did not return interpretable result")

        logger.info("CoherencyTask successful: %s", result)
        return result


coherency_task = CoherencyTask()
