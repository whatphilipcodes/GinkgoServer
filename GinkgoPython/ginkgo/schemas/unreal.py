from typing import Union

from pydantic import BaseModel, Field

from ginkgo.models.enums import ContextFrontend, GinkgoMessageType, GSODAttribute


class GinkgoInput(BaseModel):
    id: int = Field(ge=0)
    text: str = ""
    attribute: GSODAttribute
    traitOffset: float = Field(ge=0.0, le=1.0)
    traitEntailment: float = Field(ge=0.0, le=1.0)
    scoreHealth: float = Field(ge=0.0, le=1.0)
    scoreSplit: float = Field(ge=0.0, le=1.0)
    scoreImpact: float = Field(ge=0.0, le=1.0)


class GinkgoKeystroke(BaseModel):
    key: str = ""
    context: ContextFrontend


class GinkgoMessage(BaseModel):
    messageType: GinkgoMessageType
    payloadJson: Union[GinkgoInput, GinkgoKeystroke]
