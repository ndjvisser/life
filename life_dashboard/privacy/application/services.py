"""
Privacy application services - use case orchestration for privacy and consent management.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from ..domain.entities import (
    ConsentRecord,
    ConsentStatus,
    DataCategory,
    DataProcessingActivity,
    DataProcessingPurpose,
    DataSubjectRequest,
    PrivacySettings,
)
from ..domain.repositories import (
    ConsentRepository,
    DataSubjectRequestRepository,
    PrivacySettingsRepository,
    ProcessingActivityRepository,
)


class ConsentService:
    """Service for managing user consent."""

    def __init__(
        self,
        consent_repo: ConsentRepository,
        activity_repo: ProcessingActivityRepository,
    ):
        self.consent_repo = consent_repo
        self.activity_repo = activity_repo

    def grant_consent(
        self,
        user_id: int,
        purpose: DataProcessingPurpose,
        data_categories: Set[DataCategory],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ConsentRecord:
        """Grant consent for a specific purpose and data categories."""
        # Check if consent already exists
        existing_consent = self.consent_repo.get_by_user_and_purpose(user_id, purpose)

        if existing_consent:
            # Update existing consent
            existing_consent.data_categories = data_categories
            existing_consent.grant_consent(ip_address, user_agent)
            consent = self.consent_repo.save(existing_consent)
        else:
            # Create new consent
            consent = ConsentRecord(
                user_id=user_id,
                purpose=purpose,
                data_categories=data_categories,
                status=ConsentStatus.GRANTED,
            )
            consent.grant_consent(ip_address, user_agent)
            consent = self.consent_repo.create(consent)

        # Log the consent activity
        activity = DataProcessingActivity(
            user_id=user_id,
            purpose=purpose,
            data_categories=data_categories,
            processing_type="consent_granted",
            context="privacy_service",
            legal_basis="consent",
            consent_id=consent.consent_id,
        )
        self.activity_repo.log_activity(activity)

        return consent

    def withdraw_consent(
        self, user_id: int, purpose: DataProcessingPurpose
    ) -> Optional[ConsentRecord]:
        """Withdraw consent for a specific purpose."""
        consent = self.consent_repo.get_by_user_and_purpose(user_id, purpose)

        if not consent:
            return None

        consent.withdraw_consent()
        updated_consent = self.consent_repo.save(consent)

        # Log the withdrawal
        activity = DataProcessingActivity(
            user_id=user_id,
            purpose=purpose,
            data_categories=consent.data_categories,
            processing_type="consent_withdrawn",
            context="privacy_service",
            legal_basis="consent",
            consent_id=consent.consent_id,
        )
        self.activity_repo.log_activity(activity)

        return updated_consent

    def check_consent(
        self, user_id: int, purpose: DataProcessingPurpose, data_category: DataCategory
    ) -> bool:
        """Check if user has valid consent for purpose and data category."""
        consent = self.consent_repo.get_by_user_and_purpose(user_id, purpose)

        if not consent:
            return False

        return consent.is_valid() and consent.covers_data_category(data_category)

    def get_user_consents(self, user_id: int) -> List[ConsentRecord]:
        """Get all consent records for a user."""
        return self.consent_repo.get_all_for_user(user_id)

    def refresh_expired_consents(self) -> int:
        """Mark expired consents and return count."""
        expired_consents = self.consent_repo.get_expired_consents()
        count = 0

        for consent in expired_consents:
            if consent.is_expired():
                consent.status = ConsentStatus.EXPIRED
                self.consent_repo.save(consent)
                count += 1

        return count


class PrivacyService:
    """Service for managing privacy settings and compliance."""

    def __init__(
        self,
        settings_repo: PrivacySettingsRepository,
        activity_repo: ProcessingActivityRepository,
        consent_service: ConsentService,
    ):
        self.settings_repo = settings_repo
        self.activity_repo = activity_repo
        self.consent_service = consent_service

    def get_or_create_privacy_settings(self, user_id: int) -> PrivacySettings:
        """Get existing privacy settings or create defaults."""
        settings = self.settings_repo.get_by_user_id(user_id)

        if not settings:
            settings = PrivacySettings(
                user_id=user_id,
                # Default to privacy-friendly settings
                analytics_enabled=False,
                ai_insights_enabled=False,
                social_features_enabled=False,
                marketing_enabled=False,
            )
            settings = self.settings_repo.create(settings)

        return settings

    def update_privacy_setting(
        self, user_id: int, setting_name: str, value: Any
    ) -> PrivacySettings:
        """Update a specific privacy setting."""
        settings = self.get_or_create_privacy_settings(user_id)
        settings.update_setting(setting_name, value)

        updated_settings = self.settings_repo.save(settings)

        # Log the settings change
        activity = DataProcessingActivity(
            user_id=user_id,
            purpose=DataProcessingPurpose.CORE_FUNCTIONALITY,
            data_categories={DataCategory.BASIC_PROFILE},
            processing_type="settings_updated",
            context="privacy_service",
            legal_basis="legitimate_interest",
        )
        self.activity_repo.log_activity(activity)

        return updated_settings

    def can_process_data(
        self, user_id: int, purpose: DataProcessingPurpose, data_category: DataCategory
    ) -> bool:
        """Check if data can be processed based on consent and settings."""
        # Check consent first
        has_consent = self.consent_service.check_consent(
            user_id, purpose, data_category
        )

        if not has_consent:
            return False

        # Check privacy settings
        settings = self.get_or_create_privacy_settings(user_id)

        # Map purposes to settings
        purpose_settings_map = {
            DataProcessingPurpose.ANALYTICS: settings.analytics_enabled,
            DataProcessingPurpose.AI_INSIGHTS: settings.ai_insights_enabled,
            DataProcessingPurpose.SOCIAL_FEATURES: settings.social_features_enabled,
            DataProcessingPurpose.MARKETING: settings.marketing_enabled,
        }

        # Core functionality is always allowed with consent
        if purpose == DataProcessingPurpose.CORE_FUNCTIONALITY:
            return True

        return purpose_settings_map.get(purpose, False)

    def log_data_access(
        self,
        user_id: int,
        purpose: DataProcessingPurpose,
        data_categories: Set[DataCategory],
        processing_type: str,
        context: str,
        request_id: Optional[str] = None,
    ) -> DataProcessingActivity:
        """Log data processing activity."""
        activity = DataProcessingActivity(
            user_id=user_id,
            purpose=purpose,
            data_categories=data_categories,
            processing_type=processing_type,
            context=context,
            request_id=request_id,
            legal_basis="consent",
        )

        return self.activity_repo.log_activity(activity)

    def get_user_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get summary of user's data processing activities."""
        return self.activity_repo.get_activity_summary(user_id, days)


