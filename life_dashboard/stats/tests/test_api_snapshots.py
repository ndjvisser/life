"""
Snapshot tests for stats API responses to prevent breaking changes.

These tests capture the exact structure and format of API responses
and detect any unintended changes to the API contract.
"""

import json
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pytest_snapshot.plugin import Snapshot

from ..domain.entities import CoreStat, LifeStat, StatHistory


@pytest.mark.snapshot
@pytest.mark.unit
class TestCoreStatSnapshots:
    """Snapshot tests for CoreStat API responses."""

    def test_core_stat_basic_response_snapshot(self, snapshot: Snapshot):
        """Test basic CoreStat response structure."""
        core_stat = CoreStat(
            user_id=1,
            strength=15,
            endurance=12,
            agility=18,
            intelligence=20,
            wisdom=14,
            charisma=16,
            experience_points=2500,
        )

        # Set predictable timestamps for snapshot consistency
        fixed_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        core_stat.created_at = fixed_time
        core_stat.updated_at = fixed_time

        response_data = core_stat.to_dict()

        # Convert datetime objects to ISO strings for JSON serialization
        if response_data.get("created_at"):
            response_data["created_at"] = response_data["created_at"].isoformat()
        if response_data.get("updated_at"):
            response_data["updated_at"] = response_data["updated_at"].isoformat()

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True), "core_stat_basic.json"
        )

    def test_core_stat_minimal_response_snapshot(self, snapshot: Snapshot):
        """Test minimal CoreStat response (default values)."""
        core_stat = CoreStat(user_id=42)
        response_data = core_stat.to_dict()

        # Remove timestamps for consistent snapshots
        response_data.pop("created_at", None)
        response_data.pop("updated_at", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "core_stat_minimal.json",
        )

    def test_core_stat_max_level_response_snapshot(self, snapshot: Snapshot):
        """Test CoreStat response with maximum experience."""
        core_stat = CoreStat(
            user_id=1,
            strength=100,
            endurance=100,
            agility=100,
            intelligence=100,
            wisdom=100,
            charisma=100,
            experience_points=2**31 - 1,  # Maximum experience
        )

        response_data = core_stat.to_dict()

        # Remove timestamps for consistent snapshots
        response_data.pop("created_at", None)
        response_data.pop("updated_at", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "core_stat_max_level.json",
        )

    def test_core_stat_list_response_snapshot(self, snapshot: Snapshot):
        """Test list of CoreStat responses."""
        core_stats = [
            CoreStat(user_id=1, strength=15, experience_points=1500),
            CoreStat(user_id=2, strength=20, intelligence=25, experience_points=3000),
            CoreStat(user_id=3, charisma=30, wisdom=18, experience_points=500),
        ]

        response_data = []
        for stat in core_stats:
            stat_data = stat.to_dict()
            # Remove timestamps for consistent snapshots
            stat_data.pop("created_at", None)
            stat_data.pop("updated_at", None)
            response_data.append(stat_data)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True), "core_stat_list.json"
        )


