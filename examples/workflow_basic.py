from rlam.action import Action
from rlam.executor import execute_action
from rlam.trace import ExecutionTrace
from rlam.utils import compute_environment_hash
from datetime import datetime


# --- Tool functions (deterministic, simple) ---

def load_data(path: str):
    return [1, 2, 3, 4, 5]

def preprocess(data):
    return [x * 2 for x in data]

def train_model(data, lr: float):
    return {
        "weights": sum(data) * lr,
        "loss": 0.1
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
    timestamp=datetime.now(datetime.timezone.utc)
)

r2 = execute_action(a2, preprocess)
trace.add_result(r2, parents=["A1"])


# --- Action A3: Train model ---
a3 = Action(
    action_id="A3",
    action_type="train_model",
    inputs={"data": r2.output},
    parameters={"lr": 0.01},
    environment_hash=env_hash,
    timestamp=datetime.now(datetime.timezone.utc)
)

r3 = execute_action(a3, train_model)
trace.add_result(r3, parents=["A2"])


# --- Sanity check ---
print("Final model output:", r3.output)