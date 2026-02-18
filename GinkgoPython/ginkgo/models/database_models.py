from datetime import datetime, timezone

from sqlmodel import Field

from ginkgo.schemas.frontend import Input


class InputRecord(Input, table=True):
    """Database model for user inputs with automatic timestamps

    Inherits text and type fields from Input schema.
    Adds id and timestamp fields for persistence.
    """

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
