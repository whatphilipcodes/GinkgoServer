import json
from dataclasses import dataclass

import langcodes
from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidateResult:
    valid: bool
    language: str | None


class ValidateTask(BaseTask):
    def __init__(self) -> None:
        super().__init__("validate.md")

    def infer(self, input_text: str) -> ValidateResult:
        self.ensure_inspector_initialized()

        prompt = self.create_prompt({"input_text": input_text})
        raw_output = self.inspector.generate(prompt)
        logger.debug("Validate raw model output:\n%s", raw_output)

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
            result = ValidateResult(parsed.get("valid", False), language_code)
            logger.info(
                "Validation successful - valid: %s, language: %s",
                result.valid,
                result.language,
            )
            return result
        except Exception:
            logger.warning("failed to parse JSON from model output; returning fallback")
            return ValidateResult(False, None)


validate_task = ValidateTask()
