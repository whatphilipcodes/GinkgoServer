from sqlmodel import Field

from ginkgo.models.base import TextInput, TextInputBase
from ginkgo.models.enums import InputSource


class PromptCreate(TextInput):
    pass


class Prompt(TextInputBase, table=True):
    __tablename__ = "prompts"
    id: int | None = Field(default=None, primary_key=True)


class PromptRead(TextInputBase):
    id: int


class PromptUpdate(TextInput):
    text: str | None = None
    lang: str | None = None
    source: InputSource | None = None
