# Architecture Documentation

This directory contains documentation for the Life Dashboard architecture, which follows Domain-Driven Design (DDD) principles with strict bounded context boundaries.

## Quick Start

### Check Architecture Boundaries

```bash
# Run all architecture checks
make check-architecture

# Generate detailed report
make architecture-report

# Check specific violations
python scripts/check-architecture.py
```

### Install Development Tools

```bash
# Install all development dependencies
make dev-install

# Install pre-commit hooks
pre-commit install
```

### Development Workflow

```bash
# Full development check
make dev

# Individual checks
make lint
make type-check
make test
make check-boundaries
```

## Architecture Overview

The Life Dashboard uses a **Modular Monolith** architecture with the following bounded contexts:

- **Dashboard** - User management, authentication, central coordination
- **Stats** - Core RPG stats and life metrics tracking
- **Quests** - Goal management, quests, and habits
- **Skills** - Skill tracking and development
- **Achievements** - Achievement and milestone tracking
- **Journals** - Personal reflection and journaling

Each context follows a layered DDD architecture:

```
Context/
├── domain/          # Pure Python business logic
├── application/     # Use case orchestration
├── infrastructure/  # Django ORM, external APIs
└── interfaces/      # Views, serializers, API endpoints
```

## Key Principles

### 1. Bounded Context Independence

Each context is independent and cannot directly import from other contexts' domain layers.

```python
# ❌ FORBIDDEN
from life_dashboard.stats.domain.entities import CoreStat

# ✅ ALLOWED
from life_dashboard.shared.queries import get_user_basic_info
```

### 2. Pure Domain Layers

Domain layers contain only pure Python business logic with no framework dependencies.

```python
# ❌ FORBIDDEN in domain layer
from django.db import models

# ✅ ALLOWED in domain layer
from dataclasses import dataclass
from typing import Optional
```

### 3. Layered Architecture

Dependencies flow inward toward the domain core:

```
Interfaces → Application → Domain ← Infrastructure
```

### 4. Cross-Context Communication

Use the shared query layer for read-only cross-context data access:

```python
from life_dashboard.shared.queries import CrossContextQueries

user_data = CrossContextQueries.get_user_summary(user_id)
```

## Enforcement

### Automated Checks

- **Import Linter** - Enforces import boundaries in `pyproject.toml`
- **CI/CD Pipeline** - Runs architecture checks on every PR
- **Pre-commit Hooks** - Catches violations before commit
- **Local Tools** - `make check-architecture` for development

### Manual Review

- **Code Reviews** - Architecture violations should be caught in PR reviews
- **Documentation** - This documentation should be updated when architecture changes
- **Training** - New team members should understand these principles

## Files

- [`bounded-contexts.md`](./bounded-contexts.md) - Detailed context definitions and rules
- [`dependency-graph.svg`](./dependency-graph.svg) - Visual dependency graph (generated)
- [`architecture-report.txt`](./architecture-report.txt) - Latest architecture analysis (generated)

## Tools

### Local Development

```bash
# Check all boundaries
make check-architecture

# Generate dependency graph
make dependency-graph

# Run architecture report
make architecture-report

# Full development workflow
make dev
```

### CI/CD Integration

The architecture is automatically validated in CI/CD:

- GitHub Actions workflow validates boundaries on every PR
- Import linter enforces rules defined in `pyproject.toml`
- Type checking ensures domain layer purity
- Custom scripts detect common violations

### Pre-commit Hooks

Install pre-commit hooks to catch violations early:

```bash
pre-commit install
```

This will run architecture checks before every commit.

## Troubleshooting

### Common Issues

1. **Django imports in domain layer**
   - Move Django-specific code to infrastructure layer
   - Use pure Python dataclasses in domain

2. **Cross-context imports**
   - Use shared query layer for cross-context data
   - Implement domain events for notifications

3. **Layer violations**
   - Ensure dependencies flow toward domain core
   - Use dependency injection for external dependencies

### Getting Help

- Run `make check-architecture` for detailed analysis
- Check CI/CD logs for specific violations
- Review [`bounded-contexts.md`](./bounded-contexts.md) for patterns
- Ask team members familiar with DDD principles

## Future Enhancements

### Domain Events

Implement domain events for cross-context communication:

```python
# Future implementation
from life_dashboard.shared.events import publish_event

publish_event(QuestCompleted(user_id=1, quest_id=123))
```

### Microservice Extraction

The bounded context architecture prepares for potential microservice extraction:

- Clear context boundaries make service extraction mechanical
- Service layers provide natural API boundaries
- Domain events enable async communication
- Repository pattern abstracts data access

### Advanced Analytics

Add architecture analytics and monitoring:

- Dependency drift detection
- Context coupling metrics
- Architecture evolution tracking
- Automated refactoring suggestions

## Contributing

When adding new features:

1. **Identify the correct context** for your feature
2. **Follow DDD patterns** - domain, application, infrastructure layers
3. **Avoid cross-context dependencies** - use shared queries
4. **Write domain tests** - test business logic without Django
5. **Run architecture checks** - `make check-architecture`
6. **Update documentation** - if you change architecture patterns

The architecture is designed to support the long-term evolution of the Life Dashboard while maintaining clean boundaries and testable code.
