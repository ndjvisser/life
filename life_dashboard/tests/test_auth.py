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
        self.driver.get(f"{self.live_server_url}{reverse('dashboard:register')}")
        assert "Register" in self.driver.page_source

    def test_login_page_selenium(self):
        self.driver.get(f"{self.live_server_url}{reverse('dashboard:login')}")
        assert "Login" in self.driver.page_source

    def fill_registration_form(self, username, email, password):
        """Fill out the registration form with the provided data."""
        print(f"[DEBUG] Filling registration form for user: {username}")

        # Wait for form to be ready and page to be fully loaded
        self.wait.until(ec.presence_of_element_located((By.ID, "registration-form")))
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )

        # Fill username using JavaScript
        username_input = self.wait.until(
            ec.presence_of_element_located((By.ID, "id_username"))
        )
        self.driver.execute_script(
            "arguments[0].value = arguments[1];", username_input, username
        )
        print(f"[DEBUG] Username field value: {username_input.get_attribute('value')}")

        # Fill email using JavaScript
        email_input = self.wait.until(
            ec.presence_of_element_located((By.ID, "id_email"))
        )
        self.driver.execute_script(
            "arguments[0].value = arguments[1];", email_input, email
        )
        print(f"[DEBUG] Email field value: {email_input.get_attribute('value')}")

        # Fill passwords using JavaScript
        password1_input = self.wait.until(
            ec.presence_of_element_located((By.ID, "id_password1"))
        )
        password2_input = self.wait.until(
            ec.presence_of_element_located((By.ID, "id_password2"))
        )

        self.driver.execute_script(
            "arguments[0].value = arguments[1];", password1_input, password
        )
        self.driver.execute_script(
            "arguments[0].value = arguments[1];", password2_input, password
        )
        print("[DEBUG] Passwords filled")

        return username_input, email_input, password1_input, password2_input

    def verify_form_values(
        self,
        username_input,
        email_input,
        password1_input,
        password2_input,
        username,
        email,
        password,
    ):
        """Verify that form fields contain the expected values."""
        assert username_input.get_attribute("value") == username, (
            "Username not set correctly"
        )
        assert email_input.get_attribute("value") == email, "Email not set correctly"
        assert password1_input.get_attribute("value") == password, (
            "Password1 not set correctly"
        )
        assert password2_input.get_attribute("value") == password, (
            "Password2 not set correctly"
        )

    def check_javascript_errors(self):
        """Check for any JavaScript errors in the browser console."""
        js_errors = self.driver.execute_script(
            "return window.performance.getEntriesByType('resource')"
            ".filter(r => r.name.includes('error'));"
        )
        if js_errors:
            print(f"[DEBUG] JavaScript errors found: {js_errors}")
        return js_errors

    def check_form_errors(self):
        """Check for any form validation errors."""
        try:
            error_elements = self.driver.find_elements(By.CLASS_NAME, "errorlist")
            if error_elements:
                print("[DEBUG] Form errors found:")
                for error in error_elements:
                    print(f"[DEBUG] Error: {error.text}")
            return error_elements
        except Exception as e:
            print(f"[DEBUG] Error checking form errors: {str(e)}")
            return []

    def wait_for_redirect(self, expected_url, timeout=20):
        """Wait for the page to redirect to the expected URL."""
        print(f"[DEBUG] Waiting for URL: {expected_url}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_url = self.driver.current_url
            print(f"[DEBUG] Current URL: {current_url}")
            if expected_url in current_url:
                return True
            time.sleep(0.5)
        return False

    def verify_user_creation(self, username):
        """Verify that the user was created in the database."""
        print(f"[DEBUG] Checking if user {username} exists in database")
        user_exists = User.objects.filter(username=username).exists()
        if not user_exists:
            print("[DEBUG] User not found in database. Checking all users:")
            for user in User.objects.all():
                print(f"[DEBUG] Found user: {user.username} (ID: {user.id})")
        assert user_exists, f"User {username} was not created in the database"

    def test_register_user_selenium(self):
        """Test the complete user registration flow."""
        self.driver.get(f"{self.live_server_url}{reverse('dashboard:register')}")
        username = "newuser_selenium"
        email = "new@example.com"
        password = "testpass123"

        # Fill and verify form
        form_inputs = self.fill_registration_form(username, email, password)
        self.verify_form_values(*form_inputs, username, email, password)

        # Check for JavaScript errors before submitting
        self.check_javascript_errors()

        # Submit the form
        print("[DEBUG] Submitting registration form")
        self.driver.execute_script(
            "document.getElementById('registration-form').submit();"
        )

        # Check for form errors
        self.check_form_errors()

        # Wait for redirect to dashboard
        expected_url = self.live_server_url + reverse("dashboard:dashboard")
        assert self.wait_for_redirect(expected_url), "Failed to redirect to dashboard"

        # Check for JavaScript errors after submitting
        self.check_javascript_errors()

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

        # Verify user creation
        self.verify_user_creation(username)

    def test_login_user_selenium(self):
        self.driver.get(f"{self.live_server_url}{reverse('dashboard:login')}")
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
        self.driver.get(f"{self.live_server_url}{reverse('dashboard:logout')}")
        assert (
            self.driver.current_url
            == f"{self.live_server_url}{reverse('dashboard:login')}"
        )
