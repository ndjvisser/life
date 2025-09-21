"""
Privacy application services - use case orchestration for privacy and consent management.
"""

from datetime import datetime, timezone
from typing import Any

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
        """
        Initialize the ConsentService with repository dependencies.

        Stores the consent and processing activity repositories for use by service methods that manage consents and log related activities.
        """
        self.consent_repo = consent_repo
        self.activity_repo = activity_repo

    def grant_consent(
        self,
        user_id: int,
        purpose: DataProcessingPurpose,
        data_categories: set[DataCategory],
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ConsentRecord:
        """
        Grant consent for a user for a given processing purpose and set of data categories.

        If an existing consent for (user_id, purpose) exists, its data categories are replaced and the consent is marked/granted; otherwise a new consent record is created and marked granted. A DataProcessingActivity with legal basis "consent" is logged for the action.

        Parameters:
            user_id: The identifier of the user granting consent.
            purpose: The data processing purpose for which consent is granted.
            data_categories: The set of data categories covered by the consent.
            ip_address: Optional IP address associated with the grant event.
            user_agent: Optional user agent string associated with the grant event.

        Returns:
            The persisted ConsentRecord after creation or update.
        """
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
    ) -> ConsentRecord | None:
        """
        Withdraw a user's consent for the given processing purpose.

        If a consent record for the user and purpose exists, marks it withdrawn, persists the change, and logs a corresponding DataProcessingActivity. Returns the updated ConsentRecord, or None if no matching consent was found.
        """
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
        """
        Return True if the user has an existing, currently valid consent for the given purpose that covers the specified data category.

        Checks the repository for a consent record for (user_id, purpose); returns False if none exists. If a record is found, returns True only when the record is both valid and explicitly covers the provided data_category.
        """
        consent = self.consent_repo.get_by_user_and_purpose(user_id, purpose)

        if not consent:
            return False

        return consent.is_valid_readonly() and consent.covers_data_category(
            data_category
        )

    def get_user_consents(self, user_id: int) -> list[ConsentRecord]:
        """Get all consent records for a user."""
        return self.consent_repo.get_all_for_user(user_id)

    def refresh_expired_consents(self) -> int:
        """
        Mark consents that have reached their expiry as EXPIRED and persist the changes.

        Retrieves candidates from the consent repository, sets each consent's status to ConsentStatus.EXPIRED only if its `is_expired()` check returns True, saves the updated record, and returns the number of consents updated.
        """
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
        """
        Create a PrivacyService and store repository and service dependencies.

        Initializes the service with a privacy settings repository, a processing activity repository, and a ConsentService which the service uses to evaluate consents and log processing activities.
        """
        self.settings_repo = settings_repo
        self.activity_repo = activity_repo
        self.consent_service = consent_service

    def get_or_create_privacy_settings(self, user_id: int) -> PrivacySettings:
        """
        Return the PrivacySettings for a user, creating and persisting a default (all features disabled) settings record if none exists.

        Defaults created:
        - analytics_enabled=False
        - ai_insights_enabled=False
        - social_features_enabled=False
        - marketing_enabled=False

        Returns:
            PrivacySettings: The existing or newly created privacy settings for the user.
        """
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
        """
        Update a single privacy setting for a user.

        Ensures the user's PrivacySettings exist (creating defaults if needed), updates the named setting to the provided value, persists the change, and logs a DataProcessingActivity recording the settings update. Returns the saved PrivacySettings instance.
        """
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
        """
        Return True if the given data category may be processed for the user and purpose.

        First requires an active, applicable consent for (user_id, purpose, data_category).
        If consent is present, privacy settings are consulted: for CORE_FUNCTIONALITY the method
        returns True when consent exists; for other purposes the corresponding settings flag
        (e.g., analytics_enabled, marketing_enabled) must be enabled.

        Parameters:
            user_id: ID of the user whose consent and settings are checked.
            purpose: Processing purpose being evaluated.
            data_category: Specific data category being requested for processing.

        Returns:
            bool: True when processing is allowed (consent + settings rules), False otherwise.
        """
        # Check consent first
        has_consent = self.consent_service.check_consent(
            user_id, purpose, data_category
        )

        if not has_consent:
            return False

        # Check privacy settings without mutating state
        settings = self.settings_repo.get_by_user_id(user_id)

        # Map purposes to settings, defaulting to disabled when settings are absent
        purpose_settings_map = {
            DataProcessingPurpose.ANALYTICS: settings.analytics_enabled
            if settings
            else False,
            DataProcessingPurpose.AI_INSIGHTS: settings.ai_insights_enabled
            if settings
            else False,
            DataProcessingPurpose.SOCIAL_FEATURES: settings.social_features_enabled
            if settings
            else False,
            DataProcessingPurpose.MARKETING: settings.marketing_enabled
            if settings
            else False,
        }

        # Core functionality is always allowed with consent
        if purpose == DataProcessingPurpose.CORE_FUNCTIONALITY:
            return True

        return purpose_settings_map.get(purpose, False)

    def log_data_access(
        self,
        user_id: int,
        purpose: DataProcessingPurpose,
        data_categories: set[DataCategory],
        processing_type: str,
        context: str,
        request_id: str | None = None,
    ) -> DataProcessingActivity:
        """
        Create and record a DataProcessingActivity for the given user and return the persisted activity.

        The activity is created with the provided purpose, data categories, processing type, and context, is recorded with a legal basis of `"consent"`, and is persisted via the activity repository.

        Parameters:
            user_id (int): ID of the user the activity concerns.
            purpose (DataProcessingPurpose): Purpose of the processing.
            data_categories (Set[DataCategory]): Categories of data involved.
            processing_type (str): High-level type of processing performed (e.g., "read", "export", "modify").
            context (str): Freeform context or reason for the processing (e.g., endpoint or operation name).
            request_id (Optional[str]): Optional external request or correlation identifier.

        Returns:
            DataProcessingActivity: The activity record returned by the repository after logging.
        """
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

    def get_user_activity_summary(self, user_id: int, days: int = 30) -> dict[str, Any]:
        """
        Return a summary of the user's data processing activities for the past `days` days.

        The summary is returned as a dictionary containing aggregated activity information (suitable for reporting or UI display). `days` defaults to 30.
        """
        return self.activity_repo.get_activity_summary(user_id, days)


