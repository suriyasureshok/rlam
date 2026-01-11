from typing import Any, Optional, Callable, Literal
from pydantic import BaseModel
from rlam.action import Action


class ExecutionResult(BaseModel):
    """
    Represents the outcome of executing a single action.
    """
    action: Action
    output: Optional[Any]
    status: Literal["SUCCESS", "FAILED"]
    error: Optional[str]


def execute_action(action: Action, tool_fn: Callable[..., Any]) -> ExecutionResult:
    """
    Executes a single action deterministically.

    - No retries
    - No fallback
    - No mutation
    - All errors are captured and returned
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