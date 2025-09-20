"""
Tests for skill validation, particularly the add_experience method validation.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from life_dashboard.skills.models import Skill, SkillCategory


class TestSkillValidation(TestCase):
    """Test cases for skill validation logic."""

    def setUp(self):
        """Set up test data."""
        User = get_user_model()
        self.user = User.objects.create_user(
            username="skilltest", email="skill@test.com", password="testpass123"
        )

        self.category = SkillCategory.objects.create(
            name="Test Category", description="Test category for validation tests"
        )

        self.skill = Skill.objects.create(
            user=self.user,
            name="Test Skill",
            category=self.category,
            level=1,
            experience_points=0,
        )

    def test_add_experience_positive_amount_works(self):
        """Test that positive experience amounts work correctly."""
        initial_experience = self.skill.experience_points

        # This should work without raising an exception
        self.skill.add_experience(50)

        self.assertEqual(self.skill.experience_points, initial_experience + 50)

    def test_add_experience_zero_amount_raises_validation_error(self):
        """Test that zero experience amount raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.skill.add_experience(0)

        self.assertIn("Experience amount must be positive", str(context.exception))

    def test_add_experience_negative_amount_raises_validation_error(self):
        """Test that negative experience amount raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.skill.add_experience(-10)

        self.assertIn("Experience amount must be positive", str(context.exception))

    def test_add_experience_large_negative_amount_raises_validation_error(self):
        """Test that large negative experience amount raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.skill.add_experience(-1000)

        self.assertIn("Experience amount must be positive", str(context.exception))

    def test_add_experience_validation_preserves_original_experience(self):
        """Test that validation errors don't modify the skill's experience."""
        initial_experience = self.skill.experience_points

        # Try to add zero experience (should fail)
        with self.assertRaises(ValidationError):
            self.skill.add_experience(0)

        # Experience should remain unchanged
        self.assertEqual(self.skill.experience_points, initial_experience)

        # Try to add negative experience (should fail)
        with self.assertRaises(ValidationError):
            self.skill.add_experience(-50)

        # Experience should still remain unchanged
        self.assertEqual(self.skill.experience_points, initial_experience)

    def test_add_experience_small_positive_amounts(self):
        """Test that small positive amounts work correctly."""
        initial_experience = self.skill.experience_points

        # Add 1 experience point (minimum positive amount)
        self.skill.add_experience(1)
        self.assertEqual(self.skill.experience_points, initial_experience + 1)

        # Add another small amount
        self.skill.add_experience(5)
        self.assertEqual(self.skill.experience_points, initial_experience + 6)

    def test_add_experience_error_message_matches_domain(self):
        """Test that the error message matches the domain entity error message."""
        # The domain entity uses "Experience amount must be positive"
        # The model should use the same message for consistency

        with self.assertRaises(ValidationError) as context:
            self.skill.add_experience(0)

        error_message = str(context.exception)
        self.assertIn("Experience amount must be positive", error_message)

        with self.assertRaises(ValidationError) as context:
            self.skill.add_experience(-1)

        error_message = str(context.exception)
        self.assertIn("Experience amount must be positive", error_message)

    def test_add_experience_boundary_values(self):
        """Test boundary values around zero."""
        # Test -1 (should fail)
        with self.assertRaises(ValidationError):
            self.skill.add_experience(-1)

        # Test 0 (should fail)
        with self.assertRaises(ValidationError):
            self.skill.add_experience(0)

        # Test 1 (should succeed)
        initial_experience = self.skill.experience_points
        self.skill.add_experience(1)
        self.assertEqual(self.skill.experience_points, initial_experience + 1)
