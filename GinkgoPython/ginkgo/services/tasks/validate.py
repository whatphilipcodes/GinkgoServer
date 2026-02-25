import json
from dataclasses import dataclass

import langcodes
from ginkgo.services.tasks.base import BaseClassificationTask
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidateResult:
    valid: bool
    language: str | None


class ValidateTask(BaseClassificationTask):
    """Used to validate inputs."""

    def __init__(self) -> None:
        super().__init__()

    def build_system_instruction(self) -> str:
        return self.load_task_md("validate.md")

    def infer(self, input_text: str) -> ValidateResult:
        """Run validation on input_text and return parsed JSON result.

        The `validate.md` file requires the model to return only a JSON
        object with `valid` and `language` keys; attempt to parse that JSON
        and fall back to a safe default if parsing fails or output is empty.
        """
        self.ensure_inspector_initialized()

        prompt_text = (
            f"<bos><start_of_turn>developer\n{self.system_instruction}<end_of_turn>\n"
            f"<start_of_turn>user\nUser Input: {input_text}\n\nResponse:<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )

        raw_output = self.inspector.generate(prompt_text)
        logger.debug("Validate raw model output: %s", raw_output)

        if not raw_output:
            logger.warning("empty output from model for validation input")
            return ValidateResult(False, None)

        candidate = raw_output.strip()
        try:
            parsed = json.loads(candidate)
            if not isinstance(parsed, dict):
                raise ValueError("parsed JSON is not an object")
            if "valid" not in parsed or "language" not in parsed:
                raise ValueError("missing required keys in parsed JSON")

            lang_val = parsed.get("language")
            language_code: str | None = None
            if lang_val:
                try:
                    found = langcodes.find(lang_val)
                    language_code = (found.language or str(lang_val)).lower()
                except Exception:
                    language_code = str(lang_val).lower()

            return ValidateResult(parsed.get("valid", False), language_code)
        except Exception:
            logger.warning("failed to parse JSON from model output; returning fallback")
            return ValidateResult(False, None)


validate_task = ValidateTask()