class DataSubjectService:
    """Service for handling data subject requests (GDPR compliance)."""

    def __init__(
        self,
        request_repo: DataSubjectRequestRepository,
        settings_repo: PrivacySettingsRepository,
        consent_repo: ConsentRepository,
        activity_repo: ProcessingActivityRepository,
        delete_activity_logs_on_deletion: bool = False,
    ):
        """
        Initialize the DataSubjectService.

        Stores repository dependencies used to create and process data subject requests,
        manage privacy settings and consents, and log processing activities. A policy
        toggle controls whether processing activity logs are removed when fulfilling
        deletion requests.
        """
        self.request_repo = request_repo
        self.settings_repo = settings_repo
        self.consent_repo = consent_repo
        self.activity_repo = activity_repo
        self.delete_activity_logs_on_deletion = delete_activity_logs_on_deletion

    def create_data_export_request(
        self, user_id: int, data_categories: set[DataCategory] | None = None
    ) -> DataSubjectRequest:
        """
        Create and persist a data export request for a user.

        If `data_categories` is omitted or empty, the request will include all defined DataCategory values.
        Returns the created DataSubjectRequest as persisted by the request repository.

        Parameters:
            user_id: The ID of the user requesting their data export.
            data_categories: Optional set of DataCategory values to include in the export; when None, all categories are included.

        Returns:
            The persisted DataSubjectRequest instance.
        """
        if not data_categories:
            data_categories = set(DataCategory)  # All categories by default

        request = DataSubjectRequest(
            user_id=user_id, request_type="export", data_categories=data_categories
        )

        return self.request_repo.create(request)

    def create_data_deletion_request(self, user_id: int) -> DataSubjectRequest:
        """
        Create and persist a data deletion request for the given user that covers all data categories.

        The created DataSubjectRequest has type "delete" and its `data_categories` set contains every DataCategory. The request is saved via the request repository and the persisted object is returned.

        Returns:
            DataSubjectRequest: The persisted deletion request.
        """
        request = DataSubjectRequest(
            user_id=user_id,
            request_type="delete",
            data_categories=set(DataCategory),  # All categories
        )

        return self.request_repo.create(request)

    def process_export_request(
        self, request_id: str, processor_id: int, verification_method: str | None = None
    ) -> dict[str, Any]:
        """
        Process a data export data subject request: verify identity if needed, mark it as processing,
        collect the requested user data, mark the request completed, and persist state changes.

        Parameters:
            request_id (str): Identifier of the data subject request to process.
            processor_id (int): Internal ID of the actor or worker handling the request.
            verification_method (Optional[str]): Method used to verify identity (e.g., "email", "sms", "in_person").
                Required if identity is not already verified.

        Returns:
            Dict[str, Any]: Collected export data for the request.

        Raises:
            ValueError: If no request exists for the given request_id or if identity verification is required but not provided.
            RuntimeError: If identity verification fails.
        """
        request = self.request_repo.get_by_id(request_id)

        if not request:
            raise ValueError(f"Request {request_id} not found")

        if getattr(request, "request_type", None) != "export":
            raise ValueError(f"Request {request_id} is not an export request")

        if request.status in {"completed", "rejected"}:
            raise ValueError(
                f"Request {request_id} has already been resolved with status {request.status}"
            )

        if request.status == "processing":
            raise ValueError(
                f"Request {request_id} is already being processed and cannot be processed twice"
            )

        # Ensure identity is verified before processing
        if not request.identity_verified:
            if not verification_method:
                raise ValueError(
                    "Identity verification is required but no verification method was provided"
                )
            request.verify_identity(verification_method)
            self.request_repo.save(request)  # Persist verification status

        # Now that identity is verified, start processing
        request.start_processing(processor_id)
        self.request_repo.save(request)

        self.activity_repo.log_activity(
            DataProcessingActivity(
                user_id=request.user_id,
                purpose=DataProcessingPurpose.CORE_FUNCTIONALITY,
                data_categories=request.data_categories,
                processing_type="dsar_export_started",
                context="data_subject_service:export",
                request_id=request.request_id,
                legal_basis="legal_obligation",
            )
        )

        # Collect user data
        user_data = self._collect_user_data(request.user_id, request.data_categories)

        request.complete_request("Data export completed")
        self.request_repo.save(request)

        self.activity_repo.log_activity(
            DataProcessingActivity(
                user_id=request.user_id,
                purpose=DataProcessingPurpose.CORE_FUNCTIONALITY,
                data_categories=request.data_categories,
                processing_type="dsar_export_completed",
                context="data_subject_service:export",
                request_id=request.request_id,
                legal_basis="legal_obligation",
            )
        )

        return user_data

    def process_deletion_request(
        self, request_id: str, processor_id: int, verification_method: str | None = None
    ) -> bool:
        """
        Process a data deletion request: verify identity if needed, mark it as processing,
        delete the user's data, mark the request completed, and persist updates.

        Parameters:
            request_id (str): Identifier of the data subject request to process.
            processor_id (int): Identifier of the actor performing the processing.
            verification_method (Optional[str]): Method used to verify identity (e.g., "email", "sms", "in_person").
                Required if identity is not already verified.

        Returns:
            bool: True if the request was processed successfully.

        Raises:
            ValueError: If no request exists for the given request_id or if identity verification is required but not provided.
            RuntimeError: If identity verification fails.
        """
        request = self.request_repo.get_by_id(request_id)

        if not request:
            raise ValueError(f"Request {request_id} not found")

        if request.status in {"completed", "rejected"}:
            raise ValueError(
                f"Request {request_id} has already been resolved with status {request.status}"
            )

        if request.status == "processing":
            raise ValueError(
                f"Request {request_id} is already being processed and cannot be processed twice"
            )

        if getattr(request, "request_type", None) not in {"delete", "deletion"}:
            raise ValueError(f"Request {request_id} is not a deletion request")

        # Ensure identity is verified before processing
        if not request.identity_verified:
            if not verification_method:
                raise ValueError(
                    "Identity verification is required but no verification method was provided"
                )
            request.verify_identity(verification_method)
            self.request_repo.save(request)  # Persist verification status

        # Now that identity is verified, start processing
        request.start_processing(processor_id)
        self.request_repo.save(request)

        self.activity_repo.log_activity(
            DataProcessingActivity(
                user_id=request.user_id,
                purpose=DataProcessingPurpose.CORE_FUNCTIONALITY,
                data_categories=request.data_categories,
                processing_type="dsar_deletion_started",
                context="data_subject_service:deletion",
                request_id=request.request_id,
                legal_basis="legal_obligation",
            )
        )

        # Delete user data
        deleted_count = self._delete_user_data(
            request.user_id, delete_activities=self.delete_activity_logs_on_deletion
        )

        request.complete_request(f"Deleted {deleted_count} records")
        self.request_repo.save(request)

        self.activity_repo.log_activity(
            DataProcessingActivity(
                user_id=request.user_id,
                purpose=DataProcessingPurpose.CORE_FUNCTIONALITY,
                data_categories=request.data_categories,
                processing_type="dsar_deletion_completed",
                context="data_subject_service:deletion",
                request_id=request.request_id,
                legal_basis="legal_obligation",
            )
        )

        return True

    def _collect_user_data(
        self, user_id: int, data_categories: set[DataCategory]
    ) -> dict[str, Any]:
        """
        Assemble an export payload containing a user's requested data categories.

        If DataCategory.BASIC_PROFILE is requested and settings exist, includes the user's privacy settings. Always includes all consent records for the user and up to 1000 processing activity records.

        Parameters:
            user_id (int): ID of the user whose data is being collected.
            data_categories (Set[DataCategory]): Categories of data to include in the export.

        Returns:
            Dict[str, Any]: Export payload with the following top-level keys:
                - user_id: the requested user_id
                - export_timestamp: UTC ISO-formatted timestamp of the export
                - data_categories: list of requested data category names
                - data: dictionary containing any of:
                    - privacy_settings (optional): the user's privacy settings as a dict
                    - consent_records: list of consent record dicts
                    - processing_activities: list of processing activity dicts (max 1000)
        """
        export_data = {
            "user_id": user_id,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
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

    def _delete_user_data(
        self, user_id: int, *, delete_activities: bool = False
    ) -> int:
        """
        Delete stored privacy-related data for a user.

        Deletes the user's privacy settings and consent records, and optionally deletes processing
        activities when `delete_activities` is True. Returns the total number of records/items removed.

        Parameters:
            user_id (int): ID of the user whose data will be deleted.
            delete_activities (bool): When True, delete processing activities in addition to settings
                and consents. Defaults to False so audit trails are retained unless explicitly removed.

        Returns:
            int: Total count of deleted items across settings, consents, and activities.
        """
        deleted_count = 0

        # Delete privacy settings
        if self.settings_repo.delete_by_user(user_id):
            deleted_count += 1

        # Delete consent records
        deleted_count += self.consent_repo.delete_by_user(user_id)

        # Delete processing activities when explicitly requested
        if delete_activities:
            deleted_count += self.activity_repo.delete_activities_for_user(user_id)

        return deleted_count

    def get_pending_requests(self) -> list[DataSubjectRequest]:
        """Get all pending data subject requests."""
        return self.request_repo.get_pending_requests()

    def get_overdue_requests(self, days_limit: int = 30) -> list[DataSubjectRequest]:
        """
        Return data subject requests that are overdue.

        Parameters:
            days_limit (int): Maximum age in days; requests older than this are considered overdue (default 30).

        Returns:
            List[DataSubjectRequest]: All requests from the repository considered overdue.
        """
        return self.request_repo.get_overdue_requests(days_limit)
