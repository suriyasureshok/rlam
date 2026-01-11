from rlam.action import Action
from rlam.executor import execute_action
from rlam.trace import ExecutionTrace
from rlam.fork import fork_trace
from rlam.replay import replay_action
from rlam.utils import compute_environment_hash
from datetime import datetime


# --- Tool functions ---

def load_data(path: str):
    return [1, 2, 3, 4, 5]

def preprocess(data):
    return [x * 2 for x in data]

def train_model(data, lr: float):
    return {
        "weights": sum(data) * lr,
        "loss": 0.1 if lr < 0.05 else 0.5
    }


# =====================================================
# Original execution
# =====================================================

original_trace = ExecutionTrace()
env_hash = compute_environment_hash()

# A1: Load data
a1 = Action(
    action_id="A1",
    action_type="load_data",
    inputs={"path": "dummy.csv"},
    parameters={},
    environment_hash=env_hash,
    timestamp=datetime.utcnow()
)
r1 = execute_action(a1, load_data)
original_trace.add_result(r1)

# A2: Preprocess
a2 = Action(
    action_id="A2",
    action_type="preprocess",
    inputs={"data": r1.output},
    parameters={},
    environment_hash=env_hash,
    timestamp=datetime.utcnow()
)
r2 = execute_action(a2, preprocess)
original_trace.add_result(r2, parents=["A1"])

# A3: Train (original hyperparameter)
a3 = Action(
    action_id="A3",
    action_type="train_model",
    inputs={"data": r2.output},
    parameters={"lr": 0.01},
    environment_hash=env_hash,
    timestamp=datetime.utcnow()
)
r3 = execute_action(a3, train_model)
original_trace.add_result(r3, parents=["A2"])


# =====================================================
# Forked execution (hyperparameter change)
# =====================================================

forked_trace = fork_trace(original_trace, fork_point="A2")

# Reuse outputs via replay (NO re-execution)
replayed_data = replay_action(forked_trace, "A2")

# A3′: Train with modified hyperparameter
a3_prime = Action(
    action_id="A3_prime",
    action_type="train_model",
    inputs={"data": replayed_data},
    parameters={"lr": 0.001},  # modified
    environment_hash=env_hash,
    timestamp=datetime.utcnow()
)
r3_prime = execute_action(a3_prime, train_model)
forked_trace.add_result(r3_prime, parents=["A2"])


# --- Comparison ---
print("Original A3 output:", r3.output)
print("Forked A3′ output:", r3_prime.output)
