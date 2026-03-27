from sqlmodel import Field, SQLModel

from ginkgo.models.base import TextInput, TextInputBase
from ginkgo.models.enums import GSODAttribute, GSODTrait, InputSource


class Thought(TextInputBase, table=True):
    __tablename__ = "thoughts"

    id: int | None = Field(default=None, primary_key=True)
    prompt_id: int = Field(foreign_key="prompts.id", nullable=False)
    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None
    trait_entailment: float | None = Field(default=None, ge=0.0, le=1.0)
    score_health: float | None = Field(default=None, ge=0.0, le=1.0)
    score_split: float | None = Field(default=None, ge=0.0, le=1.0)
    score_impact: float | None = Field(default=None, ge=0.0, le=1.0)

    def __repr__(self) -> str:
        return (
            "<Thought("
            f"id={self.id}, "
            f"prompt_id={self.prompt_id}, "
            f"text={self.text!r}, "
            f"lang={self.lang!r}, "
            f"source={self.source}, "
            f"created_at={self.created_at}, "
            f"modified_at={self.modified_at}, "
            f"attribute_class={self.attribute_class}, "
            f"trait={self.trait}, "
            f"trait_entailment={self.trait_entailment}, "
            f"score_health={self.score_health}, "
            f"score_split={self.score_split}, "
            f"score_impact={self.score_impact}"
            ")>"
        )


class ThoughtCreate(TextInput):
    prompt_id: int
    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None
    trait_entailment: float | None = Field(default=None, ge=0.0, le=1.0)
    score_health: float | None = Field(default=None, ge=0.0, le=1.0)
    score_split: float | None = Field(default=None, ge=0.0, le=1.0)
    score_impact: float | None = Field(default=None, ge=0.0, le=1.0)


class ThoughtRead(TextInputBase):
    id: int
    prompt_id: int
    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None
    trait_entailment: float | None = None
    score_health: float | None = None
    score_split: float | None = None
    score_impact: float | None = None


class ThoughtUpdate(SQLModel):
    text: str | None = None
    lang: str | None = None
    source: InputSource | None = None
    prompt_id: int | None = None
    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None
    trait_entailment: float | None = None
    score_health: float | None = None
    score_split: float | None = None
    score_impact: float | None = None
