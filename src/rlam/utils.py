"""
Utility functions for environment and system information.

This module provides utilities for computing environment hashes
and other system-level operations that support reproducibility
and auditability in R-LAM workflows.

Notes
-----
Environment hashing binds actions to specific software contexts,
enabling deterministic execution and audit trails.
"""
import sys
import platform
import hashlib
from importlib.metadata import distributions


def compute_environment_hash() -> str:
    """
    Compute a deterministic hash representing the execution environment.

    This hash captures the Python version, operating system platform,
    and installed package versions to create a unique identifier
    for the execution environment.

    Returns
    -------
    str
        SHA256 hash of the environment representation.

    Notes
    -----
    The environment hash binds actions to a specific software context
    for auditability and reproducibility. Changes in Python version,
    OS platform, or package versions will result in different hashes.

    Examples
    --------
    >>> env_hash = compute_environment_hash()
    >>> print(env_hash)  # e.g., 'a1b2c3d4...'
    """
    python_version = sys.version
    os_platform = platform.platform()

    packages = sorted(
        [(dist.metadata["Name"], dist.version) for dist in distributions()]
    )

    env_repr = {
        "python_version": python_version,
        "os_platform": os_platform,
        "packages": packages,
    }

    env_string = repr(env_repr).encode("utf-8")
    return hashlib.sha256(env_string).hexdigest()
