# Bounded Contexts Architecture

This document defines the bounded contexts in the Life Dashboard application and the rules for maintaining strict boundaries between them.

## Overview

The Life Dashboard follows a **Modular Monolith** architecture with strict bounded context boundaries. Each context is responsible for a specific domain area and maintains independence from other contexts.

## Bounded Contexts

### 1. Dashboard Context (`life_dashboard.dashboard`)

**Responsibility**: User management, authentication, central coordination, and cross-context data aggregation.

**Domain Concepts**:
- User Profile
- Experience Points & Leveling
- Authentication & Authorization
- Onboarding State Machine
- Cross-context queries

**Key Entities**:
- `UserProfile` - User profile with experience and level
- `OnboardingStateMachine` - User onboarding workflow

**External Dependencies**: None (core context)

### 2. Stats Context (`life_dashboard.stats`)

**Responsibility**: Core RPG stats and life metrics tracking with trend analysis.

**Domain Concepts**:
- Core Stats (Strength, Endurance, Agility, Intelligence, Wisdom, Charisma)
- Life Stats (Health, Wealth, Relationships metrics)
- Stat History & Trend Analysis
- Statistical calculations

**Key Entities**:
- `CoreStat` - RPG-style attributes
- `LifeStat` - Real-world metrics
- `StatHistory` - Change tracking

**External Dependencies**: None

### 3. Quests Context (`life_dashboard.quests`)

**Responsibility**: Goal management, quests, and habits with auto-completion capabilities.

**Domain Concepts**:
- Multi-level Quests (Life Goals, Annual, Main, Side, Weekly, Daily)
- Habits with streak tracking
- Quest chains and dependencies
- Auto-completion from external data

**Key Entities**:
- `Quest` - Goal tracking with state machine
- `Habit` - Recurring activities
- `QuestChain` - Linked quest progressions

**External Dependencies**: Stats (for experience rewards)

### 4. Skills Context (`life_dashboard.skills`)

**Responsibility**: Skill tracking and development with recommendation engine.

**Domain Concepts**:
- Skill Categories (Health, Wealth, Social)
- Skill progression with exponential XP curves
- Skill trees and prerequisites
- Practice logging and recommendations

**Key Entities**:
- `Skill` - Individual skills with leveling
- `SkillCategory` - Skill groupings
- `SkillTree` - Prerequisite relationships

**External Dependencies**: Stats (for experience tracking)

### 5. Achievements Context (`life_dashboard.achievements`)

**Responsibility**: Achievement and milestone tracking with intelligent triggers.

**Domain Concepts**:
- Tiered Achievements (Bronze, Silver, Gold)
- Dynamic achievement rules
- Titles and badges
- Cross-context achievement triggers

**Key Entities**:
- `Achievement` - Unlockable milestones
- `UserAchievement` - User's unlocked achievements
- `Title` - Unlockable user titles

**External Dependencies**: All contexts (for achievement triggers)

### 6. Journals Context (`life_dashboard.journals`)

**Responsibility**: Personal reflection, journaling, and AI-powered insight generation.

**Domain Concepts**:
- Journal entries with mood tracking
- Insight generation from patterns
- Reflection prompts
- Pattern detection

**Key Entities**:
- `JournalEntry` - Personal reflections
- `GeneratedInsight` - AI-generated insights
- `PatternDetection` - Behavioral patterns

**External Dependencies**: Quests, Achievements (for related content)

## Boundary Rules

### 1. No Direct Cross-Context Dependencies

**Rule**: Domain layers cannot import from other contexts' domain layers.

```python
# ❌ FORBIDDEN
from life_dashboard.stats.domain.entities import CoreStat

# ✅ ALLOWED - Use cross-context queries
from life_dashboard.shared.queries import get_user_basic_info
```

### 2. Pure Domain Layers

**Rule**: Domain layers cannot import Django or any framework code.

```python
# ❌ FORBIDDEN in domain layer
from django.db import models
from django.contrib.auth.models import User

# ✅ ALLOWED in domain layer
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
```

### 3. Layered Architecture

**Rule**: Dependencies must flow inward toward the domain.

```
Interfaces → Application → Domain ← Infrastructure
```

- Domain: Pure business logic, no external dependencies
- Application: Use case orchestration, can import Domain
- Infrastructure: Django ORM, external APIs, can import Domain & Application
- Interfaces: Views, serializers, can import Application & Domain

