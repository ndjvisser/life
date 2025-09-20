# LIFE - Level Up Your Life

LIFE is a comprehensive, RPG-inspired personal life dashboard that helps you "level up your life" through gamified tracking and development. The platform provides a holistic view of personal growth across health, wealth, and relationships using engaging RPG mechanics.

## Features

### Core RPG System
- **Core Stats**: Strength, Endurance, Agility, Intelligence, Wisdom, Charisma
- **Experience Points**: Progression system with leveling
- **Achievements & Titles**: Bronze, Silver, Gold badges with custom titles

### Life Tracking
- **Life Stats**: Comprehensive tracking across Health, Wealth, and Relationships
- **Quests**: Multi-level goals (Life Goals, Annual, Main/Side/Weekly/Daily)
- **Habits**: Daily, weekly, monthly routines with streak tracking
- **Skills**: Categorized skill development with leveling system

### Reflection & Insights
- **Journals**: Daily reflections, weekly reviews, milestone entries
- **Overview Dashboards**: Health, Wealth, and Relationships trend analysis
- **Progress Tracking**: Visual indicators and historical data

## Architecture

LIFE follows a **Modular Monolith** architecture with strict bounded context boundaries:

- **Dashboard** - User management, authentication, central coordination
- **Stats** - Core RPG stats and life metrics tracking
- **Quests** - Goal management, quests, and habits
- **Skills** - Skill tracking and development
- **Achievements** - Achievement and milestone tracking
- **Journals** - Personal reflection and journaling

Each context follows Domain-Driven Design (DDD) principles with layered architecture.

### Quick Architecture Check

```bash
# Check architecture boundaries
make check-architecture

# Generate architecture report
make architecture-report

# Full development workflow
make dev
```

See [`docs/architecture/`](docs/architecture/) for detailed architecture documentation.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/life.git
cd life
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the project in development mode with all dependencies:
```bash
# Install the project in development mode with all dependencies
pip install -e ".[dev]"

# Generate the constraints file (used for reproducible builds)
make generate-constraints
```

4. Create a .env file in the project root with the following content:
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. (Optional) For production, you can install with production-only dependencies:
```bash
pip install -e .
```

5. Set up the database:
```bash
python manage.py setup
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Visit http://localhost:8000 in your browser.

## Usage

### Admin Access

- URL: http://localhost:8000/admin
- Username: admin
- Password: admin

### Test User

- Username: test
- Password: test

## Development

### Quick Start

```bash
# Install development dependencies
make dev-install

# Set up project
make setup

# Run development server
make runserver

# Run all checks
make dev
```

### Available Commands

```bash
# Setup & Installation
make install          # Install production dependencies
make dev-install      # Install development dependencies
make setup           # Initial project setup

# Development
make runserver       # Run development server
make test           # Run all tests
make lint           # Run linting
make format         # Format code
make check-architecture  # Check architecture boundaries

# Database
make migrate        # Run migrations
make resetdb        # Reset database
make setup-sample-data  # Create sample data

# Architecture
make check-boundaries    # Check bounded context boundaries
make architecture-report # Generate architecture report
make dependency-graph   # Generate dependency graph
```

### Project Structure

```
life_dashboard/
├── dashboard/          # Dashboard context (user management, auth)
│   ├── domain/        # Pure business logic
│   ├── application/   # Use case orchestration
│   ├── infrastructure/ # Django ORM implementations
│   └── interfaces/    # Views, serializers
├── stats/             # Stats context (RPG stats, life metrics)
├── quests/            # Quests context (goals, habits)
├── skills/            # Skills context (skill development)
├── achievements/      # Achievements context (badges, titles)
├── journals/          # Journals context (reflection, insights)
├── shared/            # Cross-context utilities
└── life_dashboard/    # Project settings
```

### Architecture Principles

1. **Bounded Context Independence** - Each context is independent
2. **Pure Domain Layers** - No Django imports in domain logic
3. **Layered Architecture** - Dependencies flow toward domain core
4. **Cross-Context Queries** - Use shared query layer for data access

See [`docs/architecture/bounded-contexts.md`](docs/architecture/bounded-contexts.md) for detailed rules.

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