@pytest.mark.snapshot
@pytest.mark.unit
class TestLifeStatSnapshots:
    """Snapshot tests for LifeStat API responses."""

    def test_life_stat_health_response_snapshot(self, snapshot: Snapshot):
        """Test LifeStat health category response."""
        life_stat = LifeStat(
            user_id=1,
            category="health",
            name="weight",
            value=Decimal("70.5"),
            target=Decimal("65.0"),
            unit="kg",
            notes="Weekly weigh-in goal",
        )

        # Set predictable timestamp
        fixed_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        life_stat.last_updated = fixed_time
        life_stat.created_at = fixed_time

        response_data = life_stat.to_dict()

        # Convert datetime objects to ISO strings
        if response_data.get("last_updated"):
            response_data["last_updated"] = response_data["last_updated"].isoformat()
        if response_data.get("created_at"):
            response_data["created_at"] = response_data["created_at"].isoformat()

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True), "life_stat_health.json"
        )

    def test_life_stat_wealth_response_snapshot(self, snapshot: Snapshot):
        """Test LifeStat wealth category response."""
        life_stat = LifeStat(
            user_id=1,
            category="wealth",
            name="savings",
            value=Decimal("15000.50"),
            target=Decimal("50000.00"),
            unit="USD",
            notes="Emergency fund target",
        )

        response_data = life_stat.to_dict()

        # Remove timestamps for consistent snapshots
        response_data.pop("last_updated", None)
        response_data.pop("created_at", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True), "life_stat_wealth.json"
        )

    def test_life_stat_relationships_response_snapshot(self, snapshot: Snapshot):
        """Test LifeStat relationships category response."""
        life_stat = LifeStat(
            user_id=1,
            category="relationships",
            name="social_events_attended",
            value=Decimal("8"),
            target=Decimal("12"),
            unit="events/month",
            notes="Monthly social engagement goal",
        )

        response_data = life_stat.to_dict()

        # Remove timestamps for consistent snapshots
        response_data.pop("last_updated", None)
        response_data.pop("created_at", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "life_stat_relationships.json",
        )

    def test_life_stat_no_target_response_snapshot(self, snapshot: Snapshot):
        """Test LifeStat response without target."""
        life_stat = LifeStat(
            user_id=1,
            category="health",
            name="steps_today",
            value=Decimal("8500"),
            unit="steps",
            notes="Daily step count",
        )

        response_data = life_stat.to_dict()

        # Remove timestamps for consistent snapshots
        response_data.pop("last_updated", None)
        response_data.pop("created_at", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "life_stat_no_target.json",
        )

    def test_life_stat_achieved_target_response_snapshot(self, snapshot: Snapshot):
        """Test LifeStat response with achieved target."""
        life_stat = LifeStat(
            user_id=1,
            category="wealth",
            name="monthly_savings",
            value=Decimal("1200.00"),
            target=Decimal("1000.00"),
            unit="USD",
            notes="Exceeded monthly savings goal!",
        )

        response_data = life_stat.to_dict()

        # Remove timestamps for consistent snapshots
        response_data.pop("last_updated", None)
        response_data.pop("created_at", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "life_stat_achieved.json",
        )

    def test_life_stat_list_by_category_snapshot(self, snapshot: Snapshot):
        """Test list of LifeStats grouped by category."""
        health_stats = [
            LifeStat(
                user_id=1,
                category="health",
                name="weight",
                value=Decimal("70.5"),
                unit="kg",
            ),
            LifeStat(
                user_id=1,
                category="health",
                name="steps",
                value=Decimal("10000"),
                unit="steps/day",
            ),
            LifeStat(
                user_id=1,
                category="health",
                name="sleep",
                value=Decimal("7.5"),
                unit="hours",
            ),
        ]

        wealth_stats = [
            LifeStat(
                user_id=1,
                category="wealth",
                name="savings",
                value=Decimal("25000"),
                unit="USD",
            ),
            LifeStat(
                user_id=1,
                category="wealth",
                name="investments",
                value=Decimal("15000"),
                unit="USD",
            ),
        ]

        relationships_stats = [
            LifeStat(
                user_id=1,
                category="relationships",
                name="family_time",
                value=Decimal("10"),
                unit="hours/week",
            ),
        ]

        response_data = {
            "health": [stat.to_dict() for stat in health_stats],
            "wealth": [stat.to_dict() for stat in wealth_stats],
            "relationships": [stat.to_dict() for stat in relationships_stats],
        }

        # Remove timestamps for consistent snapshots
        for category_stats in response_data.values():
            for stat_data in category_stats:
                stat_data.pop("last_updated", None)
                stat_data.pop("created_at", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "life_stat_by_category.json",
        )


