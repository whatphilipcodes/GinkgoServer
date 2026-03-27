from pydantic import BaseModel, Field

from ginkgo.models.enums import ContextFrontend, GinkgoMessageType, GSODAttribute
from ginkgo.models.thought import ThoughtRead
from ginkgo.utils.math import map_trait_offset


class GinkgoInput(BaseModel):
    id: int = Field(ge=0)
    text: str = ""
    attribute: GSODAttribute
    traitOffset: float = Field(ge=0.0, le=1.0)
    traitEntailment: float = Field(ge=0.0, le=1.0)
    scoreHealth: float = Field(ge=0.0, le=1.0)
    scoreSplit: float = Field(ge=0.0, le=1.0)
    scoreImpact: float = Field(ge=0.0, le=1.0)

    @classmethod
    def from_thought(cls, thought: ThoughtRead) -> "GinkgoInput":
        return cls(
            id=thought.id,
            text=thought.text,
            attribute=thought.attribute_class
            if thought.attribute_class
            else GSODAttribute.INVALID,
            traitOffset=map_trait_offset(thought.trait) if thought.trait else 0.0,
            traitEntailment=thought.trait_entailment
            if thought.trait_entailment
            else 0.0,
            scoreHealth=thought.score_health if thought.score_health else 0.0,
            scoreSplit=thought.score_split if thought.score_split else 0.0,
            scoreImpact=thought.score_impact if thought.score_impact else 0.0,
        )


class GinkgoInputList(BaseModel):
    entries: list[GinkgoInput]


class GinkgoKeystroke(BaseModel):
    key: str = ""
    context: ContextFrontend


class GinkgoMessage(BaseModel):
    messageType: GinkgoMessageType
    payloadJson: GinkgoInput | GinkgoInputList | GinkgoKeystroke
