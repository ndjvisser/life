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
        """
        Retrieve the consent record for a specific user and data-processing purpose.
        
        Returns the ConsentRecord matching the given user ID and DataProcessingPurpose, or None if no record exists. The function does not modify data.
        """
        pass

    @abstractmethod
    def get_all_for_user(self, user_id: int) -> List[ConsentRecord]:
        """Get all consent records for a user."""
        pass

    @abstractmethod
    def save(self, consent: ConsentRecord) -> ConsentRecord:
        """
        Save updates to an existing ConsentRecord and return the persisted record.
        
        This method persists changes made to the provided `consent` (an existing consent record). Implementations should update the corresponding storage entry and return the stored/updated ConsentRecord instance.
        
        Parameters:
            consent (ConsentRecord): Consent record with modifications to persist.
        
        Returns:
            ConsentRecord: The persisted consent record reflecting any storage-side changes (e.g., timestamps, identifiers).
        """
        pass

    @abstractmethod
    def create(self, consent: ConsentRecord) -> ConsentRecord:
        """
        Create and persist a new ConsentRecord.
        
        Parameters:
            consent (ConsentRecord): Consent data to be created.
        
        Returns:
            ConsentRecord: The persisted consent record — may include persistence-generated fields (e.g., id, timestamps) populated by the implementation.
        """
        pass

    @abstractmethod
    def get_expired_consents(self) -> List[ConsentRecord]:
        """
        Return all consent records that are expired.
        
        An "expired" consent is a ConsentRecord whose expiry timestamp is in the past. Returns an empty list if no expired consents are found.
        
        Returns:
            List[ConsentRecord]: A list of expired consent records.
        """
        pass

    @abstractmethod
    def delete_by_user(self, user_id: int) -> int:
        """
        Delete all consent records associated with the given user.
        
        Returns the number of consent records removed.
        """
        pass


