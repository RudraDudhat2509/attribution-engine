import pytest
from src.graph import build_graph


@pytest.fixture
def app():
    return build_graph()


def initial_state(topic="test topic"):
    return {
        "topic": topic,
        "retrieved_docs": [],
        "analysis": "",
        "draft": "",
        "final_report": "",
        "revision_count": 0,
        "routing_history": [],
    }


def test_pipeline_produces_final_report(app):
    result = app.invoke(initial_state())
    assert result["final_report"] != ""
    assert "test topic" in result["final_report"]


def test_pipeline_exercises_all_four_routing_paths(app):
    result = app.invoke(initial_state())
    routed_to_sequence = [d["routed_to"] for d in result["routing_history"]]
    assert routed_to_sequence == ["researcher", "analyst", "writer", "end"]


def test_routing_history_accumulates_not_overwrites(app):
    result = app.invoke(initial_state())
    assert len(result["routing_history"]) == 4


def test_revision_count_increments_on_each_non_terminal_route(app):
    result = app.invoke(initial_state())
    decisions = result["routing_history"]
    assert [d["revision_number"] for d in decisions] == [0, 1, 2, 3]


def test_final_decision_has_no_further_revision(app):
    result = app.invoke(initial_state())
    last_decision = result["routing_history"][-1]
    assert last_decision["routed_to"] == "end"
    assert last_decision["reason"] == "all checks passed"
