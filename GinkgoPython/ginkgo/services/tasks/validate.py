from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class ValidateResult(BaseModel):
    valid: bool
    language: str | None


class ValidateTask(BaseTask):
    def __init__(self) -> None:
        super().__init__("validate.md")

    def infer(self, input_text: str) -> ValidateResult:
        self.ensure_inspector_initialized()

        prompt = self.create_prompt({"input_text": input_text})
        result = self.parse_result(ValidateResult, self.inspector.generate(prompt))

        if not result:
            raise RuntimeError("Model did not return interpretable result")

        logger.info("ValidationTask successful: %s", result)
        return result


validate_task = ValidateTask()
