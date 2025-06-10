from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from life_dashboard.quests.models import Habit, Quest

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def test_user():
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture
def test_quest(test_user):
    return Quest.objects.create(
        title="Test Quest",
        description="Test Description",
        difficulty="medium",
        quest_type="main",
        status="active",
        experience_reward=10,
        start_date=date.today(),
        due_date=date.today(),
        user=test_user,
    )


@pytest.fixture
def test_habit(test_user):
    return Habit.objects.create(
        name="Test Habit",
        description="Test Description",
        frequency="daily",
        user=test_user,
    )


class SeleniumTestCase(StaticLiveServerTestCase):
    """Base test case for Selenium tests with proper transaction handling."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            # Use ChromeDriverManager with explicit ChromeType
            driver_path = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
            print(f"[DEBUG] ChromeDriver path: {driver_path}")

            # Ensure we have the correct executable
            if not driver_path.lower().endswith(".exe"):
                # Find the actual chromedriver.exe in the directory
                import os

                driver_dir = os.path.dirname(driver_path)
                for file in os.listdir(driver_dir):
                    if file.lower() == "chromedriver.exe":
                        driver_path = os.path.join(driver_dir, file)
                        break
                else:
                    raise FileNotFoundError(
                        f"Could not find chromedriver.exe in {driver_dir}"
                    )

            print(f"[DEBUG] Using ChromeDriver at: {driver_path}")
            service = Service(executable_path=driver_path)
            cls.driver = webdriver.Chrome(service=service, options=chrome_options)
            cls.wait = WebDriverWait(cls.driver, 10)
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {str(e)}")
            raise

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """Set up test environment with a fresh database and authenticated user."""
        super().setUp()
        # Create test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Log in the user
        self.client.login(username="testuser", password="testpass123")
        session = self.client.session
        session.save()

        # Set up Selenium session
        self.driver.get(self.live_server_url)
        self.driver.add_cookie(
            {
                "name": "sessionid",
                "value": session.session_key,
                "path": "/",
            }
        )
        self.driver.refresh()

    def tearDown(self):
        """Clean up after each test."""
        super().tearDown()
        # Clear any remaining cookies
        self.driver.delete_all_cookies()

    def create_test_quest(self):
        """Helper method to create a test quest."""
        return Quest.objects.create(
            title="Test Quest",
            description="Test Description",
            difficulty="medium",
            quest_type="main",
            status="active",
            experience_reward=10,
            start_date=date.today(),
            due_date=date.today(),
            user=self.user,
        )

    def create_test_habit(self):
        """Helper method to create a test habit."""
        return Habit.objects.create(
            name="Test Habit",
            description="Test Description",
            frequency="daily",
            user=self.user,
        )
