"""
Contract tests for Skills domain services using Pydantic models.

These tests validate service layer APIs and ensure consistent interfaces.
"""

from datetime import datetime
from typing import Any
from unittest.mock import Mock

import pytest

pytest.importorskip("pydantic")
from pydantic import BaseModel, ValidationError

from life_dashboard.skills.domain.entities import (
    Skill,
    SkillCategory,
)
from life_dashboard.skills.domain.services import SkillCategoryService, SkillService
from life_dashboard.skills.domain.value_objects import (
    CategoryName,
    ExperiencePoints,
    SkillCategoryId,
    SkillId,
    SkillLevel,
    SkillName,
    UserId,
)


# Pydantic models for API contracts
class SkillCategoryCreateRequest(BaseModel):
    """Contract for skill category creation requests"""

    name: str
    description: str = ""
    icon: str = ""

    class Config:
        schema_extra = {
            "example": {
                "name": "Programming",
                "description": "Software development and programming skills",
                "icon": "code",
            }
        }


class SkillCategoryResponse(BaseModel):
    """Contract for skill category responses"""

    category_id: int
    name: str
    description: str
    icon: str
    created_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "category_id": 1,
                "name": "Programming",
                "description": "Software development and programming skills",
                "icon": "code",
                "created_at": "2024-01-01T10:00:00",
            }
        }


class SkillCreateRequest(BaseModel):
    """Contract for skill creation requests"""

    user_id: int
    category_id: int
    name: str
    description: str = ""

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "category_id": 1,
                "name": "Python Programming",
                "description": "Advanced Python development skills",
            }
        }


class SkillResponse(BaseModel):
    """Contract for skill responses"""

    skill_id: int
    user_id: int
    category_id: int
    name: str
    description: str
    level: int
    experience_points: int
    experience_to_next_level: int
    mastery_level: str
    skill_rank: str
    progress_percentage: float
    created_at: datetime
    last_practiced: datetime | None

    class Config:
        schema_extra = {
            "example": {
                "skill_id": 1,
                "user_id": 1,
                "category_id": 1,
                "name": "Python Programming",
                "description": "Advanced Python development skills",
                "level": 15,
                "experience_points": 2500,
                "experience_to_next_level": 1500,
                "mastery_level": "novice",
                "skill_rank": "Improving",
                "progress_percentage": 62.5,
                "created_at": "2024-01-01T10:00:00",
                "last_practiced": "2024-01-15T14:30:00",
            }
        }


class AddExperienceRequest(BaseModel):
    """Contract for add experience requests"""

    skill_id: int
    amount: int
    practice_notes: str = ""

    class Config:
        schema_extra = {
            "example": {
                "skill_id": 1,
                "amount": 500,
                "practice_notes": "Completed advanced Python course",
            }
        }


class AddExperienceResponse(BaseModel):
    """Contract for add experience responses"""

    skill: SkillResponse
    experience_gained: int
    levels_gained: list[int]

    class Config:
        schema_extra = {
            "example": {
                "skill": {"skill_id": 1, "level": 16, "experience_points": 1000},
                "experience_gained": 500,
                "levels_gained": [16],
            }
        }


class PracticeSkillRequest(BaseModel):
    """Contract for practice skill requests"""

    skill_id: int
    practice_duration_minutes: int
    practice_notes: str = ""

    class Config:
        schema_extra = {
            "example": {
                "skill_id": 1,
                "practice_duration_minutes": 60,
                "practice_notes": "Worked on web scraping project",
            }
        }


class PracticeSkillResponse(BaseModel):
    """Contract for practice skill responses"""

    skill: SkillResponse
    experience_gained: int
    levels_gained: list[int]
    practice_efficiency: float

    class Config:
        schema_extra = {
            "example": {
                "skill": {
                    "skill_id": 1,
                    "level": 15,
                    "last_practiced": "2024-01-15T14:30:00",
                },
                "experience_gained": 600,
                "levels_gained": [],
                "practice_efficiency": 1.0,
            }
        }


class SkillProgressSummaryResponse(BaseModel):
    """Contract for skill progress summary responses"""

    total_skills: int
    average_level: float
    total_experience: int
    mastery_distribution: dict[str, int]
    top_skills: list[dict[str, Any]]
    stagnant_skills: list[dict[str, Any]]
    next_milestones: list[dict[str, Any]]

    class Config:
        schema_extra = {
            "example": {
                "total_skills": 5,
                "average_level": 12.4,
                "total_experience": 25000,
                "mastery_distribution": {
                    "novice": 3,
                    "apprentice": 2,
                    "journeyman": 0,
                    "expert": 0,
                    "master": 0,
                },
                "top_skills": [
                    {
                        "name": "Python Programming",
                        "level": 18,
                        "mastery": "novice",
                        "rank": "Improving",
                    }
                ],
                "stagnant_skills": [
                    {"name": "JavaScript", "level": 8, "days_since_practice": 45}
                ],
                "next_milestones": [
                    {
                        "skill_name": "Python Programming",
                        "current_level": 18,
                        "next_milestone": 20,
                        "progress_percentage": 75.0,
                    }
                ],
            }
        }


