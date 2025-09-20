import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Defer Django setup to pytest-django. Only set the env var if it's not already set.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "life_dashboard.life_dashboard.test_settings"
)
