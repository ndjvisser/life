from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from life_dashboard.conftest import SeleniumTestCase
from life_dashboard.quests.models import Quest

User = get_user_model()


@pytest.mark.django_db
class QuestTests:
    def test_quest_list_page(self, authenticated_client):
        response = authenticated_client.get(reverse("quests:quest_list"))
        assert response.status_code == 200
        assert "Quests" in response.content.decode()

    def test_quest_create(self, authenticated_client):
        url = reverse("quests:quest_create")
        data = {
            "title": "Test Quest",
            "description": "Test Description",
            "difficulty": "medium",
            "quest_type": "main",
            "status": "active",
            "experience_reward": 50,
            "start_date": date.today(),
            "due_date": date.today(),
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        quest = Quest.objects.get(title="Test Quest")
        assert quest.description == "Test Description"
        assert quest.difficulty == "medium"
        assert quest.quest_type == "main"
        assert quest.status == "active"
        assert quest.experience_reward == 50
        assert quest.start_date == date.today()
        assert quest.due_date == date.today()

    def test_quest_update(self, authenticated_client, test_quest):
        url = reverse("quests:quest_update", args=[test_quest.pk])
        data = {
            "title": "Updated Quest",
            "description": "Updated Description",
            "difficulty": "hard",
            "quest_type": "side",
            "status": "completed",
            "experience_reward": 100,
            "start_date": date.today(),
            "due_date": date.today(),
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        test_quest.refresh_from_db()
        assert test_quest.title == "Updated Quest"
        assert test_quest.description == "Updated Description"
        assert test_quest.difficulty == "hard"
        assert test_quest.quest_type == "side"
        assert test_quest.status == "completed"
        assert test_quest.experience_reward == 100
        assert test_quest.start_date == date.today()
        assert test_quest.due_date == date.today()

    def test_quest_delete(self, authenticated_client, test_quest):
        url = reverse("quests:quest_delete", args=[test_quest.pk])
        response = authenticated_client.post(url)
        assert response.status_code == 302
        assert not Quest.objects.filter(pk=test_quest.pk).exists()


@pytest.mark.django_db
class QuestSeleniumTests(SeleniumTestCase):
    def test_quest_creation_flow(self):
        self.driver.get(self.live_server_url + reverse("quests:quest_list"))
        self.wait.until(
            ec.presence_of_element_located((By.LINK_TEXT, "Add New Quest"))
        ).click()

        # Fill in the quest form
        self.wait.until(ec.presence_of_element_located((By.NAME, "title"))).send_keys(
            "Test Quest"
        )
        self.driver.find_element(By.NAME, "description").send_keys("Test Description")
        self.driver.find_element(By.NAME, "difficulty").send_keys("medium")
        self.driver.find_element(By.NAME, "quest_type").send_keys("main")
        self.driver.find_element(By.NAME, "status").send_keys("active")
        self.driver.find_element(By.NAME, "experience_reward").clear()
        self.driver.find_element(By.NAME, "experience_reward").send_keys("50")
        self.driver.find_element(By.NAME, "start_date").clear()
        self.driver.find_element(By.NAME, "start_date").send_keys(
            date.today().strftime("%Y-%m-%d")
        )
        self.driver.find_element(By.NAME, "due_date").clear()
        self.driver.find_element(By.NAME, "due_date").send_keys(
            date.today().strftime("%Y-%m-%d")
        )
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify quest was created
        self.wait.until(
            ec.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Test Quest" in self.driver.page_source

    def test_quest_update_flow(self):
        # Create a quest first
        quest = self.create_test_quest()
        self.driver.get(
            self.live_server_url + reverse("quests:quest_detail", args=[quest.pk])
        )
        self.wait.until(ec.presence_of_element_located((By.LINK_TEXT, "Edit"))).click()

        # Update the quest
        title_input = self.wait.until(
            ec.presence_of_element_located((By.NAME, "title"))
        )
        title_input.clear()
        title_input.send_keys("Updated Quest")
        self.driver.find_element(By.NAME, "description").clear()
        self.driver.find_element(By.NAME, "description").send_keys(
            "Updated Description"
        )
        self.driver.find_element(By.NAME, "difficulty").send_keys("hard")
        self.driver.find_element(By.NAME, "quest_type").send_keys("side")
        self.driver.find_element(By.NAME, "status").send_keys("completed")
        self.driver.find_element(By.NAME, "experience_reward").clear()
        self.driver.find_element(By.NAME, "experience_reward").send_keys("100")
        self.driver.find_element(By.NAME, "start_date").clear()
        self.driver.find_element(By.NAME, "start_date").send_keys(
            date.today().strftime("%Y-%m-%d")
        )
        self.driver.find_element(By.NAME, "due_date").clear()
        self.driver.find_element(By.NAME, "due_date").send_keys(
            date.today().strftime("%Y-%m-%d")
        )
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify quest was updated
        self.wait.until(
            ec.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Updated Quest" in self.driver.page_source

    def test_quest_delete_flow(self):
        # Create a quest first
        quest = self.create_test_quest()
        self.driver.get(
            self.live_server_url + reverse("quests:quest_detail", args=[quest.pk])
        )
        self.wait.until(
            ec.presence_of_element_located((By.LINK_TEXT, "Delete Quest"))
        ).click()

        # Confirm deletion
        self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
        ).click()

        # Verify quest was deleted
        self.wait.until(
            ec.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Test Quest" not in self.driver.page_source

    def test_quest_completion(self):
        quest = Quest.objects.create(
            title="Test Quest",
            description="Test Description",
            difficulty="easy",
            quest_type="main",
            status="active",
            experience_reward=10,
            start_date=date.today(),
            due_date=date.today(),
            user=self.user,
        )
        self.selenium.get(
            f'{self.live_server_url}{reverse("quests:quest_detail", args=[quest.pk])}'
        )
        self.selenium.find_element(By.CSS_SELECTOR, "button.complete-quest").click()

        WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".completion-success"))
        )
