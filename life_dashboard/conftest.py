from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def test_user():
    from life_dashboard.stats.models import Stats

    User = get_user_model()
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    # Ensure related Stats exists even if signals didn't fire yet
    Stats.objects.get_or_create(user=user)
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture
def test_quest(test_user):
    from life_dashboard.quests.models import Quest

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
    from life_dashboard.quests.models import Habit

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
            # Prefer Selenium Manager (Selenium 4.6+) to resolve drivers cross-platform
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.wait = WebDriverWait(cls.driver, 10)
        except Exception as e:
            # If Chrome isn't available in CI, skip Selenium-based tests gracefully
            pytest.skip(f"Skipping Selenium tests: {e}")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """Set up test environment with a fresh database and authenticated user."""
        super().setUp()
        from life_dashboard.stats.models import Stats

        # Create test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        # Ensure stats exists for this user
        Stats.objects.get_or_create(user=self.user)

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
        from life_dashboard.quests.models import Quest

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
        from life_dashboard.quests.models import Habit

        return Habit.objects.create(
            name="Test Habit",
            description="Test Description",
            frequency="daily",
            user=self.user,
        )


if __name__ == "__main__":
    pytest.main(["-v", "-s", "conftest.py"])
