from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from ginkgo.models.enums import InputLanguage, InputSource


class TextInputBase(SQLModel):
    text: str
    valid: bool = True
    lang: InputLanguage
    source: InputSource = InputSource.AUDIENCE
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False,
    )
