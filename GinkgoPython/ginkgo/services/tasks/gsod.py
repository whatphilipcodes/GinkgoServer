from typing import Optional, Tuple

from ginkgo.services.inspector import inspector_service
from ginkgo.services.tasks.base import BaseClassificationTask
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


class GSODTask(BaseClassificationTask):
    """Encapsulates the GSOD classification task."""

    def __init__(self):
        super().__init__(labels_filename="labels.json")

    def build_system_instruction(self) -> str:
        # override to provide the full instruction, inserting the base class
        # generated category list.
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

    def classify(self, input_text: str) -> Tuple[Optional[str], Optional[str]]:
        """Run the inspection model on `input_text` and interpret the result.

        Returns a tuple ``(trait, attribute)`` where either element may be ``None``
        if the model failed to produce a valid label.
        """
        if inspector_service.model is None or inspector_service.tokenizer is None:
            raise RuntimeError(
                "InspectorService not initialized; call initialize() first."
            )

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


# module-level singleton used by the rest of the codebase
gsod_task = GSODTask()
