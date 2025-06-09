import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from quests.models import Habit
from .conftest import SeleniumTestCase

class TestHabits:
    def test_habit_list_view(self, authenticated_client):
        url = reverse('habit_list')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert 'Habits' in response.content.decode()

    def test_habit_create(self, authenticated_client):
        url = reverse('habit_create')
        data = {
            'name': 'New Habit',
            'description': 'Test Description',
            'frequency': 'daily',
            'target_count': 1,
            'experience_reward': 50
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        assert Habit.objects.filter(name='New Habit').exists()

    def test_habit_update(self, authenticated_client, test_habit):
        url = reverse('habit_update', args=[test_habit.pk])
        data = {
            'name': 'Updated Habit',
            'description': 'Updated Description',
            'frequency': 'daily',
            'target_count': 2,
            'experience_reward': 75
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        test_habit.refresh_from_db()
        assert test_habit.name == 'Updated Habit'
        assert test_habit.target_count == 2
        assert test_habit.experience_reward == 75

    def test_habit_delete(self, authenticated_client, test_habit):
        url = reverse('habit_delete', args=[test_habit.pk])
        response = authenticated_client.post(url)
        assert response.status_code == 302
        assert not Habit.objects.filter(pk=test_habit.pk).exists()

    def test_habit_completion(self, authenticated_client, test_habit):
        url = reverse('complete_habit', args=[test_habit.pk])
        response = authenticated_client.post(url)
        assert response.status_code == 302
        test_habit.refresh_from_db()
        assert test_habit.current_streak == 1

class TestHabitsSelenium(SeleniumTestCase):
    def test_habit_creation_flow(self):
        self.selenium.get(f'{self.live_server_url}{reverse("habit_create")}')
        
        # Fill in habit form
        name = self.selenium.find_element(By.NAME, 'name')
        description = self.selenium.find_element(By.NAME, 'description')
        frequency = self.selenium.find_element(By.NAME, 'frequency')
        target_count = self.selenium.find_element(By.NAME, 'target_count')
        experience_reward = self.selenium.find_element(By.NAME, 'experience_reward')
        
        name.send_keys('Selenium Habit')
        description.send_keys('Created via Selenium')
        frequency.send_keys('daily')
        target_count.send_keys('1')
        experience_reward.send_keys('50')
        
        # Submit form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for redirect to habit list
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains(reverse('habit_list'))
        )
        
        # Verify habit was created
        assert Habit.objects.filter(name='Selenium Habit').exists()

    def test_habit_completion_flow(self):
        # Create a habit first
        habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            description='Test Description',
            frequency='daily',
            target_count=1,
            experience_reward=50
        )
        
        self.selenium.get(f'{self.live_server_url}{reverse("habit_list")}')
        
        # Find and click complete button
        complete_button = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-habit-id="{habit.pk}"] .complete-btn'))
        )
        complete_button.click()
        
        # Wait for streak update
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, f'[data-habit-id="{habit.pk}"] .current-streak'), '1')
        )
        
        # Verify habit was completed
        habit.refresh_from_db()
        assert habit.current_streak == 1 