import time

import pytest
from django.urls import reverse
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from life_dashboard.conftest import SeleniumTestCase
from life_dashboard.quests.models import Habit, Quest


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
        initial_experience = test_user.stats.experience
        response = authenticated_client.post(
            reverse("quests:complete_habit", args=[habit.pk]),
            {"count": 1},
        )
        assert response.status_code == 302
        test_user.stats.refresh_from_db()
        assert test_user.stats.experience > initial_experience


@pytest.mark.django_db
class DashboardTests(SeleniumTestCase):
    def test_dashboard_page(self):
        self.driver.get(f'{self.live_server_url}{reverse("dashboard:dashboard")}')
        assert "Welcome" in self.driver.page_source

    def test_level_up_flow(self):
        self.driver.get(f'{self.live_server_url}{reverse("dashboard:dashboard")}')
        initial_level = self.user.stats.level

        # Complete a quest to gain experience
        quest = self.create_test_quest()
        self.driver.get(
            f'{self.live_server_url}{reverse("quests:quest_detail", args=[quest.pk])}'
        )
        self.driver.find_element(By.CSS_SELECTOR, "button.complete-quest").click()

        # Wait for level up
        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".level-up-notification"))
        )

        self.user.stats.refresh_from_db()
        assert self.user.stats.level > initial_level

    def test_profile_update_flow(self):
        self.driver.get(f'{self.live_server_url}{reverse("dashboard:profile")}')

        # Fill out the form
        first_name_input = self.driver.find_element(By.NAME, "first_name")
        last_name_input = self.driver.find_element(By.NAME, "last_name")
        email_input = self.driver.find_element(By.NAME, "email")

        first_name_input.clear()
        last_name_input.clear()
        email_input.clear()

        first_name_input.send_keys("Test")
        last_name_input.send_keys("User")
        email_input.send_keys("updated@example.com")

        # Submit the form
        submit_button = self.driver.find_element(
            By.CSS_SELECTOR, "button[type='submit']"
        )
        submit_button.click()

        # Wait for the profile page to reload
        expected_url = self.live_server_url + reverse("dashboard:profile")
        print(f"[DEBUG] Waiting for URL: {expected_url}")

        # Wait for URL to change and contain the expected path
        max_wait = 20  # Increase timeout to 20 seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            current_url = self.driver.current_url
            print(f"[DEBUG] Current URL: {current_url}")
            if expected_url in current_url:
                break
            time.sleep(0.5)

        # Wait for the success message
        print("[DEBUG] Waiting for success message")
        try:
            self.wait.until(
                ec.presence_of_element_located((By.ID, "profile-success-message"))
            )
        except TimeoutException:
            print("[DEBUG] Page source after timeout:")
            print(self.driver.page_source)
            raise

        # Verify the success message content
        success_message = self.driver.find_element(By.ID, "profile-success-message")
        self.assertIn("Profile updated successfully", success_message.text)

    def test_quest_creation(self):
        self.driver.get(f'{self.live_server_url}{reverse("quests:quest_create")}')
        self.driver.find_element(By.NAME, "title").send_keys("New Quest")
        self.driver.find_element(By.NAME, "description").send_keys("Test Description")
        self.driver.find_element(By.NAME, "difficulty").send_keys("easy")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".quest-list"))
        )

    def create_test_quest(self):
        return Quest.objects.create(
            title="Test Quest",
            description="Test Description",
            difficulty="easy",
            quest_type="main",
            status="active",
            experience_reward=1500,  # High enough to trigger level up
            user=self.user,
        )
