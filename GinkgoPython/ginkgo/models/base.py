from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from ginkgo.models.enums import InputSource


class TextInputBase(SQLModel):
    text: str
    valid: bool = True
    lang: str | None = None
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
