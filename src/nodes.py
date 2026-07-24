"""
Stub node implementations — deterministic, no real LLM calls yet.

Purpose: verify the GRAPH STRUCTURE (routing, loops, state accumulation) works
correctly before introducing the cost and non-determinism of real LLM calls.
Each stub's behavior is driven by revision_count so every routing path
(retrieval failure, grounding failure, generation failure, success) can be
exercised deterministically in tests.
"""

from src.state import PipelineState

RETRIEVAL_THRESHOLD = 0.6
GROUNDING_THRESHOLD = 0.6
GENERATION_THRESHOLD = 0.6
MAX_REVISIONS = 3


def researcher_node(state: PipelineState) -> dict:
    docs = [f"stub_doc_about_{state['topic']}_{i}" for i in range(3)]
    return {"retrieved_docs": docs}


def analyst_node(state: PipelineState) -> dict:
    analysis = f"analysis of {len(state['retrieved_docs'])} docs re: {state['topic']}"
    return {"analysis": analysis}


def writer_node(state: PipelineState) -> dict:
    draft = f"draft report based on: {state['analysis']}"
    return {"draft": draft}


def critic_node(state: PipelineState) -> dict:
    """
    Deterministic stub scoring, driven by revision_count so tests can force
    every routing path:
      revision 0 -> low retrieval score  -> routes to researcher
      revision 1 -> low grounding score  -> routes to analyst
      revision 2 -> low generation score -> routes to writer
      revision 3+ -> everything passes   -> routes to end
    """
    rc = state["revision_count"]

    retrieval_score = 0.3 if rc == 0 else 0.9
    grounding_score = 0.3 if rc == 1 else 0.9
    generation_score = 0.3 if rc == 2 else 0.9

    if retrieval_score < RETRIEVAL_THRESHOLD:
        routed_to, reason = "researcher", "retrieved docs insufficiently relevant"
    elif grounding_score < GROUNDING_THRESHOLD:
        routed_to, reason = "analyst", "analysis not grounded in retrieved docs"
    elif generation_score < GENERATION_THRESHOLD:
        routed_to, reason = "writer", "draft doesn't faithfully reflect the analysis"
    else:
        routed_to, reason = "end", "all checks passed"

    if rc >= MAX_REVISIONS and routed_to != "end":
        routed_to, reason = "end", f"hit max revisions ({MAX_REVISIONS}) without approval"

    decision = {
        "revision_number": rc,
        "retrieval_score": retrieval_score,
        "grounding_score": grounding_score,
        "generation_score": generation_score,
        "routed_to": routed_to,
        "reason": reason,
    }

    update = {"routing_history": [decision]}
    if routed_to == "end":
        update["final_report"] = state["draft"]
    else:
        update["revision_count"] = rc + 1

    return update


def route_from_critic(state: PipelineState) -> str:
    """Conditional edge function — reads the last routing decision, tells the graph where to go."""
    return state["routing_history"][-1]["routed_to"]
