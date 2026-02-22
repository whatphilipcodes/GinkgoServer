from sqlmodel import Session, create_engine

from ginkgo.core.config import settings
from ginkgo.models.decree import Decree, DecreeCreate, DecreeRead
from ginkgo.models.prompt import Prompt, PromptCreate, PromptRead
from ginkgo.models.thought import Thought, ThoughtCreate, ThoughtRead
from ginkgo.services.crud import BaseCRUD


class DatabaseService:
    def __init__(self):
        self.engine = create_engine(
            f"sqlite:///{settings.database_path}",
            echo=settings.database_echo,
        )

        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        return Session(self.engine)

    def _get_crud(self, model_class, create_schema, read_schema):
        session = self.get_session()
        return BaseCRUD(model_class, create_schema, read_schema, session)

    def get_thought_crud(self) -> BaseCRUD[Thought, ThoughtCreate, ThoughtRead]:
        return self._get_crud(Thought, ThoughtCreate, ThoughtRead)

    def get_prompt_crud(self) -> BaseCRUD[Prompt, PromptCreate, PromptRead]:
        return self._get_crud(Prompt, PromptCreate, PromptRead)

    def get_decree_crud(self) -> BaseCRUD[Decree, DecreeCreate, DecreeRead]:
        return self._get_crud(Decree, DecreeCreate, DecreeRead)

    def add_thought(
        self,
        text: str,
        lang,
        source=None,
        valid: bool = True,
        attribute_class=None,
        trait=None,
    ) -> ThoughtRead:
        from ginkgo.models.enums import InputSource

        if source is None:
            source = InputSource.AUDIENCE
        create_obj = ThoughtCreate(
            text=text,
            lang=lang,
            source=source,
            valid=valid,
            attribute_class=attribute_class,
            trait=trait,
        )
        crud = self.get_thought_crud()
        result = crud.add(create_obj)
        crud.session.close()
        return result

    def get_thought_by_id(self, record_id: int) -> ThoughtRead | None:
        crud = self.get_thought_crud()
        result = crud.get_by_id(record_id)
        crud.session.close()
        return result

    def get_all_thoughts(
        self, limit: int | None = None, offset: int = 0
    ) -> list[ThoughtRead]:
        crud = self.get_thought_crud()
        result = crud.get_all(limit=limit, offset=offset)
        crud.session.close()
        return result

    def get_recent_thoughts(self, hours: int = 24) -> list[ThoughtRead]:
        crud = self.get_thought_crud()
        result = crud.get_recent(hours=hours)
        crud.session.close()
        return result

    def update_thought(
        self,
        record_id: int,
        new_text: str,
        valid: bool | None = None,
        attribute_class=None,
        trait=None,
        trait_offset: float | None = None,
        trait_entailment: float | None = None,
        score_health: float | None = None,
        score_split: float | None = None,
        score_impact: float | None = None,
    ) -> ThoughtRead | None:
        update_data = {
            "text": new_text,
            "valid": valid,
            "attribute_class": attribute_class,
            "trait": trait,
            "trait_offset": trait_offset,
            "trait_entailment": trait_entailment,
            "score_health": score_health,
            "score_split": score_split,
            "score_impact": score_impact,
        }
        crud = self.get_thought_crud()
        result = crud.update(record_id, update_data)
        crud.session.close()
        return result

    def delete_thought(self, record_id: int) -> bool:
        crud = self.get_thought_crud()
        result = crud.delete(record_id)
        crud.session.close()
        return result

    def count_thoughts(self) -> int:
        crud = self.get_thought_crud()
        result = crud.count()
        crud.session.close()
        return result

    def get_thoughts_by_source(self, source) -> list[ThoughtRead]:
        crud = self.get_thought_crud()
        result = crud.get_by_field("source", source)
        crud.session.close()
        return result

    def add_prompt(
        self,
        text: str,
        lang,
        source=None,
        valid: bool = True,
    ) -> PromptRead:
        from ginkgo.models.enums import InputSource

        if source is None:
            source = InputSource.AUDIENCE
        create_obj = PromptCreate(
            text=text,
            lang=lang,
            source=source,
            valid=valid,
        )
        crud = self.get_prompt_crud()
        result = crud.add(create_obj)
        crud.session.close()
        return result

    def get_prompt_by_id(self, record_id: int) -> PromptRead | None:
        crud = self.get_prompt_crud()
        result = crud.get_by_id(record_id)
        crud.session.close()
        return result

    def get_all_prompts(
        self, limit: int | None = None, offset: int = 0
    ) -> list[PromptRead]:
        crud = self.get_prompt_crud()
        result = crud.get_all(limit=limit, offset=offset)
        crud.session.close()
        return result

    def get_recent_prompts(self, hours: int = 24) -> list[PromptRead]:
        crud = self.get_prompt_crud()
        result = crud.get_recent(hours=hours)
        crud.session.close()
        return result

    def update_prompt(
        self,
        record_id: int,
        new_text: str,
        valid: bool | None = None,
    ) -> PromptRead | None:
        update_data = {
            "text": new_text,
            "valid": valid,
        }
        crud = self.get_prompt_crud()
        result = crud.update(record_id, update_data)
        crud.session.close()
        return result

    def delete_prompt(self, record_id: int) -> bool:
        crud = self.get_prompt_crud()
        result = crud.delete(record_id)
        crud.session.close()
        return result

    def count_prompts(self) -> int:
        crud = self.get_prompt_crud()
        result = crud.count()
        crud.session.close()
        return result

    def get_prompts_by_source(self, source) -> list[PromptRead]:
        crud = self.get_prompt_crud()
        result = crud.get_by_field("source", source)
        crud.session.close()
        return result

    def add_decree(
        self,
        text: str,
        lang,
        source=None,
        valid: bool = True,
    ) -> DecreeRead:
        from ginkgo.models.enums import InputSource

        if source is None:
            source = InputSource.AUDIENCE
        create_obj = DecreeCreate(
            text=text,
            lang=lang,
            source=source,
            valid=valid,
        )
        crud = self.get_decree_crud()
        result = crud.add(create_obj)
        crud.session.close()
        return result

    def get_decree_by_id(self, record_id: int) -> DecreeRead | None:
        crud = self.get_decree_crud()
        result = crud.get_by_id(record_id)
        crud.session.close()
        return result

    def get_all_decrees(
        self, limit: int | None = None, offset: int = 0
    ) -> list[DecreeRead]:
        crud = self.get_decree_crud()
        result = crud.get_all(limit=limit, offset=offset)
        crud.session.close()
        return result

    def get_recent_decrees(self, hours: int = 24) -> list[DecreeRead]:
        crud = self.get_decree_crud()
        result = crud.get_recent(hours=hours)
        crud.session.close()
        return result

    def update_decree(
        self,
        record_id: int,
        new_text: str,
        valid: bool | None = None,
    ) -> DecreeRead | None:
        update_data = {
            "text": new_text,
            "valid": valid,
        }
        crud = self.get_decree_crud()
        result = crud.update(record_id, update_data)
        crud.session.close()
        return result

    def delete_decree(self, record_id: int) -> bool:
        crud = self.get_decree_crud()
        result = crud.delete(record_id)
        crud.session.close()
        return result

    def count_decrees(self) -> int:
        crud = self.get_decree_crud()
        result = crud.count()
        crud.session.close()
        return result

    def get_decrees_by_source(self, source) -> list[DecreeRead]:
        crud = self.get_decree_crud()
        result = crud.get_by_field("source", source)
        crud.session.close()
        return result


db_service = DatabaseService()
