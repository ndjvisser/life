# Development Guide

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and architecture compliance. All hooks should pass before committing code.

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

### GitHub Desktop Users

If you're using GitHub Desktop and encounter issues with the `import-linter` hook, you have a few options:

1. **Install import-linter globally** (recommended):
   ```bash
   pip install import-linter
   ```

2. **Use the command line for commits** when the hook fails:
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

3. **The hook will gracefully degrade** - if import-linter is not available, it will show a warning but won't block your commit.

### Hook Details

The pre-commit configuration includes:

- **Code Quality**: ruff (linting), ruff-format (formatting), mypy (type checking)
- **Architecture Validation**: import-linter (boundary enforcement), custom domain purity checks
- **General**: trailing whitespace, file endings, YAML validation, merge conflict detection

### Architecture Enforcement

The following architecture rules are automatically enforced:

1. **Domain Layer Purity**: No Django imports in domain layers
2. **Cross-Context Isolation**: Domain layers cannot import from other contexts
3. **Bounded Context Independence**: Each context maintains clear boundaries

If any of these rules are violated, the commit will be blocked with a clear error message.

## Manual Architecture Validation

You can also run architecture checks manually:

```bash
# Full architecture validation
make check-architecture

# Import boundary validation only
python scripts/run-import-linter.py

# Individual checks
make lint
make format
make type-check
```

## Troubleshooting

### Import-linter Issues

If you see "import-linter not installed" errors:

1. Make sure you're in the correct virtual environment
2. Install the development dependencies: `pip install -r requirements-dev.txt`
3. Or install import-linter specifically: `pip install import-linter`

### Pre-commit Hook Failures

If pre-commit hooks fail:

1. Read the error message carefully - it usually tells you exactly what to fix
2. Run `pre-commit run --all-files` to see all issues at once
3. Many issues can be auto-fixed by running the hooks again
4. For architecture violations, you'll need to refactor the code to comply with DDD principles

### Environment Issues

If you're having environment-related issues:

1. Make sure you're using the project's virtual environment
2. Reinstall pre-commit hooks: `pre-commit uninstall && pre-commit install`
3. Clear pre-commit cache: `pre-commit clean`
