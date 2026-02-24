from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

from ginkgo.core.config import settings
from ginkgo.services.inspector import inspector_service
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


class BaseClassificationTask:
    """Shared logic for classification-style tasks.

    Subclasses are expected to supply a ``build_system_instruction`` method that
    returns the task-specific prompt text (the portion after "ROLE/TASK/..." in
    the old implementation).  The base class handles label loading and the
    generic `classify` implementation that calls into the shared model.
    """

    def __init__(self, labels_filename: str):
        self.labels: Dict[str, Any] = {}
        self.system_instruction: str = ""
        self._load_labels(labels_filename)
        self.system_instruction = self.build_system_instruction()

    def _load_labels(self, filename: str) -> None:
        labels_path = settings.data_dir / filename
        if not labels_path.exists():
            raise RuntimeError(f"Labels file not found: {labels_path}")

        with open(labels_path, "r") as f:
            self.labels = json.load(f)

    def build_system_instruction(self) -> str:
        """Return the full system instruction string for the task.

        The default helper simply enumerates the labels; subclasses should override
        to provide role/task context and any task-specific rules.
        """
        formatted = "\n".join(
            [
                f"- {label}: {info.get('detail', '')}"
                for label, info in self.labels.items()
            ]
        )
        return formatted

    def classify(self, input_text: str) -> Tuple[Optional[str], Optional[str]]:
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
        logger.debug("raw model output: %s", raw_output)

        if not raw_output:
            return None, None

        prediction = raw_output.strip()
        if prediction in self.labels:
            attribute = self.labels[prediction].get("attribute")
            return prediction, attribute
        elif prediction == "INVALID":
            return prediction, None

        logger.warning("Prediction '%s' not found in labels", prediction)
        return None, None
