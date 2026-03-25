from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger
from ginkgo.utils.msc import validate_iso_639_3
from pydantic import BaseModel

logger = get_logger(__name__)


class AugmentResult(BaseModel):
    language: str


class AugmentTask(BaseTask):
    def __init__(self) -> None:
        super().__init__("augment.md")

    def infer(self, input_user: str, input_prompt: str | None = None) -> AugmentResult:
        self.ensure_inspector_initialized()

        prompt = self.create_prompt({"input_user": input_user})
        result = self.parse_result(AugmentResult, self.inspector.generate(prompt))

        if not result:
            raise RuntimeError("Model did not return interpretable result")

        result.language = validate_iso_639_3(result.language)

        logger.info("AugmentTask successful: %s", result)
        return result


augment_task = AugmentTask()
