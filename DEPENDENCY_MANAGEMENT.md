# Dependency Management

This project uses pip-tools for reproducible dependency management.

## Overview

- `requirements.in` - Production dependencies with version ranges
- `requirements-dev.in` - Development dependencies with version ranges
- `requirements.txt` - Compiled application dependencies (generated)
- `constraints.txt` - Pinned production dependencies (generated)
- `constraints-dev.txt` - Pinned development dependencies (generated)
- `pyproject.toml` - Single source of truth for project metadata and dependencies

## Workflow

### Adding New Dependencies

1. Add the dependency to the appropriate `.in` file:
   - `requirements.in` for production dependencies
   - `requirements-dev.in` for development dependencies

2. Regenerate constraints files:
   ```bash
   make compile-deps
   ```

3. Install the updated dependencies:
   ```bash
   make sync-deps
   ```

   This runs `pip-sync requirements.txt -c constraints.txt` to install packages
   from the compiled requirements while enforcing constraint pins.

4. Commit both the `.in` file changes and the generated constraints files.

### Updating Dependencies

To update all dependencies to their latest compatible versions:

```bash
make update-deps
make sync-deps
```

### Installing Dependencies

For development:
```bash
pip install -r constraints-dev.txt
```

For production:
```bash
pip install -r constraints.txt
```

### CI/CD

The CI pipeline:
1. Installs dependencies from constraints files for reproducible builds
2. Validates that constraints are up to date
3. Fails if constraints drift from the `.in` files

## Commands

- `make compile-deps` - Generate constraints files from .in files
- `make sync-deps` - Install dependencies from constraints files
- `make update-deps` - Update all dependencies to latest compatible versions
- `make check-deps` - Verify constraints are up to date (used in CI)

## Why This Approach?

1. **Reproducible Builds**: Constraints files pin exact versions
2. **Security**: Bounded version ranges prevent unexpected breaking changes
3. **Flexibility**: Easy to update dependencies when needed
4. **CI Safety**: Builds use exact versions, preventing "works on my machine" issues
5. **Single Source**: pyproject.toml is the authoritative source for project metadata
