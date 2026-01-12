# R-LAM: Reproducibility-Constrained Large Action Models

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**R-LAM** is a reproducibility-constrained execution framework for Large Action Models in scientific workflow automation. It enables adaptive, agent-driven workflow execution while enforcing strict guarantees on auditability, determinism, and replayability.

> **Research Artifact:** R-LAM is a lightweight research prototype (v0.1.0) demonstrating reproducibility constraints in LAM-based execution. This is NOT production software.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Design Principles](#design-principles)
- [Core Concepts](#core-concepts)
- [Minimal Example](#minimal-example)
- [Failure Handling](#failure-handling)
- [Replay and Forking](#replay-and-forking)
- [What This Is NOT](#what-this-is-not)
- [Non-Goals](#non-goals)
- [Limitations](#limitations)
- [Citation](#citation)

## Overview

Large Action Models enable autonomous tool execution but lack reproducibility guarantees required for scientific workflows.

**R-LAM enforces:**
- Immutable action schemas (no implicit state)
- Deterministic execution (no retries, no fallbacks)
- Complete provenance logging (logged-only execution)
- Explicit failure handling (no silent recovery)

## Key Features

- **Reproducibility by Design**: Immutable action schema, deterministic execution, and complete provenance logging
- **Execution Trace Graphs**: DAG-based trace store with complete lineage and auditable history
- **Replay and Forking**: Output reuse and controlled divergence for exploratory experimentation
- **Failure Handling**: First-class failures with explicit recovery and no silent corruption

## Design Principles

1. **Reproducibility as a First-Class Constraint**: Every design decision prioritizes reproducibility over convenience
2. **Explicit Over Implicit**: All execution intent must be explicitly represented before execution
3. **Logged-Only Execution**: Any side effect not reflected in the execution trace is invalid
4. **Separation of Concerns**: Action selection (LAM) is decoupled from action execution (engine)
5. **Failure Transparency**: Failures are first-class events, never hidden or silently recovered

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

## Minimal Example

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

## Failure Handling

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

## Replay and Forking

```python
from rlam.examples.workflow_fork import run_fork_workflow

original_trace, forked_trace = run_fork_workflow()

# Compare results
original_result = original_trace.get_result("A3")
forked_result = forked_trace.get_result("A3_prime")

print(f"Original output: {original_result.output}")
print(f"Forked output: {forked_result.output}")
```

## What This Is NOT

R-LAM is **not**:
- A production workflow engine (use Airflow, Prefect, etc.)
- A general-purpose LLM agent framework (use LangChain, AutoGPT, etc.)
- A distributed execution system (single-machine only)
- A cyber-physical system controller (no hardware interaction)
- Optimized for performance (optimized for correctness)
- Feature-complete software (research prototype)
## Non-Goals

R-LAM explicitly **does not**:
- Support asynchronous or concurrent execution
- Implement automatic retry logic or error recovery
- Provide agent intelligence or action selection (LAM's responsibility)
- Scale to production workloads (100+ actions)
- Handle streaming data or real-time execution
- Integrate with cloud platforms or orchestration systems
- Optimize execution performance or resource usage

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

## Limitations

**By Design:**
- Single-machine execution only (no distribution)
- Synchronous execution only (no async/await)
- Small-scale workflows only (<100 actions)
- No agent intelligence (action selection external)

**Technical:**
- No hardware/cyber-physical system support
- No streaming or real-time processing
- No cloud integration or orchestration
- Inherits LLM limitations (non-determinism, hallucination)

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

Check out the [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

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

### Documentation

R-LAM uses NumPy-style docstrings for all public modules, classes, and functions. Docstrings follow the standard NumPy format with:

- **Parameters**: Detailed parameter descriptions with types
- **Returns**: Return value descriptions with types  
- **Raises**: Exception descriptions
- **Notes**: Implementation details and design rationale
- **Examples**: Usage examples where applicable

All documentation is generated from docstrings and should be kept current with code changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **Suriya Sureshkumar** - [suriyasureshkumarkannian@gmail.com](mailto:suriyasureshkumarkannian@gmail.com)

## Acknowledgments

This work was conducted at the Department of AI & Data Science, RMK Engineering College, Chennai, India.

## Contact

For questions, issues, or collaboration opportunities:
- GitHub Issues: [https://github.com/suriyasureshok/rlam/issues](https://github.com/suriyasureshok/rlam/issues)
- Email: suriyasureshkumarkannian@gmail.com

---

**R-LAM** - Making Large Action Models reproducible for scientific research.