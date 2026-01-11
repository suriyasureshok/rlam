# R-LAM: Reproducibility-Constrained Large Action Models

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**R-LAM** is a reproducibility-constrained execution framework for Large Action Models in scientific workflow automation. It enables adaptive, agent-driven workflow execution while enforcing strict guarantees on auditability, determinism, and replayability.

> **Note:** R-LAM is a lightweight research artifact, not a full workflow engine. It demonstrates how reproducibility constraints can be systematically integrated into LAM-based execution.

## Overview

Large Action Models (LAMs) extend large language models by enabling autonomous decision-making and tool execution. However, scientific workflows impose strict requirements on reproducibility, auditability, and deterministic execution that generic LLM-based agents don't satisfy.

R-LAM addresses this gap by:
- **Treating actions as structured, first-class entities** with explicit schemas
- **Enforcing deterministic execution policies** that separate reasoning from execution
- **Recording complete execution traces** for provenance and replay
- **Supporting failure-aware execution** and controlled workflow forking

## Key Features

### Reproducibility by Design
- **Immutable Action Schema**: All actions are structured, declarative objects with complete metadata
- **Deterministic Execution**: Fixed execution order, controlled randomness, and explicit environment binding
- **Provenance Logging**: Every executed action produces a complete provenance record

### Execution Trace Graphs
- **DAG-based Trace Store**: Directed acyclic graph representation of workflow execution
- **Complete Lineage**: Explicit data and control dependencies between actions
- **Auditable History**: All state transitions are observable and verifiable

### Replay and Forking
- **Output Reuse**: Replay workflows by reusing logged action outputs (no re-execution)
- **Controlled Divergence**: Fork execution traces to explore parameter variations
- **Exploratory Experimentation**: Support what-if analysis without contaminating original traces

### Failure Handling
- **First-Class Failures**: Failed actions remain in the execution trace
- **Explicit Recovery**: Recovery actions are explicitly linked to failures
- **No Silent Corruption**: All failures and recovery attempts are fully logged

## Installation

### From PyPI (Coming Soon)
```bash
pip install rlam
```

### From Source
```bash
git clone https://github.com/suriyasureshok/rlam.git
cd rlam
pip install -e .
```

### Requirements
- Python >= 3.10
- pydantic >= 2.0
- networkx >= 3.0

## Quick Start

### Basic Workflow

```python
from rlam.action import Action
from rlam.executor import execute_action
from rlam.trace import ExecutionTrace
from rlam.utils import compute_environment_hash
from datetime import datetime

# Initialize trace and environment
trace = ExecutionTrace()
env_hash = compute_environment_hash()

# Define action
action = Action(
    action_id="A1",
    action_type="load_data",
    inputs={"path": "data.csv"},
    parameters={},
    environment_hash=env_hash,
    timestamp=datetime.utcnow()
)

# Execute action
result = execute_action(action, lambda path: [1, 2, 3, 4, 5])
trace.add_result(result)
```

### Workflow with Failure Recovery

```python
from rlam.examples.workflow_failure import run_failure_workflow

trace = run_failure_workflow()

# Inspect failure
failed_action = trace.get_result("A3")
print(f"Status: {failed_action.status}")
print(f"Error: {failed_action.error}")

# Check recovery
recovery_action = trace.get_result("A4")
print(f"Recovery status: {recovery_action.status}")
```

### Workflow Forking

```python
from rlam.examples.workflow_fork import run_fork_workflow

original_trace, forked_trace = run_fork_workflow()

# Compare results
original_result = original_trace.get_result("A3")
forked_result = forked_trace.get_result("A3_prime")

print(f"Original output: {original_result.output}")
print(f"Forked output: {forked_result.output}")
```

## Project Structure

```
rlam/
├── src/rlam/              # Core framework implementation
│   ├── action.py          # Action schema definition
│   ├── executor.py        # Deterministic execution engine
│   ├── trace.py           # Execution trace store (DAG)
│   ├── replay.py          # Replay mechanism
│   ├── fork.py            # Forking mechanism
│   └── utils.py           # Environment hashing utilities
├── examples/              # Example workflows
│   ├── workflow_basic.py  # Linear success workflow
│   ├── workflow_failure.py # Failure + recovery workflow
│   └── workflow_fork.py   # Replay and forking workflow
├── tests/                 # Test suite
├── pyproject.toml         # Package configuration
├── LICENSE                # MIT License
└── README.md              # This file
```

## Core Concepts

### Action Schema
An action is the smallest unit of executable behavior, defined as:
```python
Action = {
    action_id: str,          # Unique identifier
    action_type: str,        # Execution primitive
    inputs: dict,            # Required data
    parameters: dict,        # Configuration values
    environment_hash: str,   # Execution context
    timestamp: datetime      # Execution time
}
```

### Execution Trace
A directed acyclic graph (DAG) where:
- **Nodes** represent executed actions with their inputs, outputs, and status
- **Edges** encode data and control dependencies
- **Invariant**: An action that is not logged is treated as non-existent

### Replay vs Re-execution
- **Replay**: Reconstruct outcomes by reusing logged action outputs
- **Re-execution**: Run actions again (may introduce non-determinism)
- R-LAM uses replay to prevent non-deterministic behavior

## Examples

Three complete workflow examples are included:

1. **workflow_basic.py**: Demonstrates successful linear execution (A1 → A2 → A3)
2. **workflow_failure.py**: Shows failure handling with explicit recovery
3. **workflow_fork.py**: Illustrates replay and forking for parameter exploration

Run examples:
```bash
python examples/workflow_basic.py
python examples/workflow_failure.py
python examples/workflow_fork.py
```

## Design Principles

1. **Reproducibility as a First-Class Constraint**: Every design decision prioritizes reproducibility over convenience
2. **Explicit Over Implicit**: All execution intent must be explicitly represented before execution
3. **Logged-Only Execution**: Any side effect not reflected in the execution trace is invalid
4. **Separation of Concerns**: Action selection (LAM) is decoupled from action execution (engine)
5. **Failure Transparency**: Failures are first-class events, never hidden or silently recovered

## Limitations

- **Scale**: Designed for representative workflows, not production-scale pipelines
- **Hardware**: No support for physical instruments or cyber-physical systems
- **LLM Dependency**: Inherits limitations of underlying language models
- **Scope**: Research artifact, not a replacement for production workflow engines

## Citation

If you use R-LAM in your research, please cite:

```bibtex
@article{rlam2026,
  title={R-LAM: Reproducibility-Constrained Large Action Models for Scientific Workflow Automation},
  author={Sureshkumar, Suriya and Nilash X, Ivan},
  journal={IEEE Conference Proceedings},
  year={2026}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
# Clone repository
git clone https://github.com/suriyasureshok/rlam.git
cd rlam

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Suriya Sureshkumar** - [suriyasureshkumarkannian@gmail.com](mailto:suriyasureshkumarkannian@gmail.com)
- **Ivan Nilash X** - [ivannilash1206@gmail.com](mailto:ivannilash1206@gmail.com)

*Both authors contributed equally to this work.*

## Acknowledgments

This work was conducted at the Department of AI & Data Science, RMK Engineering College, Chennai, India.

## Contact

For questions, issues, or collaboration opportunities:
- GitHub Issues: [https://github.com/suriyasureshok/rlam/issues](https://github.com/suriyasureshok/rlam/issues)
- Email: suriyasureshkumarkannian@gmail.com

---

**R-LAM** - Making Large Action Models reproducible for scientific research.