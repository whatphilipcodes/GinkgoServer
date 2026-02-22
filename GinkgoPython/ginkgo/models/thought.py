from typing import Optional

from sqlmodel import Field

from ginkgo.models.base import GSODAttribute, GSODTrait, TextInputBase


class ThoughtBase(TextInputBase):
    attribute_class: Optional[GSODAttribute] = None
    trait: Optional[GSODTrait] = None


class Thought(ThoughtBase, table=True):
    __tablename__ = "thoughts"

    id: Optional[int] = Field(default=None, primary_key=True)
    trait_offset: float = Field(default=0.0, ge=0.0, le=1.0)
    trait_entailment: float = Field(default=0.0, ge=0.0, le=1.0)
    score_health: float = Field(default=0.0, ge=0.0, le=1.0)
    score_split: float = Field(default=0.0, ge=0.0, le=1.0)
    score_impact: float = Field(default=0.0, ge=0.0, le=1.0)

    def __repr__(self) -> str:
        return (
            f"<Thought(id={self.id}, trait={self.trait}, created_at={self.created_at})>"
        )


class ThoughtCreate(ThoughtBase):
    pass


class ThoughtRead(ThoughtBase):
    id: int
    trait_offset: float = 0.0
    trait_entailment: float = 0.0
    score_health: float = 0.0
    score_split: float = 0.0
    score_impact: float = 0.0
