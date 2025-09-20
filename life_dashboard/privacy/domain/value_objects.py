"""
Privacy domain value objects - immutable privacy-related concepts.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Set


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
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def is_valid_for_purpose(self, required_scope: ConsentScope) -> bool:
        """Check if consent is sufficient for required scope."""
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
        if self.retention_days < 0:
            raise ValueError("Retention days cannot be negative")

    def is_expired(self, created_at: datetime) -> bool:
        """Check if data should be deleted based on retention policy."""
        if not self.auto_delete:
            return False

        expiry_date = created_at + timedelta(days=self.retention_days)
        return datetime.utcnow() > expiry_date

    def expiry_date(self, created_at: datetime) -> datetime:
        """Calculate when data expires."""
        return created_at + timedelta(days=self.retention_days)


@dataclass(frozen=True)
class PrivacyImpactLevel:
    """Value object for privacy impact assessment."""

    level: str  # low, medium, high, critical
    score: int  # 1-10
    factors: Set[str]

    def __post_init__(self):
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
        """Check if Data Protection Officer review is required."""
        return self.level in ["high", "critical"]

    def requires_user_notification(self) -> bool:
        """Check if users should be notified of this processing."""
        return self.score >= 7
