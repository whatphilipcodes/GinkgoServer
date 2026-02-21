from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from ginkgo.schemas.frontend import InputLanguage, InputSource, InputType


class InputRecordBase(SQLModel):
    """Base schema for user inputs"""

    text: str
    type: InputType
    lang: InputLanguage
    source: InputSource = InputSource.AUDIENCE
    attribute_class: str | None = None
    trait: str | None = None


class InputRecordCreate(InputRecordBase):
    """Schema for creating new InputRecords"""

    pass


class InputRecordRead(InputRecordBase):
    """Schema for reading InputRecords from database."""

    id: int
    created_at: datetime
    updated_at: datetime


class InputRecord(InputRecordBase, table=True):
    """Database table model for user inputs made to Ginkgo installation via the frontend"""

    __tablename__ = "user_inputs"

    id: int | None = Field(default=None, primary_key=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<InputRecord(id={self.id}, type={self.type}, created_at={self.created_at})>"
