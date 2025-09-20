"""
Privacy domain repository interfaces - abstract data access contracts.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from .entities import (
    ConsentRecord,
    DataProcessingActivity,
    DataProcessingPurpose,
    DataSubjectRequest,
    PrivacySettings,
)


class ConsentRepository(ABC):
    """Abstract repository for consent management."""

    @abstractmethod
    def get_by_user_and_purpose(
        self, user_id: int, purpose: DataProcessingPurpose
    ) -> Optional[ConsentRecord]:
        """Get consent record for user and purpose."""
        pass

    @abstractmethod
    def get_all_for_user(self, user_id: int) -> List[ConsentRecord]:
        """Get all consent records for a user."""
        pass

    @abstractmethod
    def save(self, consent: ConsentRecord) -> ConsentRecord:
        """Save consent record."""
        pass

    @abstractmethod
    def create(self, consent: ConsentRecord) -> ConsentRecord:
        """Create new consent record."""
        pass

    @abstractmethod
    def get_expired_consents(self) -> List[ConsentRecord]:
        """Get all expired consent records."""
        pass

    @abstractmethod
    def delete_by_user(self, user_id: int) -> int:
        """Delete all consent records for a user."""
        pass


class ProcessingActivityRepository(ABC):
    """Abstract repository for data processing activity logging."""

    @abstractmethod
    def log_activity(self, activity: DataProcessingActivity) -> DataProcessingActivity:
        """Log a data processing activity."""
        pass

    @abstractmethod
    def get_activities_for_user(
        self, user_id: int, limit: int = 100
    ) -> List[DataProcessingActivity]:
        """Get processing activities for a user."""
        pass

    @abstractmethod
    def get_activities_by_purpose(
        self, purpose: DataProcessingPurpose, start_date: datetime, end_date: datetime
    ) -> List[DataProcessingActivity]:
        """Get activities by purpose within date range."""
        pass

    @abstractmethod
    def get_activities_by_context(
        self, context: str, start_date: datetime, end_date: datetime
    ) -> List[DataProcessingActivity]:
        """Get activities by context within date range."""
        pass

    @abstractmethod
    def delete_activities_for_user(self, user_id: int) -> int:
        """Delete all processing activities for a user."""
        pass

    @abstractmethod
    def get_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get summary of processing activities for a user."""
        pass


class PrivacySettingsRepository(ABC):
    """Abstract repository for privacy settings."""

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[PrivacySettings]:
        """Get privacy settings for a user."""
        pass

    @abstractmethod
    def save(self, settings: PrivacySettings) -> PrivacySettings:
        """Save privacy settings."""
        pass

    @abstractmethod
    def create(self, settings: PrivacySettings) -> PrivacySettings:
        """Create new privacy settings."""
        pass

    @abstractmethod
    def delete_by_user(self, user_id: int) -> bool:
        """Delete privacy settings for a user."""
        pass


class DataSubjectRequestRepository(ABC):
    """Abstract repository for data subject requests."""

    @abstractmethod
    def create(self, request: DataSubjectRequest) -> DataSubjectRequest:
        """Create new data subject request."""
        pass

    @abstractmethod
    def get_by_id(self, request_id: str) -> Optional[DataSubjectRequest]:
        """Get request by ID."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[DataSubjectRequest]:
        """Get all requests for a user."""
        pass

    @abstractmethod
    def save(self, request: DataSubjectRequest) -> DataSubjectRequest:
        """Save request updates."""
        pass

    @abstractmethod
    def get_pending_requests(self) -> List[DataSubjectRequest]:
        """Get all pending requests."""
        pass

    @abstractmethod
    def get_overdue_requests(self, days_limit: int = 30) -> List[DataSubjectRequest]:
        """Get overdue requests."""
        pass

    @abstractmethod
    def delete_completed_requests(self, older_than_days: int = 90) -> int:
        """Delete old completed requests."""
        pass
