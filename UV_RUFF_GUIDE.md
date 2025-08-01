# BharatVerse - uv & ruff Development Guide

This project has been migrated to use **uv** for dependency management and **ruff** for code quality, replacing the previous tools (poetry, black, isort, flake8, pylint).

## 🚀 Quick Start

### Prerequisites
Install uv (Python package manager):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### Installation
```bash
# Install core dependencies
uv pip install -e .

# Install with development dependencies
uv pip install -e ".[dev]"

# Install with AI dependencies
uv pip install -e ".[ai]"

# Install with all optional dependencies
uv pip install -e ".[dev,ai,docs]"
```

## 🛠️ Development Workflow

### Code Quality with Ruff
Ruff replaces multiple tools (black, isort, flake8, pylint) with a single, fast tool:

```bash
# Check code quality
make lint
# or
uv run ruff check .

# Format code
make format
# or
uv run ruff format .

# Auto-fix issues
make fix
# or
uv run ruff check --fix .
uv run ruff format .
```

### Testing
```bash
# Run tests
make test
# or
uv run pytest tests/

# Run tests with coverage
make test-coverage
# or
uv run pytest tests/ --cov=. --cov-report=html
```

### Type Checking
```bash
# Run type checking
make typecheck
# or
uv run mypy .
```

### All Checks
```bash
# Run all checks (lint + test)
make check
```

## 📋 Available Make Commands

```bash
make help              # Show all available commands
make install           # Install core dependencies with uv
make install-dev       # Install development dependencies with uv
make sync              # Sync dependencies with uv
make run               # Run the application
make test              # Run tests
make lint              # Run linting with ruff
make format            # Format code with ruff
make check             # Run all checks (lint + test)
make fix               # Auto-fix code issues with ruff
make typecheck         # Run type checking with mypy
make clean             # Clean temporary files
make docker-up         # Start Docker services
make docker-down       # Stop Docker services
make dev-setup         # Setup development environment
```

## 🔧 Configuration

### Ruff Configuration
All ruff configuration is in `pyproject.toml`:
- **Linting**: Comprehensive rule set including security, performance, and style checks
- **Formatting**: Replaces black with consistent formatting
- **Import sorting**: Replaces isort with intelligent import organization

### Key Features
- **Fast**: Ruff is 10-100x faster than traditional tools
- **Comprehensive**: Covers linting, formatting, and import sorting
- **Configurable**: Extensive per-file and per-rule configuration
- **IDE Integration**: Works with VS Code, PyCharm, and other editors

## 📦 Dependency Management

### Project Structure
```
pyproject.toml          # Main project configuration
├── [project]           # Core dependencies
├── [project.optional-dependencies]
│   ├── dev            # Development tools (pytest, ruff, mypy, etc.)
│   ├── ai             # AI/ML dependencies (torch, transformers, etc.)
│   └── docs           # Documentation tools (sphinx, etc.)
```

### Legacy Files
The following files are kept for compatibility but dependencies are now managed in `pyproject.toml`:
- `requirements.txt` - Core dependencies (for deployment)
- `requirements/dev.txt` - Development dependencies
- `requirements/ai.txt` - AI dependencies

## 🔄 Migration from Old Tools

### Replaced Tools
| Old Tool | New Tool | Purpose |
|----------|----------|---------|
| poetry | uv | Dependency management |
| black | ruff format | Code formatting |
| isort | ruff (I rules) | Import sorting |
| flake8 | ruff check | Linting |
| pylint | ruff (PL rules) | Advanced linting |

### Command Mapping
| Old Command | New Command |
|-------------|-------------|
| `poetry install` | `uv pip install -e .` |
| `black .` | `uv run ruff format .` |
| `isort .` | `uv run ruff check --select I --fix .` |
| `flake8 .` | `uv run ruff check .` |
| `pylint bharatverse` | `uv run ruff check --select PL .` |

## 🚀 Performance Benefits

### uv Benefits
- **Speed**: 10-100x faster than pip
- **Reliability**: Better dependency resolution
- **Compatibility**: Drop-in replacement for pip
- **Modern**: Built in Rust for performance

### ruff Benefits
- **Speed**: 10-100x faster than traditional tools
- **All-in-one**: Replaces multiple tools
- **Comprehensive**: 700+ rules from popular linters
- **Configurable**: Fine-grained control over rules

## 🔍 Pre-commit Hooks

Pre-commit configuration is in `.pre-commit-config.yaml`:
```bash
# Install pre-commit hooks
uv pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 🐛 Troubleshooting

### Common Issues

1. **uv not found**
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Restart terminal
   ```

2. **Dependencies not found**
   ```bash
   # Reinstall dependencies
   uv pip install -e ".[dev]"
   ```

3. **Ruff errors**
   ```bash
   # Auto-fix most issues
   uv run ruff check --fix .
   uv run ruff format .
   ```

4. **Legacy pip commands**
   - Replace `pip` with `uv pip` in all commands
   - Use `uv run` for running tools

## 📚 Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [Migration Guide](https://docs.astral.sh/ruff/migration/)
- [VS Code Integration](https://docs.astral.sh/ruff/editors/vscode/)

## 🤝 Contributing

When contributing to BharatVerse:

1. **Setup**: `make dev-setup`
2. **Code**: Write your changes
3. **Format**: `make fix`
4. **Test**: `make check`
5. **Commit**: Pre-commit hooks will run automatically

All code must pass ruff checks and tests before merging.