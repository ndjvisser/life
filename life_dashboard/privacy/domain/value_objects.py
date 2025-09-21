"""
Privacy domain value objects - immutable privacy-related concepts.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class PrivacyLevel(Enum):
    """Privacy levels for data and features."""

    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"
    ANONYMOUS = "anonymous"


class ConsentScope(Enum):
    """Scope of consent for data processing."""

    MINIMAL = "minimal"  # Only essential data
    STANDARD = "standard"  # Standard features
    ENHANCED = "enhanced"  # All features including AI
    RESEARCH = "research"  # Include research participation


@dataclass(frozen=True)
class ConsentDecision:
    """Value object representing a consent decision."""

    granted: bool
    scope: ConsentScope
    timestamp: datetime
    ip_address: str | None = None
    user_agent: str | None = None

    def is_valid_for_purpose(self, required_scope: ConsentScope) -> bool:
        """
        Return True if this consent decision grants the required consent scope.

        The decision is considered sufficient only if `granted` is True and the decision's
        scope is at least as permissive as `required_scope` according to the internal
        hierarchy (MINIMAL < STANDARD < ENHANCED < RESEARCH).
        """
        if not self.granted:
            return False

        scope_hierarchy = {
            ConsentScope.MINIMAL: 1,
            ConsentScope.STANDARD: 2,
            ConsentScope.ENHANCED: 3,
            ConsentScope.RESEARCH: 4,
        }

        return scope_hierarchy[self.scope] >= scope_hierarchy[required_scope]


@dataclass(frozen=True)
class DataRetentionPolicy:
    """Value object for data retention policies."""

    category: str
    retention_days: int
    auto_delete: bool = True

    def __post_init__(self):
        """
        Validate the DataRetentionPolicy after initialization.

        Ensures `retention_days` is not negative.

        Raises:
            ValueError: If `retention_days` is less than 0.
        """
        if self.retention_days < 0:
            raise ValueError("Retention days cannot be negative")

    def is_expired(self, created_at: datetime) -> bool:
        """
        Return True if the retention period has passed for the given creation time.

        If auto_delete is False this always returns False. The expiry is computed as
        created_at + retention_days (days). The current time used for comparison matches
        the timezone awareness of `created_at` to avoid naive/aware datetime mismatches.

        Parameters:
            created_at (datetime): Object creation timestamp. Should represent UTC time
                (either a naive datetime in UTC or an aware datetime with UTC tzinfo).

        Returns:
            bool: True when the current time (aligned with `created_at`'s timezone awareness)
                is strictly after the computed expiry.
        """
        if not self.auto_delete:
            return False

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        expiry_date = created_at + timedelta(days=self.retention_days)

        now = datetime.now(created_at.tzinfo)

        return now > expiry_date

    def expiry_date(self, created_at: datetime) -> datetime:
        """
        Return the exact expiration datetime for data created at `created_at`.

        The expiration is computed by adding this policy's `retention_days` (in days) to `created_at`. The returned value preserves the timezone information of `created_at`.

        Parameters:
            created_at (datetime): The creation timestamp to base the expiry on.

        Returns:
            datetime: The computed expiration timestamp (created_at + retention_days days).
        """
        return created_at + timedelta(days=self.retention_days)


@dataclass(frozen=True)
class PrivacyImpactLevel:
    """Value object for privacy impact assessment."""

    level: str  # low, medium, high, critical
    score: int  # 1-10
    factors: frozenset[str]

    def __post_init__(self):
        if not 1 <= self.score <= 10:
            raise ValueError("Privacy impact score must be between 1 and 10")
        # Enforce immutability of factors
        object.__setattr__(self, "factors", frozenset(self.factors))
        """
        Validate the PrivacyImpactLevel fields after initialization.

        Ensures `score` is within the absolute range 1–10 and that the numeric `score` falls within the expected range for the textual `level`. Known level ranges are:
        - "low": 1–3
        - "medium": 4–6
        - "high": 7–8
        - "critical": 9–10

        If `level` is unrecognized it is treated as allowing the full 1–10 range.

        Raises:
            ValueError: If `score` is outside 1–10, or if `score` does not fall within the range associated with `level`.
        """
        if not 1 <= self.score <= 10:
            raise ValueError("Privacy impact score must be between 1 and 10")

        level_map = {
            "low": (1, 3),
            "medium": (4, 6),
            "high": (7, 8),
            "critical": (9, 10),
        }

        min_score, max_score = level_map.get(self.level, (1, 10))
        if not min_score <= self.score <= max_score:
            raise ValueError(f"Score {self.score} doesn't match level {self.level}")

    def requires_dpo_review(self) -> bool:
        """
        Return whether this impact level requires a Data Protection Officer (DPO) review.

        Returns:
            bool: True if the privacy impact level is "high" or "critical"; otherwise False.
        """
        return self.level in ["high", "critical"]

    def requires_user_notification(self) -> bool:
        """
        Return True if the privacy impact requires notifying affected users.

        Detailed: Determines whether user notification is required based on the impact score.
        Uses a fixed threshold: returns True when `score` is greater than or equal to 7, otherwise False.

        Returns:
            bool: True if notification is required (score >= 7), False otherwise.
        """
        return self.score >= 7