@pytest.mark.snapshot
@pytest.mark.unit
class TestStatHistorySnapshots:
    """Snapshot tests for StatHistory API responses."""

    def test_stat_history_increase_response_snapshot(self, snapshot: Snapshot):
        """Test StatHistory response for stat increase."""
        history = StatHistory(
            user_id=1,
            stat_type="core",
            stat_name="strength",
            old_value=Decimal("15"),
            new_value=Decimal("18"),
            change_reason="Completed strength training quest",
        )

        # Set predictable timestamp
        fixed_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        history.timestamp = fixed_time

        response_data = history.to_dict()

        # Convert datetime to ISO string
        if response_data.get("timestamp"):
            response_data["timestamp"] = response_data["timestamp"].isoformat()

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "stat_history_increase.json",
        )

    def test_stat_history_decrease_response_snapshot(self, snapshot: Snapshot):
        """Test StatHistory response for stat decrease."""
        history = StatHistory(
            user_id=1,
            stat_type="life",
            stat_name="weight",
            old_value=Decimal("72.0"),
            new_value=Decimal("70.5"),
            change_reason="Weekly weigh-in - diet progress",
        )

        response_data = history.to_dict()

        # Remove timestamp for consistent snapshots
        response_data.pop("timestamp", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "stat_history_decrease.json",
        )

    def test_stat_history_zero_old_value_response_snapshot(self, snapshot: Snapshot):
        """Test StatHistory response with zero old value."""
        history = StatHistory(
            user_id=1,
            stat_type="life",
            stat_name="savings",
            old_value=Decimal("0"),
            new_value=Decimal("1000"),
            change_reason="First savings deposit",
        )

        response_data = history.to_dict()

        # Remove timestamp for consistent snapshots
        response_data.pop("timestamp", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "stat_history_zero_old.json",
        )

    def test_stat_history_no_change_response_snapshot(self, snapshot: Snapshot):
        """Test StatHistory response with no change."""
        history = StatHistory(
            user_id=1,
            stat_type="core",
            stat_name="intelligence",
            old_value=Decimal("20"),
            new_value=Decimal("20"),
            change_reason="Stat review - no change",
        )

        response_data = history.to_dict()

        # Remove timestamp for consistent snapshots
        response_data.pop("timestamp", None)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "stat_history_no_change.json",
        )

    def test_stat_history_list_response_snapshot(self, snapshot: Snapshot):
        """Test list of StatHistory responses."""
        histories = [
            StatHistory(
                user_id=1,
                stat_type="core",
                stat_name="strength",
                old_value=Decimal("15"),
                new_value=Decimal("18"),
                change_reason="Training quest completed",
            ),
            StatHistory(
                user_id=1,
                stat_type="life",
                stat_name="weight",
                old_value=Decimal("72.0"),
                new_value=Decimal("70.5"),
                change_reason="Diet progress",
            ),
            StatHistory(
                user_id=1,
                stat_type="core",
                stat_name="charisma",
                old_value=Decimal("12"),
                new_value=Decimal("14"),
                change_reason="Social interaction quest",
            ),
        ]

        response_data = []
        for history in histories:
            history_data = history.to_dict()
            # Remove timestamps for consistent snapshots
            history_data.pop("timestamp", None)
            response_data.append(history_data)

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "stat_history_list.json",
        )


