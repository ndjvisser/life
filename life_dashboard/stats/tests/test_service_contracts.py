"""
Contract tests for stats service layer APIs using Pydantic models.

These tests validate that service layer APIs maintain their contracts
and return properly structured data that can be serialized/deserialized.
"""

from datetime import datetime
from decimal import Decimal

import pytest

pytest.importorskip("pydantic")
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..domain.entities import CoreStat, LifeStat, StatHistory


# Pydantic models for service layer contracts
class CoreStatResponse(BaseModel):
    """Contract model for CoreStat API responses."""

    user_id: int = Field(..., gt=0, description="User ID must be positive")
    strength: int = Field(..., ge=1, le=100, description="Strength stat (1-100)")
    endurance: int = Field(..., ge=1, le=100, description="Endurance stat (1-100)")
    agility: int = Field(..., ge=1, le=100, description="Agility stat (1-100)")
    intelligence: int = Field(
        ..., ge=1, le=100, description="Intelligence stat (1-100)"
    )
    wisdom: int = Field(..., ge=1, le=100, description="Wisdom stat (1-100)")
    charisma: int = Field(..., ge=1, le=100, description="Charisma stat (1-100)")
    experience_points: int = Field(
        ..., ge=0, description="Experience points (non-negative)"
    )
    level: int = Field(..., ge=1, description="Character level (minimum 1)")
    stat_total: int = Field(..., ge=6, le=600, description="Sum of all stats")
    stat_average: float = Field(
        ..., ge=1.0, le=100.0, description="Average of all stats"
    )
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat() if v else None}
    )


class LifeStatResponse(BaseModel):
    """Contract model for LifeStat API responses."""

    user_id: int = Field(..., gt=0, description="User ID must be positive")
    category: str = Field(
        ..., pattern="^(health|wealth|relationships)$", description="Valid category"
    )
    name: str = Field(..., min_length=1, max_length=100, description="Stat name")
    value: float = Field(..., description="Current stat value")
    target: float | None = Field(None, description="Target value (optional)")
    unit: str = Field("", max_length=20, description="Unit of measurement")
    notes: str = Field("", max_length=500, description="Additional notes")
    progress_percentage: float = Field(
        ..., ge=0.0, le=100.0, description="Progress percentage"
    )
    is_target_achieved: bool = Field(..., description="Whether target is achieved")
    distance_to_target: float | None = Field(None, description="Distance to target")
    last_updated: datetime | None = Field(None, description="Last update timestamp")
    created_at: datetime | None = Field(None, description="Creation timestamp")

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat() if v else None}
    )


class StatHistoryResponse(BaseModel):
    """Contract model for StatHistory API responses."""

    user_id: int = Field(..., gt=0, description="User ID must be positive")
    stat_type: str = Field(..., min_length=1, description="Type of stat")
    stat_name: str = Field(..., min_length=1, description="Name of stat")
    old_value: float = Field(..., description="Previous value")
    new_value: float = Field(..., description="New value")
    change_amount: float = Field(..., description="Amount of change")
    change_reason: str = Field("", max_length=200, description="Reason for change")
    is_increase: bool = Field(..., description="Whether this is an increase")
    is_decrease: bool = Field(..., description="Whether this is a decrease")
    percentage_change: float | None = Field(None, description="Percentage change")
    timestamp: datetime | None = Field(None, description="When change occurred")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class StatUpdateRequest(BaseModel):
    """Contract model for stat update requests."""

    stat_name: str = Field(
        ..., pattern="^(strength|endurance|agility|intelligence|wisdom|charisma)$"
    )
    value: int = Field(..., ge=1, le=100, description="New stat value (1-100)")


class LifeStatUpdateRequest(BaseModel):
    """Contract model for life stat update requests."""

    category: str = Field(..., pattern="^(health|wealth|relationships)$")
    name: str = Field(..., min_length=1, max_length=100)
    value: float = Field(..., description="New stat value")
    target: float | None = Field(None, description="Target value (optional)")
    unit: str = Field("", max_length=20)
    notes: str = Field("", max_length=500)


class ExperienceAwardRequest(BaseModel):
    """Contract model for experience award requests."""

    points: int = Field(
        ..., gt=0, le=10000, description="Experience points to award (1-10000)"
    )
    reason: str = Field(
        "", max_length=200, description="Reason for awarding experience"
    )


class StatSummaryResponse(BaseModel):
    """Contract model for stat summary responses."""

    user_id: int = Field(..., gt=0)
    total_stats: int = Field(..., ge=0)
    total_changes: int = Field(..., ge=0)
    recent_changes: int = Field(..., ge=0)
    categories: list[str] = Field(..., description="Available stat categories")
    last_activity: datetime | None = Field(None)

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat() if v else None}
    )


