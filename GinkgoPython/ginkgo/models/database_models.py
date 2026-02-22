from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from ginkgo.schemas.frontend import InputLanguage, InputSource


# —— Base class for all input types ——————————————————————————
class InputBase(SQLModel):
    """Base schema for user inputs"""

    text: str
    lang: InputLanguage
    source: InputSource = InputSource.AUDIENCE
    attribute_class: str | None = None
    trait: str | None = None


# —— Thought models ——————————————————————————————————————————
class ThoughtCreate(InputBase):
    """Schema for creating new Thoughts"""

    pass


class ThoughtRead(InputBase):
    """Schema for reading Thoughts from database."""

    id: int
    created_at: datetime
    updated_at: datetime


class Thought(InputBase, table=True):
    """Database table model for thoughts"""

    __tablename__ = "thoughts"

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
        return f"<Thought(id={self.id}, created_at={self.created_at})>"


# —— Prompt models ———————————————————————————————————————————
class PromptCreate(InputBase):
    """Schema for creating new Prompts"""

    pass


class PromptRead(InputBase):
    """Schema for reading Prompts from database."""

    id: int
    created_at: datetime
    updated_at: datetime


class Prompt(InputBase, table=True):
    """Database table model for prompts"""

    __tablename__ = "prompts"

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
        return f"<Prompt(id={self.id}, created_at={self.created_at})>"


# —— Decree models ———————————————————————————————————————————
class DecreeCreate(InputBase):
    """Schema for creating new Decrees"""

    pass


class DecreeRead(InputBase):
    """Schema for reading Decrees from database."""

    id: int
    created_at: datetime
    updated_at: datetime


class Decree(InputBase, table=True):
    """Database table model for decrees"""

    __tablename__ = "decrees"

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
        return f"<Decree(id={self.id}, created_at={self.created_at})>"
