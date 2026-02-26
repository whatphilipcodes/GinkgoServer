from typing import Annotated, Literal, Union

from pydantic import BaseModel, Discriminator, Field, field_validator

from ginkgo.models.enums import InputSource


class AllFilterPayload(BaseModel):
    """Payload for querying all records with pagination"""

    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class RecentFilterPayload(BaseModel):
    """Payload for querying recent records"""

    hours: int = Field(default=24, ge=1)


class ByIdFilterPayload(BaseModel):
    """Payload for querying by a specific ID"""

    record_id: int = Field(ge=1)


class TextInputCommand(BaseModel):
    text: str
    lang: str
    source: InputSource = InputSource.AUDIENCE


class AddThoughtCommand(TextInputCommand):
    action: Literal["add"] = "add"
    type: Literal["thought"] = "thought"


class QueryAllThoughts(BaseModel):
    """Query all thoughts with pagination"""

    action: Literal["query"] = "query"
    type: Literal["thought"] = "thought"
    query_type: Literal["all"]
    filters: AllFilterPayload


class QueryRecentThoughts(BaseModel):
    """Query recent thoughts"""

    action: Literal["query"] = "query"
    type: Literal["thought"] = "thought"
    query_type: Literal["recent"]
    filters: RecentFilterPayload


class QueryThoughtsById(BaseModel):
    """Query a thought by ID"""

    action: Literal["query"] = "query"
    type: Literal["thought"] = "thought"
    query_type: Literal["by_id"]
    filters: ByIdFilterPayload


QueryThoughtCommand = Annotated[
    Union[QueryAllThoughts, QueryRecentThoughts, QueryThoughtsById],
    Discriminator("query_type"),
]


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


class QueryAllPrompts(BaseModel):
    """Query all prompts with pagination"""

    action: Literal["query"] = "query"
    type: Literal["prompt"] = "prompt"
    query_type: Literal["all"]
    filters: AllFilterPayload


class QueryRecentPrompts(BaseModel):
    """Query recent prompts"""

    action: Literal["query"] = "query"
    type: Literal["prompt"] = "prompt"
    query_type: Literal["recent"]
    filters: RecentFilterPayload


class QueryPromptsById(BaseModel):
    """Query a prompt by ID"""

    action: Literal["query"] = "query"
    type: Literal["prompt"] = "prompt"
    query_type: Literal["by_id"]
    filters: ByIdFilterPayload


QueryPromptCommand = Annotated[
    Union[QueryAllPrompts, QueryRecentPrompts, QueryPromptsById],
    Discriminator("query_type"),
]


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


class QueryAllDecrees(BaseModel):
    """Query all decrees with pagination"""

    action: Literal["query"] = "query"
    type: Literal["decree"] = "decree"
    query_type: Literal["all"]
    filters: AllFilterPayload


class QueryRecentDecrees(BaseModel):
    """Query recent decrees"""

    action: Literal["query"] = "query"
    type: Literal["decree"] = "decree"
    query_type: Literal["recent"]
    filters: RecentFilterPayload


class QueryDecreesById(BaseModel):
    """Query a decree by ID"""

    action: Literal["query"] = "query"
    type: Literal["decree"] = "decree"
    query_type: Literal["by_id"]
    filters: ByIdFilterPayload


QueryDecreeCommand = Annotated[
    Union[QueryAllDecrees, QueryRecentDecrees, QueryDecreesById],
    Discriminator("query_type"),
]


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
    | QueryAllThoughts
    | QueryRecentThoughts
    | QueryThoughtsById
    | UpdateThoughtCommand
    | DeleteThoughtCommand
    | AddPromptCommand
    | QueryAllPrompts
    | QueryRecentPrompts
    | QueryPromptsById
    | UpdatePromptCommand
    | DeletePromptCommand
    | AddDecreeCommand
    | QueryAllDecrees
    | QueryRecentDecrees
    | QueryDecreesById
    | UpdateDecreeCommand
    | DeleteDecreeCommand
)
