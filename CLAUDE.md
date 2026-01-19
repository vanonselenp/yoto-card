# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**yoto-card** is a Python 3 project using `uv` as the package manager and build tool. The project follows best Python practices with emphasis on testing, type safety, and code quality.

## Development Setup

### Initial Project Setup (if not yet completed)

The project should be initialized with a `pyproject.toml` following modern Python standards (PEP 517/518):

```bash
uv init --name yoto-card
```

### Environment and Dependencies

- **Python Version**: Python 3 (latest stable)
- **Package Manager**: `uv` (for fast, reliable dependency management)
- **Lock File**: `uv.lock` (commit to version control for reproducibility)

Install dependencies:
```bash
uv sync
```

## Common Development Commands

### Running Tests

Run all tests:
```bash
uv run pytest
```

Run tests in a specific file:
```bash
uv run pytest tests/test_module.py
```

Run a specific test function:
```bash
uv run pytest tests/test_module.py::test_function_name
```

Run tests with coverage:
```bash
uv run pytest --cov=src --cov-report=html
```

Run tests in watch mode (requires pytest-watch):
```bash
uv run ptw
```

### Code Quality and Linting

Format code with Ruff (opinionated, fast formatter):
```bash
uv run ruff format src tests
```

Lint code with Ruff:
```bash
uv run ruff check src tests --fix
```

Type checking with pyright or mypy:
```bash
uv run pyright src
# or
uv run mypy src
```

### Running the Application

Run the main application:
```bash
uv run python -m yoto_card
```

Or if there's an entry point defined in `pyproject.toml`:
```bash
uv run yoto-card
```

## Project Structure (Expected)

```
yoto-card/
├── src/yoto_card/          # Main package
│   ├── __init__.py
│   └── ...                 # Module files
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest configuration and fixtures
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── pyproject.toml          # Project configuration and dependencies
├── uv.lock                 # Locked dependencies (commit to version control)
├── README.md               # Project documentation
├── CLAUDE.md               # This file
└── LICENSE                 # MIT License
```

## Testing Strategy

- **Framework**: pytest (standard, extensible test framework)
- **Location**: `tests/` directory organized by test type (unit, integration)
- **Fixtures**: Defined in `tests/conftest.py` for reusable test setup
- **Coverage**: Aim for high coverage; use `pytest-cov` to track
- **Parametrization**: Use `pytest.mark.parametrize` for testing multiple cases

## Code Quality Standards

- **Formatting**: Ruff format (consistent, opinionated, fast)
- **Linting**: Ruff check (catches errors and style issues)
- **Type Checking**: Type hints throughout; validate with pyright or mypy
- **Testing**: All public functions tested; aim for high coverage

## Key Development Principles

1. **Use `uv run` prefix**: All commands should use `uv run` to execute in the managed environment
2. **Test-driven**: Write tests first or alongside implementation
3. **Type safety**: Use type hints for all function signatures
4. **Reproducibility**: Keep `uv.lock` committed to version control
5. **Python best practices**: Follow PEP 8, PEP 484 (typing), PEP 517 (build system)

## Configuration Files

- **pyproject.toml**: Defines project metadata, dependencies, tool configurations, and build system
  - Development dependencies: pytest, ruff, type checkers
  - Optional tools config: [tool.pytest.ini_options], [tool.ruff], [tool.mypy]
- **uv.lock**: Auto-generated lock file (commit to version control)
- **.gitignore**: Comprehensive Python ignore patterns already in place

## Debugging

Run Python with debugging:
```bash
uv run python -m pdb -m yoto_card
```

Run a specific test with debugging:
```bash
uv run pytest --pdb tests/test_module.py::test_function_name
```

## Common Tasks

When making changes:
1. Write/update tests first
2. Implement the feature or fix
3. Run `uv run ruff format` to format code
4. Run `uv run ruff check --fix` to auto-fix issues
5. Run `uv run pytest` to verify tests pass
6. Run type checker to verify type safety

## Resources

- [uv documentation](https://docs.astral.sh/uv/)
- [pytest documentation](https://docs.pytest.org/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Python Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)
