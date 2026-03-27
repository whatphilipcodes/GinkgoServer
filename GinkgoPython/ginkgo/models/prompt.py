from sqlmodel import Field

from ginkgo.models.base import TextInput, TextInputBase
from ginkgo.models.enums import InputSource


class Prompt(TextInputBase, table=True):
    __tablename__ = "prompts"

    id: int | None = Field(default=None, primary_key=True)

    def __repr__(self) -> str:
        return (
            "<Prompt("
            f"id={self.id}, "
            f"text={self.text!r}, "
            f"lang={self.lang!r}, "
            f"source={self.source}, "
            f"created_at={self.created_at}, "
            f"modified_at={self.modified_at}"
            ")>"
        )


class PromptCreate(TextInput):
    pass


class PromptRead(TextInputBase):
    id: int


class PromptUpdate(TextInput):
    text: str | None = None
    lang: str | None = None
    source: InputSource | None = None
