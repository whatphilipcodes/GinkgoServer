from pydantic import BaseModel, Field


class UEDataPayload(BaseModel):
    ID: int = Field(ge=0)
    PillarID: int = Field(ge=0, le=3)
    PositionAlongsidePillar: float = Field(ge=0.0, le=1.0)
    DistanceFromPillar: float = Field(ge=0.0, le=1.0)
    InnerColour: float = Field(ge=0.0, le=1.0)
    OuterColour: float = Field(ge=0.0, le=1.0)
    SplitSize: float = Field(ge=0.0, le=1.0)
    LeafSize: float = Field(ge=0.0, le=1.0)
    RotationOffset: float = Field(ge=0.0, le=1.0)
    V5: float = Field(ge=0.0, le=1.0)
