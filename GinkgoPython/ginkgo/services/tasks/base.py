import inspect
from pathlib import Path
from string import Template
from typing import Mapping

from ginkgo.core.config import settings
from ginkgo.services.inspector import inspector_service
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


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

    def create_prompt(self, template_substitutes: Mapping[str, object]) -> str:
        instruction = self.task_template.safe_substitute(template_substitutes)
        prompt = inspect.cleandoc(
            f"<bos><start_of_turn>user\n{instruction.strip()}\n<end_of_turn>\n<start_of_turn>model"
        )
        logger.critical("Raw model input:\n%s", prompt)  # debug
        return prompt

    def infer(self, input_text: str):
        raise NotImplementedError()

    def ensure_inspector_initialized(self) -> None:
        if inspector_service.model is None or inspector_service.tokenizer is None:
            raise RuntimeError(
                "InspectorService not initialized; call initialize() on the inspector first."
            )
