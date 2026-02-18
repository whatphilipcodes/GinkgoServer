from typing import Literal

from pydantic import BaseModel, field_validator

from ginkgo.schemas.frontend import Input


class AddInputCommand(Input):
    """Command to add a new input to the database"""

    action: Literal["add"] = "add"


class QueryInputCommand(BaseModel):
    """Command to query inputs by type"""

    action: Literal["query"] = "query"
    query_type: str  # "all", "by_type", "recent", "by_id"
    filters: dict = {}

    @field_validator("query_type")
    @classmethod
    def validate_query_type(cls, v: str) -> str:
        """Validate query type is one of the allowed values"""
        allowed = {"all", "by_type", "recent", "by_id"}
        if v not in allowed:
            raise ValueError(f"query_type must be one of {allowed}, got '{v}'")
        return v


class DeleteInputCommand(BaseModel):
    """Command to delete an input"""

    action: Literal["delete"] = "delete"
    record_id: int

    @field_validator("record_id")
    @classmethod
    def validate_record_id(cls, v: int) -> int:
        """Validate record_id is positive"""
        if v <= 0:
            raise ValueError(f"record_id must be positive, got {v}")
        return v


class UpdateInputCommand(BaseModel):
    """Command to update an input's text"""

    action: Literal["update"] = "update"
    record_id: int
    text: str

    @field_validator("record_id")
    @classmethod
    def validate_record_id(cls, v: int) -> int:
        """Validate record_id is positive"""
        if v <= 0:
            raise ValueError(f"record_id must be positive, got {v}")
        return v

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text is not empty"""
        if not v or not v.strip():
            raise ValueError("text cannot be empty")
        return v.strip()
