from dataclasses import dataclass

from ginkgo.services.tasks.base import BaseClassificationTask


@dataclass
class HealthResult:
    trait: float


class HealthTask(BaseClassificationTask):
    def __init__(self):
        super().__init__()

    def build_system_instruction(self) -> str:
        return ""

    def infer(self, input_text: str):
        pass