class TestSkillCategoryServiceContracts:
    """Test SkillCategoryService API contracts"""

    def setup_method(self):
        """Set up test dependencies"""
        self.mock_repository = Mock()
        self.category_service = SkillCategoryService(self.mock_repository)

    def test_create_category_contract_validation(self):
        """Test category creation request contract validation"""
        # Valid request should pass validation
        valid_request = SkillCategoryCreateRequest(
            name="Programming",
            description="Software development skills",
            icon="code",
        )

        assert valid_request.name == "Programming"
        assert valid_request.description == "Software development skills"
        assert valid_request.icon == "code"

    def test_create_category_contract_validation_errors(self):
        """Test category creation request validation errors"""
        # Missing required fields should raise ValidationError
        with pytest.raises(ValidationError):
            SkillCategoryCreateRequest(
                # Missing name
                description="Test",
                icon="test",
            )

    def test_category_service_create_returns_valid_response(self):
        """Test that category service returns valid response contract"""
        # Mock repository to return a category
        mock_category = SkillCategory(
            category_id=SkillCategoryId(1),
            name=CategoryName("Programming"),
            description="Software development skills",
            icon="code",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
        )
        self.mock_repository.save.return_value = mock_category

        # Create category through service
        result = self.category_service.create_category(
            name="Programming",
            description="Software development skills",
            icon="code",
        )

        # Validate response can be serialized to contract
        response_data = {
            "category_id": result.category_id.value,
            "name": result.name.value,
            "description": result.description,
            "icon": result.icon,
            "created_at": result.created_at,
        }

        # Should not raise validation error
        response = SkillCategoryResponse(**response_data)
        assert response.category_id == 1
        assert response.name == "Programming"


