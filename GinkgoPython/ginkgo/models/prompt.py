from sqlmodel import Field

from ginkgo.models.base import TextInputBase


class PromptBase(TextInputBase):
    pass


class Prompt(PromptBase, table=True):
    __tablename__ = "prompts"

    id: int | None = Field(default=None, primary_key=True)

    def __repr__(self) -> str:
        return f"<Prompt(id={self.id}, created_at={self.created_at})>"


class PromptCreate(PromptBase):
    pass


class PromptRead(PromptBase):
    id: int
