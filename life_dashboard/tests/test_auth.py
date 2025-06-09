import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .conftest import SeleniumTestCase

User = get_user_model()

class TestAuthentication:
    def test_register_view(self, client):
        url = reverse('register')
        response = client.get(url)
        assert response.status_code == 200
        assert 'Register' in response.content.decode()

    def test_register_user(self, client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()

    def test_login_view(self, client):
        url = reverse('login')
        response = client.get(url)
        assert response.status_code == 200
        assert 'Login' in response.content.decode()

    def test_login_user(self, client, test_user):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post(url, data)
        assert response.status_code == 302

    def test_logout(self, authenticated_client):
        url = reverse('logout')
        response = authenticated_client.get(url)
        assert response.status_code == 302

class TestAuthenticationSelenium(SeleniumTestCase):
    def test_register_flow(self):
        self.selenium.get(f'{self.live_server_url}{reverse("register")}')
        
        # Fill in registration form
        username = self.selenium.find_element(By.NAME, 'username')
        email = self.selenium.find_element(By.NAME, 'email')
        password1 = self.selenium.find_element(By.NAME, 'password1')
        password2 = self.selenium.find_element(By.NAME, 'password2')
        
        username.send_keys('seleniumuser')
        email.send_keys('selenium@example.com')
        password1.send_keys('testpass123')
        password2.send_keys('testpass123')
        
        # Submit form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for redirect to dashboard
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains(reverse('dashboard'))
        )
        
        assert User.objects.filter(username='seleniumuser').exists()

    def test_login_flow(self):
        self.selenium.get(f'{self.live_server_url}{reverse("login")}')
        
        # Fill in login form
        username = self.selenium.find_element(By.NAME, 'username')
        password = self.selenium.find_element(By.NAME, 'password')
        
        username.send_keys('testuser')
        password.send_keys('testpass123')
        
        # Submit form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for redirect to dashboard
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains(reverse('dashboard'))
        )
        
        # Verify we're logged in
        assert 'Welcome' in self.selenium.page_source 


if name == '__main__':
    pytest.main()
    