### 4. Cross-Context Communication

**Rule**: Use the shared query layer for read-only cross-context access.

```python
# ✅ CORRECT - Use shared queries
from life_dashboard.shared.queries import CrossContextQueries

user_summary = CrossContextQueries.get_user_summary(user_id)
```

**Rule**: Use domain events for cross-context notifications (future implementation).

```python
# ✅ FUTURE - Domain events
from life_dashboard.shared.events import publish_event

publish_event(QuestCompleted(user_id=1, quest_id=123, experience_reward=50))
```

## Enforcement Mechanisms

### 1. Import Linter

Configuration in `pyproject.toml` enforces:
- Context independence
- Domain layer purity
- Layered architecture
- No cross-context domain dependencies

### 2. CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/architecture-check.yml`) runs:
- Import boundary checks
- Django import detection in domain layers
- Cross-context import detection
- Layer violation detection

### 3. Pre-commit Hooks

Pre-commit configuration (`.pre-commit-config.yaml`) catches violations before commit:
- Import linter
- Django import checker
- Cross-context import checker
- Context structure validator

### 4. Local Development Tools

- `make check-architecture` - Run all architecture checks
- `python scripts/check-architecture.py` - Detailed boundary analysis
- `make architecture-report` - Generate architecture report

## Cross-Context Data Access

### Read-Only Queries

Use `life_dashboard.shared.queries.CrossContextQueries` for safe cross-context data access:

```python
# Get user summary across contexts
user_data = CrossContextQueries.get_user_summary(user_id)

# Get activity counts for dashboard
activity_counts = CrossContextQueries.get_user_activity_counts(user_id)

# Get recent activity feed
recent_activity = CrossContextQueries.get_recent_activity(user_id, limit=10)
```

### Convenience Functions

```python
from life_dashboard.shared.queries import get_user_dashboard_data, get_user_basic_info

# Get all dashboard data
dashboard_data = get_user_dashboard_data(user_id)

# Get basic user info safe for sharing
basic_info = get_user_basic_info(user_id)
```

## Migration Strategy

### From Existing Code

1. **Identify Context**: Determine which context the code belongs to
2. **Extract Domain Logic**: Move business logic to domain layer
3. **Create Services**: Implement application services for use cases
4. **Update Views**: Use services instead of direct model access
5. **Add Tests**: Create domain layer tests

### Example Migration

```python
# BEFORE - Business logic in Django model
class Quest(models.Model):
    def complete(self):
        self.status = "completed"
        self.save()
        self.user.profile.add_experience(self.experience_reward)

# AFTER - Business logic in domain service
class QuestService:
    def complete_quest(self, user_id: int, quest_id: int):
        quest = self.quest_repo.get_by_id(quest_id)
        quest.complete()
        self.quest_repo.save(quest)

        # Use cross-context service for experience
        user_service = get_user_service()
        user_service.add_experience(user_id, quest.experience_reward)
```

## Benefits

### 1. Maintainability
- Clear separation of concerns
- Easier to understand and modify
- Reduced coupling between features

### 2. Testability
- Pure domain logic is easy to test
- No Django dependencies in business logic
- Fast unit tests without database

### 3. Scalability
- Contexts can be extracted to microservices if needed
- Clear API boundaries already defined
- Independent deployment possible

### 4. Team Collaboration
- Teams can work on different contexts independently
- Clear ownership boundaries
- Reduced merge conflicts

## Troubleshooting

### Common Violations

1. **Django imports in domain layer**
   ```bash
   # Check for violations
   grep -r "from django" life_dashboard/*/domain/
   ```

2. **Cross-context imports**
   ```bash
   # Check specific context
   grep -r "from life_dashboard.stats" life_dashboard/dashboard/domain/
   ```

3. **Layer violations**
   ```bash
   # Check domain importing from application
   grep -r "from.*application" life_dashboard/*/domain/
   ```

### Fixing Violations

1. **Move business logic to domain layer**
2. **Use shared queries for cross-context data**
3. **Implement proper service layer**
4. **Add repository pattern for data access**

### Getting Help

- Run `make check-architecture` for detailed analysis
- Check CI/CD pipeline for specific violations
- Review this documentation for proper patterns
- Use shared query layer for cross-context needs
