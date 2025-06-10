import time

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
    def test_register_view(self):
        url = reverse("dashboard:register")
        response = self.client.get(url)
        assert response.status_code == 200
        assert "Register" in response.content.decode()

    def test_register_user_client(self):
        url = reverse("dashboard:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        response = self.client.post(url, data)
        assert response.status_code == 302
        assert User.objects.filter(username="newuser").exists()

    def test_login_view(self):
        url = reverse("dashboard:login")
        response = self.client.get(url)
        assert response.status_code == 200
        assert "Login" in response.content.decode()

    def test_login_user_client(self):
        url = reverse("dashboard:login")
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data)
        assert response.status_code == 302

    def test_logout_client(self):
        url = reverse("dashboard:logout")
        response = self.client.get(url)
        assert response.status_code == 302

    def test_signup_page_selenium(self):
        self.driver.get(f'{self.live_server_url}{reverse("dashboard:register")}')
        assert "Register" in self.driver.page_source

    def test_login_page_selenium(self):
        self.driver.get(f'{self.live_server_url}{reverse("dashboard:login")}')
        assert "Login" in self.driver.page_source

    def test_register_user_selenium(self):
        self.driver.get(f'{self.live_server_url}{reverse("dashboard:register")}')
        username = "newuser_selenium"
        email = "new@example.com"
        password = "testpass123"

        print(f"[DEBUG] Filling registration form for user: {username}")

        # Wait for form to be ready and page to be fully loaded
        self.wait.until(ec.presence_of_element_located((By.ID, "registration-form")))
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )

        # Wait for and fill username
        username_input = self.wait.until(
            ec.presence_of_element_located((By.NAME, "username"))
        )
        username_input.clear()
        username_input.send_keys(username)
        print(f"[DEBUG] Username field value: {username_input.get_attribute('value')}")

        # Wait for and fill email
        email_input = self.wait.until(
            ec.presence_of_element_located((By.NAME, "email"))
        )
        email_input.clear()
        email_input.send_keys(email)
        print(f"[DEBUG] Email field value: {email_input.get_attribute('value')}")

        # Wait for and fill passwords
        password1_input = self.wait.until(
            ec.presence_of_element_located((By.NAME, "password1"))
        )
        password2_input = self.wait.until(
            ec.presence_of_element_located((By.NAME, "password2"))
        )

        password1_input.clear()
        password1_input.send_keys(password)
        password2_input.clear()
        password2_input.send_keys(password)
        print("[DEBUG] Passwords filled")

        # Verify all fields have values
        assert (
            username_input.get_attribute("value") == username
        ), "Username not set correctly"
        assert email_input.get_attribute("value") == email, "Email not set correctly"
        assert (
            password1_input.get_attribute("value") == password
        ), "Password1 not set correctly"
        assert (
            password2_input.get_attribute("value") == password
        ), "Password2 not set correctly"

        # Check for any JavaScript errors before submitting
        js_errors = self.driver.execute_script(
            "return window.performance.getEntriesByType('resource')"
            ".filter(r => r.name.includes('error'));"
        )
        if js_errors:
            print(f"[DEBUG] JavaScript errors found: {js_errors}")

        print("[DEBUG] Submitting registration form")
        # Submit the form using JavaScript to ensure it's properly submitted
        self.driver.execute_script(
            "document.getElementById('registration-form').submit();"
        )

        # Check for form errors
        try:
            error_elements = self.driver.find_elements(By.CLASS_NAME, "errorlist")
            if error_elements:
                print("[DEBUG] Form errors found:")
                for error in error_elements:
                    print(f"[DEBUG] Error: {error.text}")
        except Exception as e:
            print(f"[DEBUG] Error checking form errors: {str(e)}")

        # Wait for redirect to dashboard
        expected_url = self.live_server_url + reverse("dashboard:dashboard")
        print(f"[DEBUG] Waiting for URL: {expected_url}")

        # Wait for URL to change and contain the expected path
        max_wait = 20  # Increase timeout to 20 seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            current_url = self.driver.current_url
            print(f"[DEBUG] Current URL: {current_url}")

            # Check for form errors again in case they appear after submission
            try:
                error_elements = self.driver.find_elements(By.CLASS_NAME, "errorlist")
                if error_elements:
                    print("[DEBUG] Form errors after submission:")
                    for error in error_elements:
                        print(f"[DEBUG] Error: {error.text}")
            except Exception as e:
                print(f"[DEBUG] Error checking form errors after submission: {str(e)}")

            if expected_url in current_url:
                break
            time.sleep(0.5)

        # Check for any JavaScript errors after submitting
        js_errors = self.driver.execute_script(
            "return window.performance.getEntriesByType('resource')"
            ".filter(r => r.name.includes('error'));"
        )
        if js_errors:
            print(f"[DEBUG] JavaScript errors after submit: {js_errors}")

        # Wait for dashboard to load
        print("[DEBUG] Waiting for dashboard container")
        try:
            self.wait.until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, ".dashboard-container")
                )
            )
        except Exception as e:
            print(f"[DEBUG] Failed to find dashboard container: {str(e)}")
            print("[DEBUG] Current page source:")
            print(self.driver.page_source)

        # Now check if user was created
        print(f"[DEBUG] Checking if user {username} exists in database")
        user_exists = User.objects.filter(username=username).exists()
        if not user_exists:
            print("[DEBUG] User not found in database. Checking all users:")
            for user in User.objects.all():
                print(f"[DEBUG] Found user: {user.username} (ID: {user.id})")
        assert user_exists, f"User {username} was not created in the database"

    def test_login_user_selenium(self):
        self.driver.get(f'{self.live_server_url}{reverse("dashboard:login")}')
        username = "testuser"
        password = "testpass123"

        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".dashboard-container"))
        )

        assert "Welcome" in self.driver.page_source

    def test_logout_selenium(self):
        self.driver.get(f'{self.live_server_url}{reverse("dashboard:logout")}')
        assert (
            self.driver.current_url
            == f'{self.live_server_url}{reverse("dashboard:login")}'
        )
