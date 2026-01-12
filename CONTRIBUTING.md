# Contributing to R-LAM

Thank you for your interest in contributing to R-LAM! This document provides guidelines for contributing to the project.

## Research Artifact Status

R-LAM is a **research prototype** (v0.1.0) demonstrating reproducibility constraints in Large Action Model execution. Contributions should prioritize clarity, reproducibility, and documentation over performance or feature completeness.

## Development Setup

### Prerequisites
- Python 3.10 or higher
- Git

### Setup Steps

```bash
# Clone repository
git clone https://github.com/suriyasureshok/rlam.git
cd rlam

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
pytest
```

## Contribution Workflow

1. **Open an Issue**: For major changes, open an issue first to discuss your proposal
2. **Fork & Branch**: Fork the repository and create a feature branch
3. **Make Changes**: Implement your changes following the guidelines below
4. **Test**: Ensure all tests pass and add new tests for new functionality
5. **Submit PR**: Open a Pull Request with a clear description of your changes

## Guidelines

### Code Style

- Follow PEP 8 for Python code style
- Use type hints for all function parameters and return values
- Use timezone-aware datetimes: `datetime.now(timezone.utc)`
- Maintain immutability where applicable (especially for Actions)

### Documentation

R-LAM uses **NumPy-style docstrings** for all public modules, classes, and functions:

```python
def example_function(param: str, value: int) -> bool:
    """
    Brief one-line description.
    
    More detailed explanation if needed.
    
    Parameters
    ----------
    param : str
        Description of param.
    value : int
        Description of value.
    
    Returns
    -------
    bool
        Description of return value.
    
    Raises
    ------
    ValueError
        When value is invalid.
    
    Notes
    -----
    Additional implementation details or design rationale.
    
    Examples
    --------
    >>> example_function("test", 42)
    True
    """
```

### Testing

- Write comprehensive unit tests for all new functionality
- Tests should verify both success and failure cases
- Use descriptive test names: `test_action_immutability_prevents_modification`
- Maintain test coverage for core invariants
- All tests must pass before submitting a PR

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/rlam --cov-report=html
```

### Design Principles

When contributing, keep R-LAM's core design principles in mind:

1. **Reproducibility First**: Every design decision prioritizes reproducibility
2. **Explicit Over Implicit**: All execution intent must be explicitly represented
3. **Logged-Only Execution**: Side effects not in trace are invalid
4. **Immutability**: Actions and execution results should be immutable
5. **Failure Transparency**: Failures are first-class events, never hidden

## What to Contribute

### Welcome Contributions

- Bug fixes with test cases
- Documentation improvements
- Additional test cases for edge cases
- Performance optimizations that maintain reproducibility guarantees
- Examples demonstrating R-LAM usage patterns
- Improvements to error messages and debugging aids

### Not Suitable

- Breaking changes to core reproducibility guarantees
- Features that compromise determinism
- Silent error recovery mechanisms
- Mutable action modifications

## Questions?

For questions or discussions:
- Open an issue on GitHub: https://github.com/suriyasureshok/rlam/issues
- Email: suriyasureshkumarkannian@gmail.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make Large Action Models reproducible for scientific research!**
