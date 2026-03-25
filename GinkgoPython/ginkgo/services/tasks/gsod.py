import json

from ginkgo.core.config import settings
from ginkgo.models.enums import GSODAttribute, GSODTrait
from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class GSODResult(BaseModel):
    trait: GSODTrait | None
    entailment: float
    attribute: GSODAttribute | None


class GSODModelOutput(BaseModel):
    trait: str
    entailment: float


class GSODTask(BaseTask):
    def __init__(self):
        self.labels = {}
        try:
            self._load_labels("gsod_labels.json")
        except Exception as e:
            logger.warning("unable to load GSOD labels at import: %s", e)
        super().__init__("gsod.md")

    def _load_labels(self, filename: str) -> None:
        labels_path = settings.data_dir / filename
        if not labels_path.exists():
            raise RuntimeError(f"Labels file not found: {labels_path}")

        with open(labels_path, "r", encoding="utf-8") as f:
            self.labels = json.load(f)

    def infer(self, input_user: str, input_prompt: str) -> GSODResult:
        self.ensure_inspector_initialized()

        prompt = self.create_prompt(
            {"input_prompt": input_prompt, "input_user": input_user}
        )
        intermediate = self.parse_result(
            GSODModelOutput, self.inspector.generate(prompt)
        )

        result = GSODResult(trait=None, entailment=0.0, attribute=None)

        if not intermediate:
            return result

        try:
            trait_value = GSODTrait[intermediate.trait]
        except KeyError:
            trait_value = None

        label_entry = self.labels.get(intermediate.trait)

        attribute_value = (
            label_entry.get("attribute")
            if isinstance(label_entry, dict)
            else getattr(label_entry, "attribute", None)
        )

        result = GSODResult(
            trait=trait_value,
            entailment=intermediate.entailment,
            attribute=attribute_value,
        )

        logger.info("GSODTask successful: %s", result)
        return result


gsod_task = GSODTask()
