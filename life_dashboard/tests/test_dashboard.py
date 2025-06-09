import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from life_dashboard.conftest import SeleniumTestCase
from life_dashboard.quests.models import Quest


class TestDashboard:
    def test_dashboard_view(self, authenticated_client):
        url = reverse("dashboard")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "Dashboard" in response.content.decode()

    def test_profile_view(self, authenticated_client):
        url = reverse("profile")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "Profile" in response.content.decode()

    def test_profile_update(self, authenticated_client, test_user):
        url = reverse("profile")
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

    def test_experience_gain(self, authenticated_client, test_user, test_quest):
        initial_experience = test_user.profile.experience
        url = reverse("complete_quest", args=[test_quest.pk])
        response = authenticated_client.post(url)
        assert response.status_code == 302
        test_user.profile.refresh_from_db()
        assert (
            test_user.profile.experience
            == initial_experience + test_quest.experience_reward
        )


@pytest.mark.django_db
class DashboardTests(SeleniumTestCase):
    def test_dashboard_page(self):
        self.selenium.get(f'{self.live_server_url}{reverse("dashboard")}')

        # Verify dashboard elements
        assert "Welcome" in self.selenium.page_source
        assert "Stats Overview" in self.selenium.page_source
        assert "Recent Activity" in self.selenium.page_source

    def test_profile_update_flow(self):
        self.selenium.get(f'{self.live_server_url}{reverse("profile")}')

        # Fill in profile form
        first_name = self.selenium.find_element(By.NAME, "first_name")
        last_name = self.selenium.find_element(By.NAME, "last_name")
        email = self.selenium.find_element(By.NAME, "email")

        first_name.clear()
        last_name.clear()
        email.clear()

        first_name.send_keys("Selenium")
        last_name.send_keys("User")
        email.send_keys("selenium@example.com")

        # Submit form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Wait for success message
        WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )

        # Verify profile was updated
        self.user.refresh_from_db()
        assert self.user.first_name == "Selenium"
        assert self.user.last_name == "User"
        assert self.user.email == "selenium@example.com"

    def test_level_up_flow(self):
        # Set up initial state
        self.profile.experience = 0
        self.profile.save()

        # Create and complete a quest
        quest = Quest.objects.create(
            user=self.user,
            title="Level Up Quest",
            description="Test Description",
            quest_type="daily",
            status="active",
            experience_reward=1000,  # Enough to level up
        )

        self.selenium.get(f'{self.live_server_url}{reverse("quest_list")}')

        # Complete the quest
        complete_button = WebDriverWait(self.selenium, 10).until(
            ec.element_to_be_clickable(
                (By.CSS_SELECTOR, f'[data-quest-id="{quest.pk}"] .complete-btn')
            )
        )
        complete_button.click()

        # Wait for level up notification
        WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "level-up-notification"))
        )

        # Verify level up
        self.profile.refresh_from_db()
        assert self.profile.level > 1

    def test_quest_creation(self):
        """Test quest creation."""
        self.selenium.get(f"{self.live_server_url}{reverse('quest_create')}")

        # Fill in quest form
        title = "Test Quest"
        description = "Test Description"

        self.selenium.find_element(By.NAME, "title").send_keys(title)
        self.selenium.find_element(By.NAME, "description").send_keys(description)

        # Submit form
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for redirect to dashboard
        WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".dashboard-container"))
        )

        # Verify quest was created
        quest = Quest.objects.get(title=title)
        assert quest.description == description
