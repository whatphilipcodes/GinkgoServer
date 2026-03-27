from sqlmodel import Field, SQLModel

from ginkgo.models.base import TextInput, TextInputBase
from ginkgo.models.enums import GSODAttribute, GSODTrait, InputSource


class ThoughtFields(SQLModel):
    prompt_id: int = Field(foreign_key="prompts.id")
    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None
    trait_entailment: float | None = Field(default=None, ge=0.0, le=1.0)
    score_health: float | None = Field(default=None, ge=0.0, le=1.0)
    score_split: float | None = Field(default=None, ge=0.0, le=1.0)
    score_impact: float | None = Field(default=None, ge=0.0, le=1.0)


class ThoughtCreate(TextInput, ThoughtFields):
    pass


class Thought(TextInputBase, ThoughtFields, table=True):
    __tablename__ = "thoughts"
    id: int | None = Field(default=None, primary_key=True)


class ThoughtRead(TextInputBase, ThoughtFields):
    id: int


class ThoughtUpdate(SQLModel):
    text: str | None = None
    lang: str | None = None
    source: InputSource | None = None
    prompt_id: int | None = None
    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None
    trait_entailment: float | None = Field(default=None, ge=0.0, le=1.0)
    score_health: float | None = Field(default=None, ge=0.0, le=1.0)
    score_split: float | None = Field(default=None, ge=0.0, le=1.0)
    score_impact: float | None = Field(default=None, ge=0.0, le=1.0)