@pytest.mark.contract
@pytest.mark.unit
class TestCoreStatContracts:
    """Test CoreStat service contracts."""

    def test_core_stat_response_contract_valid(self):
        """Test that valid CoreStat data conforms to response contract."""
        # Create a valid CoreStat
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

        # Convert to dict (simulating service layer response)
        data = core_stat.to_dict()

        # Validate against contract
        response = CoreStatResponse(**data)

        assert response.user_id == 1
        assert response.strength == 15
        assert response.level == 3  # 2500 XP = level 3
        assert response.stat_total == 95
        assert response.stat_average == 95 / 6

    def test_core_stat_response_contract_invalid_stats(self):
        """Test that invalid stat values are rejected by contract."""
        invalid_data = {
            "user_id": 1,
            "strength": 0,  # Invalid: below minimum
            "endurance": 12,
            "agility": 18,
            "intelligence": 20,
            "wisdom": 14,
            "charisma": 16,
            "experience_points": 1000,
            "level": 2,
            "stat_total": 80,
            "stat_average": 13.33,
        }

        with pytest.raises(ValidationError) as exc_info:
            CoreStatResponse(**invalid_data)

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "strength" for error in errors)

    def test_core_stat_response_contract_invalid_user_id(self):
        """Test that invalid user ID is rejected by contract."""
        invalid_data = {
            "user_id": 0,  # Invalid: not positive
            "strength": 10,
            "endurance": 10,
            "agility": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
            "experience_points": 0,
            "level": 1,
            "stat_total": 60,
            "stat_average": 10.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            CoreStatResponse(**invalid_data)

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "user_id" for error in errors)

    def test_stat_update_request_contract(self):
        """Test StatUpdateRequest contract validation."""
        # Valid request
        valid_request = StatUpdateRequest(stat_name="strength", value=25)
        assert valid_request.stat_name == "strength"
        assert valid_request.value == 25

        # Invalid stat name
        with pytest.raises(ValidationError):
            StatUpdateRequest(stat_name="invalid_stat", value=25)

        # Invalid value (too low)
        with pytest.raises(ValidationError):
            StatUpdateRequest(stat_name="strength", value=0)

        # Invalid value (too high)
        with pytest.raises(ValidationError):
            StatUpdateRequest(stat_name="strength", value=101)

    def test_experience_award_request_contract(self):
        """Test ExperienceAwardRequest contract validation."""
        # Valid request
        valid_request = ExperienceAwardRequest(points=500, reason="Quest completion")
        assert valid_request.points == 500
        assert valid_request.reason == "Quest completion"

        # Valid request without reason
        valid_request_no_reason = ExperienceAwardRequest(points=100)
        assert valid_request_no_reason.points == 100
        assert valid_request_no_reason.reason == ""

        # Invalid points (too low)
        with pytest.raises(ValidationError):
            ExperienceAwardRequest(points=0)

        # Invalid points (too high)
        with pytest.raises(ValidationError):
            ExperienceAwardRequest(points=20000)


@pytest.mark.contract
@pytest.mark.unit
class TestLifeStatContracts:
    """Test LifeStat service contracts."""

    def test_life_stat_response_contract_valid(self):
        """Test that valid LifeStat data conforms to response contract."""
        # Create a valid LifeStat
        life_stat = LifeStat(
            user_id=1,
            category="health",
            name="weight",
            value=Decimal("70.5"),
            target=Decimal("65.0"),
            unit="kg",
            notes="Weekly weigh-in",
        )

        # Convert to dict (simulating service layer response)
        data = life_stat.to_dict()

        # Validate against contract
        response = LifeStatResponse(**data)

        assert response.user_id == 1
        assert response.category == "health"
        assert response.name == "weight"
        assert response.value == 70.5
        assert response.target == 65.0
        assert response.unit == "kg"
        assert response.notes == "Weekly weigh-in"

    def test_life_stat_response_contract_invalid_category(self):
        """Test that invalid category is rejected by contract."""
        invalid_data = {
            "user_id": 1,
            "category": "invalid_category",  # Invalid category
            "name": "test",
            "value": 50.0,
            "progress_percentage": 0.0,
            "is_target_achieved": False,
        }

        with pytest.raises(ValidationError) as exc_info:
            LifeStatResponse(**invalid_data)

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "category" for error in errors)

    def test_life_stat_update_request_contract(self):
        """Test LifeStatUpdateRequest contract validation."""
        # Valid request
        valid_request = LifeStatUpdateRequest(
            category="health",
            name="weight",
            value=70.5,
            target=65.0,
            unit="kg",
            notes="Target weight loss",
        )
        assert valid_request.category == "health"
        assert valid_request.name == "weight"
        assert valid_request.value == 70.5

        # Invalid category
        with pytest.raises(ValidationError):
            LifeStatUpdateRequest(
                category="invalid",
                name="test",
                value=50.0,
            )

        # Invalid name (empty)
        with pytest.raises(ValidationError):
            LifeStatUpdateRequest(
                category="health",
                name="",
                value=50.0,
            )


