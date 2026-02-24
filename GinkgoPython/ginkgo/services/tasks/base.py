from ginkgo.services.inspector import inspector_service


class BaseClassificationTask:
    """Template skeleton for inference tasks.
    """

    def __init__(self) -> None:
        self.ensure_inspector_initialized()
        self.system_instruction = self.build_system_instruction()

    def build_system_instruction(self) -> str:
        raise NotImplementedError()

    def infer(self, input_text: str):
        raise NotImplementedError()

    def ensure_inspector_initialized(self) -> None:
        if inspector_service.model is None or inspector_service.tokenizer is None:
            raise RuntimeError(
                "InspectorService not initialized; call initialize() on the inspector first."
            )
