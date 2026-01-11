import networkx as nx
from rlam.trace import ExecutionTrace


def fork_trace(original_trace: ExecutionTrace, fork_point: str) -> ExecutionTrace:
    """
    Creates a new execution trace by copying the prefix of an existing trace
    up to (and including) the specified fork point.

    No actions are re-executed during forking.
    """
    original_trace.require_action(fork_point)

    new_trace = ExecutionTrace()

    # Copy nodes and edges in topological order
    for node in nx.topological_sort(original_trace.graph):
        node_data = original_trace.graph.nodes[node]
        new_trace.graph.add_node(node, **node_data)

        # Copy incoming edges
        for parent in original_trace.graph.predecessors(node):
            new_trace.graph.add_edge(parent, node)

        if node == fork_point:
            break

    return new_trace
