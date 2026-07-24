from typing import Annotated
from typing_extensions import TypedDict
import operator


class RoutingDecision(TypedDict):
    """One Critic routing decision — this list, across a run, IS the attribution dataset."""
    revision_number: int
    retrieval_score: float
    grounding_score: float
    generation_score: float
    routed_to: str          # "researcher" | "analyst" | "writer" | "end"
    reason: str


class PipelineState(TypedDict):
    topic: str
    retrieved_docs: list[str]
    analysis: str
    draft: str
    final_report: str
    revision_count: int
    # accumulates across the whole run instead of being overwritten each loop
    routing_history: Annotated[list[RoutingDecision], operator.add]
