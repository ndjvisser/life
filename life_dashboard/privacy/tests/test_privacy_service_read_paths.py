"""Tests covering read-only privacy service behaviour."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from life_dashboard.privacy.application.services import ConsentService, PrivacyService
from life_dashboard.privacy.domain.entities import (
    ConsentRecord,
    ConsentStatus,
    DataCategory,
    DataProcessingPurpose,
)


def test_check_consent_does_not_mutate_expired_record():
    """Expired consents should remain unchanged when checked for validity."""
    consent_repo = MagicMock()
    activity_repo = MagicMock()
    service = ConsentService(consent_repo, activity_repo)

    expired_consent = ConsentRecord(
        user_id=1,
        purpose=DataProcessingPurpose.ANALYTICS,
        data_categories={DataCategory.BEHAVIORAL},
        status=ConsentStatus.GRANTED,
        granted_at=datetime.now(timezone.utc) - timedelta(days=10),
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )

    consent_repo.get_by_user_and_purpose.return_value = expired_consent

    result = service.check_consent(1, DataProcessingPurpose.ANALYTICS, DataCategory.BEHAVIORAL)

    assert result is False
    assert expired_consent.status == ConsentStatus.GRANTED


def test_can_process_data_defaults_to_disabled_settings_when_missing():
    """A missing privacy settings record should not be created during a read path."""
    settings_repo = MagicMock()
    activity_repo = MagicMock()
    consent_service = MagicMock()
    consent_service.check_consent.return_value = True

    service = PrivacyService(settings_repo, activity_repo, consent_service)

    settings_repo.get_by_user_id.return_value = None

    result = service.can_process_data(
        user_id=2,
        purpose=DataProcessingPurpose.ANALYTICS,
        data_category=DataCategory.BEHAVIORAL,
    )

    assert result is False
    settings_repo.get_by_user_id.assert_called_once_with(2)
    settings_repo.create.assert_not_called()


def test_can_process_data_core_functionality_allows_when_consent_present():
    """Core functionality should remain accessible when consent is granted even without settings."""
    settings_repo = MagicMock()
    activity_repo = MagicMock()
    consent_service = MagicMock()
    consent_service.check_consent.return_value = True

    service = PrivacyService(settings_repo, activity_repo, consent_service)

    settings_repo.get_by_user_id.return_value = None

    result = service.can_process_data(
        user_id=3,
        purpose=DataProcessingPurpose.CORE_FUNCTIONALITY,
        data_category=DataCategory.BASIC_PROFILE,
    )

    assert result is True
    settings_repo.get_by_user_id.assert_called_once_with(3)

