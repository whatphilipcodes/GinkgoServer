from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class FilterResult(BaseModel):
    valid: bool


class FilterTask(BaseTask):
    def __init__(self) -> None:
        super().__init__("filter.md")

    def infer(self, input_user: str, input_prompt: str | None = None) -> FilterResult:
        self.ensure_inspector_initialized()

        prompt = self.create_prompt({"input_user": input_user})
        result = self.parse_result(FilterResult, self.inspector.generate(prompt))

        if not result:
            raise RuntimeError("Model did not return interpretable result")

        logger.info("FilterTask successful: %s", result)
        return result


filter_task = FilterTask()
