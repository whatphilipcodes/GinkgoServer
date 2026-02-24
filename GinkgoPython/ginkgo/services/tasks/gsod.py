from typing import Optional, Tuple
import json

from ginkgo.core.config import settings
from ginkgo.services.inspector import inspector_service
from ginkgo.services.tasks.base import BaseClassificationTask
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


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

        formatted_labels = "\n".join(
            [
                f"- {label}: {info.get('detail', '')}"
                for label, info in self.labels.items()
            ]
        )

        return f"""
            ### ROLE
            You are an expert statement classifier specializing in political science and governance metrics.

            ### TASK
            Match the concept discussed in the user input with exactly ONE of the labels below.
            - Classify based on the topic/concept, regardless of whether the sentiment is positive or negative.
            - If the input seems nonsensical/gibberish ie. not match any category, use the label: INVALID.

            ### CATEGORIES
            {formatted_labels}

            ### OUTPUT FORMAT
            Output ONLY the label name in plain text. Do not include quotes, prefixes, or explanations.
            """.strip()

    def infer(self, input_text: str) -> Tuple[Optional[str], Optional[str]]:
        self.ensure_inspector_initialized()
        
        """Run the inspection model on `input_text` and interpret the result."""
        prompt_text = (
            f"<bos><start_of_turn>developer\n{self.system_instruction}<end_of_turn>\n"
            f"<start_of_turn>user\nUser Input: {input_text}\n\nClassification:<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )

        raw_output = inspector_service.generate(prompt_text)
        logger.debug("GSOD raw model output: %s", raw_output)

        if not raw_output:
            logger.warning("empty output from model for GSOD input")
            return None, None

        prediction = raw_output.strip()
        trait = prediction
        if trait in self.labels:
            attribute_class = self.labels[trait].get("attribute")
            logger.info(
                "GSOD classification successful - Trait: %s, Attribute: %s",
                trait,
                attribute_class,
            )
            return trait, attribute_class
        elif trait == "INVALID":
            logger.info("GSOD input classified as INVALID")
            return trait, None

        logger.warning("GSOD prediction '%s' not found in labels", trait)
        return None, None


gsod_task = GSODTask()
