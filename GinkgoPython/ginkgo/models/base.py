from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class InputSource(str, Enum):
    SEED = "seed"
    AUDIENCE = "audience"


class InputLanguage(str, Enum):
    EN = "en"
    DE = "de"


class GSODAttribute(str, Enum):
    REPRESENTATION = "REPRESENTATION"
    RIGHTS = "RIGHTS"
    RULE_OF_LAW = "RULE_OF_LAW"
    PARTICIPATION = "PARTICIPATION"


class GSODTrait(str, Enum):
    CREDIBLE_ELECTIONS = "CREDIBLE_ELECTIONS"
    INCLUSIVE_SUFFRAGE = "INCLUSIVE_SUFFRAGE"
    FREE_POLITICAL_PARTIES = "FREE_POLITICAL_PARTIES"
    ELECTED_GOVERNMENT = "ELECTED_GOVERNMENT"
    EFFECTIVE_PARLIAMENT = "EFFECTIVE_PARLIAMENT"
    LOCAL_DEMOCRACY = "LOCAL_DEMOCRACY"

    ACCESS_TO_JUSTICE = "ACCESS_TO_JUSTICE"
    CIVIL_LIBERTIES = "CIVIL_LIBERTIES"
    BASIC_WELFARE = "BASIC_WELFARE"
    POLITICAL_EQUALITY = "POLITICAL_EQUALITY"

    JUDICIAL_INDEPENDENCE = "JUDICIAL_INDEPENDENCE"
    ABSENCE_OF_CORRUPTION = "ABSENCE_OF_CORRUPTION"
    PREDICTABLE_ENFORCEMENT = "PREDICTABLE_ENFORCEMENT"
    PERSONAL_INTEGRITY_AND_SECURITY = "PERSONAL_INTEGRITY_AND_SECURITY"

    CIVIL_SOCIETY = "CIVIL_SOCIETY"
    CIVIC_ENGAGEMENT = "CIVIC_ENGAGEMENT"
    ELECTORAL_PARTICIPATION = "ELECTORAL_PARTICIPATION"


class TextInputBase(SQLModel):
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
