from enum import Enum

from sqlmodel import SQLModel


class InputType(str, Enum):
    THOUGHT = "thought"
    PROMPT = "prompt"
    DECREE = "decree"


class InputSource(str, Enum):
    SEED = "seed"
    AUDIENCE = "audience"


class InputLanguage(str, Enum):
    EN = "en"
    DE = "de"


class Input(SQLModel, table=False):
    """Base schema for user input - shared between API and database"""

    text: str
    type: InputType
    lang: InputLanguage
    source: InputSource = InputSource.AUDIENCE
