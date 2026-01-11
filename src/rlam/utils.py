import sys
import platform
import hashlib
from importlib.metadata import distributions


def compute_environment_hash() -> str:
    """
    Computes a deterministic hash representing the execution environment.
    This hash binds actions to a specific software context for auditability
    and reproducibility.
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