class DataSubjectService:
    """Service for handling data subject requests (GDPR compliance)."""

    def __init__(
        self,
        request_repo: DataSubjectRequestRepository,
        settings_repo: PrivacySettingsRepository,
        consent_repo: ConsentRepository,
        activity_repo: ProcessingActivityRepository,
    ):
        self.request_repo = request_repo
        self.settings_repo = settings_repo
        self.consent_repo = consent_repo
        self.activity_repo = activity_repo

    def create_data_export_request(
        self, user_id: int, data_categories: Optional[Set[DataCategory]] = None
    ) -> DataSubjectRequest:
        """Create a data export request."""
        if not data_categories:
            data_categories = set(DataCategory)  # All categories by default

        request = DataSubjectRequest(
            user_id=user_id, request_type="export", data_categories=data_categories
        )

        return self.request_repo.create(request)

    def create_data_deletion_request(self, user_id: int) -> DataSubjectRequest:
        """Create a data deletion request."""
        request = DataSubjectRequest(
            user_id=user_id,
            request_type="delete",
            data_categories=set(DataCategory),  # All categories
        )

        return self.request_repo.create(request)

    def process_export_request(
        self, request_id: str, processor_id: int
    ) -> Dict[str, Any]:
        """Process a data export request."""
        request = self.request_repo.get_by_id(request_id)

        if not request:
            raise ValueError(f"Request {request_id} not found")

        request.start_processing(processor_id)
        self.request_repo.save(request)

        # Collect user data
        user_data = self._collect_user_data(request.user_id, request.data_categories)

        request.complete_request("Data export completed")
        self.request_repo.save(request)

        return user_data

    def process_deletion_request(self, request_id: str, processor_id: int) -> bool:
        """Process a data deletion request."""
        request = self.request_repo.get_by_id(request_id)

        if not request:
            raise ValueError(f"Request {request_id} not found")

        request.start_processing(processor_id)
        self.request_repo.save(request)

        # Delete user data
        deleted_count = self._delete_user_data(request.user_id)

        request.complete_request(f"Deleted {deleted_count} records")
        self.request_repo.save(request)

        return True

    def _collect_user_data(
        self, user_id: int, data_categories: Set[DataCategory]
    ) -> Dict[str, Any]:
        """Collect all user data for export."""
        export_data = {
            "user_id": user_id,
            "export_timestamp": datetime.utcnow().isoformat(),
            "data_categories": [cat.value for cat in data_categories],
            "data": {},
        }

        # Get privacy settings
        if DataCategory.BASIC_PROFILE in data_categories:
            settings = self.settings_repo.get_by_user_id(user_id)
            if settings:
                export_data["data"]["privacy_settings"] = settings.to_dict()

        # Get consent records
        consents = self.consent_repo.get_all_for_user(user_id)
        export_data["data"]["consent_records"] = [c.to_dict() for c in consents]

        # Get processing activities
        activities = self.activity_repo.get_activities_for_user(user_id, limit=1000)
        export_data["data"]["processing_activities"] = [a.to_dict() for a in activities]

        return export_data

    def _delete_user_data(self, user_id: int) -> int:
        """Delete all user data."""
        deleted_count = 0

        # Delete privacy settings
        if self.settings_repo.delete_by_user(user_id):
            deleted_count += 1

        # Delete consent records
        deleted_count += self.consent_repo.delete_by_user(user_id)

        # Delete processing activities
        deleted_count += self.activity_repo.delete_activities_for_user(user_id)

        return deleted_count

    def get_pending_requests(self) -> List[DataSubjectRequest]:
        """Get all pending data subject requests."""
        return self.request_repo.get_pending_requests()

    def get_overdue_requests(self, days_limit: int = 30) -> List[DataSubjectRequest]:
        """Get overdue data subject requests."""
        return self.request_repo.get_overdue_requests(days_limit)
