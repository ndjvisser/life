"""
Privacy domain entities - pure Python privacy and consent management logic.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4


class ConsentStatus(Enum):
    """Status of user consent for data processing."""

    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"


class DataProcessingPurpose(Enum):
    """Purposes for which personal data can be processed."""

    CORE_FUNCTIONALITY = "core_functionality"  # Essential app features
    ANALYTICS = "analytics"  # Usage analytics and insights
    AI_INSIGHTS = "ai_insights"  # AI-powered recommendations
    SOCIAL_FEATURES = "social_features"  # Social sharing and community
    MARKETING = "marketing"  # Marketing communications
    RESEARCH = "research"  # Product research and improvement
    EXTERNAL_INTEGRATIONS = "external_integrations"  # Third-party data sync


class DataCategory(Enum):
    """Categories of personal data."""

    BASIC_PROFILE = "basic_profile"  # Name, email, basic info
    BEHAVIORAL = "behavioral"  # Usage patterns, interactions
    HEALTH = "health"  # Health metrics and data
    FINANCIAL = "financial"  # Financial data and metrics
    SOCIAL = "social"  # Social interactions and relationships
    LOCATION = "location"  # Location data
    BIOMETRIC = "biometric"  # Biometric identifiers
    SENSITIVE = "sensitive"  # Special category data


class RetentionPeriod(Enum):
    """Data retention periods."""

    SESSION = "session"  # Until session ends
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    MONTHS_6 = "6_months"
    YEAR_1 = "1_year"
    YEARS_2 = "2_years"
    YEARS_5 = "5_years"
    INDEFINITE = "indefinite"  # Until user deletion


@dataclass
class ConsentRecord:
    """Domain entity for tracking user consent."""

    consent_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    purpose: DataProcessingPurpose = DataProcessingPurpose.CORE_FUNCTIONALITY
    data_categories: set[DataCategory] = field(default_factory=set)
    status: ConsentStatus = ConsentStatus.PENDING
    granted_at: datetime | None = None
    withdrawn_at: datetime | None = None
    expires_at: datetime | None = None
    version: str = "1.0"

    # Metadata
    ip_address: str | None = None
    user_agent: str | None = None
    consent_method: str = "web_form"  # web_form, api, import, etc.

    def __post_init__(self):
        """
        Ensure timestamps match initial consent status.

        If the record is initialized with status GRANTED and no `granted_at` is provided, set `granted_at` to the current UTC time. If initialized with status WITHDRAWN and no `withdrawn_at` is provided, set `withdrawn_at` to the current UTC time.
        """
        if self.status == ConsentStatus.GRANTED and not self.granted_at:
            self.granted_at = datetime.utcnow()

        if self.status == ConsentStatus.WITHDRAWN and not self.withdrawn_at:
            self.withdrawn_at = datetime.utcnow()

    def grant_consent(
        self, ip_address: str | None = None, user_agent: str | None = None
    ) -> None:
        """
        Mark this consent record as granted and record audit metadata.

        Updates:
        - Sets status to ConsentStatus.GRANTED.
        - Sets granted_at to current UTC time and clears withdrawn_at.
        - Optionally records ip_address and user_agent for audit purposes.
        - For MARKETING and RESEARCH purposes, sets expires_at to one year from now.

        Parameters:
            ip_address (Optional[str]): Source IP to record for the grant event (audit).
            user_agent (Optional[str]): User agent string to record for the grant event (audit).
        """
        self.status = ConsentStatus.GRANTED
        self.granted_at = datetime.utcnow()
        self.withdrawn_at = None

        if ip_address:
            self.ip_address = ip_address
        if user_agent:
            self.user_agent = user_agent

        # Set expiration based on purpose (some consents expire)
        if self.purpose in [
            DataProcessingPurpose.MARKETING,
            DataProcessingPurpose.RESEARCH,
        ]:
            self.expires_at = datetime.utcnow() + timedelta(days=365)  # 1 year

    def withdraw_consent(self) -> None:
        """
        Withdraw previously granted consent.

        If the current status is ConsentStatus.GRANTED, sets status to ConsentStatus.WITHDRAWN
        and records the withdrawal time (UTC) in `withdrawn_at`. No action is taken if the
        consent is not currently granted.
        """
        if self.status == ConsentStatus.GRANTED:
            self.status = ConsentStatus.WITHDRAWN
            self.withdrawn_at = datetime.utcnow()

    def is_valid(self) -> bool:
        """
        Return True if the consent is currently valid (GRANTED and not expired), otherwise False.

        If the consent status is not GRANTED this returns False. If an expiration time exists and is past
        the current UTC time, the method updates the record's status to ConsentStatus.EXPIRED and returns False.
        """
        if self.status != ConsentStatus.GRANTED:
            return False

        if self.expires_at and datetime.utcnow() > self.expires_at:
            self.status = ConsentStatus.EXPIRED
            return False

        return True

    def is_expired(self) -> bool:
        """
        Return True if the consent has a configured expiration time that is in the past.

        Detailed:
        - Returns True only when `expires_at` is set and the current UTC time is later than `expires_at`.
        - Does not modify the consent's status or other fields; it only performs a read check.
        """
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False

    def covers_data_category(self, category: DataCategory) -> bool:
        """
        Return True if this consent record includes the given DataCategory.

        Parameters:
            category (DataCategory): The data category to check.

        Returns:
            bool: True if `category` is present in this consent's `data_categories`, otherwise False.
        """
        return category in self.data_categories

    def to_dict(self) -> dict:
        """
        Return a JSON-serializable dictionary representation of this ConsentRecord.

        The dictionary includes identifier fields, enum values (purpose and status) and a list of data category values, ISO-8601 strings for any timestamps (or None), the stored version, and computed flags `is_valid` and `is_expired`. Intended for logging, audit trails, or API responses.

        Returns:
            Dict: A mapping with keys:
                - consent_id (str)
                - user_id (int)
                - purpose (str)
                - data_categories (List[str])
                - status (str)
                - granted_at (str|None) ISO-8601 or None
                - withdrawn_at (str|None) ISO-8601 or None
                - expires_at (str|None) ISO-8601 or None
                - version (str)
                - is_valid (bool)
                - is_expired (bool)
        """
        return {
            "consent_id": self.consent_id,
            "user_id": self.user_id,
            "purpose": self.purpose.value,
            "data_categories": [cat.value for cat in self.data_categories],
            "status": self.status.value,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "withdrawn_at": self.withdrawn_at.isoformat()
            if self.withdrawn_at
            else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "version": self.version,
            "is_valid": self.is_valid(),
            "is_expired": self.is_expired(),
        }


@dataclass
class DataProcessingActivity:
    """Domain entity for tracking data processing activities."""

    activity_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    purpose: DataProcessingPurpose = DataProcessingPurpose.CORE_FUNCTIONALITY
    data_categories: set[DataCategory] = field(default_factory=set)
    processing_type: str = "read"  # read, write, update, delete, analyze, share
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Context information
    context: str = ""  # Which part of the system
    request_id: str | None = None
    session_id: str | None = None

    # Legal basis
    legal_basis: str = "consent"  # consent, legitimate_interest, contract, etc.
    consent_id: str | None = None

    def __post_init__(self):
        """
        Ensure the activity has a non-empty processing context after initialization.

        Raises:
            ValueError: If the required `context` attribute is empty or falsy.
        """
        if not self.context:
            raise ValueError("Processing context is required")

    def to_dict(self) -> dict:
        """
        Return a serializable dictionary representation of the activity for audit logging.

        Enum fields are converted to their `.value` and the timestamp is ISO-formatted. The resulting dict contains:
        `activity_id`, `user_id`, `purpose`, `data_categories`, `processing_type`, `timestamp`, `context`,
        `request_id`, `session_id`, `legal_basis`, and `consent_id`.

        Returns:
            Dict: Mapping suitable for logging or JSON encoding.
        """
        return {
            "activity_id": self.activity_id,
            "user_id": self.user_id,
            "purpose": self.purpose.value,
            "data_categories": [cat.value for cat in self.data_categories],
            "processing_type": self.processing_type,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "legal_basis": self.legal_basis,
            "consent_id": self.consent_id,
        }


@dataclass
class PrivacySettings:
    """Domain entity for user privacy preferences."""

    user_id: int = 0

    # Data retention preferences
    retention_preferences: dict[DataCategory, RetentionPeriod] = field(
        default_factory=dict
    )

    # Feature-specific privacy settings
    analytics_enabled: bool = True
    ai_insights_enabled: bool = True
    social_features_enabled: bool = False
    marketing_enabled: bool = False

    # Sharing preferences
    achievement_sharing: str = "private"  # private, friends, public
    progress_sharing: str = "private"
    profile_visibility: str = "private"

    # Data export preferences
    export_format: str = "json"  # json, csv, xml
    include_derived_data: bool = True

    # Notification preferences
    privacy_notifications: bool = True
    consent_reminders: bool = True
    data_breach_notifications: bool = True

    # Advanced settings
    differential_privacy: bool = True
    data_minimization: bool = True
    pseudonymization: bool = True

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def update_setting(self, setting_name: str, value) -> None:
        """
        Update a named privacy setting on this PrivacySettings instance and refresh the updated_at timestamp.

        Parameters:
            setting_name (str): Attribute name of the setting to update; must match an existing attribute on the instance.
            value: New value to assign to the setting.

        Raises:
            ValueError: If the given setting_name does not correspond to an existing attribute.
        """
        if hasattr(self, setting_name):
            setattr(self, setting_name, value)
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError(f"Unknown privacy setting: {setting_name}")

    def get_retention_period(self, data_category: DataCategory) -> RetentionPeriod:
        """
        Return the configured retention period for the given data category.

        If no explicit preference exists for the category, returns RetentionPeriod.YEAR_1 (1 year) as the default.
        """
        return self.retention_preferences.get(data_category, RetentionPeriod.YEAR_1)

    def is_feature_enabled(self, feature: str) -> bool:
        """
        Return whether a named privacy-related feature is enabled for this user.

        Accepts feature keys: "analytics", "ai_insights", "social_features", and "marketing".
        Lookup is exact (case-sensitive); unknown keys return False.
        """
        feature_map = {
            "analytics": self.analytics_enabled,
            "ai_insights": self.ai_insights_enabled,
            "social_features": self.social_features_enabled,
            "marketing": self.marketing_enabled,
        }
        return feature_map.get(feature, False)

    def get_sharing_level(self, content_type: str) -> str:
        """
        Return the user's sharing level for a given content type.

        Parameters:
            content_type (str): Type of content to query. Recognized values are
                "achievements", "progress", and "profile". Unknown values return "private".

        Returns:
            str: Sharing level for the content (e.g., "public", "friends", "private"); defaults to "private" for unrecognized content types.
        """
        sharing_map = {
            "achievements": self.achievement_sharing,
            "progress": self.progress_sharing,
            "profile": self.profile_visibility,
        }
        return sharing_map.get(content_type, "private")

    def to_dict(self) -> dict:
        """
        Serialize PrivacySettings to a dictionary suitable for storage or JSON encoding.

        Returns:
            dict: A mapping of field names to serializable values. Enum keys and values in
            `retention_preferences` are converted to their `.value` strings; `created_at`
            and `updated_at` are returned as ISO-8601 formatted strings.
        """
        return {
            "user_id": self.user_id,
            "retention_preferences": {
                cat.value: period.value
                for cat, period in self.retention_preferences.items()
            },
            "analytics_enabled": self.analytics_enabled,
            "ai_insights_enabled": self.ai_insights_enabled,
            "social_features_enabled": self.social_features_enabled,
            "marketing_enabled": self.marketing_enabled,
            "achievement_sharing": self.achievement_sharing,
            "progress_sharing": self.progress_sharing,
            "profile_visibility": self.profile_visibility,
            "export_format": self.export_format,
            "include_derived_data": self.include_derived_data,
            "privacy_notifications": self.privacy_notifications,
            "consent_reminders": self.consent_reminders,
            "data_breach_notifications": self.data_breach_notifications,
            "differential_privacy": self.differential_privacy,
            "data_minimization": self.data_minimization,
            "pseudonymization": self.pseudonymization,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class DataSubjectRequest:
    """Domain entity for handling data subject requests (GDPR, etc.)."""

    request_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    request_type: str = "export"  # export, delete, rectify, restrict, object
    status: str = "pending"  # pending, processing, completed, rejected

    # Request details
    requested_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    data_categories: set[DataCategory] = field(default_factory=set)

    # Processing information
    processor_id: int | None = None
    processing_notes: str = ""
    rejection_reason: str | None = None

    # Verification
    identity_verified: bool = False
    verification_method: str | None = None

    def verify_identity(self, method: str) -> None:
        """
        Mark the request's identity as verified and record the verification method.

        Parameters:
            method (str): The verification method used (for example: "email", "sms", "in_person", "two_factor"); stored in `verification_method`.
        """
        self.identity_verified = True
        self.verification_method = method

    def start_processing(self, processor_id: int) -> None:
        """
        Mark the data subject request as being processed and record the responsible processor.

        Requires that identity verification has completed; otherwise raises ValueError.
        Sets the request's status to "processing" and assigns processor_id.

        Parameters:
            processor_id (int): Identifier of the processor handling this request.
        """
        if not self.identity_verified:
            raise ValueError("Identity must be verified before processing")

        self.status = "processing"
        self.processor_id = processor_id

    def complete_request(self, notes: str = "") -> None:
        """
        Mark this data subject request as completed.

        Sets the request status to "completed", records the completion timestamp (UTC) and stores optional processing notes.

        Parameters:
            notes (str): Optional notes or summary of actions taken during processing (defaults to empty string).

        Returns:
            None
        """
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.processing_notes = notes

    def reject_request(self, reason: str) -> None:
        """
        Mark the data subject request as rejected.

        Sets the request status to "rejected", records the provided rejection reason, and timestamps completion with the current UTC time.

        Parameters:
            reason (str): Human-readable explanation for rejecting the request.
        """
        self.status = "rejected"
        self.rejection_reason = reason
        self.completed_at = datetime.utcnow()

    def is_overdue(self, days_limit: int = 30) -> bool:
        """
        Return True if the data subject request is past its processing deadline.

        By default uses a 30-day statutory window; requests with status "completed" or "rejected" are never considered overdue.

        Parameters:
            days_limit (int): Number of days after `requested_at` that defines the deadline (default 30).

        Returns:
            bool: True if the current UTC time is later than `requested_at + days_limit`, otherwise False.
        """
        if self.status in ["completed", "rejected"]:
            return False

        deadline = self.requested_at + timedelta(days=days_limit)
        return datetime.utcnow() > deadline

    def to_dict(self) -> dict:
        """
        Return a serializable dictionary representation of the DataSubjectRequest.

        The dictionary contains all public fields with datetime values formatted as ISO 8601 strings, the set of data categories converted to their enum values, and a computed `is_overdue` boolean. `completed_at` is None when the request is not finished.

        Returns:
            Dict: Serialized mapping suitable for JSON encoding and audit/logging.
        """
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "request_type": self.request_type,
            "status": self.status,
            "requested_at": self.requested_at.isoformat(),
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "data_categories": [cat.value for cat in self.data_categories],
            "processor_id": self.processor_id,
            "processing_notes": self.processing_notes,
            "rejection_reason": self.rejection_reason,
            "identity_verified": self.identity_verified,
            "verification_method": self.verification_method,
            "is_overdue": self.is_overdue(),
        }
