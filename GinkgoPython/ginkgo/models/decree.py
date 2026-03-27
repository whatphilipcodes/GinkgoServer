from sqlmodel import Field

from ginkgo.models.base import TextInput, TextInputBase
from ginkgo.models.enums import InputSource


class DecreeCreate(TextInput):
    pass


class Decree(TextInputBase, table=True):
    __tablename__ = "decrees"
    id: int | None = Field(default=None, primary_key=True)


class DecreeRead(TextInputBase):
    id: int


class DecreeUpdate(TextInput):
    text: str | None = None
    lang: str | None = None
    source: InputSource | None = None
