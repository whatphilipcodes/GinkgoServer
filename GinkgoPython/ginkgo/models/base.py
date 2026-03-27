from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from ginkgo.models.enums import InputSource


class TextInput(SQLModel):
    text: str
    lang: str
    source: InputSource


class Timestamped(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False,
    )


class TextInputBase(TextInput, Timestamped):
    pass
