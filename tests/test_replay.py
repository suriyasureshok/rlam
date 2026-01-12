"""
Unit tests for replay mechanism and fork behavior.
Verifies replay uses trace data only and fork creates independent branches.
"""
import pytest
from datetime import datetime, timezone
from rlam.action import Action
from rlam.executor import execute_action
from rlam.trace import ExecutionTrace
from rlam.replay import replay_action
from rlam.fork import fork_trace


# ============================================================================
# Replay Tests
# ============================================================================

def test_workflow_stores_outputs_in_trace():
    """Executing a workflow stores outputs in the execution trace."""
    trace = ExecutionTrace()
    
    # Execute a simple workflow: A1 -> A2
    action1 = Action(
        action_id="A1",
        action_type="load",
        inputs={"value": 10},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result1 = execute_action(action1, lambda value: value * 2)
    trace.add_result(result1)
    
    action2 = Action(
        action_id="A2",
        action_type="transform",
        inputs={"value": 20},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, lambda value: value + 5)
    trace.add_result(result2, parents=["A1"])
    
    # Verify outputs are stored
    assert trace.get_result("A1")["output"] == 20
    assert trace.get_result("A2")["output"] == 25


def test_replay_does_not_reexecute_functions():
    """Replaying workflow does not re-execute underlying functions."""
    execution_count = {"count": 0}
    
    def tracked_function(x):
        execution_count["count"] += 1
        return x * 3
    
    trace = ExecutionTrace()
    action = Action(
        action_id="A1",
        action_type="compute",
        inputs={"x": 7},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    
    # Execute once
    result = execute_action(action, tracked_function)
    trace.add_result(result)
    
    assert execution_count["count"] == 1
    assert result.output == 21
    
    # Replay multiple times
    replayed1 = replay_action(trace, "A1")
    replayed2 = replay_action(trace, "A1")
    replayed3 = replay_action(trace, "A1")
    
    # Assert: Function was NOT re-executed
    assert execution_count["count"] == 1
    assert replayed1 == 21
    assert replayed2 == 21
    assert replayed3 == 21


def test_replay_outputs_identical_to_original():
    """Outputs returned during replay are identical to original execution."""
    trace = ExecutionTrace()
    
    # Execute with complex output
    action = Action(
        action_id="A1",
        action_type="generate",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    
    original_output = {"data": [1, 2, 3], "metadata": {"count": 3}}
    result = execute_action(action, lambda: original_output)
    trace.add_result(result)
    
    # Replay and verify identity
    replayed_output = replay_action(trace, "A1")
    
    assert replayed_output == original_output
    assert replayed_output["data"] == [1, 2, 3]
    assert replayed_output["metadata"]["count"] == 3


def test_replay_nonexistent_action_raises_error():
    """Attempting to replay action not in trace raises error."""
    trace = ExecutionTrace()
    
    # Add one action
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result = execute_action(action, lambda: "exists")
    trace.add_result(result)
    
    # Try to replay non-existent action
    with pytest.raises(RuntimeError, match="does not exist in trace"):
        replay_action(trace, "A_NONEXISTENT")


def test_replay_workflow_sequence():
    """Replaying workflow sequence returns correct outputs in order."""
    trace = ExecutionTrace()
    
    # Build workflow: A1 -> A2 -> A3
    values = [10, 20, 30]
    for i, val in enumerate(values, 1):
        action = Action(
            action_id=f"A{i}",
            action_type="step",
            inputs={"value": val},
            parameters={},
            environment_hash="env",
            timestamp=datetime.now(timezone.utc)
        )
        result = execute_action(action, lambda value: value + i)
        parents = [f"A{i-1}"] if i > 1 else None
        trace.add_result(result, parents=parents)
    
    # Replay all actions
    output1 = replay_action(trace, "A1")
    output2 = replay_action(trace, "A2")
    output3 = replay_action(trace, "A3")
    
    assert output1 == 11  # 10 + 1
    assert output2 == 22  # 20 + 2
    assert output3 == 33  # 30 + 3


# ============================================================================
# Fork Tests
# ============================================================================

def test_fork_creates_trace_with_shared_prefix():
    """Forking creates new trace sharing prefix with original."""
    trace = ExecutionTrace()
    
    # Build original trace: A1 -> A2 -> A3
    for i in range(1, 4):
        action = Action(
            action_id=f"A{i}",
            action_type="step",
            inputs={"i": i},
            parameters={},
            environment_hash="env",
            timestamp=datetime.now(timezone.utc)
        )
        result = execute_action(action, lambda i: i * 10)
        parents = [f"A{i-1}"] if i > 1 else None
        trace.add_result(result, parents=parents)
    
    # Fork at A2
    forked = fork_trace(trace, "A2")
    
    # Verify shared prefix
    assert forked.has_action("A1")
    assert forked.has_action("A2")
    assert not forked.has_action("A3")  # Not in forked trace
    
    # Verify original unchanged
    assert trace.has_action("A1")
    assert trace.has_action("A2")
    assert trace.has_action("A3")


def test_fork_upstream_not_reexecuted():
    """Upstream actions are not re-executed during fork."""
    execution_count = {"count": 0}
    
    def counted_function(x):
        execution_count["count"] += 1
        return x * 2
    
    trace = ExecutionTrace()
    
    # Execute A1 and A2
    action1 = Action(
        action_id="A1",
        action_type="compute",
        inputs={"x": 5},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result1 = execute_action(action1, counted_function)
    trace.add_result(result1)
    
    action2 = Action(
        action_id="A2",
        action_type="compute",
        inputs={"x": 10},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, counted_function)
    trace.add_result(result2, parents=["A1"])
    
    assert execution_count["count"] == 2
    
    # Fork at A2
    forked = fork_trace(trace, "A2")
    
    # Assert: No additional executions
    assert execution_count["count"] == 2
    assert forked.has_action("A1")
    assert forked.has_action("A2")


def test_fork_modified_parameters_different_outputs():
    """Modified parameters in forked trace result in different outputs."""
    trace = ExecutionTrace()
    
    # Original workflow: A1 -> A2
    action1 = Action(
        action_id="A1",
        action_type="init",
        inputs={"value": 10},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result1 = execute_action(action1, lambda value: value)
    trace.add_result(result1)
    
    action2 = Action(
        action_id="A2",
        action_type="multiply",
        inputs={"value": 10},
        parameters={"factor": 2},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, lambda value, factor=2: value * factor)
    trace.add_result(result2, parents=["A1"])
    
    # Fork at A1 and add A2 with different parameters
    forked = fork_trace(trace, "A1")
    
    action2_modified = Action(
        action_id="A2_modified",
        action_type="multiply",
        inputs={"value": 10},
        parameters={"factor": 5},  # Different factor
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result2_modified = execute_action(action2_modified, lambda value, factor=5: value * factor)
    forked.add_result(result2_modified, parents=["A1"])
    
    # Compare outputs
    original_output = trace.get_result("A2")["output"]
    forked_output = forked.get_result("A2_modified")["output"]
    
    assert original_output == 20  # 10 * 2
    assert forked_output == 50     # 10 * 5
    assert original_output != forked_output


def test_original_trace_unchanged_after_fork():
    """Original trace remains unchanged after forking."""
    trace = ExecutionTrace()
    
    # Build original: A1 -> A2
    action1 = Action(
        action_id="A1",
        action_type="step1",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result1 = execute_action(action1, lambda: "output1")
    trace.add_result(result1)
    
    action2 = Action(
        action_id="A2",
        action_type="step2",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, lambda: "output2")
    trace.add_result(result2, parents=["A1"])
    
    # Fork at A1
    forked = fork_trace(trace, "A1")
    
    # Modify forked trace by adding new action
    action3 = Action(
        action_id="A3",
        action_type="step3",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result3 = execute_action(action3, lambda: "output3")
    forked.add_result(result3, parents=["A1"])
    
    # Verify original trace unchanged
    assert trace.has_action("A1")
    assert trace.has_action("A2")
    assert not trace.has_action("A3")
    
    # Verify forked trace has new action
    assert forked.has_action("A1")
    assert not forked.has_action("A2")  # Not copied
    assert forked.has_action("A3")


def test_fork_preserves_graph_structure():
    """Fork preserves graph structure and edges from original trace."""
    trace = ExecutionTrace()
    
    # Build branching structure: A1 -> A2, A1 -> A3, A2 -> A4, A3 -> A4
    action1 = Action(
        action_id="A1",
        action_type="root",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result1 = execute_action(action1, lambda: 1)
    trace.add_result(result1)
    
    action2 = Action(
        action_id="A2",
        action_type="branch1",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, lambda: 2)
    trace.add_result(result2, parents=["A1"])
    
    action3 = Action(
        action_id="A3",
        action_type="branch2",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result3 = execute_action(action3, lambda: 3)
    trace.add_result(result3, parents=["A1"])
    
    action4 = Action(
        action_id="A4",
        action_type="merge",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result4 = execute_action(action4, lambda: 4)
    trace.add_result(result4, parents=["A2", "A3"])
    
    # Fork at A3 (includes A1, A2, A3 but not A4)
    forked = fork_trace(trace, "A3")
    
    # Verify structure preserved
    assert forked.has_action("A1")
    assert forked.has_action("A2")
    assert forked.has_action("A3")
    assert not forked.has_action("A4")
    
    # Verify edges preserved
    assert forked.graph.has_edge("A1", "A2")
    assert forked.graph.has_edge("A1", "A3")
    assert not forked.graph.has_edge("A2", "A4")  # A4 not in fork


def test_fork_trace_identity_differs_from_original():
    """Forked trace has different identity from original."""
    trace = ExecutionTrace()
    
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash="env",
        timestamp=datetime.now(timezone.utc)
    )
    result = execute_action(action, lambda: "data")
    trace.add_result(result)
    
    forked = fork_trace(trace, "A1")
    
    # Different object identities
    assert trace is not forked
    assert trace.graph is not forked.graph
    
    # But equivalent content
    assert trace.get_result("A1")["output"] == forked.get_result("A1")["output"]
