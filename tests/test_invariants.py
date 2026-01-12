"""
Boring tests for core invariants.
These tests verify fundamental guarantees, not edge cases.
"""
import pytest
from datetime import datetime, timezone
from rlam.action import Action
from rlam.executor import execute_action, ExecutionResult
from rlam.trace import ExecutionTrace
from rlam.replay import replay_action
from rlam.fork import fork_trace


def test_replay_returns_identical_output():
    """Replay must return the exact same output that was logged."""
    # Setup
    trace = ExecutionTrace()
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={"x": 5},
        parameters={},
        environment_hash="test_env",
        timestamp=datetime.now(timezone.utc)
    )
    
    # Execute and log
    result = execute_action(action, lambda x: x * 2)
    trace.add_result(result)
    
    # Replay
    replayed_output = replay_action(trace, "A1")
    
    # Assert: Output must be identical
    assert replayed_output == 10
    assert replayed_output == result.output


def test_replay_fails_on_unlogged_action():
    """Replay must fail if action was never logged."""
    trace = ExecutionTrace()
    
    # Assert: Replay unlogged action raises RuntimeError
    with pytest.raises(RuntimeError, match="does not exist in trace"):
        replay_action(trace, "A_NONEXISTENT")


def test_failure_stays_in_trace():
    """Failed actions must remain in trace with FAILED status."""
    # Setup
    trace = ExecutionTrace()
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash="test_env",
        timestamp=datetime.now(timezone.utc)
    )
    
    # Execute action that fails
    def failing_tool():
        raise ValueError("Expected failure")
    
    result = execute_action(action, failing_tool)
    trace.add_result(result)
    
    # Assert: Action exists in trace with FAILED status
    assert trace.has_action("A1")
    logged_result = trace.get_result("A1")
    assert logged_result["status"] == "FAILED"
    assert logged_result["error"] is not None


def test_fork_does_not_rerun_upstream():
    """Fork must copy actions without re-executing them."""
    # Setup: Create trace with action that has side effect
    execution_count = {"count": 0}
    
    def tool_with_side_effect(x):
        execution_count["count"] += 1
        return x * 2
    
    trace = ExecutionTrace()
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={"x": 5},
        parameters={},
        environment_hash="test_env",
        timestamp=datetime.now(timezone.utc)
    )
    
    # Execute once
    result = execute_action(action, tool_with_side_effect)
    trace.add_result(result)
    
    initial_count = execution_count["count"]
    assert initial_count == 1
    
    # Fork
    forked = fork_trace(trace, "A1")
    
    # Assert: No re-execution occurred
    assert execution_count["count"] == initial_count
    assert forked.has_action("A1")


def test_fork_creates_independent_trace():
    """Forked trace must be independent from original."""
    # Setup
    trace = ExecutionTrace()
    action1 = Action(
        action_id="A1",
        action_type="test",
        inputs={"x": 1},
        parameters={},
        environment_hash="test_env",
        timestamp=datetime.now(timezone.utc)
    )
    
    result1 = execute_action(action1, lambda x: x)
    trace.add_result(result1)
    
    # Fork at A1
    forked = fork_trace(trace, "A1")
    
    # Add action to original trace
    action2 = Action(
        action_id="A2",
        action_type="test",
        inputs={"x": 2},
        parameters={},
        environment_hash="test_env",
        timestamp=datetime.now(timezone.utc)
    )
    result2 = execute_action(action2, lambda x: x)
    trace.add_result(result2, parents=["A1"])
    
    # Assert: Forked trace is unaffected
    assert trace.has_action("A2")
    assert not forked.has_action("A2")
    assert forked.has_action("A1")


def test_cannot_add_duplicate_action():
    """Adding the same action ID twice must fail."""
    trace = ExecutionTrace()
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash="test_env",
        timestamp=datetime.now(timezone.utc)
    )
    
    result = execute_action(action, lambda: 1)
    trace.add_result(result)
    
    # Try to add same action ID again
    result2 = execute_action(action, lambda: 2)
    
    # Assert: Must raise RuntimeError
    with pytest.raises(RuntimeError, match="already exists in trace"):
        trace.add_result(result2)


def test_cannot_reference_unlogged_parent():
    """Adding action with unlogged parent must fail."""
    trace = ExecutionTrace()
    action = Action(
        action_id="A2",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash="test_env",
        timestamp=datetime.now(timezone.utc)
    )
    
    result = execute_action(action, lambda: 1)
    
    # Assert: Must raise RuntimeError for missing parent
    with pytest.raises(RuntimeError, match="not logged"):
        trace.add_result(result, parents=["A1_MISSING"])
