from rlam.action import Action
from rlam.executor import execute_action
from rlam.trace import ExecutionTrace
from rlam.utils import compute_environment_hash
from datetime import datetime


# --- Tool functions ---

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


# --- Initialize trace ---
trace = ExecutionTrace()
env_hash = compute_environment_hash()


# --- Action A1: Load data ---
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


# --- Action A2: Preprocess ---
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


# --- Action A3: Train model (FAILURE) ---
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


# --- Action A4: Recovery ---
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


# --- Sanity check ---
print("A3 status:", r3.status)
print("A3 error:", r3.error)
print("A4 recovery output:", r4.output)
