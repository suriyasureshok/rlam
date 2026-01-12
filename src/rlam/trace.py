"""
Execution trace management for reproducibility-constrained workflows.

This module defines the data structures and operations required to
record, query, and replay execution traces produced by R-LAM.
It enforces strict provenance guarantees by treating all executed
actions as immutable trace nodes.

Notes
-----
This module does not perform execution or reasoning.
It is purely responsible for provenance representation.
"""
from typing import List
import networkx as nx
from rlam.executor import ExecutionResult


class ExecutionTrace:
    """
    Directed acyclic graph capturing the provenance of executed actions.

    ExecutionTrace maintains a DAG where nodes represent executed actions
    and edges represent data/control dependencies between actions.
    This structure enables provenance tracking, replay, and auditing.

    Notes
    -----
    The core invariant is that an action that is not logged is treated
    as non-existent. Any reference to an unlogged action violates
    the logged-only execution principle.
    """

    def __init__(self):
        """Initialize an empty execution trace."""
        self.graph = nx.DiGraph()

    def add_result(
        self,
        result: ExecutionResult,
        parents: List[str] | None = None
    ):
        """
        Add an executed action to the execution trace.

        Parameters
        ----------
        result : ExecutionResult
            Result of the executed action.
        parents : list of str, optional
            IDs of parent actions this action depends on.

        Raises
        ------
        RuntimeError
            If action already exists or parent dependencies are not logged.

        Notes
        -----
        Enforces the invariant that all dependencies must exist before
        dependent actions can be added to the trace.
        """
        if parents is None:
            parents = []

        action_id = result.action.action_id
        
        # Enforce: No duplicate action IDs
        if action_id in self.graph.nodes:
            raise RuntimeError(
                f"Invariant violation: Action '{action_id}' already exists in trace. "
                "Actions cannot be re-logged."
            )
        
        # Enforce: All dependencies must be logged
        for parent_id in parents:
            if parent_id not in self.graph.nodes:
                raise RuntimeError(
                    f"Invariant violation: Parent action '{parent_id}' not logged. "
                    "Dependencies must exist before dependent actions."
                )

        # Add node with full execution metadata
        self.graph.add_node(
            action_id,
            action=result.action,
            output=result.output,
            status=result.status,
            error=result.error
        )

        # Add dependency edges
        for parent_id in parents:
            self.graph.add_edge(parent_id, action_id)

    def get_result(self, action_id: str):
        """
        Retrieve the execution record for a given action.

        Parameters
        ----------
        action_id : str
            ID of the action to retrieve.

        Returns
        -------
        dict
            Node data containing action, output, status, and error.

        Raises
        ------
        RuntimeError
            If action is not in the execution trace.
        """
        if action_id not in self.graph.nodes:
            raise KeyError(
                f"Action '{action_id}' does not exist in the execution trace."
            )
        return self.graph.nodes[action_id]

    def has_action(self, action_id: str) -> bool:
        """
        Check if an action exists in the execution trace.

        Parameters
        ----------
        action_id : str
            ID of the action to check.

        Returns
        -------
        bool
            True if action exists in trace, False otherwise.
        """
        return action_id in self.graph.nodes
    
    def require_action(self, action_id: str):
        """
        Enforce the logged-only execution invariant.

        Parameters
        ----------
        action_id : str
            ID of the action to validate.

        Raises
        ------
        RuntimeError
            If action is not in the execution trace.

        Notes
        -----
        This method centralizes the core invariant that only logged
        actions may be referenced. Any unlogged action reference
        violates the logged-only execution principle.
        """
        if action_id not in self.graph.nodes:
            raise RuntimeError(
                f"Invariant violation: Action '{action_id}' does not exist in trace. "
                "Only logged actions may be referenced (logged-only execution)."
            )
        
    def add_recovery(
        self,
        failed_action_id: str,
        recovery_result
    ):
        """
        Add a recovery action explicitly linked to a failed action.

        Parameters
        ----------
        failed_action_id : str
            ID of the failed action being recovered from.
        recovery_result : ExecutionResult
            Result of the recovery action execution.

        Raises
        ------
        RuntimeError
            If failed action doesn't exist or is not in FAILED status.

        Notes
        -----
        Recovery actions must be explicitly linked to failures.
        Failures are first-class events and cannot be silently recovered.
        """
        # Enforce: Failed action must exist in trace
        self.require_action(failed_action_id)

        # Enforce: Recovery only valid for FAILED actions
        failed_node = self.graph.nodes[failed_action_id]
        if failed_node["status"] != "FAILED":
            raise RuntimeError(
                f"Invariant violation: Recovery requires FAILED status. "
                f"Action '{failed_action_id}' has status '{failed_node['status']}'. "
                "Only failed actions may have recovery actions."
            )

        # Recovery action becomes child of failed action in trace DAG
        self.add_result(recovery_result, parents=[failed_action_id])