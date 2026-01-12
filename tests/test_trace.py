"""
Unit tests for the ExecutionTrace class.
Verifies DAG structure, nodes, edges, and metadata storage.
"""
import pytest
from datetime import datetime, timezone
from rlam.action import Action
from rlam.executor import execute_action, ExecutionResult
from rlam.trace import ExecutionTrace


def test_new_trace_starts_empty():
    """A new ExecutionTrace starts with an empty graph."""
    trace = ExecutionTrace()
    
    assert trace.graph.number_of_nodes() == 0
    assert trace.graph.number_of_edges() == 0


def test_adding_action_inserts_node():
    """Adding an action result inserts a node into the trace graph."""
    trace = ExecutionTrace()
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    
    result = execute_action(action, lambda: 42)
    trace.add_result(result)
    
    assert trace.graph.number_of_nodes() == 1
    assert "A1" in trace.graph.nodes


def test_data_dependencies_create_edges():
    """Data dependencies between actions create directed edges."""
    trace = ExecutionTrace()
    
    # Create parent action
    action1 = Action(
        action_id="A1",
        action_type="source",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result1 = execute_action(action1, lambda: [1, 2, 3])
    trace.add_result(result1)
    
    # Create child action with dependency
    action2 = Action(
        action_id="A2",
        action_type="transform",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, lambda: [2, 4, 6])
    trace.add_result(result2, parents=["A1"])
    
    # Verify edge exists
    assert trace.graph.has_edge("A1", "A2")
    assert trace.graph.number_of_edges() == 1


def test_control_dependencies_create_distinct_edges():
    """Control dependencies create distinct edges in the trace."""
    trace = ExecutionTrace()
    
    # Create three actions with different dependency patterns
    action1 = Action(
        action_id="A1",
        action_type="init",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result1 = execute_action(action1, lambda: "initialized")
    trace.add_result(result1)
    
    action2 = Action(
        action_id="A2",
        action_type="process",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, lambda: "processed")
    trace.add_result(result2, parents=["A1"])
    
    # A3 depends on both A1 and A2 (control dependencies)
    action3 = Action(
        action_id="A3",
        action_type="finalize",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result3 = execute_action(action3, lambda: "done")
    trace.add_result(result3, parents=["A1", "A2"])
    
    # Verify distinct edges
    assert trace.graph.has_edge("A1", "A2")
    assert trace.graph.has_edge("A1", "A3")
    assert trace.graph.has_edge("A2", "A3")
    assert trace.graph.number_of_edges() == 3


def test_trace_graph_is_dag():
    """The trace graph is a directed acyclic graph (DAG)."""
    import networkx as nx
    
    trace = ExecutionTrace()
    
    # Build a linear chain: A1 -> A2 -> A3
    for i in range(1, 4):
        action = Action(
            action_id=f"A{i}",
            action_type="step",
            inputs={},
            parameters={},
            environment_hash="hash",
            timestamp=datetime.now(timezone.utc)
        )
        result = execute_action(action, lambda: i)
        parents = [f"A{i-1}"] if i > 1 else None
        trace.add_result(result, parents=parents)
    
    # Verify it's a DAG
    assert nx.is_directed_acyclic_graph(trace.graph)


def test_trace_prevents_cycles():
    """Adding edges that would create a cycle raises an error."""
    trace = ExecutionTrace()
    
    # Create A1 and A2 with A1 -> A2
    action1 = Action(
        action_id="A1",
        action_type="start",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result1 = execute_action(action1, lambda: 1)
    trace.add_result(result1)
    
    action2 = Action(
        action_id="A2",
        action_type="next",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, lambda: 2)
    trace.add_result(result2, parents=["A1"])
    
    # Cannot add A1 again with A2 as parent (would create cycle)
    # This is prevented by duplicate action check
    action1_dup = Action(
        action_id="A1",
        action_type="start",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result1_dup = execute_action(action1_dup, lambda: 1)
    
    with pytest.raises(RuntimeError, match="already exists in trace"):
        trace.add_result(result1_dup, parents=["A2"])


def test_stored_nodes_contain_action_metadata():
    """All stored nodes contain complete action metadata."""
    trace = ExecutionTrace()
    
    action = Action(
        action_id="A1",
        action_type="compute",
        inputs={"x": 10},
        parameters={},
        environment_hash="env_hash_123",
        timestamp=datetime.now(timezone.utc)
    )
    
    result = execute_action(action, lambda x: x * 2)
    trace.add_result(result)
    
    # Retrieve node data
    node_data = trace.graph.nodes["A1"]
    
    # Verify all metadata is stored
    assert node_data["action"] == action
    assert node_data["output"] == 20
    assert node_data["status"] == "SUCCESS"
    assert node_data["error"] is None


def test_stored_nodes_contain_failure_metadata():
    """Failed actions store error information in node metadata."""
    trace = ExecutionTrace()
    
    action = Action(
        action_id="A1",
        action_type="failing_op",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    
    def failing_function():
        raise ValueError("Expected test failure")
    
    result = execute_action(action, failing_function)
    trace.add_result(result)
    
    # Verify failure metadata
    node_data = trace.graph.nodes["A1"]
    assert node_data["status"] == "FAILED"
    assert "Expected test failure" in node_data["error"]
    assert node_data["output"] is None


def test_stored_nodes_preserve_environment_hash():
    """Node metadata preserves environment hash from action."""
    trace = ExecutionTrace()
    
    env_hash = "unique_env_hash_abc123"
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash=env_hash,
        timestamp=datetime.now(timezone.utc)
    )
    
    result = execute_action(action, lambda: "output")
    trace.add_result(result)
    
    node_data = trace.graph.nodes["A1"]
    assert node_data["action"].environment_hash == env_hash


def test_multiple_parents_create_multiple_edges():
    """An action with multiple parents has multiple incoming edges."""
    trace = ExecutionTrace()
    
    # Create two parent actions
    action1 = Action(
        action_id="A1",
        action_type="source1",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result1 = execute_action(action1, lambda: 1)
    trace.add_result(result1)
    
    action2 = Action(
        action_id="A2",
        action_type="source2",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, lambda: 2)
    trace.add_result(result2)
    
    # Create child with both parents
    action3 = Action(
        action_id="A3",
        action_type="merge",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    result3 = execute_action(action3, lambda: 3)
    trace.add_result(result3, parents=["A1", "A2"])
    
    # Verify both edges exist
    assert trace.graph.has_edge("A1", "A3")
    assert trace.graph.has_edge("A2", "A3")
    
    # Verify A3 has exactly 2 predecessors
    predecessors = list(trace.graph.predecessors("A3"))
    assert len(predecessors) == 2
    assert "A1" in predecessors
    assert "A2" in predecessors


def test_trace_get_result_returns_node_data():
    """get_result returns complete node data for an action."""
    trace = ExecutionTrace()
    
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={"value": 100},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    
    result = execute_action(action, lambda value: value + 50)
    trace.add_result(result)
    
    retrieved = trace.get_result("A1")
    
    assert retrieved["action"].action_id == "A1"
    assert retrieved["output"] == 150
    assert retrieved["status"] == "SUCCESS"


def test_trace_has_action_returns_true_for_logged_action():
    """has_action returns True for actions in the trace."""
    trace = ExecutionTrace()
    
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    
    result = execute_action(action, lambda: None)
    trace.add_result(result)
    
    assert trace.has_action("A1") is True
    assert trace.has_action("A2") is False
