from rlam.action import Action
from rlam.executor import execute_action
from rlam.trace import ExecutionTrace
from rlam.utils import compute_environment_hash
from datetime import datetime


def run_failure_workflow() -> ExecutionTrace:
    """
    Execute a workflow demonstrating failure handling and recovery.
    
    This workflow performs four actions:
    - A1: Load data from a file
    - A2: Preprocess the loaded data
    - A3: Attempt to train a model (intentionally fails)
    - A4: Recovery training with corrected parameters
    
    Returns:
        ExecutionTrace: Complete trace including failed and recovery actions
    """
    trace = ExecutionTrace()
    env_hash = compute_environment_hash()

    def load_data(path: str):
        return [1, 2, 3, 4, 5]

    def preprocess(data):
        return [x * 2 for x in data]
    
    def train_model_fail(data, lr: float):
        # Intentionally fail for demonstration
        raise RuntimeError("Numerical instability during training")

    def train_model_recovery(data, lr: float):
        # Recovery version with safer parameters
        return {
            "weights": sum(data) * lr,
            "loss": 0.2
        }

    a1 = Action(
        action_id="A1",
        action_type="load_data",
        inputs={"path": "dummy.csv"},
        parameters={},
        environment_hash=env_hash,
        timestamp=datetime.utcnow()
    )
    r1 = execute_action(a1, load_data)
    trace.add_result(r1)

    a2 = Action(
        action_id="A2",
        action_type="preprocess",
        inputs={"data": r1.output},
        parameters={},
        environment_hash=env_hash,
        timestamp=datetime.utcnow()
    )
    r2 = execute_action(a2, preprocess)
    trace.add_result(r2, parents=["A1"])

    a3 = Action(
        action_id="A3",
        action_type="train_model",
        inputs={"data": r2.output},
        parameters={"lr": 10.0},  # intentionally bad
        environment_hash=env_hash,
        timestamp=datetime.utcnow()
    )
    r3 = execute_action(a3, train_model_fail)
    trace.add_result(r3, parents=["A2"])

    a4 = Action(
        action_id="A4",
        action_type="train_model_recovery",
        inputs={"data": r2.output},
        parameters={"lr": 0.01},
        environment_hash=env_hash,
        timestamp=datetime.utcnow()
    )
    r4 = execute_action(a4, train_model_recovery)
    trace.add_result(r4, parents=["A3"])

    return trace

if __name__ == "__main__":
    execution_trace = run_failure_workflow()
    print(execution_trace)