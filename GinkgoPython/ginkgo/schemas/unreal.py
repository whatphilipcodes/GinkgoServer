from pydantic import BaseModel, Field

from ginkgo.models.enums import GSODAttribute


class UEDataPayload(BaseModel):
    id: int = Field(ge=0)
    attribute: GSODAttribute
    traitOffset: float = Field(ge=0.0, le=1.0)
    traitEntailment: float = Field(ge=0.0, le=1.0)
    scoreHealth: float = Field(ge=0.0, le=1.0)
    scoreSplit: float = Field(ge=0.0, le=1.0)
    scoreImpact: float = Field(ge=0.0, le=1.0)
