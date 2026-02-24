from pathlib import Path

from ginkgo.core.config import settings
from ginkgo.services.inspector import inspector_service
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


class BaseClassificationTask:
    """Template skeleton for inference tasks."""

    def __init__(self) -> None:
        self.inspector = inspector_service
        self.system_instruction = self.build_system_instruction()

    def build_system_instruction(self) -> str:
        """Return the system instruction string for this task.

        Subclasses must override this method and return the text of the
        system instruction (typically loaded from a markdown file).
        """
        raise NotImplementedError(
            "Subclasses must implement build_system_instruction() and return the instruction string"
        )

    def load_task_md(self, md_filename: str) -> str:
        """Load and return the contents of a markdown task file.

        Files are expected under `settings.data_dir / 'tasks' / md_filename`.
        Raises RuntimeError if the file does not exist or is empty.
        """
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

        return content

    def infer(self, input_text: str):
        raise NotImplementedError()

    def ensure_inspector_initialized(self) -> None:
        if inspector_service.model is None or inspector_service.tokenizer is None:
            raise RuntimeError(
                "InspectorService not initialized; call initialize() on the inspector first."
            )
