import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from life_dashboard.conftest import SeleniumTestCase
from life_dashboard.quests.models import Habit


@pytest.mark.django_db
class TestDashboard:
    def test_profile_view(self, authenticated_client):
        url = reverse("dashboard:profile")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "Profile" in response.content.decode()

    def test_profile_update(self, authenticated_client, test_user):
        url = reverse("dashboard:profile")
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "updated@example.com",
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        test_user.refresh_from_db()
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.email == "updated@example.com"

    def test_experience_gain(self, authenticated_client, test_user):
        # Create a test habit
        habit = Habit.objects.create(
            name="Test Habit",
            description="Test Description",
            frequency="daily",
            user=test_user,
        )
        initial_experience = test_user.profile.experience
        response = authenticated_client.post(
            reverse("quests:complete_habit", args=[habit.pk]),
            {"count": 1},
        )
        assert response.status_code == 302
        test_user.profile.refresh_from_db()
        assert test_user.profile.experience > initial_experience


@pytest.mark.django_db
class DashboardTests(SeleniumTestCase):
    def test_dashboard_page(self):
        self.selenium.get(f'{self.live_server_url}{reverse("dashboard:dashboard")}')
        assert "Welcome" in self.selenium.page_source

    def test_level_up_flow(self):
        self.selenium.get(f'{self.live_server_url}{reverse("dashboard:dashboard")}')
        initial_level = self.user.profile.level

        # Complete a quest to gain experience
        quest = self.create_test_quest()
        self.selenium.get(
            f'{self.live_server_url}{reverse("quests:quest_detail", args=[quest.pk])}'
        )
        self.selenium.find_element(By.CSS_SELECTOR, "button.complete-quest").click()

        # Wait for level up
        WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".level-up-notification"))
        )

        self.user.profile.refresh_from_db()
        assert self.user.profile.level > initial_level

    def test_profile_update_flow(self):
        self.selenium.get(f'{self.live_server_url}{reverse("dashboard:profile")}')
        self.selenium.find_element(By.NAME, "first_name").send_keys("Test")
        self.selenium.find_element(By.NAME, "last_name").send_keys("User")
        self.selenium.find_element(By.NAME, "email").send_keys("updated@example.com")
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".profile-updated"))
        )

        self.user.refresh_from_db()
        assert self.user.first_name == "Test"
        assert self.user.last_name == "User"
        assert self.user.email == "updated@example.com"

    def test_quest_creation(self):
        self.selenium.get(f'{self.live_server_url}{reverse("quests:quest_create")}')
        self.selenium.find_element(By.NAME, "title").send_keys("New Quest")
        self.selenium.find_element(By.NAME, "description").send_keys("Test Description")
        self.selenium.find_element(By.NAME, "difficulty").send_keys("easy")
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".quest-list"))
        )
