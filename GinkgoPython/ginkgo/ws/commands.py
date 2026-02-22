from typing import Literal

from pydantic import BaseModel, field_validator

from ginkgo.models.base import InputLanguage, InputSource


class TextInputCommand(BaseModel):
    text: str
    lang: InputLanguage
    source: InputSource = InputSource.AUDIENCE


# —— Thought commands —————————————————————————————————————————
class AddThoughtCommand(TextInputCommand):
    action: Literal["add"] = "add"
    type: Literal["thought"] = "thought"


class QueryThoughtCommand(BaseModel):
    """Command to query thoughts"""

    action: Literal["query"] = "query"
    type: Literal["thought"] = "thought"
    query_type: str  # "all", "recent", "by_id"
    filters: dict = {}

    @field_validator("query_type")
    @classmethod
    def validate_query_type(cls, v: str) -> str:
        """Validate query type is one of the allowed values"""
        allowed = {"all", "recent", "by_id"}
        if v not in allowed:
            raise ValueError(f"query_type must be one of {allowed}, got '{v}'")
        return v


class UpdateThoughtCommand(BaseModel):
    """Command to update a thought's text"""

    action: Literal["update"] = "update"
    type: Literal["thought"] = "thought"
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


class DeleteThoughtCommand(BaseModel):
    """Command to delete a thought"""

    action: Literal["delete"] = "delete"
    type: Literal["thought"] = "thought"
    record_id: int

    @field_validator("record_id")
    @classmethod
    def validate_record_id(cls, v: int) -> int:
        """Validate record_id is positive"""
        if v <= 0:
            raise ValueError(f"record_id must be positive, got {v}")
        return v


# —— Prompt commands —————————————————————————————————————————
class AddPromptCommand(TextInputCommand):
    action: Literal["add"] = "add"
    type: Literal["prompt"] = "prompt"


class QueryPromptCommand(BaseModel):
    """Command to query prompts"""

    action: Literal["query"] = "query"
    type: Literal["prompt"] = "prompt"
    query_type: str  # "all", "recent", "by_id"
    filters: dict = {}

    @field_validator("query_type")
    @classmethod
    def validate_query_type(cls, v: str) -> str:
        """Validate query type is one of the allowed values"""
        allowed = {"all", "recent", "by_id"}
        if v not in allowed:
            raise ValueError(f"query_type must be one of {allowed}, got '{v}'")
        return v


class UpdatePromptCommand(BaseModel):
    """Command to update a prompt's text"""

    action: Literal["update"] = "update"
    type: Literal["prompt"] = "prompt"
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


class DeletePromptCommand(BaseModel):
    """Command to delete a prompt"""

    action: Literal["delete"] = "delete"
    type: Literal["prompt"] = "prompt"
    record_id: int

    @field_validator("record_id")
    @classmethod
    def validate_record_id(cls, v: int) -> int:
        """Validate record_id is positive"""
        if v <= 0:
            raise ValueError(f"record_id must be positive, got {v}")
        return v


# —— Decree commands —————————————————————————————————————————
class AddDecreeCommand(TextInputCommand):
    action: Literal["add"] = "add"
    type: Literal["decree"] = "decree"


class QueryDecreeCommand(BaseModel):
    """Command to query decrees"""

    action: Literal["query"] = "query"
    type: Literal["decree"] = "decree"
    query_type: str  # "all", "recent", "by_id"
    filters: dict = {}

    @field_validator("query_type")
    @classmethod
    def validate_query_type(cls, v: str) -> str:
        """Validate query type is one of the allowed values"""
        allowed = {"all", "recent", "by_id"}
        if v not in allowed:
            raise ValueError(f"query_type must be one of {allowed}, got '{v}'")
        return v


class UpdateDecreeCommand(BaseModel):
    """Command to update a decree's text"""

    action: Literal["update"] = "update"
    type: Literal["decree"] = "decree"
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


class DeleteDecreeCommand(BaseModel):
    """Command to delete a decree"""

    action: Literal["delete"] = "delete"
    type: Literal["decree"] = "decree"
    record_id: int

    @field_validator("record_id")
    @classmethod
    def validate_record_id(cls, v: int) -> int:
        """Validate record_id is positive"""
        if v <= 0:
            raise ValueError(f"record_id must be positive, got {v}")
        return v


# —— Type union for any command ———————————————————————————
WebSocketCommand = (
    AddThoughtCommand
    | QueryThoughtCommand
    | UpdateThoughtCommand
    | DeleteThoughtCommand
    | AddPromptCommand
    | QueryPromptCommand
    | UpdatePromptCommand
    | DeletePromptCommand
    | AddDecreeCommand
    | QueryDecreeCommand
    | UpdateDecreeCommand
    | DeleteDecreeCommand
)