@pytest.mark.snapshot
@pytest.mark.unit
class TestAPIErrorSnapshots:
    """Snapshot tests for API error responses."""

    def test_validation_error_response_snapshot(self, snapshot: Snapshot):
        """Test validation error response structure."""
        error_response = {
            "error": "ValidationError",
            "message": "Invalid input data",
            "details": [
                {
                    "field": "strength",
                    "message": "Stat value must be between 1 and 100",
                    "invalid_value": 0,
                },
                {
                    "field": "user_id",
                    "message": "User ID must be positive",
                    "invalid_value": -1,
                },
            ],
            "timestamp": "2024-01-15T10:30:00Z",
            "request_id": "req_123456789",
        }

        snapshot.assert_match(
            json.dumps(error_response, indent=2, sort_keys=True),
            "validation_error.json",
        )

    def test_not_found_error_response_snapshot(self, snapshot: Snapshot):
        """Test not found error response structure."""
        error_response = {
            "error": "NotFound",
            "message": "CoreStat not found for user",
            "details": {
                "user_id": 999,
                "resource": "CoreStat",
            },
            "timestamp": "2024-01-15T10:30:00Z",
            "request_id": "req_987654321",
        }

        snapshot.assert_match(
            json.dumps(error_response, indent=2, sort_keys=True), "not_found_error.json"
        )

    def test_server_error_response_snapshot(self, snapshot: Snapshot):
        """Test server error response structure."""
        error_response = {
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {
                "error_id": "err_abc123def456",
                "support_contact": "support@lifedashboard.com",
            },
            "timestamp": "2024-01-15T10:30:00Z",
            "request_id": "req_error_001",
        }

        snapshot.assert_match(
            json.dumps(error_response, indent=2, sort_keys=True), "server_error.json"
        )


@pytest.mark.snapshot
@pytest.mark.unit
class TestAPIMetadataSnapshots:
    """Snapshot tests for API metadata and pagination."""

    def test_paginated_response_snapshot(self, snapshot: Snapshot):
        """Test paginated API response structure."""
        paginated_response = {
            "data": [
                {
                    "user_id": 1,
                    "stat_type": "core",
                    "stat_name": "strength",
                    "old_value": 15.0,
                    "new_value": 18.0,
                    "change_amount": 3.0,
                    "change_reason": "Training quest",
                    "is_increase": True,
                    "is_decrease": False,
                    "percentage_change": 20.0,
                },
            ],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total_items": 45,
                "total_pages": 3,
                "has_next": True,
                "has_prev": False,
                "next_page": 2,
                "prev_page": None,
            },
            "meta": {
                "request_id": "req_pagination_001",
                "timestamp": "2024-01-15T10:30:00Z",
                "api_version": "v1",
                "response_time_ms": 42,
            },
        }

        snapshot.assert_match(
            json.dumps(paginated_response, indent=2, sort_keys=True),
            "paginated_response.json",
        )

    def test_api_info_response_snapshot(self, snapshot: Snapshot):
        """Test API info/health response structure."""
        api_info_response = {
            "api": {
                "name": "Life Dashboard Stats API",
                "version": "1.0.0",
                "description": "RPG-inspired personal life dashboard statistics API",
            },
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "uptime_seconds": 86400,
            "features": {
                "core_stats": True,
                "life_stats": True,
                "stat_history": True,
                "achievements": True,
                "integrations": False,
            },
            "limits": {
                "max_stats_per_user": 1000,
                "max_history_entries": 10000,
                "rate_limit_per_minute": 100,
            },
        }

        snapshot.assert_match(
            json.dumps(api_info_response, indent=2, sort_keys=True), "api_info.json"
        )

    def test_bulk_operation_response_snapshot(self, snapshot: Snapshot):
        """Test bulk operation response structure."""
        bulk_response = {
            "operation": "bulk_update_stats",
            "total_requested": 5,
            "successful": 4,
            "failed": 1,
            "results": [
                {"id": 1, "status": "success", "message": "CoreStat updated"},
                {"id": 2, "status": "success", "message": "CoreStat updated"},
                {"id": 3, "status": "success", "message": "CoreStat updated"},
                {"id": 4, "status": "success", "message": "CoreStat updated"},
                {
                    "id": 5,
                    "status": "error",
                    "message": "Invalid stat value",
                    "error_code": "VALIDATION_ERROR",
                },
            ],
            "summary": {
                "success_rate": 0.8,
                "processing_time_ms": 150,
                "errors_by_type": {
                    "VALIDATION_ERROR": 1,
                },
            },
            "timestamp": "2024-01-15T10:30:00Z",
            "request_id": "req_bulk_001",
        }

        snapshot.assert_match(
            json.dumps(bulk_response, indent=2, sort_keys=True), "bulk_operation.json"
        )
