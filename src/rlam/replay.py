from rlam.trace import ExecutionTrace


def replay_action(trace: ExecutionTrace, action_id: str):
    """
    Replays an action by reusing its logged output.

    Replay does NOT re-execute the action. If the action
    is not present in the execution trace, replay fails.
    """
    trace.require_action(action_id)
    record = trace.get_result(action_id)
    return record["output"]
