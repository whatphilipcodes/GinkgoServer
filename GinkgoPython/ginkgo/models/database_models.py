from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel

from ginkgo.schemas.frontend import InputLanguage, InputSource


# —— GSOD Enums (based on labels.json) ————————————————————
class GSODAttribute(str, Enum):
    """Democratic quality attribute dimensions from GSOD framework"""

    REPRESENTATION = "REPRESENTATION"
    RIGHTS = "RIGHTS"
    RULE_OF_LAW = "RULE_OF_LAW"
    PARTICIPATION = "PARTICIPATION"


class GSODTrait(str, Enum):
    """Specific traits/indicators from GSOD framework"""

    # Representation
    CREDIBLE_ELECTIONS = "CREDIBLE_ELECTIONS"
    INCLUSIVE_SUFFRAGE = "INCLUSIVE_SUFFRAGE"
    FREE_POLITICAL_PARTIES = "FREE_POLITICAL_PARTIES"
    ELECTED_GOVERNMENT = "ELECTED_GOVERNMENT"
    EFFECTIVE_PARLIAMENT = "EFFECTIVE_PARLIAMENT"
    LOCAL_DEMOCRACY = "LOCAL_DEMOCRACY"

    # Rights
    ACCESS_TO_JUSTICE = "ACCESS_TO_JUSTICE"
    CIVIL_LIBERTIES = "CIVIL_LIBERTIES"
    BASIC_WELFARE = "BASIC_WELFARE"
    POLITICAL_EQUALITY = "POLITICAL_EQUALITY"

    # Rule of Law
    JUDICIAL_INDEPENDENCE = "JUDICIAL_INDEPENDENCE"
    ABSENCE_OF_CORRUPTION = "ABSENCE_OF_CORRUPTION"
    PREDICTABLE_ENFORCEMENT = "PREDICTABLE_ENFORCEMENT"
    PERSONAL_INTEGRITY_AND_SECURITY = "PERSONAL_INTEGRITY_AND_SECURITY"

    # Participation
    CIVIL_SOCIETY = "CIVIL_SOCIETY"
    CIVIC_ENGAGEMENT = "CIVIC_ENGAGEMENT"
    ELECTORAL_PARTICIPATION = "ELECTORAL_PARTICIPATION"


# —— Base class for text inputs ——————————————————————————
class TextInputBase(SQLModel):
    """Base schema for all text-based inputs"""

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


# —— Thought models ——————————————————————————————————————————
class ThoughtCreate(TextInputBase):
    """Schema for creating new Thoughts"""

    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None


class ThoughtRead(TextInputBase):
    """Schema for reading Thoughts from database."""

    id: int
    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None
    trait_offset: float = 0.0
    trait_entailment: float = 0.0
    score_health: float = 0.0
    score_split: float = 0.0
    score_impact: float = 0.0


class Thought(TextInputBase, table=True):
    """Database table model for thoughts with GSOD scoring"""

    __tablename__ = "thoughts"

    id: int | None = Field(default=None, primary_key=True)

    # GSOD classification
    attribute_class: GSODAttribute | None = None
    trait: GSODTrait | None = None

    # GSOD scores
    trait_offset: float = Field(default=0.0, ge=0.0, le=1.0)
    trait_entailment: float = Field(default=0.0, ge=0.0, le=1.0)
    score_health: float = Field(default=0.0, ge=0.0, le=1.0)
    score_split: float = Field(default=0.0, ge=0.0, le=1.0)
    score_impact: float = Field(default=0.0, ge=0.0, le=1.0)

    def __repr__(self) -> str:
        return (
            f"<Thought(id={self.id}, trait={self.trait}, created_at={self.created_at})>"
        )


# —— Prompt models ———————————————————————————————————————————
class PromptCreate(TextInputBase):
    """Schema for creating new Prompts"""

    pass


class PromptRead(TextInputBase):
    """Schema for reading Prompts from database."""

    id: int


class Prompt(TextInputBase, table=True):
    """Database table model for prompts"""

    __tablename__ = "prompts"

    id: int | None = Field(default=None, primary_key=True)

    def __repr__(self) -> str:
        return f"<Prompt(id={self.id}, created_at={self.created_at})>"


# —— Decree models ———————————————————————————————————————————
class DecreeCreate(TextInputBase):
    """Schema for creating new Decrees"""

    pass


class DecreeRead(TextInputBase):
    """Schema for reading Decrees from database."""

    id: int


class Decree(TextInputBase, table=True):
    """Database table model for decrees"""

    __tablename__ = "decrees"

    id: int | None = Field(default=None, primary_key=True)

    def __repr__(self) -> str:
        return f"<Decree(id={self.id}, created_at={self.created_at})>"