@pytest.mark.contract
@pytest.mark.unit
class TestStatHistoryContracts:
    """Test StatHistory service contracts."""

    def test_stat_history_response_contract_valid(self):
        """Test that valid StatHistory data conforms to response contract."""
        # Create a valid StatHistory
        history = StatHistory(
            user_id=1,
            stat_type="core",
            stat_name="strength",
            old_value=Decimal("10"),
            new_value=Decimal("15"),
            change_reason="Training session",
        )

        # Convert to dict (simulating service layer response)
        data = history.to_dict()

        # Validate against contract
        response = StatHistoryResponse(**data)

        assert response.user_id == 1
        assert response.stat_type == "core"
        assert response.stat_name == "strength"
        assert response.old_value == 10.0
        assert response.new_value == 15.0
        assert response.change_amount == 5.0
        assert response.is_increase is True
        assert response.is_decrease is False

    def test_stat_history_response_contract_invalid_user_id(self):
        """Test that invalid user ID is rejected by contract."""
        invalid_data = {
            "user_id": -1,  # Invalid: negative
            "stat_type": "core",
            "stat_name": "strength",
            "old_value": 10.0,
            "new_value": 15.0,
            "change_amount": 5.0,
            "change_reason": "",
            "is_increase": True,
            "is_decrease": False,
        }

        with pytest.raises(ValidationError) as exc_info:
            StatHistoryResponse(**invalid_data)

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "user_id" for error in errors)


@pytest.mark.contract
@pytest.mark.unit
class TestServiceContractSerialization:
    """Test contract model serialization/deserialization."""

    def test_core_stat_json_serialization(self):
        """Test CoreStat contract JSON serialization."""
        core_stat = CoreStat(user_id=1, strength=15, experience_points=1500)
        data = core_stat.to_dict()

        # Create contract model
        response = CoreStatResponse(**data)

        # Serialize to JSON
        json_data = response.model_dump_json()
        assert isinstance(json_data, str)

        # Deserialize from JSON
        deserialized = CoreStatResponse.model_validate_json(json_data)
        assert deserialized.user_id == response.user_id
        assert deserialized.strength == response.strength

    def test_life_stat_json_serialization(self):
        """Test LifeStat contract JSON serialization."""
        life_stat = LifeStat(
            user_id=1,
            category="health",
            name="weight",
            value=Decimal("70.5"),
        )
        data = life_stat.to_dict()

        # Create contract model
        response = LifeStatResponse(**data)

        # Serialize to JSON
        json_data = response.model_dump_json()
        assert isinstance(json_data, str)

        # Deserialize from JSON
        deserialized = LifeStatResponse.model_validate_json(json_data)
        assert deserialized.user_id == response.user_id
        assert deserialized.category == response.category
        assert deserialized.value == response.value

    def test_contract_model_dict_conversion(self):
        """Test contract model dictionary conversion."""
        request_data = {
            "stat_name": "strength",
            "value": 25,
        }

        # Create from dict
        request = StatUpdateRequest(**request_data)

        # Convert back to dict
        result_dict = request.model_dump()
        assert result_dict["stat_name"] == "strength"
        assert result_dict["value"] == 25

    def test_contract_validation_error_details(self):
        """Test that contract validation provides detailed error information."""
        invalid_data = {
            "user_id": -1,  # Invalid
            "strength": 0,  # Invalid
            "endurance": 101,  # Invalid
            "agility": "not_a_number",  # Invalid type
            "intelligence": 20,
            "wisdom": 14,
            "charisma": 16,
            "experience_points": -100,  # Invalid
            "level": 0,  # Invalid
            "stat_total": 95,
            "stat_average": 15.83,
        }

        with pytest.raises(ValidationError) as exc_info:
            CoreStatResponse(**invalid_data)

        errors = exc_info.value.errors()

        # Should have multiple validation errors
        assert len(errors) >= 4

        # Check that error details are informative
        error_fields = [error["loc"][0] for error in errors]
        assert "user_id" in error_fields
        assert "strength" in error_fields
        assert "endurance" in error_fields
        assert "experience_points" in error_fields
        assert "level" in error_fields


@pytest.mark.contract
@pytest.mark.unit
class TestContractCompatibility:
    """Test contract compatibility and evolution."""

    def test_contract_backward_compatibility(self):
        """Test that contracts are backward compatible with minimal data."""
        # Minimal valid CoreStat data
        minimal_data = {
            "user_id": 1,
            "strength": 10,
            "endurance": 10,
            "agility": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
            "experience_points": 0,
            "level": 1,
            "stat_total": 60,
            "stat_average": 10.0,
        }

        # Should work without optional fields
        response = CoreStatResponse(**minimal_data)
        assert response.user_id == 1
        assert response.created_at is None
        assert response.updated_at is None

    def test_contract_forward_compatibility(self):
        """Test that contracts ignore unknown fields gracefully."""
        # Data with extra unknown fields
        data_with_extras = {
            "user_id": 1,
            "strength": 15,
            "endurance": 12,
            "agility": 18,
            "intelligence": 20,
            "wisdom": 14,
            "charisma": 16,
            "experience_points": 1500,
            "level": 2,
            "stat_total": 95,
            "stat_average": 15.83,
            "unknown_field": "should_be_ignored",  # Extra field
            "another_extra": 42,  # Another extra field
        }

        # Should work and ignore extra fields
        response = CoreStatResponse(**data_with_extras)
        assert response.user_id == 1
        assert response.strength == 15
        # Extra fields should not be present
        assert not hasattr(response, "unknown_field")
        assert not hasattr(response, "another_extra")
