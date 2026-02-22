from enum import Enum

from sqlmodel import SQLModel


class InputSource(str, Enum):
    SEED = "seed"
    AUDIENCE = "audience"


class InputLanguage(str, Enum):
    EN = "en"
    DE = "de"


# —— Thought schema ——————————————————————————————————————————
class Thought(SQLModel, table=False):
    """Schema for thought input"""

    text: str
    lang: InputLanguage
    source: InputSource = InputSource.AUDIENCE


# —— Prompt schema ———————————————————————————————————————————
class Prompt(SQLModel, table=False):
    """Schema for prompt input"""

    text: str
    lang: InputLanguage
    source: InputSource = InputSource.AUDIENCE


# —— Decree schema ———————————————————————————————————————————
class Decree(SQLModel, table=False):
    """Schema for decree input"""

    text: str
    lang: InputLanguage
    source: InputSource = InputSource.AUDIENCE
