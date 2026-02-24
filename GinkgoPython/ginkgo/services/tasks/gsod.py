import json
from dataclasses import dataclass
from typing import Optional

from ginkgo.core.config import settings
from ginkgo.models.enums import GSODAttribute, GSODTrait
from ginkgo.services.tasks.base import BaseClassificationTask
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GSODResult:
    trait: Optional[GSODTrait]
    attribute: Optional[GSODAttribute]


class GSODTask(BaseClassificationTask):
    """Encapsulates the GSOD classification task."""

    def __init__(self):
        self.labels = {}
        try:
            self._load_labels("gsod_labels.json")
        except Exception as e:
            logger.warning("unable to load GSOD labels at import: %s", e)
        super().__init__()

    def _load_labels(self, filename: str) -> None:
        labels_path = settings.data_dir / filename
        if not labels_path.exists():
            raise RuntimeError(f"Labels file not found: {labels_path}")

        with open(labels_path, "r", encoding="utf-8") as f:
            self.labels = json.load(f)

    def build_system_instruction(self) -> str:
        return self.load_task_md("gsod.md")

    def infer(self, input_text: str) -> GSODResult:
        """Run GSOD analysis on `input_text`"""

        self.ensure_inspector_initialized()

        prompt_text = (
            f"<bos><start_of_turn>developer\n{self.system_instruction}<end_of_turn>\n"
            f"<start_of_turn>user\nUser Input: {input_text}\n\nClassification:<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )

        raw_output = self.inspector.generate(prompt_text)
        logger.debug("GSOD raw model output: %s", raw_output)

        if not raw_output:
            logger.warning("empty output from model for GSOD input")
            return GSODResult(trait=None, attribute=None)

        prediction = raw_output.strip()

        # Normalize prediction token and handle explicit NONE
        token = prediction.split()[0].strip().upper().replace(" ", "_")
        if token == "NONE":
            logger.info("GSOD input classified as NONE")
            return GSODResult(None, None)

        # Try to convert model output to GSODTrait
        trait_enum: Optional[GSODTrait] = None
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

        # Lookup attribute from labels (if available) and validate against GSODAttribute
        attribute_enum: Optional[GSODAttribute] = None
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
