from sqlmodel import Field

from ginkgo.models.base import TextInputBase
from ginkgo.models.enums import GSODAttribute, GSODTrait


class ThoughtBase(TextInputBase):
    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None


class Thought(ThoughtBase, table=True):
    __tablename__ = "thoughts"

    id: int | None = Field(default=None, primary_key=True)
    trait_entailment: float = Field(default=0.0, ge=0.0, le=1.0)
    score_health: float = Field(default=0.0, ge=0.0, le=1.0)
    score_split: float = Field(default=0.0, ge=0.0, le=1.0)
    score_impact: float = Field(default=0.0, ge=0.0, le=1.0)

    def __repr__(self) -> str:
        return (
            f"<Thought(id={self.id}, trait={self.trait}, created_at={self.created_at})>"
        )


class ThoughtCreate(ThoughtBase):
    trait_entailment: float = 0.0
    score_health: float = 0.0
    score_split: float = 0.0
    score_impact: float = 0.0


class ThoughtRead(ThoughtBase):
    id: int
    trait_entailment: float = 0.0
    score_health: float = 0.0
    score_split: float = 0.0
    score_impact: float = 0.0