class ProcessingActivityRepository(ABC):
    """Abstract repository for data processing activity logging."""

    @abstractmethod
    def log_activity(self, activity: DataProcessingActivity) -> DataProcessingActivity:
        """
        Log and persist a data processing activity record and return the persisted record.
        
        Parameters:
            activity (DataProcessingActivity): The activity to record (purpose, subject, context, timestamp, etc.). Implementations typically persist this and may augment it (e.g., assign an ID or normalized timestamps).
        
        Returns:
            DataProcessingActivity: The persisted activity instance (may be the same object or a new instance with persistence metadata populated).
        """
        pass

    @abstractmethod
    def get_activities_for_user(
        self, user_id: int, limit: int = 100
    ) -> List[DataProcessingActivity]:
        """
        Retrieve processing activities associated with a user.
        
        Returns up to `limit` DataProcessingActivity records for the given `user_id`. The `limit`
        parameter caps the number of returned activities (default 100).
        
        Parameters:
            user_id (int): ID of the user whose activities are requested.
            limit (int, optional): Maximum number of activities to return. Defaults to 100.
        
        Returns:
            List[DataProcessingActivity]: A list of data processing activity records for the user.
        """
        pass

    @abstractmethod
    def get_activities_by_purpose(
        self, purpose: DataProcessingPurpose, start_date: datetime, end_date: datetime
    ) -> List[DataProcessingActivity]:
        """
        Return processing activities matching a specific data processing purpose within a date range.
        
        Retrieves all DataProcessingActivity records whose declared purpose equals `purpose` and whose timestamp falls between `start_date` and `end_date` (inclusive).
        
        Parameters:
            purpose (DataProcessingPurpose): The processing purpose to filter activities by.
            start_date (datetime): Start of the date range (inclusive).
            end_date (datetime): End of the date range (inclusive).
        
        Returns:
            List[DataProcessingActivity]: A list of matching processing activity records (may be empty).
        """
        pass

    @abstractmethod
    def get_activities_by_context(
        self, context: str, start_date: datetime, end_date: datetime
    ) -> List[DataProcessingActivity]:
        """
        Return all data processing activities that were recorded for a given context within a date range.
        
        Context:
            A string identifying the processing context (e.g., "billing", "analytics"). Matching should be implementation-defined
            (exact match or namespaced).
        
        Parameters:
            context (str): Context identifier to filter activities.
            start_date (datetime): Start of the date range (inclusive).
            end_date (datetime): End of the date range (inclusive).
        
        Returns:
            List[DataProcessingActivity]: Activities associated with `context` whose timestamps fall between `start_date` and `end_date`.
        """
        pass

    @abstractmethod
    def delete_activities_for_user(self, user_id: int) -> int:
        """
        Delete all processing activity records for the given user.
        
        Removes any stored DataProcessingActivity entries associated with the provided user_id and returns how many records were deleted.
        
        Parameters:
            user_id (int): ID of the user whose processing activities should be removed.
        
        Returns:
            int: Number of processing activity records deleted.
        """
        pass

    @abstractmethod
    def get_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Return aggregated processing-activity metrics for a user over a recent time window.
        
        Detailed description:
            Computes a summary of data processing activities for the given user covering the
            past `days` days (inclusive). The summary is returned as a dictionary of
            aggregated metrics and breakdowns keyed by metric name (for example: total
            activity count, counts grouped by processing purpose or context, and recent
            timestamps). The exact keys and structure are implementation-defined but will
            represent high-level aggregates suitable for dashboards and reporting.
        
        Parameters:
            user_id (int): Identifier of the user whose activities are summarized.
            days (int): Lookback window in days to include in the summary. Defaults to 30.
        
        Returns:
            Dict[str, Any]: A mapping from metric names to aggregated values (counts,
            lists, or nested mappings) representing the activity summary for the user.
        """
        pass


class PrivacySettingsRepository(ABC):
    """Abstract repository for privacy settings."""

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[PrivacySettings]:
        """
        Retrieve the privacy settings for the given user.
        
        Returns the user's PrivacySettings if present, otherwise None.
        """
        pass

    @abstractmethod
    def save(self, settings: PrivacySettings) -> PrivacySettings:
        """
        Persist updates to an existing PrivacySettings entity and return the persisted instance.
        
        Parameters:
            settings (PrivacySettings): PrivacySettings object containing updated values to store.
        
        Returns:
            PrivacySettings: The saved PrivacySettings instance (may include fields populated by the repository, e.g., timestamps or persistence identifiers).
        """
        pass

    @abstractmethod
    def create(self, settings: PrivacySettings) -> PrivacySettings:
        """
        Create and persist new privacy settings for a user.
        
        This method stores the provided PrivacySettings as a new record and returns the created instance (including any fields set by the persistence layer, e.g., identifiers or timestamps).
        
        Parameters:
            settings (PrivacySettings): Privacy settings to create for a user.
        
        Returns:
            PrivacySettings: The created PrivacySettings instance as persisted.
        """
        pass

    @abstractmethod
    def delete_by_user(self, user_id: int) -> bool:
        """
        Delete privacy settings for the specified user.
        
        Returns:
            bool: True if privacy settings were deleted (or existed and were removed), False if no settings were found or deletion failed.
        """
        pass


class DataSubjectRequestRepository(ABC):
    """Abstract repository for data subject requests."""

    @abstractmethod
    def create(self, request: DataSubjectRequest) -> DataSubjectRequest:
        """
        Create and persist a new data subject request.
        
        Parameters:
            request (DataSubjectRequest): DataSubjectRequest entity to store. Implementations may populate repository-assigned fields (e.g., id, timestamps, initial status).
        
        Returns:
            DataSubjectRequest: The stored request with any assigned identifiers or metadata populated.
        """
        pass

    @abstractmethod
    def get_by_id(self, request_id: str) -> Optional[DataSubjectRequest]:
        """
        Retrieve a DataSubjectRequest by its identifier.
        
        Parameters:
            request_id (str): Unique identifier of the data subject request (e.g., UUID).
        
        Returns:
            Optional[DataSubjectRequest]: The matching request, or None if no request exists with the given id.
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[DataSubjectRequest]:
        """
        Return all data subject requests associated with the given user.
        
        Retrieves every DataSubjectRequest linked to the user's internal identifier. Results may include requests in any state (pending, completed, cancelled); ordering is implementation-dependent.
        
        Parameters:
            user_id (int): Internal unique identifier of the user whose requests should be retrieved.
        
        Returns:
            List[DataSubjectRequest]: A list of data subject requests for the user; empty if none exist.
        """
        pass

    @abstractmethod
    def save(self, request: DataSubjectRequest) -> DataSubjectRequest:
        """
        Persist updates to a DataSubjectRequest and return the saved instance.
        
        Implementations should update an existing request record with fields from `request` and return the stored/normalized DataSubjectRequest (including any datastore-assigned fields such as timestamps or IDs).
        """
        pass

    @abstractmethod
    def get_pending_requests(self) -> List[DataSubjectRequest]:
        """Get all pending requests."""
        pass

    @abstractmethod
    def get_overdue_requests(self, days_limit: int = 30) -> List[DataSubjectRequest]:
        """
        Retrieve data subject requests that are overdue.
        
        A request is considered overdue if it has been pending for more than `days_limit` days. The default is 30 days.
        
        Parameters:
            days_limit (int): Maximum allowed age in days before a pending request is considered overdue.
        
        Returns:
            List[DataSubjectRequest]: All data subject requests considered overdue.
        """
        pass

    @abstractmethod
    def delete_completed_requests(self, older_than_days: int = 90) -> int:
        """
        Delete data subject requests that are completed and older than the given age.
        
        Removes requests whose status is completed and whose completion timestamp is at least
        `older_than_days` days in the past. Returns the number of requests deleted.
        
        Parameters:
            older_than_days (int): Age threshold in days; requests completed this many days ago or earlier
                will be deleted. Defaults to 90.
        
        Returns:
            int: Number of deleted requests.
        """
        pass
