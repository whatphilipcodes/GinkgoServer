import json
from dataclasses import dataclass

from ginkgo.core.config import settings
from ginkgo.models.enums import GSODAttribute, GSODTrait
from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GSODResult:
    trait: GSODTrait | None
    attribute: GSODAttribute | None


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

    def infer(self, input_text: str) -> GSODResult:
        self.ensure_inspector_initialized()

        prompt = self.create_prompt({"input_text": input_text})
        raw_output = self.inspector.generate(prompt)
        logger.debug("GSOD raw model output:\n%s", raw_output)

        if not raw_output:
            logger.warning("empty output from model for GSOD input")
            return GSODResult(trait=None, attribute=None)

        prediction = raw_output.strip()

        token = prediction.split()[0].strip().upper().replace(" ", "_")
        if token == "NONE":
            logger.info("GSOD input classified as NONE")
            return GSODResult(None, None)

        trait_enum: GSODTrait | None = None
        try:
            trait_enum = GSODTrait[token]
        except Exception:
            try:
                trait_enum = GSODTrait(token)
            except Exception:
                logger.warning(
                    "GSOD prediction '%s' not found in GSODTrait", prediction
                )
                return GSODResult(None, None)

        attribute_enum: GSODAttribute | None = None
        label_entry = self.labels.get(trait_enum.value)
        if label_entry:
            attr_str = label_entry.get("attribute")
            if attr_str:
                try:
                    attribute_enum = GSODAttribute[attr_str]
                except Exception:
                    try:
                        attribute_enum = GSODAttribute(attr_str)
                    except Exception:
                        logger.warning(
                            "GSOD attribute '%s' not found in GSODAttribute", attr_str
                        )

        logger.info(
            "GSOD classification successful - Trait: %s, Attribute: %s",
            trait_enum.value,
            attribute_enum.value if attribute_enum else None,
        )
        return GSODResult(trait_enum, attribute_enum)


gsod_task = GSODTask()
