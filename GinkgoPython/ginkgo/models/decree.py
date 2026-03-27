from sqlmodel import Field

from ginkgo.models.base import TextInput, TextInputBase
from ginkgo.models.enums import InputSource


class Decree(TextInputBase, table=True):
    __tablename__ = "decrees"

    id: int | None = Field(default=None, primary_key=True)

    def __repr__(self) -> str:
        return (
            "<Decree("
            f"id={self.id}, "
            f"text={self.text!r}, "
            f"lang={self.lang!r}, "
            f"source={self.source}, "
            f"created_at={self.created_at}, "
            f"modified_at={self.modified_at}"
            ")>"
        )


class DecreeCreate(TextInput):
    pass


class DecreeRead(TextInputBase):
    id: int


class DecreeUpdate(TextInput):
    text: str | None = None
    lang: str | None = None
    source: InputSource | None = None
