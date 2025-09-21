"""Tests for data subject service processing safeguards and verification handling."""

from unittest.mock import MagicMock

import pytest

from life_dashboard.privacy.application.services import DataSubjectService
from life_dashboard.privacy.domain.entities import (
    DataCategory,
    DataProcessingPurpose,
    DataSubjectRequest,
)


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
        mock_request.request_id = "test_id"
        mock_request.status = "pending"
        mock_request.identity_verified = False  # Ensure identity needs verification
        mock_request.request_type = "export"

        self.request_repo.get_by_id.return_value = mock_request
        self.request_repo.mark_processing_if_pending.return_value = mock_request
        self.service._collect_user_data = MagicMock(return_value={"test": "data"})

        # Act
        result = self.service.process_export_request(
            "test_id", 456, verification_method="email"
        )

        # Assert
        mock_request.verify_identity.assert_called_once_with("email")
        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "test_id", 456
        )
        mock_request.start_processing.assert_not_called()
        assert result == {"test": "data"}

    def test_process_export_request_without_verification_method(self):
        """Test that process_export_request works without verification_method when identity already verified."""
        # Arrange
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 123
        mock_request.data_categories = {DataCategory.BASIC_PROFILE}
        mock_request.request_id = "test_id"
        mock_request.status = "pending"
        mock_request.identity_verified = True
        mock_request.request_type = "export"

        self.request_repo.get_by_id.return_value = mock_request
        self.request_repo.mark_processing_if_pending.return_value = mock_request
        self.service._collect_user_data = MagicMock(return_value={"test": "data"})

        # Act
        self.service.process_export_request("test_id", 456)

        # Assert
        mock_request.verify_identity.assert_not_called()
        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "test_id", 456
        )
        mock_request.start_processing.assert_not_called()

    def test_process_deletion_request_with_verification_method(self):
        """Test that process_deletion_request accepts and uses verification_method parameter."""
        # Arrange
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 123
        mock_request.data_categories = set(DataCategory)
        mock_request.request_id = "test_id"
        mock_request.status = "pending"
        mock_request.identity_verified = False  # Ensure identity needs verification
        mock_request.request_type = "delete"

        self.request_repo.get_by_id.return_value = mock_request
        self.request_repo.mark_processing_if_pending.return_value = mock_request
        self.service._delete_user_data = MagicMock(return_value=42)

        # Act
        result = self.service.process_deletion_request(
            "test_id", 789, verification_method="sms"
        )

        # Assert
        mock_request.verify_identity.assert_called_once_with("sms")
        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "test_id", 789
        )
        mock_request.start_processing.assert_not_called()
        assert result is True

    def test_process_deletion_request_without_verification_method(self):
        """Test that process_deletion_request works without verification_method when identity already verified."""
        # Arrange
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 123
        mock_request.data_categories = set(DataCategory)
        mock_request.request_id = "test_id"
        mock_request.status = "pending"
        mock_request.identity_verified = True
        mock_request.request_type = "delete"

        self.request_repo.get_by_id.return_value = mock_request
        self.request_repo.mark_processing_if_pending.return_value = mock_request
        self.service._delete_user_data = MagicMock(return_value=42)

        # Act
        self.service.process_deletion_request("test_id", 789)

        # Assert
        mock_request.verify_identity.assert_not_called()
        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "test_id", 789
        )
        mock_request.start_processing.assert_not_called()
        self.service._delete_user_data.assert_called_once_with(
            123, delete_activities=False
        )

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

    def test_process_export_request_rejects_non_export_type(self):
        """Processing should fail if the request is not an export type."""
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.request_type = "delete"
        mock_request.status = "pending"

        self.request_repo.get_by_id.return_value = mock_request

        with pytest.raises(ValueError, match="not an export request"):
            self.service.process_export_request("wrong-type", 1)

    def test_process_deletion_request_rejects_non_deletion_type(self):
        """Processing should fail if the request is not a deletion type."""
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.request_type = "export"
        mock_request.status = "pending"

        self.request_repo.get_by_id.return_value = mock_request

        with pytest.raises(ValueError, match="not a deletion request"):
            self.service.process_deletion_request("wrong-type", 1)

    def test_process_export_request_logs_audit_events(self):
        """Processing an export request should emit start and completion audit activities."""
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 7
        mock_request.data_categories = {DataCategory.BASIC_PROFILE}
        mock_request.request_id = "export-1"
        mock_request.status = "pending"
        mock_request.identity_verified = True
        mock_request.request_type = "export"

        self.request_repo.get_by_id.return_value = mock_request
        self.request_repo.mark_processing_if_pending.return_value = mock_request
        self.service._collect_user_data = MagicMock(return_value={})

        self.service.process_export_request("export-1", 99)

        activities = [
            call.args[0] for call in self.activity_repo.log_activity.call_args_list
        ]
        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "export-1", 99
        )
        mock_request.start_processing.assert_not_called()
        assert {activity.processing_type for activity in activities} == {
            "dsar_export_started",
            "dsar_export_completed",
        }
        for activity in activities:
            assert activity.context == "data_subject_service:export"
            assert activity.legal_basis == "legal_obligation"
            assert activity.purpose == DataProcessingPurpose.CORE_FUNCTIONALITY
            assert activity.request_id == "export-1"

    def test_process_deletion_request_logs_audit_events(self):
        """Processing a deletion request should emit start and completion audit activities."""
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 9
        mock_request.data_categories = set(DataCategory)
        mock_request.request_id = "delete-1"
        mock_request.status = "pending"
        mock_request.identity_verified = True
        mock_request.request_type = "delete"

        self.request_repo.get_by_id.return_value = mock_request
        self.request_repo.mark_processing_if_pending.return_value = mock_request
        self.service._delete_user_data = MagicMock(return_value=5)

        self.service.process_deletion_request("delete-1", 42)

        activities = [
            call.args[0] for call in self.activity_repo.log_activity.call_args_list
        ]
        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "delete-1", 42
        )
        mock_request.start_processing.assert_not_called()
        assert {activity.processing_type for activity in activities} == {
            "dsar_deletion_started",
            "dsar_deletion_completed",
        }
        for activity in activities:
            assert activity.context == "data_subject_service:deletion"
            assert activity.legal_basis == "legal_obligation"
            assert activity.purpose == DataProcessingPurpose.CORE_FUNCTIONALITY
            assert activity.request_id == "delete-1"

    def test_process_export_request_handles_processing_failure(self):
        """Export failures should reject the request and log a failure event."""
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 15
        mock_request.data_categories = {DataCategory.BASIC_PROFILE}
        mock_request.request_id = "export-fail"
        mock_request.status = "pending"
        mock_request.identity_verified = True
        mock_request.request_type = "export"

        self.request_repo.get_by_id.return_value = mock_request
        self.request_repo.mark_processing_if_pending.return_value = mock_request
        self.service._collect_user_data = MagicMock(
            side_effect=RuntimeError("boom")
        )

        with pytest.raises(RuntimeError, match="boom"):
            self.service.process_export_request("export-fail", 21)

        mock_request.reject_request.assert_called_once()
        assert "boom" in mock_request.reject_request.call_args[0][0]
        self.request_repo.save.assert_called_with(mock_request)
        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "export-fail", 21
        )
        start_activity, failure_activity = [
            call.args[0] for call in self.activity_repo.log_activity.call_args_list
        ]
        assert start_activity.processing_type == "dsar_export_started"
        assert failure_activity.processing_type == "dsar_export_failed"
        assert failure_activity.details == {"error": "boom"}
        mock_request.complete_request.assert_not_called()

    def test_process_deletion_request_handles_processing_failure(self):
        """Deletion failures should reject the request and log a failure event."""
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 20
        mock_request.data_categories = set(DataCategory)
        mock_request.request_id = "delete-fail"
        mock_request.status = "pending"
        mock_request.identity_verified = True
        mock_request.request_type = "delete"

        self.request_repo.get_by_id.return_value = mock_request
        self.request_repo.mark_processing_if_pending.return_value = mock_request
        self.service._delete_user_data = MagicMock(
            side_effect=RuntimeError("kaboom")
        )

        with pytest.raises(RuntimeError, match="kaboom"):
            self.service.process_deletion_request("delete-fail", 33)

        mock_request.reject_request.assert_called_once()
        assert "kaboom" in mock_request.reject_request.call_args[0][0]
        self.request_repo.save.assert_called_with(mock_request)
        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "delete-fail", 33
        )
        start_activity, failure_activity = [
            call.args[0] for call in self.activity_repo.log_activity.call_args_list
        ]
        assert start_activity.processing_type == "dsar_deletion_started"
        assert failure_activity.processing_type == "dsar_deletion_failed"
        assert failure_activity.details == {"error": "kaboom"}
        mock_request.complete_request.assert_not_called()

    def test_process_export_request_respects_atomic_claim(self):
        """A concurrent claim should surface as an already-claimed error."""
        initial_request = MagicMock(spec=DataSubjectRequest)
        initial_request.request_type = "export"
        initial_request.status = "pending"
        initial_request.identity_verified = True
        initial_request.request_id = "export-atomic"
        initial_request.user_id = 44
        initial_request.data_categories = {DataCategory.BASIC_PROFILE}

        claimed_request = MagicMock(spec=DataSubjectRequest)
        claimed_request.status = "completed"
        claimed_request.request_type = "export"

        self.request_repo.get_by_id.side_effect = [initial_request, claimed_request]
        self.request_repo.mark_processing_if_pending.return_value = None

        with pytest.raises(ValueError, match="already been resolved"):
            self.service.process_export_request("export-atomic", 77)

        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "export-atomic", 77
        )

    def test_process_deletion_request_respects_atomic_claim(self):
        """When another worker claims the request, processing aborts."""
        initial_request = MagicMock(spec=DataSubjectRequest)
        initial_request.request_type = "delete"
        initial_request.status = "pending"
        initial_request.identity_verified = True
        initial_request.request_id = "delete-atomic"
        initial_request.user_id = 55
        initial_request.data_categories = set(DataCategory)

        in_progress = MagicMock(spec=DataSubjectRequest)
        in_progress.status = "processing"
        in_progress.request_type = "delete"

        self.request_repo.get_by_id.side_effect = [initial_request, in_progress]
        self.request_repo.mark_processing_if_pending.return_value = None

        with pytest.raises(ValueError, match="already being processed"):
            self.service.process_deletion_request("delete-atomic", 88)

        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "delete-atomic", 88
        )

    def test_process_export_request_prevents_double_processing(self):
        """Requests that are already resolved should raise an error when reprocessed."""
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.status = "completed"
        mock_request.request_type = "export"

        self.request_repo.get_by_id.return_value = mock_request

        with pytest.raises(ValueError, match="already been resolved"):
            self.service.process_export_request("export-2", 1)

        self.request_repo.mark_processing_if_pending.assert_not_called()

    def test_process_deletion_request_prevents_double_processing(self):
        """Requests already in processing should not be processed again."""
        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.status = "processing"
        mock_request.request_type = "delete"

        self.request_repo.get_by_id.return_value = mock_request

        with pytest.raises(ValueError, match="already being processed"):
            self.service.process_deletion_request("delete-2", 1)

        self.request_repo.mark_processing_if_pending.assert_not_called()

    def test_process_deletion_respects_activity_policy_toggle(self):
        """Deletion should pass the configured activity deletion policy flag."""
        service = DataSubjectService(
            self.request_repo,
            self.settings_repo,
            self.consent_repo,
            self.activity_repo,
            delete_activity_logs_on_deletion=True,
        )

        mock_request = MagicMock(spec=DataSubjectRequest)
        mock_request.user_id = 321
        mock_request.data_categories = set(DataCategory)
        mock_request.request_id = "delete-flag"
        mock_request.status = "pending"
        mock_request.identity_verified = True
        mock_request.request_type = "delete"

        self.request_repo.get_by_id.return_value = mock_request
        self.request_repo.mark_processing_if_pending.return_value = mock_request
        service._delete_user_data = MagicMock(return_value=0)

        service.process_deletion_request("delete-flag", 5)

        service._delete_user_data.assert_called_once_with(321, delete_activities=True)
        self.request_repo.mark_processing_if_pending.assert_called_once_with(
            "delete-flag", 5
        )
