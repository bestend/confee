# Contributing to confee ☕️

Thank you for considering contributing to confee! This document provides guidelines and instructions for contributing to the project.

---

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/bestend/confee.git
   cd confee
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev,all]"
   ```

   This installs:
   - `confee` in editable mode
   - All optional dependencies (CLI, remote, TOML support)
   - Development tools (pytest, ruff, mypy, etc.)

---

## 🧪 Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_config.py
```

### Run specific test function
```bash
pytest tests/test_config.py::TestConfigBase::test_basic_config
```

### Run with coverage report
```bash
pytest --cov=confee --cov-report=html
```

View the HTML coverage report:
```bash
open htmlcov/index.html  # On macOS
```

### Run tests in watch mode (requires pytest-watch)
```bash
pip install pytest-watch
ptw
```

---

## 🔍 Code Quality

We use several tools to maintain code quality. Run these before submitting a PR:

### Linting with ruff
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

### Type checking with mypy
```bash
mypy src/
```

### Run all checks
```bash
# Lint + format + type check
ruff check . --fix && ruff format . && mypy src/ && pytest
```

---

## 📋 Code Style Guidelines

### General Principles
- Follow PEP 8 and Google-style docstrings
- Use type hints for all function signatures
- Write descriptive variable and function names
- Keep functions small and focused (single responsibility)
- Prefer explicit over implicit

### Docstring Format
```python
def load_config(path: str, format: str = "yaml") -> dict:
    """Load configuration from a file.

    Args:
        path: Path to the configuration file
        format: Configuration format (yaml, json, toml)

    Returns:
        Parsed configuration as a dictionary

    Raises:
        FileNotFoundError: If the config file doesn't exist
        ValueError: If the format is unsupported

    Examples:
        >>> config = load_config("config.yaml")
        >>> config = load_config("config.json", format="json")
    """
    ...
```

### Type Hints
```python
# Good
def process_config(config: dict[str, Any]) -> ConfigBase:
    ...

# Bad (no type hints)
def process_config(config):
    ...
```

### Imports
- Use absolute imports from `confee` package
- Group imports: stdlib → third-party → local
- Sort imports alphabetically within groups (ruff handles this)

```python
# Standard library
import json
from pathlib import Path
from typing import Any

# Third-party
import yaml
from pydantic import BaseModel

# Local
from confee.config import ConfigBase
from confee.loaders import ConfigLoader
```

---

## 🧩 Project Structure

```
confee/
├── src/confee/           # Source code
│   ├── __init__.py       # Public API exports
│   ├── config.py         # ConfigBase and SecretField
│   ├── loaders.py        # Sync file loading
│   ├── async_loader.py   # Async file loading
│   ├── overrides.py      # CLI/env override handling
│   ├── parser.py         # Config parsing logic
│   ├── plugins.py        # Plugin registry system
│   ├── schema.py         # JSON schema generation
│   ├── colors.py         # Terminal color utilities
│   ├── help_formatter.py # CLI help generation
│   └── error_formatter.py # Error message formatting
├── tests/                # Test files (mirror src/ structure)
│   ├── test_config.py
│   ├── test_loaders.py
│   ├── test_secrets.py
│   └── ...
├── examples/             # Usage examples
├── pyproject.toml        # Project configuration
├── README.md             # User documentation
├── ARCHITECTURE.md       # System architecture docs
└── CONTRIBUTING.md       # This file
```

---

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Minimal reproducible example**
   ```python
   from confee import ConfigBase

   class MyConfig(ConfigBase):
       name: str

   # This causes the bug:
   config = MyConfig.load(...)
   ```
3. **Expected behavior** vs **actual behavior**
4. **Environment details**:
   - Python version (`python --version`)
   - confee version (`pip show confee`)
   - Operating system

---

## ✨ Contributing Features

### Before Starting
1. **Check existing issues** to avoid duplicate work
2. **Open an issue** to discuss the feature before implementing
3. **Get feedback** on the design before writing code

### Feature Development Workflow
1. Create a new branch: `git checkout -b feature/my-feature`
2. Write tests first (TDD approach recommended)
3. Implement the feature
4. Ensure all tests pass: `pytest`
5. Run code quality checks: `ruff check . --fix && mypy src/`
6. Update documentation if needed
7. Commit with descriptive messages (see below)
8. Push and open a pull request

### Commit Message Format
```
<type>: <short summary>

<detailed description if needed>

Fixes #<issue-number>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring (no functionality change)
- `perf`: Performance improvements
- `chore`: Tooling, dependencies, etc.

**Examples**:
```
feat: add support for .ini file format

Implements plugin-based .ini loader using configparser.
Includes tests and documentation.

Fixes #42
```

```
fix: prevent freeze() from affecting new instances

Each config instance now tracks its own frozen state
independently using instance IDs.

Fixes #67
```

---

## 🔄 Pull Request Process

### Before Submitting
- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`ruff format .`)
- [ ] No linting errors (`ruff check .`)
- [ ] Type checks pass (`mypy src/`)
- [ ] Added tests for new functionality
- [ ] Updated documentation if needed
- [ ] Commit messages follow the format above

### PR Description Template
```markdown
## Description
Brief description of what this PR does.

## Changes
- Added X feature
- Fixed Y bug
- Refactored Z module

## Testing
- [ ] Added unit tests
- [ ] All tests pass
- [ ] Manual testing performed

## Related Issues
Fixes #123
```

### Review Process
1. Automated checks run (GitHub Actions)
2. Maintainer reviews code and provides feedback
3. Address feedback and push updates
4. Once approved, maintainer merges the PR

---

## 📝 Writing Tests

### Test Structure
```python
"""Tests for feature X."""

import pytest
from confee import ConfigBase


class SimpleConfig(ConfigBase):
    """Test fixture config."""
    name: str
    value: int


class TestFeatureX:
    """Test feature X functionality."""

    def test_basic_usage(self):
        """Test basic usage of feature X."""
        config = SimpleConfig(name="test", value=42)
        # Test assertions here
        assert config.name == "test"

    def test_edge_case(self):
        """Test edge case handling."""
        # Edge case test here
        ...

    def test_error_handling(self):
        """Test that errors are raised correctly."""
        with pytest.raises(ValueError, match="expected error message"):
            # Code that should raise
            ...
```

### Test Coverage Goals
- Aim for **90%+ coverage** on new code
- Test both **happy paths** and **edge cases**
- Include **error handling** tests
- Test **integration** with other components

### Running Specific Test Categories
```bash
# Run only unit tests (if categorized)
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

---

## 🆘 Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/bestend/confee/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/bestend/confee/issues)
- **Security**: Email maintainers privately (see README)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to confee! ☕️**
