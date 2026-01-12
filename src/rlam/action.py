"""
Action schema definition for reproducibility-constrained workflows.

This module defines the immutable Action class that serves as the
fundamental unit of reproducible execution in R-LAM. Actions encapsulate
all information required to execute, audit, and replay workflow steps
while enforcing strict immutability guarantees.

Notes
-----
Actions are designed to be immutable by construction to prevent
accidental state corruption during execution and replay.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone


class Action(BaseModel):
    """
    Immutable representation of a single executable action.

    An Action is the smallest reproducible unit in R-LAM.
    It encapsulates all information required to execute,
    audit, and replay a step in a scientific workflow.

    Parameters
    ----------
    action_id : str
        Unique identifier for the action instance.
    action_type : str
        Action category (e.g., tool invocation, script execution).
    inputs : dict
        Input artifacts required for execution.
    parameters : dict
        Configuration values controlling execution behavior.
    environment_hash : str
        Hash of the execution environment for reproducibility.
    timestamp : datetime
        Creation time of the action.

    Notes
    -----
    Action objects are immutable by design to ensure reproducible
    execution. Any mutation must be represented as a new Action.
    """
    model_config = ConfigDict(frozen=True)  # Enforce immutability invariant
    
    action_id: str
    action_type: str
    inputs: Dict[str, Any]
    parameters: Dict[str, Any]
    environment_hash: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
