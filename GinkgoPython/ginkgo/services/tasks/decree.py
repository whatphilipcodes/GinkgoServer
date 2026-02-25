from ginkgo.core.config import settings
from ginkgo.models.decree import Decree
from ginkgo.services.database import db_service
from ginkgo.services.tasks.base import BaseTask
from ginkgo.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class DecreeResult(BaseModel):
    alignment: float


class DecreeTask(BaseTask):
    def __init__(self):
        super().__init__("health.md")

    def infer(self, input_text: str) -> DecreeResult:
        self.ensure_inspector_initialized()
        limit = settings.decree_eval_limit

        with db_service.get_session() as session:
            from sqlalchemy import func
            from sqlmodel import select

            stmt = select(Decree).order_by(func.random()).limit(limit)
            records = session.exec(stmt).all()

        decrees = [rec.text for rec in records]

        if len(decrees) < 1:
            raise RuntimeError("No decrees found in database!")

        prompt = self.create_prompt(
            {"decrees": self.format_list(decrees), "input_text": input_text}
        )
        result = self.parse_result(DecreeResult, self.inspector.generate(prompt))

        if not result:
            raise RuntimeError("Model did not return interpretable result")

        logger.info("DecreeTask successful: %s", result)
        return result


decree_task = DecreeTask()
