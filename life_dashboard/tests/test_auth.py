import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from life_dashboard.conftest import SeleniumTestCase

User = get_user_model()


@pytest.mark.django_db
class AuthTests(SeleniumTestCase):
    def test_register_view(self, client):
        url = reverse("register")
        response = client.get(url)
        assert response.status_code == 200
        assert "Register" in response.content.decode()

    def test_register_user_client(self, client):
        url = reverse("register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert User.objects.filter(username="newuser").exists()

    def test_login_view(self, client):
        url = reverse("login")
        response = client.get(url)
        assert response.status_code == 200
        assert "Login" in response.content.decode()

    def test_login_user_client(self, client, test_user):
        url = reverse("login")
        data = {"username": "testuser", "password": "testpass123"}
        response = client.post(url, data)
        assert response.status_code == 302

    def test_logout_client(self, authenticated_client):
        url = reverse("logout")
        response = authenticated_client.get(url)
        assert response.status_code == 302

    def test_signup_page_selenium(self):
        self.selenium.get(f'{self.live_server_url}{reverse("register")}')
        assert "Register" in self.selenium.page_source

    def test_login_page_selenium(self):
        self.selenium.get(f'{self.live_server_url}{reverse("login")}')
        assert "Login" in self.selenium.page_source

    def test_register_user_selenium(self):
        self.selenium.get(f'{self.live_server_url}{reverse("register")}')
        username = "testuser"
        email = "test@example.com"
        password = "testpass123"

        self.selenium.find_element(By.NAME, "username").send_keys(username)
        self.selenium.find_element(By.NAME, "email").send_keys(email)
        self.selenium.find_element(By.NAME, "password1").send_keys(password)
        self.selenium.find_element(By.NAME, "password2").send_keys(password)

        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".dashboard-container"))
        )

        assert User.objects.filter(username=username).exists()

    def test_login_user_selenium(self):
        self.selenium.get(f'{self.live_server_url}{reverse("login")}')
        username = "testuser"
        password = "testpass123"

        self.selenium.find_element(By.NAME, "username").send_keys(username)
        self.selenium.find_element(By.NAME, "password").send_keys(password)

        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".dashboard-container"))
        )

        assert "Welcome" in self.selenium.page_source

    def test_logout_selenium(self):
        self.selenium.get(f'{self.live_server_url}{reverse("logout")}')
        assert self.selenium.current_url == f'{self.live_server_url}{reverse("login")}'
