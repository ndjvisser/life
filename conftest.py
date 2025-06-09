import os
import sys

import django

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "life_dashboard.test_settings")
django.setup()
