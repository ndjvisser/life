"""
Tests for verification method fix in privacy services.
"""

from unittest.mock import MagicMock

import pytest

from life_dashboard.privacy.application.services import DataSubjectService
from life_dashboard.privacy.domain.entities import DataCategory, DataSubjectRequest


class TestVerificationMethodFix:
    """Test cases for verification method parameter in privacy service methods."""

    def setup_method(self):
        """Set up test dependencies."""
        self.request_repo = MagicMock()
        self.settings_repo = MagicMock()
        self.consent_repo = MagicMock()
        self.activity_repo = MagicMock()

        self.service = DataSubjectService(
            self.request_repo, self.settings_repo, self.consent_repo, self.activity_repo
        )

    def test_process_export_request_with_verification_method(self):
        """Test that process_export_request accepts and uses verification_method parameter."""
        # Arrange
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 123
        mock_request.data_categories = {DataCategory.BASIC_PROFILE}

        self.request_repo.get_by_id.return_value = mock_request
        self.service._collect_user_data = MagicMock(return_value={"test": "data"})

        # Act
        result = self.service.process_export_request(
            "test_id", 456, verification_method="email"
        )

        # Assert
        mock_request.verify_identity.assert_called_once_with("email")
        mock_request.start_processing.assert_called_once_with(456)
        assert result == {"test": "data"}

    def test_process_export_request_without_verification_method(self):
        """Test that process_export_request works without verification_method when identity already verified."""
        # Arrange
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 123
        mock_request.data_categories = {DataCategory.BASIC_PROFILE}

        self.request_repo.get_by_id.return_value = mock_request
        self.service._collect_user_data = MagicMock(return_value={"test": "data"})

        # Act
        self.service.process_export_request("test_id", 456)

        # Assert
        mock_request.verify_identity.assert_not_called()
        mock_request.start_processing.assert_called_once_with(456)

    def test_process_deletion_request_with_verification_method(self):
        """Test that process_deletion_request accepts and uses verification_method parameter."""
        # Arrange
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 123

        self.request_repo.get_by_id.return_value = mock_request
        self.service._delete_user_data = MagicMock(return_value=42)

        # Act
        result = self.service.process_deletion_request(
            "test_id", 789, verification_method="sms"
        )

        # Assert
        mock_request.verify_identity.assert_called_once_with("sms")
        mock_request.start_processing.assert_called_once_with(789)
        assert result is True

    def test_process_deletion_request_without_verification_method(self):
        """Test that process_deletion_request works without verification_method when identity already verified."""
        # Arrange
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 123

        self.request_repo.get_by_id.return_value = mock_request
        self.service._delete_user_data = MagicMock(return_value=42)

        # Act
        self.service.process_deletion_request("test_id", 789)

        # Assert
        mock_request.verify_identity.assert_not_called()
        mock_request.start_processing.assert_called_once_with(789)

    def test_method_signatures_have_verification_method_parameter(self):
        """Test that both methods have verification_method parameter with default None."""
        import inspect

        # Check process_export_request
        export_sig = inspect.signature(self.service.process_export_request)
        assert "verification_method" in export_sig.parameters
        assert export_sig.parameters["verification_method"].default is None

        # Check process_deletion_request
        deletion_sig = inspect.signature(self.service.process_deletion_request)
        assert "verification_method" in deletion_sig.parameters
        assert deletion_sig.parameters["verification_method"].default is None

    def test_error_handling_for_missing_request(self):
        """Test that ValueError is raised when request is not found."""
        # Arrange
        self.request_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            self.service.process_export_request(
                "nonexistent", 123, verification_method="email"
            )

        with pytest.raises(ValueError, match="not found"):
            self.service.process_deletion_request(
                "nonexistent", 123, verification_method="email"
            )
