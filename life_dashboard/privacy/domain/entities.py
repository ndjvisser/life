"""
Privacy domain entities - pure Python privacy and consent management logic.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Set
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
    data_categories: Set[DataCategory] = field(default_factory=set)
    status: ConsentStatus = ConsentStatus.PENDING
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    version: str = "1.0"

    # Metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    consent_method: str = "web_form"  # web_form, api, import, etc.

    def __post_init__(self):
        """Validate consent record on creation."""
        if self.status == ConsentStatus.GRANTED and not self.granted_at:
            self.granted_at = datetime.utcnow()

        if self.status == ConsentStatus.WITHDRAWN and not self.withdrawn_at:
            self.withdrawn_at = datetime.utcnow()

    def grant_consent(
        self, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> None:
        """Grant consent for this purpose and data categories."""
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
        """Withdraw consent for this purpose."""
        if self.status == ConsentStatus.GRANTED:
            self.status = ConsentStatus.WITHDRAWN
            self.withdrawn_at = datetime.utcnow()

    def is_valid(self) -> bool:
        """Check if consent is currently valid."""
        if self.status != ConsentStatus.GRANTED:
            return False

        if self.expires_at and datetime.utcnow() > self.expires_at:
            self.status = ConsentStatus.EXPIRED
            return False

        return True

    def is_expired(self) -> bool:
        """Check if consent has expired."""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False

    def covers_data_category(self, category: DataCategory) -> bool:
        """Check if this consent covers a specific data category."""
        return category in self.data_categories

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
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
    data_categories: Set[DataCategory] = field(default_factory=set)
    processing_type: str = "read"  # read, write, update, delete, analyze, share
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Context information
    context: str = ""  # Which part of the system
    request_id: Optional[str] = None
    session_id: Optional[str] = None

    # Legal basis
    legal_basis: str = "consent"  # consent, legitimate_interest, contract, etc.
    consent_id: Optional[str] = None

    def __post_init__(self):
        """Validate processing activity on creation."""
        if not self.context:
            raise ValueError("Processing context is required")

    def to_dict(self) -> Dict:
        """Convert to dictionary for audit logging."""
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
    retention_preferences: Dict[DataCategory, RetentionPeriod] = field(
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
        """Update a privacy setting."""
        if hasattr(self, setting_name):
            setattr(self, setting_name, value)
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError(f"Unknown privacy setting: {setting_name}")

    def get_retention_period(self, data_category: DataCategory) -> RetentionPeriod:
        """Get retention period for a data category."""
        return self.retention_preferences.get(data_category, RetentionPeriod.YEAR_1)

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a privacy-sensitive feature is enabled."""
        feature_map = {
            "analytics": self.analytics_enabled,
            "ai_insights": self.ai_insights_enabled,
            "social_features": self.social_features_enabled,
            "marketing": self.marketing_enabled,
        }
        return feature_map.get(feature, False)

    def get_sharing_level(self, content_type: str) -> str:
        """Get sharing level for content type."""
        sharing_map = {
            "achievements": self.achievement_sharing,
            "progress": self.progress_sharing,
            "profile": self.profile_visibility,
        }
        return sharing_map.get(content_type, "private")

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
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
    completed_at: Optional[datetime] = None
    data_categories: Set[DataCategory] = field(default_factory=set)

    # Processing information
    processor_id: Optional[int] = None
    processing_notes: str = ""
    rejection_reason: Optional[str] = None

    # Verification
    identity_verified: bool = False
    verification_method: Optional[str] = None

    def verify_identity(self, method: str) -> None:
        """Mark identity as verified."""
        self.identity_verified = True
        self.verification_method = method

    def start_processing(self, processor_id: int) -> None:
        """Start processing the request."""
        if not self.identity_verified:
            raise ValueError("Identity must be verified before processing")

        self.status = "processing"
        self.processor_id = processor_id

    def complete_request(self, notes: str = "") -> None:
        """Mark request as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.processing_notes = notes

    def reject_request(self, reason: str) -> None:
        """Reject the request with reason."""
        self.status = "rejected"
        self.rejection_reason = reason
        self.completed_at = datetime.utcnow()

    def is_overdue(self, days_limit: int = 30) -> bool:
        """Check if request is overdue (GDPR: 30 days)."""
        if self.status in ["completed", "rejected"]:
            return False

        deadline = self.requested_at + timedelta(days=days_limit)
        return datetime.utcnow() > deadline

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
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
