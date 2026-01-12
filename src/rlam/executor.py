"""
Deterministic action execution engine.

This module provides the execution engine that runs actions
deterministically without retries, fallbacks, or implicit state
modification. All execution outcomes are captured explicitly
for provenance tracking.

Notes
-----
Execution is designed to be deterministic and side-effect free
to support reproducible replay and auditing.
"""
from typing import Any, Optional, Callable, Literal
from pydantic import BaseModel
from rlam.action import Action


class ExecutionResult(BaseModel):
    """
    Result of executing a single action.

    Contains the outcome of an action execution, including
    success/failure status, outputs, and error information.

    Parameters
    ----------
    action : Action
        The action that was executed.
    output : Any, optional
        Output produced by successful execution.
    status : {"SUCCESS", "FAILED"}
        Execution outcome status.
    error : str, optional
        Error message if execution failed.
    """
    action: Action
    output: Optional[Any] = None
    status: Literal["SUCCESS", "FAILED"]
    error: Optional[str] = None


def execute_action(action: Action, tool_fn: Callable[..., Any]) -> ExecutionResult:
    """
    Execute a single action deterministically.

    This function performs execution without retries,
    fallback logic, or implicit state modification.
    All execution outcomes are returned explicitly.

    Parameters
    ----------
    action : Action
        The action to execute.
    tool_fn : callable
        Function that performs the actual execution logic.

    Returns
    -------
    ExecutionResult
        Result object containing status, outputs, and errors.

    Notes
    -----
    Execution is deterministic and does not modify any global state.
    Failed executions are captured explicitly rather than raised as exceptions.
    """
    try:
        output = tool_fn(**action.inputs, **action.parameters)
        return ExecutionResult(
            action=action,
            output=output,
            status="SUCCESS",
            error=None
        )
    except Exception as e:
        return ExecutionResult(
            action=action,
            output=None,
            status="FAILED",
            error=str(e)
        )