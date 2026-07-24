from langgraph.graph import StateGraph, END

from src.state import PipelineState
from src.nodes import researcher_node, analyst_node, writer_node, critic_node, route_from_critic


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)

    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "writer")
    graph.add_edge("writer", "critic")

    graph.add_conditional_edges(
        "critic",
        route_from_critic,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            "end": END,
        },
    )

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({
        "topic": "why do multi-agent systems fail silently",
        "retrieved_docs": [],
        "analysis": "",
        "draft": "",
        "final_report": "",
        "revision_count": 0,
        "routing_history": [],
    })

    print("FINAL REPORT:", result["final_report"])
    print()
    print("ROUTING HISTORY (the attribution trace):")
    for decision in result["routing_history"]:
        print(f"  revision {decision['revision_number']}: "
              f"routed_to={decision['routed_to']!r}, reason={decision['reason']!r}")
