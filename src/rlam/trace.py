from typing import List
import networkx as nx
from rlam.executor import ExecutionResult


class ExecutionTrace:
    """
    Directed acyclic graph capturing the provenance of executed actions.
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_result(
        self,
        result: ExecutionResult,
        parents: List[str] | None = None
    ):
        """
        Adds an executed action to the trace.

        :param result: ExecutionResult of the action
        :param parents: List of parent action_ids this action depends on
        """
        if parents is None:
            parents = []

        action_id = result.action.action_id

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
        """
        return self.graph.nodes[action_id]

    def has_action(self, action_id: str) -> bool:
        return action_id in self.graph.nodes
    
    def get_result(self, action_id: str):
        if action_id not in self.graph.nodes:
            raise KeyError(
                f"Action '{action_id}' does not exist in the execution trace."
            )
        return self.graph.nodes[action_id]

    def require_action(self, action_id: str):
        """
        Enforces the invariant that only logged actions may be referenced.
        """
        if action_id not in self.graph.nodes:
            raise RuntimeError(
                f"Invariant violation: action '{action_id}' was not logged."
            )
        
    def add_recovery(
        self,
        failed_action_id: str,
        recovery_result
    ):
        """
        Adds a recovery action explicitly linked to a failed action.
        """
        self.require_action(failed_action_id)

        failed_node = self.graph.nodes[failed_action_id]
        if failed_node["status"] != "FAILED":
            raise RuntimeError(
                f"Recovery can only be linked to a FAILED action "
                f"(action '{failed_action_id}' is not failed)."
            )

        self.add_result(recovery_result, parents=[failed_action_id])