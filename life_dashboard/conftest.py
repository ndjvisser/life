import pytest
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from life_dashboard.dashboard.models import UserProfile
from life_dashboard.quests.models import Habit, Quest

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def test_user(db):
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    UserProfile.objects.create(user=user, level=1, experience=0)
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture
def test_quest(db, test_user):
    return Quest.objects.create(
        user=test_user,
        title="Test Quest",
        description="Test Description",
        quest_type="daily",
        status="active",
        experience_reward=100,
    )


@pytest.fixture
def test_habit(db, test_user):
    return Habit.objects.create(
        user=test_user,
        name="Test Habit",
        description="Test Description",
        frequency="daily",
        target_count=1,
        experience_reward=50,
    )


class SeleniumTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = UserProfile.objects.create(user=self.user, level=1, experience=0)
        self.client.login(username="testuser", password="testpass123")
        cookie = self.client.cookies["sessionid"]
        self.selenium.get(self.live_server_url)
        self.selenium.add_cookie(
            {"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"}
        )
