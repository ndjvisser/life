# Project Structure

## Root Directory Layout
```
├── life_dashboard/          # Main Django project directory
├── stats/                   # Legacy stats app (consider consolidation)
├── staticfiles/            # Collected static files for production
├── life/                   # Duplicate/backup directory
├── manage.py               # Django management script
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── pyproject.toml         # Ruff configuration
```

## Django Project Structure (`life_dashboard/`)

### Bounded Contexts (Django Apps)
- **`dashboard/`**: User management, authentication, central coordination, insights aggregation
- **`stats/`**: Core RPG stats and life metrics (consolidate core_stats + life_stats)
- **`integrations/`**: External API connections, data sync, validation services
- **`quests/`**: Quest and habit management system with auto-completion
- **`achievements/`**: Achievement and milestone tracking with intelligent triggers
- **`journals/`**: Personal reflection, journaling, and AI-powered insight generation
- **`skills/`**: Skill tracking and development with recommendation engine
- **`analytics/`**: Trend analysis, predictions, and intelligence services

### Context Architecture (Target Structure)

Each context follows DDD layered architecture with integration capabilities:

```
context_name/
├── domain/          # Pure Python business logic
│   ├── entities.py  # Domain entities
│   ├── value_objects.py
│   ├── repositories.py  # Abstract interfaces
│   ├── events.py    # Domain events
│   └── services.py  # Domain services
├── infrastructure/  # Django-specific implementations
│   ├── models.py    # Django ORM models
│   ├── repositories.py  # Concrete repository implementations
│   ├── integrations.py  # External API clients
│   ├── ml_models.py     # ML model implementations
│   └── migrations/
├── application/     # Use case orchestration
│   ├── services.py  # Application services
│   ├── handlers.py  # Event handlers
│   ├── sync_services.py  # Data synchronization
│   └── intelligence.py   # AI/ML orchestration
└── interfaces/      # External interfaces
    ├── views.py     # Django views
    ├── api_views.py # REST API endpoints
    ├── serializers.py
    ├── webhooks.py  # Integration webhooks
    └── urls.py
```

### Integration Context Structure

```
integrations/
├── domain/
│   ├── integration_types.py  # Health, Wealth, Productivity
│   ├── sync_policies.py      # Sync frequency, validation rules
│   └── data_transformers.py  # External data → domain models
├── infrastructure/
│   ├── health_apis.py        # Apple Health, Strava, etc.
│   ├── finance_apis.py       # Plaid, banking APIs
│   ├── productivity_apis.py  # Todoist, calendar APIs
│   └── validation.py         # Data quality checks
├── application/
│   ├── sync_orchestrator.py  # Coordinate all syncs
│   ├── data_pipeline.py      # ETL processing
│   └── error_recovery.py     # Handle API failures
└── interfaces/
    ├── webhook_handlers.py    # Receive external notifications
    ├── admin_views.py         # Integration management UI
    └── monitoring.py          # Health checks and metrics
```

### Current vs Target State

**Current**: Traditional Django apps with direct model imports
**Target**: DDD-structured contexts with service layers and domain events

### Project Configuration
- **`life_dashboard/`**: Django project settings and configuration
  - `settings.py`: Main configuration
  - `test_settings.py`: Test-specific settings
  - `urls.py`: URL routing
  - `celery.py`: Celery configuration

### Shared Resources
- **`templates/`**: Project-wide HTML templates
- **`static/`**: CSS, JavaScript, and image assets
- **`tests/`**: Integration and cross-app tests

## Django App Conventions

Each Django app follows standard structure:
```
app_name/
├── migrations/          # Database migrations
├── tests/              # App-specific tests
├── __init__.py
├── admin.py            # Django admin configuration
├── apps.py             # App configuration
├── models.py           # Database models
├── views.py            # View logic
├── urls.py             # URL patterns (if needed)
└── forms.py            # Form definitions (if needed)
```

## Key Files & Directories

- **`manage.py`**: Entry point for Django management commands
- **`conftest.py`**: Pytest configuration and fixtures
- **`db.sqlite3`**: Development database
- **`.env`**: Environment variables (not in repo)
- **`staticfiles/`**: Production static files collection

## Key Models by App

### Dashboard App
- `UserProfile`: User experience points, level, bio, location, preferences
- `DashboardWidget`: Configurable dashboard components
- `Notification`: System alerts and celebrations
- `InsightSummary`: Aggregated insights and recommendations

### Stats App (Consolidated)
- `CoreStat`: RPG attributes (strength, endurance, agility, intelligence, wisdom, charisma)
- `LifeStat`: Health/Wealth/Relationships metrics with subcategories
- `StatHistory`: Historical tracking and trend data
- `StatMilestone`: Achievement thresholds and progress markers

### Integrations App
- `Integration`: External service connections (health, finance, productivity)
- `SyncJob`: Scheduled data synchronization tasks
- `ExternalDataPoint`: Raw data from external sources
- `DataTransformation`: Mapping rules for external → internal data

### Quests App
- `Quest`: Multi-level quests with auto-completion capabilities
- `QuestChain`: Linked quest progressions and dependencies
- `Habit`: Daily/weekly/monthly habits with streak tracking
- `HabitCompletion`: Individual habit completion records
- `AutoCompletionRule`: Rules for automatic quest completion

### Skills App
- `SkillCategory`: Health, Wealth, Social skill groupings
- `Skill`: Individual skills with leveling and experience
- `SkillTree`: Prerequisite relationships and progression paths
- `SkillRecommendation`: AI-generated skill development suggestions

### Achievements App
- `Achievement`: Bronze/Silver/Gold achievements with intelligent triggers
- `UserAchievement`: User's unlocked achievements with context
- `AchievementRule`: Dynamic achievement criteria and evaluation logic
- `Title`: Unlockable user titles and recognition levels

### Journals App
- `JournalEntry`: Daily/weekly/milestone/insight entries with mood tracking
- `GeneratedInsight`: AI-generated insights from journal analysis
- `ReflectionPrompt`: Suggested reflection topics and questions
- `PatternDetection`: Identified behavioral and emotional patterns

### Analytics App
- `TrendAnalysis`: Statistical analysis of user patterns
- `Prediction`: Forecasted outcomes and recommendations
- `BalanceScore`: Health/Wealth/Relationships equilibrium metrics
- `PersonalizedRecommendation`: AI-generated action suggestions

## Naming Conventions

- Apps use lowercase with underscores: `core_stats`, `life_stats`
- Models use PascalCase: `Quest`, `Habit`, `Achievement`, `UserProfile`
- Views and functions use snake_case
- Templates follow `app_name/template_name.html` pattern
- Static files organized by type: `css/`, `js/`, `img/`
