import inspect
import json
import re
from pathlib import Path
from string import Template
from typing import Mapping, Type, TypeVar

from ginkgo.core.config import settings
from ginkgo.services.inspector import inspector_service
from ginkgo.utils.logger import get_logger
from pydantic import BaseModel, ValidationError

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseTask:
    def __init__(self, template_filename: str) -> None:
        self.inspector = inspector_service
        self.task_template = self._load_task_template(template_filename)

    def _load_task_template(self, md_filename: str) -> Template:
        md_path = Path(settings.data_dir, "tasks", md_filename)

        if not md_path.exists():
            raise RuntimeError(
                f"task description file [{md_filename}] not found: {md_path}"
            )

        content = md_path.read_text(encoding="utf-8").strip()

        if not content:
            raise RuntimeError(
                f"task description file [{md_filename}] is empty: {md_path}"
            )

        return Template(content)

    def create_prompt(
        self, template_substitutes: Mapping[str, object] | None = None
    ) -> str:
        if template_substitutes:
            instruction = self.task_template.safe_substitute(template_substitutes)
        else:
            instruction = self.task_template.template
        if not instruction:
            raise RuntimeError(
                "Prompt creation failed: No Instruction could be derived from task template."
            )
        prompt = inspect.cleandoc(
            f"<bos><start_of_turn>user\n{instruction.strip()}\n<end_of_turn>\n<start_of_turn>model"
        )
        logger.debug("Raw model input:\n%s", prompt)
        return prompt

    def infer(self, input_text: str):
        raise NotImplementedError()

    def ensure_inspector_initialized(self) -> None:
        if inspector_service.model is None or inspector_service.tokenizer is None:
            raise RuntimeError(
                "InspectorService not initialized; call initialize() on the inspector first."
            )

    @staticmethod
    def parse_result(model_type: Type[T], json_str: str) -> T | None:
        logger.debug(f"Attempting to parse: {json_str}")
        try:
            return model_type.model_validate_json(json_str)
        except (ValidationError, json.JSONDecodeError) as e:
            extracted = BaseTask.extract_json(json_str)
            if extracted and extracted != json_str:
                try:
                    return model_type.model_validate_json(extracted)
                except ValidationError as e2:
                    logger.warning(
                        f"--- JSON Validation Failed for {model_type.__name__} (after extraction) ---"
                    )
                    for error in e2.errors():
                        field_path = " -> ".join(str(p) for p in error["loc"])
                        error_msg = error["msg"]
                        input_provided = error.get("input", "N/A")

                        logger.warning(f"Field: [{field_path}]")
                        logger.warning(f"Error: {error_msg}")
                        logger.warning(f"Input Provided: {input_provided}")
                        logger.warning("-" * 30)
                except json.JSONDecodeError:
                    logger.warning("Error: Extracted content is not valid JSON syntax.")

            if isinstance(e, ValidationError):
                logger.warning(
                    f"--- JSON Validation Failed for {model_type.__name__} ---"
                )
                for error in e.errors():
                    field_path = " -> ".join(str(p) for p in error["loc"])
                    error_msg = error["msg"]
                    input_provided = error.get("input", "N/A")

                    logger.warning(f"Field: [{field_path}]")
                    logger.warning(f"Error: {error_msg}")
                    logger.warning(f"Input Provided: {input_provided}")
                    logger.warning("-" * 30)
            else:
                logger.warning("Error: The provided string is not valid JSON syntax.")

        return None

    @staticmethod
    def extract_json(invalid_json: str) -> str:
        match = re.search(r"\{.*\}", invalid_json, flags=re.DOTALL)
        if match:
            return match.group(0)
        return invalid_json

    @staticmethod
    def format_list(items: list[str]) -> str:
        """Convert a sequence of strings into a markdown-style bullet list."""
        if not items:
            raise RuntimeError(
                "Parameter input to format_list did not match expected type"
            )
        return "\n".join(f"- {s}" for s in items)
