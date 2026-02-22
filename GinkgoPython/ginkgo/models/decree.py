from typing import Optional

from sqlmodel import Field

from ginkgo.models.base import TextInputBase


class DecreeBase(TextInputBase):
    pass


class Decree(DecreeBase, table=True):
    __tablename__ = "decrees"

    id: Optional[int] = Field(default=None, primary_key=True)

    def __repr__(self) -> str:
        return f"<Decree(id={self.id}, created_at={self.created_at})>"


class DecreeCreate(DecreeBase):
    pass


class DecreeRead(DecreeBase):
    id: int
