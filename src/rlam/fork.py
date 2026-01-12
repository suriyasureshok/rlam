"""
Fork mechanism for controlled experimentation in workflows.

This module provides the fork functionality that enables creating
independent execution branches from existing traces. Forking
preserves provenance while allowing controlled divergence for
experimentation and alternative execution paths.

Notes
-----
Forking creates a new trace that can diverge from the original,
enabling exploration of alternative execution paths without
contaminating the original provenance record.
"""
import networkx as nx
from rlam.trace import ExecutionTrace


def fork_trace(original_trace: ExecutionTrace, fork_point: str) -> ExecutionTrace:
    """
    Create a new ExecutionTrace by branching from an existing trace.

    Forking creates an independent execution path that diverges from
    the original trace at the specified fork point. The new trace
    contains all actions up to and including the fork point, but
    can then diverge with new actions.

    Parameters
    ----------
    original_trace : ExecutionTrace
        Source execution trace to fork from.
    fork_point : str
        Action ID where the fork should branch.

    Returns
    -------
    ExecutionTrace
        New execution trace containing actions up to the fork point.

    Raises
    ------
    RuntimeError
        If fork point is not in the original trace.

    Notes
    -----
    This function does not re-execute actions or modify the original trace.
    It preserves all provenance from the original trace while enabling
    controlled experimentation through branching.

    Examples
    --------
    >>> forked = fork_trace(original, "A2")  # Returns new ExecutionTrace
    >>> # forked contains actions up to A2 and can now diverge
    """
    # Enforce: Fork point must exist in original trace
    original_trace.require_action(fork_point)

    new_trace = ExecutionTrace()

    # Copy nodes and edges in topological order (DAG traversal)
    for node in nx.topological_sort(original_trace.graph):
        node_data = original_trace.graph.nodes[node]
        new_trace.graph.add_node(node, **node_data)

        # Copy incoming edges (preserve dependencies)
        for parent in original_trace.graph.predecessors(node):
            new_trace.graph.add_edge(parent, node)

        # Stop at fork point (don't copy actions after this)
        if node == fork_point:
            break

    return new_trace