class TestSkillServiceContracts:
    """Test SkillService API contracts"""

    def setup_method(self):
        """Set up test dependencies"""
        self.mock_skill_repository = Mock()
        self.mock_category_repository = Mock()
        self.skill_service = SkillService(
            self.mock_skill_repository, self.mock_category_repository
        )

    def test_create_skill_contract_validation(self):
        """Test skill creation request contract validation"""
        # Valid request should pass validation
        valid_request = SkillCreateRequest(
            user_id=1,
            category_id=1,
            name="Python Programming",
            description="Advanced Python skills",
        )

        assert valid_request.user_id == 1
        assert valid_request.category_id == 1
        assert valid_request.name == "Python Programming"

    def test_add_experience_contract_validation(self):
        """Test add experience request contract validation"""
        # Valid request should pass validation
        valid_request = AddExperienceRequest(
            skill_id=1,
            amount=500,
            practice_notes="Completed course",
        )

        assert valid_request.skill_id == 1
        assert valid_request.amount == 500
        assert valid_request.practice_notes == "Completed course"

        # Invalid amount should raise ValidationError
        with pytest.raises(ValidationError):
            AddExperienceRequest(
                skill_id=1,
                amount="invalid",  # Should be int
            )

    def test_practice_skill_contract_validation(self):
        """Test practice skill request contract validation"""
        # Valid request should pass validation
        valid_request = PracticeSkillRequest(
            skill_id=1,
            practice_duration_minutes=60,
            practice_notes="Web scraping project",
        )

        assert valid_request.skill_id == 1
        assert valid_request.practice_duration_minutes == 60

        # Default values should work
        minimal_request = PracticeSkillRequest(
            skill_id=1,
            practice_duration_minutes=30,
        )
        assert minimal_request.practice_notes == ""

    def test_skill_service_create_returns_valid_response(self):
        """Test that skill service returns valid response contract"""
        # Mock category exists
        mock_category = SkillCategory(
            category_id=SkillCategoryId(1),
            name=CategoryName("Programming"),
            description="Programming skills",
        )
        self.mock_category_repository.get_by_id.return_value = mock_category

        # Mock repository to return a skill
        mock_skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Python Programming"),
            description="Advanced Python skills",
            level=SkillLevel(1),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
        )
        self.mock_skill_repository.save.return_value = mock_skill

        # Create skill through service
        result = self.skill_service.create_skill(
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name="Python Programming",
            description="Advanced Python skills",
        )

        # Validate response can be serialized to contract
        response_data = {
            "skill_id": result.skill_id.value,
            "user_id": result.user_id.value,
            "category_id": result.category_id.value,
            "name": result.name.value,
            "description": result.description,
            "level": result.level.value,
            "experience_points": result.experience_points.value,
            "experience_to_next_level": result.experience_to_next_level.value,
            "mastery_level": result.get_mastery_level().value,
            "skill_rank": result.get_skill_rank(),
            "progress_percentage": result.calculate_progress_percentage(),
            "created_at": result.created_at,
            "last_practiced": result.last_practiced,
        }

        # Should not raise validation error
        response = SkillResponse(**response_data)
        assert response.skill_id == 1
        assert response.name == "Python Programming"

    def test_add_experience_returns_valid_response(self):
        """Test that add experience returns valid response contract"""
        # Mock skill
        mock_skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Python Programming"),
            description="Advanced Python skills",
            level=SkillLevel(5),
            experience_points=ExperiencePoints(800),
            experience_to_next_level=ExperiencePoints(1000),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
        )

        # Mock updated skill after adding experience
        updated_skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Python Programming"),
            description="Advanced Python skills",
            level=SkillLevel(6),
            experience_points=ExperiencePoints(300),  # 800 + 500 - 1000
            experience_to_next_level=ExperiencePoints(1100),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            last_practiced=datetime(2024, 1, 15, 14, 30, 0),
        )

        self.mock_skill_repository.get_by_id.return_value = mock_skill
        self.mock_skill_repository.save.return_value = updated_skill

        # Add experience
        result_skill, levels_gained = self.skill_service.add_experience(
            SkillId(1), 500, "Completed course"
        )

        # Validate response contract
        skill_data = {
            "skill_id": result_skill.skill_id.value,
            "user_id": result_skill.user_id.value,
            "category_id": result_skill.category_id.value,
            "name": result_skill.name.value,
            "description": result_skill.description,
            "level": result_skill.level.value,
            "experience_points": result_skill.experience_points.value,
            "experience_to_next_level": result_skill.experience_to_next_level.value,
            "mastery_level": result_skill.get_mastery_level().value,
            "skill_rank": result_skill.get_skill_rank(),
            "progress_percentage": result_skill.calculate_progress_percentage(),
            "created_at": result_skill.created_at,
            "last_practiced": result_skill.last_practiced,
        }

        add_exp_response = AddExperienceResponse(
            skill=SkillResponse(**skill_data),
            experience_gained=500,
            levels_gained=levels_gained,
        )

        assert add_exp_response.experience_gained == 500
        assert add_exp_response.skill.level == 6

    def test_skill_progress_summary_returns_valid_response(self):
        """Test that skill progress summary returns valid response contract"""
        # Mock user skills
        mock_skills = [
            Skill(
                skill_id=SkillId(1),
                user_id=UserId(1),
                category_id=SkillCategoryId(1),
                name=SkillName("Python Programming"),
                description="Python skills",
                level=SkillLevel(18),
                experience_points=ExperiencePoints(500),
                experience_to_next_level=ExperiencePoints(1000),
                last_practiced=datetime(2024, 1, 1, 10, 0, 0),
            ),
            Skill(
                skill_id=SkillId(2),
                user_id=UserId(1),
                category_id=SkillCategoryId(1),
                name=SkillName("JavaScript"),
                description="JS skills",
                level=SkillLevel(8),
                experience_points=ExperiencePoints(200),
                experience_to_next_level=ExperiencePoints(800),
                last_practiced=datetime(2023, 11, 1, 10, 0, 0),  # Stagnant
            ),
        ]

        self.mock_skill_repository.get_user_skills.return_value = mock_skills

        # Get progress summary
        summary = self.skill_service.get_skill_progress_summary(UserId(1))

        # Validate response contract
        summary_response = SkillProgressSummaryResponse(**summary)

        assert summary_response.total_skills == 2
        assert summary_response.average_level > 0
        assert len(summary_response.top_skills) > 0
        assert len(summary_response.mastery_distribution) == 5

    def test_contract_schema_examples_are_valid(self):
        """Test that all contract schema examples are valid"""
        # Test SkillCreateRequest example
        skill_example = SkillCreateRequest.Config.schema_extra["example"]
        skill_request = SkillCreateRequest(**skill_example)
        assert skill_request.name == "Python Programming"

        # Test AddExperienceRequest example
        exp_example = AddExperienceRequest.Config.schema_extra["example"]
        exp_request = AddExperienceRequest(**exp_example)
        assert exp_request.amount == 500

        # Test PracticeSkillRequest example
        practice_example = PracticeSkillRequest.Config.schema_extra["example"]
        practice_request = PracticeSkillRequest(**practice_example)
        assert practice_request.practice_duration_minutes == 60
