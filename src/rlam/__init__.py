"""
R-LAM: Reproducibility-constrained Language Agentic Machine.

This package provides a framework for reproducible, provenance-tracked
execution of language model actions. R-LAM enforces strict reproducibility
guarantees through immutable actions, complete execution logging, and
deterministic replay/fork mechanisms.

Core Components
---------------
Action : Immutable action schemas with validation
ExecutionTrace : DAG-based provenance tracking
Executor : Action execution with logging
Replay : Deterministic output retrieval
Fork : Controlled execution branching

Notes
-----
R-LAM treats execution as first-class data. The core invariant is that
an action that is not logged is treated as non-existent. All operations
preserve provenance and enable auditability.
"""