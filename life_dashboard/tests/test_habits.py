import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from life_dashboard.conftest import SeleniumTestCase
from life_dashboard.quests.models import Habit

User = get_user_model()


@pytest.mark.django_db
class TestHabits:
    def test_habit_list_view(self, authenticated_client):
        response = authenticated_client.get(reverse("quests:habit_list"))
        assert response.status_code == 200
        assert "Habits" in response.content.decode()

    def test_habit_create(self, authenticated_client):
        url = reverse("quests:habit_create")
        data = {
            "name": "Test Habit",
            "description": "Test Description",
            "frequency": "daily",
            "target_count": 1,
            "experience_reward": 10,
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        habit = Habit.objects.get(name="Test Habit")
        assert habit.description == "Test Description"
        assert habit.frequency == "daily"
        assert habit.target_count == 1
        assert habit.experience_reward == 10

    def test_habit_update(self, authenticated_client, test_habit):
        url = reverse("quests:habit_update", args=[test_habit.pk])
        data = {
            "name": "Updated Habit",
            "description": "Updated Description",
            "frequency": "weekly",
            "target_count": 2,
            "experience_reward": 20,
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        test_habit.refresh_from_db()
        assert test_habit.name == "Updated Habit"
        assert test_habit.description == "Updated Description"
        assert test_habit.frequency == "weekly"
        assert test_habit.target_count == 2
        assert test_habit.experience_reward == 20

    def test_habit_delete(self, authenticated_client, test_habit):
        url = reverse("quests:habit_delete", args=[test_habit.pk])
        response = authenticated_client.post(url)
        assert response.status_code == 302
        assert not Habit.objects.filter(pk=test_habit.pk).exists()

    def test_habit_completion(self, authenticated_client, test_habit):
        url = reverse("quests:complete_habit", args=[test_habit.pk])
        response = authenticated_client.post(url, {"count": 1})
        assert response.status_code == 302


@pytest.mark.django_db
class HabitTests(SeleniumTestCase):
    def test_habit_creation_flow(self):
        self.driver.get(f"{self.live_server_url}{reverse('quests:habit_create')}")
        self.driver.find_element(By.NAME, "name").send_keys("New Habit")
        self.driver.find_element(By.NAME, "description").send_keys("Test Description")
        self.driver.find_element(By.NAME, "frequency").send_keys("daily")
        self.driver.find_element(By.NAME, "experience_reward").send_keys("15")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".habit-list"))
        )

        habit = Habit.objects.get(name="New Habit")
        assert habit.experience_reward == 15

    def test_habit_completion_flow(self):
        habit = Habit.objects.create(
            name="Test Habit",
            description="Test Description",
            frequency="daily",
            user=self.user,
        )
        self.driver.get(
            f"{self.live_server_url}{reverse('quests:habit_detail', args=[habit.pk])}"
        )
        self.driver.find_element(By.CSS_SELECTOR, "button.complete-habit").click()

        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".completion-success"))
        )
