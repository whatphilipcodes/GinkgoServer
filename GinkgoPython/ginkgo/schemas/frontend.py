from typing import Literal

from pydantic import BaseModel


class UserInput(BaseModel):
    text: str
    type: Literal["thought", "prompt", "decree"]
