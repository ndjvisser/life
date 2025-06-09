from django.urls import reverse
from quests.models import Quest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from .conftest import SeleniumTestCase


class TestQuests:
    def test_quest_list_view(self, authenticated_client):
        url = reverse("quest_list")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "Quests" in response.content.decode()

    def test_quest_create(self, authenticated_client):
        url = reverse("quest_create")
        data = {
            "title": "New Quest",
            "description": "Test Description",
            "quest_type": "daily",
            "status": "in_progress",
            "experience_reward": 100,
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        assert Quest.objects.filter(title="New Quest").exists()

    def test_quest_update(self, authenticated_client, test_quest):
        url = reverse("quest_update", args=[test_quest.pk])
        data = {
            "title": "Updated Quest",
            "description": "Updated Description",
            "quest_type": "daily",
            "status": "in_progress",
            "experience_reward": 150,
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        test_quest.refresh_from_db()
        assert test_quest.title == "Updated Quest"
        assert test_quest.experience_reward == 150

    def test_quest_delete(self, authenticated_client, test_quest):
        url = reverse("quest_delete", args=[test_quest.pk])
        response = authenticated_client.post(url)
        assert response.status_code == 302
        assert not Quest.objects.filter(pk=test_quest.pk).exists()


class TestQuestsSelenium(SeleniumTestCase):
    def test_quest_creation_flow(self):
        self.selenium.get(f'{self.live_server_url}{reverse("quest_create")}')

        # Fill in quest form
        title = self.selenium.find_element(By.NAME, "title")
        description = self.selenium.find_element(By.NAME, "description")
        quest_type = self.selenium.find_element(By.NAME, "quest_type")
        experience_reward = self.selenium.find_element(By.NAME, "experience_reward")

        title.send_keys("Selenium Quest")
        description.send_keys("Created via Selenium")
        quest_type.send_keys("daily")
        experience_reward.send_keys("100")

        # Submit form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Wait for redirect to quest list
        WebDriverWait(self.selenium, 10).until(ec.url_contains(reverse("quest_list")))

        # Verify quest was created
        assert Quest.objects.filter(title="Selenium Quest").exists()

    def test_quest_completion(self):
        # Create a quest first
        quest = Quest.objects.create(
            user=self.user,
            title="Test Quest",
            description="Test Description",
            quest_type="daily",
            status="in_progress",
            experience_reward=100,
        )

        self.selenium.get(f'{self.live_server_url}{reverse("quest_list")}')

        # Find and click complete button
        complete_button = WebDriverWait(self.selenium, 10).until(
            ec.element_to_be_clickable(
                (By.CSS_SELECTOR, f'[data-quest-id="{quest.pk}"] .complete-btn')
            )
        )
        complete_button.click()

        # Wait for status update
        WebDriverWait(self.selenium, 10).until(
            ec.text_to_be_present_in_element(
                (By.CSS_SELECTOR, f'[data-quest-id="{quest.pk}"] .status'), "Completed"
            )
        )

        # Verify quest was completed
        quest.refresh_from_db()
        assert quest.status == "completed"
