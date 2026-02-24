from typing import Annotated, Literal, Union

from pydantic import BaseModel, Discriminator, Field, field_validator

from ginkgo.models.enums import InputLanguage, InputSource


class AllFilter(BaseModel):
    """Filter for querying all records with pagination"""

    query_type: Literal["all"]
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class RecentFilter(BaseModel):
    """Filter for querying recent records"""

    query_type: Literal["recent"]
    hours: int = Field(default=24, ge=1)


class ByIdFilter(BaseModel):
    """Filter for querying by a specific ID"""

    query_type: Literal["by_id"]
    record_id: int = Field(ge=1)


# Discriminated union for filters
ThoughtFilter = Annotated[
    Union[AllFilter, RecentFilter, ByIdFilter],
    Discriminator("query_type"),
]

PromptFilter = Annotated[
    Union[AllFilter, RecentFilter, ByIdFilter],
    Discriminator("query_type"),
]

DecreeFilter = Annotated[
    Union[AllFilter, RecentFilter, ByIdFilter],
    Discriminator("query_type"),
]


class TextInputCommand(BaseModel):
    text: str
    lang: InputLanguage
    source: InputSource = InputSource.AUDIENCE


class AddThoughtCommand(TextInputCommand):
    action: Literal["add"] = "add"
    type: Literal["thought"] = "thought"


class QueryThoughtCommand(BaseModel):
    """Command to query thoughts"""

    action: Literal["query"] = "query"
    type: Literal["thought"] = "thought"
    filters: ThoughtFilter


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


class AddPromptCommand(TextInputCommand):
    action: Literal["add"] = "add"
    type: Literal["prompt"] = "prompt"


class QueryPromptCommand(BaseModel):
    """Command to query prompts"""

    action: Literal["query"] = "query"
    type: Literal["prompt"] = "prompt"
    filters: PromptFilter


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


class AddDecreeCommand(TextInputCommand):
    action: Literal["add"] = "add"
    type: Literal["decree"] = "decree"


class QueryDecreeCommand(BaseModel):
    """Command to query decrees"""

    action: Literal["query"] = "query"
    type: Literal["decree"] = "decree"
    filters: DecreeFilter


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
