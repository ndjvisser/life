"""
Snapshot tests for Skills API responses.

These tests capture API response structures to prevent breaking changes.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

pytest.importorskip("pytest_snapshot")

from tests.snapshot_utils import assert_json_snapshot

from life_dashboard.skills.domain.entities import (
    Skill,
    SkillCategory,
    SkillMasteryLevel,
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


class TestSkillCategoryAPISnapshots:
    """Snapshot tests for SkillCategory API responses"""

    def setup_method(self):
        """Set up test dependencies"""
        self.mock_repository = Mock()
        self.category_service = SkillCategoryService(self.mock_repository)

    def test_category_creation_response_snapshot(self, snapshot):
        """Test skill category creation API response structure"""
        # Mock repository response
        mock_category = SkillCategory(
            category_id=SkillCategoryId(1),
            name=CategoryName("Programming & Development"),
            description="Software development, programming languages, and technical skills",
            icon="code",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
        )
        self.mock_repository.save.return_value = mock_category

        # Create category through service
        result = self.category_service.create_category(
            name="Programming & Development",
            description="Software development, programming languages, and technical skills",
            icon="code",
        )

        # Convert to API response format
        api_response = {
            "category_id": result.category_id.value,
            "name": result.name.value,
            "description": result.description,
            "icon": result.icon,
            "created_at": result.created_at.isoformat(),
        }

        # Snapshot the response structure
        assert_json_snapshot(
            snapshot, api_response, "category_creation_response.json"
        )


class TestSkillAPISnapshots:
    """Snapshot tests for Skill API responses"""

    def setup_method(self):
        """Set up test dependencies"""
        self.mock_skill_repository = Mock()
        self.mock_category_repository = Mock()
        self.skill_service = SkillService(
            self.mock_skill_repository, self.mock_category_repository
        )

    def test_skill_creation_response_snapshot(self, snapshot):
        """Test skill creation API response structure"""
        # Mock category exists
        mock_category = SkillCategory(
            category_id=SkillCategoryId(1),
            name=CategoryName("Programming"),
            description="Programming skills",
        )
        self.mock_category_repository.get_by_id.return_value = mock_category

        # Mock repository response
        mock_skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Python Programming"),
            description="Advanced Python development including web frameworks, data science, and automation",
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
            description="Advanced Python development including web frameworks, data science, and automation",
        )

        # Convert to API response format
        api_response = {
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
            "total_experience_for_level": result.calculate_total_experience_for_level(
                result.level.value
            ),
            "can_level_up": result.can_level_up(),
            "next_milestone": result.next_milestone(),
            "created_at": result.created_at.isoformat(),
            "last_practiced": result.last_practiced.isoformat()
            if result.last_practiced
            else None,
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "skill_creation_response.json")

    def test_add_experience_response_snapshot(self, snapshot):
        """Test add experience API response structure"""
        # Mock existing skill
        mock_skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Python Programming"),
            description="Advanced Python development",
            level=SkillLevel(15),
            experience_points=ExperiencePoints(800),
            experience_to_next_level=ExperiencePoints(1000),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            last_practiced=datetime(2024, 1, 10, 14, 0, 0),
        )

        # Mock updated skill after adding experience (level up)
        updated_skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Python Programming"),
            description="Advanced Python development",
            level=SkillLevel(16),
            experience_points=ExperiencePoints(300),  # 800 + 500 - 1000
            experience_to_next_level=ExperiencePoints(1100),  # 10% increase
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            last_practiced=datetime(2024, 1, 15, 14, 30, 0),
        )

        self.mock_skill_repository.get_by_id.return_value = mock_skill
        self.mock_skill_repository.save.return_value = updated_skill

        # Add experience
        result_skill, levels_gained = self.skill_service.add_experience(
            SkillId(1), 500, "Completed advanced Python course with practical projects"
        )

        # Convert to API response format
        api_response = {
            "skill": {
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
                "created_at": result_skill.created_at.isoformat(),
                "last_practiced": result_skill.last_practiced.isoformat()
                if result_skill.last_practiced
                else None,
            },
            "experience_gained": 500,
            "levels_gained": levels_gained,
            "level_up_occurred": len(levels_gained) > 0,
            "new_mastery_level": result_skill.get_mastery_level().value,
            "new_skill_rank": result_skill.get_skill_rank(),
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "add_experience_response.json")

    def test_practice_skill_response_snapshot(self, snapshot):
        """Test practice skill API response structure"""
        # Mock existing skill
        mock_skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("JavaScript Development"),
            description="Frontend and backend JavaScript development",
            level=SkillLevel(25),
            experience_points=ExperiencePoints(1500),
            experience_to_next_level=ExperiencePoints(2000),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            last_practiced=datetime(2024, 1, 10, 14, 0, 0),  # 5 days ago
        )

        # Mock updated skill after practice
        updated_skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("JavaScript Development"),
            description="Frontend and backend JavaScript development",
            level=SkillLevel(25),
            experience_points=ExperiencePoints(
                2040
            ),  # 1500 + 540 (90 min * 10 * 0.6 efficiency)
            experience_to_next_level=ExperiencePoints(2000),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            last_practiced=datetime(2024, 1, 15, 16, 30, 0),
        )

        self.mock_skill_repository.get_by_id.return_value = mock_skill
        self.mock_skill_repository.save.return_value = updated_skill

        # Practice skill (90 minutes)
        result_skill, experience_gained, levels_gained = (
            self.skill_service.practice_skill(
                SkillId(1), 90, "Built a React application with Node.js backend"
            )
        )

        # Calculate efficiency (5 days since last practice)
        efficiency = mock_skill.calculate_practice_efficiency(5)

        # Convert to API response format
        api_response = {
            "skill": {
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
                "created_at": result_skill.created_at.isoformat(),
                "last_practiced": result_skill.last_practiced.isoformat()
                if result_skill.last_practiced
                else None,
            },
            "practice_session": {
                "duration_minutes": 90,
                "base_experience": 900,  # 90 * 10
                "efficiency_multiplier": efficiency,
                "experience_gained": experience_gained,
                "practice_notes": "Built a React application with Node.js backend",
            },
            "levels_gained": levels_gained,
            "level_up_occurred": len(levels_gained) > 0,
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "practice_skill_response.json")

    def test_skill_progress_summary_response_snapshot(self, snapshot):
        """Test skill progress summary API response structure"""
        # Mock user skills with diverse levels and mastery
        mock_skills = [
            Skill(
                skill_id=SkillId(1),
                user_id=UserId(1),
                category_id=SkillCategoryId(1),
                name=SkillName("Python Programming"),
                description="Python development",
                level=SkillLevel(35),
                experience_points=ExperiencePoints(2500),
                experience_to_next_level=ExperiencePoints(3000),
                last_practiced=datetime(2024, 1, 14, 10, 0, 0),
            ),
            Skill(
                skill_id=SkillId(2),
                user_id=UserId(1),
                category_id=SkillCategoryId(1),
                name=SkillName("JavaScript Development"),
                description="JS development",
                level=SkillLevel(28),
                experience_points=ExperiencePoints(1800),
                experience_to_next_level=ExperiencePoints(2200),
                last_practiced=datetime(2024, 1, 12, 14, 0, 0),
            ),
            Skill(
                skill_id=SkillId(3),
                user_id=UserId(1),
                category_id=SkillCategoryId(2),
                name=SkillName("Machine Learning"),
                description="ML and AI",
                level=SkillLevel(65),
                experience_points=ExperiencePoints(5000),
                experience_to_next_level=ExperiencePoints(8000),
                last_practiced=datetime(2024, 1, 15, 9, 0, 0),
            ),
            Skill(
                skill_id=SkillId(4),
                user_id=UserId(1),
                category_id=SkillCategoryId(3),
                name=SkillName("Database Design"),
                description="SQL and NoSQL",
                level=SkillLevel(12),
                experience_points=ExperiencePoints(800),
                experience_to_next_level=ExperiencePoints(1200),
                last_practiced=datetime(2023, 12, 1, 10, 0, 0),  # Stagnant
            ),
            Skill(
                skill_id=SkillId(5),
                user_id=UserId(1),
                category_id=SkillCategoryId(4),
                name=SkillName("System Architecture"),
                description="Software architecture",
                level=SkillLevel(85),
                experience_points=ExperiencePoints(12000),
                experience_to_next_level=ExperiencePoints(15000),
                last_practiced=datetime(2024, 1, 13, 16, 0, 0),
            ),
        ]

        self.mock_skill_repository.get_user_skills.return_value = mock_skills

        # Get progress summary
        summary = self.skill_service.get_skill_progress_summary(
            UserId(1), current_time=datetime(2024, 1, 15, 18, 0, 0)
        )

        # Convert to API response format (summary is already in the right format)
        api_response = {
            "user_id": 1,
            "summary_generated_at": datetime(2024, 1, 15, 18, 0, 0).isoformat(),
            "skill_statistics": summary,
            "recommendations": {
                "focus_areas": [
                    "Consider practicing Database Design - it's been stagnant for 45 days",
                    "You're close to reaching level 70 in Machine Learning - great progress!",
                    "System Architecture is at Master level - excellent expertise!",
                ],
                "suggested_practice_time": {
                    "daily_minutes": 60,
                    "weekly_focus": "Database Design",
                    "skill_to_prioritize": "Database Design",
                },
            },
        }

        # Snapshot the response structure
        assert_json_snapshot(
            snapshot, api_response, "skill_progress_summary_response.json"
        )

    def test_skill_list_response_snapshot(self, snapshot):
        """Test skill list API response structure"""
        # Mock multiple skills for list view
        mock_skills = [
            Skill(
                skill_id=SkillId(1),
                user_id=UserId(1),
                category_id=SkillCategoryId(1),
                name=SkillName("Python Programming"),
                description="Python development",
                level=SkillLevel(18),
                experience_points=ExperiencePoints(500),
                experience_to_next_level=ExperiencePoints(1000),
                created_at=datetime(2024, 1, 1, 10, 0, 0),
                last_practiced=datetime(2024, 1, 14, 10, 0, 0),
            ),
            Skill(
                skill_id=SkillId(2),
                user_id=UserId(1),
                category_id=SkillCategoryId(1),
                name=SkillName("JavaScript"),
                description="JS development",
                level=SkillLevel(42),
                experience_points=ExperiencePoints(2800),
                experience_to_next_level=ExperiencePoints(3500),
                created_at=datetime(2024, 1, 2, 11, 0, 0),
                last_practiced=datetime(2024, 1, 13, 15, 30, 0),
            ),
            Skill(
                skill_id=SkillId(3),
                user_id=UserId(1),
                category_id=SkillCategoryId(2),
                name=SkillName("Data Science"),
                description="Data analysis and ML",
                level=SkillLevel(75),
                experience_points=ExperiencePoints(8500),
                experience_to_next_level=ExperiencePoints(12000),
                created_at=datetime(2024, 1, 3, 9, 0, 0),
                last_practiced=datetime(2024, 1, 15, 14, 0, 0),
            ),
        ]

        self.mock_skill_repository.get_user_skills.return_value = mock_skills

        # Convert to API response format
        api_response = {
            "skills": [
                {
                    "skill_id": skill.skill_id.value,
                    "user_id": skill.user_id.value,
                    "category_id": skill.category_id.value,
                    "name": skill.name.value,
                    "description": skill.description,
                    "level": skill.level.value,
                    "experience_points": skill.experience_points.value,
                    "experience_to_next_level": skill.experience_to_next_level.value,
                    "mastery_level": skill.get_mastery_level().value,
                    "skill_rank": skill.get_skill_rank(),
                    "progress_percentage": skill.calculate_progress_percentage(),
                    "next_milestone": skill.next_milestone(),
                    "is_stagnant": skill.is_stagnant(30),
                    "created_at": skill.created_at.isoformat(),
                    "last_practiced": skill.last_practiced.isoformat()
                    if skill.last_practiced
                    else None,
                }
                for skill in mock_skills
            ],
            "total_count": len(mock_skills),
            "mastery_breakdown": {
                "novice": len(
                    [
                        s
                        for s in mock_skills
                        if s.get_mastery_level() == SkillMasteryLevel.NOVICE
                    ]
                ),
                "apprentice": len(
                    [
                        s
                        for s in mock_skills
                        if s.get_mastery_level() == SkillMasteryLevel.APPRENTICE
                    ]
                ),
                "journeyman": len(
                    [
                        s
                        for s in mock_skills
                        if s.get_mastery_level() == SkillMasteryLevel.JOURNEYMAN
                    ]
                ),
                "expert": len(
                    [
                        s
                        for s in mock_skills
                        if s.get_mastery_level() == SkillMasteryLevel.EXPERT
                    ]
                ),
                "master": len(
                    [
                        s
                        for s in mock_skills
                        if s.get_mastery_level() == SkillMasteryLevel.MASTER
                    ]
                ),
            },
            "average_level": sum(skill.level.value for skill in mock_skills)
            / len(mock_skills),
            "highest_level_skill": {
                "name": max(mock_skills, key=lambda s: s.level.value).name.value,
                "level": max(skill.level.value for skill in mock_skills),
            },
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "skill_list_response.json")
