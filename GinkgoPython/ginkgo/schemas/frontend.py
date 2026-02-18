from pydantic import field_validator
from sqlmodel import SQLModel


class UserInput(SQLModel, table=False):
    """Base schema for user input - shared between API and database"""

    text: str
    type: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that type is one of the allowed values"""
        allowed = {"thought", "prompt", "decree"}
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}, got '{v}'")
        return v
