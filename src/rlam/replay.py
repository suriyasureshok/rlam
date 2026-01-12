"""
Replay mechanism for reproducibility-constrained workflows.

This module provides the replay functionality that enables retrieving
previously executed action outputs without re-execution. Replay
preserves the core reproducibility guarantee by ensuring that
only logged actions can be replayed.

Notes
-----
Replay is distinct from re-execution. It returns the exact logged
output value, maintaining deterministic behavior.
"""
from rlam.trace import ExecutionTrace
from typing import Any


def replay_action(trace: ExecutionTrace, action_id: str) -> Any:
    """
    Replay an action by retrieving its logged output.

    Replay returns the exact output value that was logged during
    execution, without re-executing the action. This preserves
    reproducibility by ensuring deterministic behavior.

    Parameters
    ----------
    trace : ExecutionTrace
        Execution trace containing the action to replay.
    action_id : str
        ID of the action to replay.

    Returns
    -------
    Any
        The logged output value of the action.

    Raises
    ------
    RuntimeError
        If action is not in the execution trace.

    Notes
    -----
    This function does not re-execute the action or modify the trace.
    It enforces the logged-only execution principle by requiring
    the action to exist in the trace before replay.

    Examples
    --------
    >>> output = replay_action(trace, "A1")  # Returns logged output
    """
    # Enforce: Action must be logged
    trace.require_action(action_id)
    record = trace.get_result(action_id)
    return record["output"]
