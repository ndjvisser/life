from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
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
    @pytest.fixture(autouse=True)
    def enable_transactional_db(self, transactional_db):
        pass

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
        call_command("flush", verbosity=0, interactive=False)

    def create_test_quest(self):
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
        return Habit.objects.create(
            name="Test Habit",
            description="Test Description",
            frequency="daily",
            user=self.user,
        )

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        session = self.client.session
        session.save()
        self.driver.add_cookie(
            {
                "name": "sessionid",
                "value": session.session_key,
                "path": "/",
            }
        )
