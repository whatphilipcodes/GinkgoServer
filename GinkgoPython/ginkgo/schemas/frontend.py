from enum import Enum

from sqlmodel import SQLModel


class InputType(str, Enum):
    THOUGHT = "thought"
    PROMPT = "prompt"
    DECREE = "decree"


class InputSource(str, Enum):
    DEFAULT = "default"
    AUDIENCE = "audience"


class InputLanguage(str, Enum):
    EN = "en"
    DE = "de"


class UserInput(SQLModel, table=False):
    """Base schema for user input - shared between API and database"""

    text: str
    type: InputType
    source: InputSource = InputSource.AUDIENCE
