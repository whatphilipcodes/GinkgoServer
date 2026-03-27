from typing import Annotated, Literal, Union

from pydantic import BaseModel, Discriminator, Field, field_validator

from ginkgo.models.enums import ContextFrontend

EntityType = Literal["thought", "prompt", "decree"]


class AllFilterPayload(BaseModel):
    """Payload for querying all records with pagination"""

    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    recent: bool = Field(default=False)


class RecentFilterPayload(BaseModel):
    """Payload for querying recent records"""

    hours: int = Field(default=24, ge=1)


class ByIdFilterPayload(BaseModel):
    """Payload for querying by a specific ID"""

    record_id: int = Field(ge=1)


class ValidatedRecordId(BaseModel):
    record_id: int

    @field_validator("record_id")
    @classmethod
    def validate_record_id(cls, v: int) -> int:
        """Validate record_id is positive"""
        if v <= 0:
            raise ValueError(f"record_id must be positive, got {v}")
        return v


class ValidatedText(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text is not empty"""
        if not v or not v.strip():
            raise ValueError("text cannot be empty")
        return v.strip()


class BaseQuery(BaseModel):
    action: Literal["query"] = "query"
    type: EntityType


class QueryAll(BaseQuery):
    """Query all records with pagination"""

    query_type: Literal["all"] = "all"
    filters: AllFilterPayload


class QueryRecent(BaseQuery):
    """Query recent records"""

    query_type: Literal["recent"] = "recent"
    filters: RecentFilterPayload


class QueryById(BaseQuery):
    """Query a record by ID"""

    query_type: Literal["by_id"] = "by_id"
    filters: ByIdFilterPayload


QueryCommand = Annotated[
    Union[QueryAll, QueryRecent, QueryById],
    Discriminator("query_type"),
]


class BaseAdd(ValidatedText):
    action: Literal["add"] = "add"


class AddThoughtCommand(BaseAdd):
    type: Literal["thought"] = "thought"
    prompt_id: int


class AddPromptCommand(BaseAdd):
    type: Literal["prompt"] = "prompt"


class AddDecreeCommand(BaseAdd):
    type: Literal["decree"] = "decree"


class BaseUpdate(ValidatedText, ValidatedRecordId):
    action: Literal["update"] = "update"


class UpdateThoughtCommand(BaseUpdate):
    type: Literal["thought"] = "thought"
    prompt_id: int


class UpdatePromptCommand(BaseUpdate):
    type: Literal["prompt"] = "prompt"


class UpdateDecreeCommand(BaseUpdate):
    type: Literal["decree"] = "decree"


class DeleteCommand(ValidatedRecordId):
    """Command to delete a generic record"""

    action: Literal["delete"] = "delete"
    type: EntityType


class SendKeystrokeCommand(BaseModel):
    """Command to forward a keystroke event"""

    action: Literal["send"] = "send"
    type: Literal["keystroke"] = "keystroke"
    key: str
    context: ContextFrontend


WebSocketCommand = (
    AddThoughtCommand
    | AddPromptCommand
    | AddDecreeCommand
    | UpdateThoughtCommand
    | UpdatePromptCommand
    | UpdateDecreeCommand
    | DeleteCommand
    | QueryCommand
    | SendKeystrokeCommand
)
