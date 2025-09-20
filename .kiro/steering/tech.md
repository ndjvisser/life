# Technology Stack

## Framework & Backend
- **Django 5.1.1**: Main web framework
- **Python 3.8+**: Programming language
- **SQLite**: Default database (configurable for PostgreSQL in production)
- **Celery**: Asynchronous task processing
- **Redis**: Message broker and caching

## Frontend & UI
- **Bootstrap 5**: CSS framework via crispy-bootstrap5
- **Django Crispy Forms**: Form rendering
- **Custom CSS/JS**: Located in `life_dashboard/static/`

## Development Tools
- **Ruff**: Code linting and formatting (replaces Black/Flake8)
- **pytest**: Testing framework with pytest-django
- **Behave**: Behavior-Driven Development for feature testing
- **Selenium**: Browser automation for integration tests
- **pre-commit**: Git hooks for code quality

## Integration Technologies

### External API Integration
- **Health APIs**: Apple HealthKit, Google Fit, Strava, Oura, Fitbit
- **Finance APIs**: Plaid, Yodlee, Open Banking APIs, CSV imports
- **Productivity APIs**: Todoist, Notion, Google Calendar, Outlook
- **Social APIs**: Email analytics, social media metrics

### Data Processing
- **Pandas**: Data transformation and analysis
- **NumPy**: Numerical computations for trend analysis
- **Scikit-learn**: Machine learning for pattern detection
- **Celery Beat**: Scheduled data synchronization

### AI/ML Stack
- **OpenAI API**: GPT integration for insight generation
- **Transformers**: Local NLP for journal analysis
- **TensorFlow/PyTorch**: Custom ML models for predictions
- **Redis**: ML model caching and feature storage

## Common Commands

### Setup & Development
```bash
# Initial setup
python manage.py setup

# Run development server
python manage.py runserver

# Database operations
python manage.py resetdb
python manage.py migrate
python manage.py createsuperuser
python manage.py createsampledata

# Integration setup
python manage.py setup_integrations
python manage.py sync_external_data --user-id=1
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest life_dashboard/tests/test_quests.py

# Run integration tests
pytest life_dashboard/tests/test_integrations.py

# Run BDD feature tests
behave features/

# Run specific feature
behave features/quest_completion.feature

# Run with coverage
pytest --cov=life_dashboard

# Run full test suite (unit + integration + BDD)
python manage.py test_all
```

### Code Quality
```bash
# Lint and format code
ruff check .
ruff format .

# Run pre-commit hooks
pre-commit run --all-files
```

### Background Tasks
```bash
# Start Celery worker
celery -A life_dashboard.life_dashboard worker -l info

# Start Celery beat scheduler (for data sync)
celery -A life_dashboard.life_dashboard beat -l info

# Monitor integration health
python manage.py check_integrations
```

### Data & Analytics
```bash
# Generate insights for user
python manage.py generate_insights --user-id=1

# Run trend analysis
python manage.py analyze_trends --days=30

# Export user data
python manage.py export_user_data --user-id=1 --format=json
```

## Configuration
- Environment variables via `.env` file
- Settings in `life_dashboard/life_dashboard/settings.py`
- Test settings in `life_dashboard/life_dashboard/test_settings.py`

## Additional Dependencies for Life OS Features
```txt
# Add to requirements.txt for full Life OS capabilities
behave==1.2.6              # BDD testing framework
pandas==2.0.3              # Data analysis and transformation
numpy==1.24.3              # Numerical computations
scikit-learn==1.3.0        # Machine learning for patterns
requests==2.31.0           # HTTP client for external APIs
cryptography==41.0.3       # Encryption for credentials
python-dateutil==2.8.2     # Date/time utilities
```
