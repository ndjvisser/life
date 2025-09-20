"""
Achievements Domain Services

Pure business logic services for achievements operations.
No Django dependencies allowed in this module.
"""

from datetime import datetime, timezone
from typing import Any

from .entities import (
    Achievement,
    AchievementCategory,
    AchievementProgress,
    AchievementTier,
    UserAchievement,
)
from .repositories import (
    AchievementProgressRepository,
    AchievementRepository,
    UserAchievementRepository,
)
from .value_objects import (
    AchievementDescription,
    AchievementIcon,
    AchievementId,
    AchievementName,
    ExperienceReward,
    RequiredLevel,
    RequiredQuestCompletions,
    RequiredSkillLevel,
    UserAchievementId,
    UserId,
)


class AchievementService:
    """Service for achievement business operations"""

    def __init__(
        self,
        achievement_repository: AchievementRepository,
        user_achievement_repository: UserAchievementRepository,
        progress_repository: AchievementProgressRepository,
    ):
        self._achievement_repository = achievement_repository
        self._user_achievement_repository = user_achievement_repository
        self._progress_repository = progress_repository

    def create_achievement(
        self,
        name: str,
        description: str,
        tier: str,
        category: str,
        icon: str,
        experience_reward: int,
        required_level: int,
        required_skill_level: int | None = None,
        required_quest_completions: int = 0,
        is_hidden: bool = False,
        is_repeatable: bool = False,
    ) -> Achievement:
        """Create a new achievement with validation"""
        # Convert string enums to domain enums
        tier_enum = AchievementTier(tier)
        category_enum = AchievementCategory(category)

        # Create value objects with validation
        achievement_name = AchievementName(name)
        achievement_description = AchievementDescription(description)
        achievement_icon = AchievementIcon(icon)
        exp_reward = ExperienceReward(experience_reward)
        req_level = RequiredLevel(required_level)
        req_skill_level = (
            RequiredSkillLevel(required_skill_level) if required_skill_level else None
        )
        req_quest_completions = RequiredQuestCompletions(required_quest_completions)

        # Generate achievement ID (in real implementation, this would come from repository)
        achievement_id = AchievementId(1)  # Placeholder

        achievement = Achievement(
            achievement_id=achievement_id,
            name=achievement_name,
            description=achievement_description,
            tier=tier_enum,
            category=category_enum,
            icon=achievement_icon,
            experience_reward=exp_reward,
            required_level=req_level,
            required_skill_level=req_skill_level,
            required_quest_completions=req_quest_completions,
            is_hidden=is_hidden,
            is_repeatable=is_repeatable,
        )

        return self._achievement_repository.save(achievement)

    def unlock_achievement(
        self,
        user_id: UserId,
        achievement_id: AchievementId,
        notes: str = "",
        unlock_context: dict[str, Any] | None = None,
    ) -> tuple[UserAchievement, int]:
        """Unlock an achievement for a user and return experience gained"""
        # Check if achievement exists
        achievement = self._achievement_repository.get_by_id(achievement_id)
        if achievement is None:
            raise ValueError(f"Achievement {achievement_id.value} not found")

        # Check if user already has this achievement (unless repeatable)
        if not achievement.is_repeatable:
            if self._user_achievement_repository.has_achievement(
                user_id, achievement_id
            ):
                raise ValueError("User already has this achievement")

        # Generate user achievement ID (in real implementation, this would come from repository)
        user_achievement_id = UserAchievementId(1)  # Placeholder

        # Create user achievement
        user_achievement = UserAchievement(
            user_achievement_id=user_achievement_id,
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=datetime.now(timezone.utc),
            notes=notes,
            unlock_context=unlock_context or {},
        )

        # Save user achievement
        saved_achievement = self._user_achievement_repository.save(user_achievement)

        # Calculate experience reward
        experience_gained = achievement.calculate_final_experience_reward()

        return saved_achievement, experience_gained

    def check_and_unlock_eligible_achievements(
        self, user_id: UserId, user_stats: dict[str, Any]
    ) -> list[tuple[UserAchievement, int]]:
        """Check for eligible achievements and unlock them automatically"""
        unlocked_achievements = []

        # Get all achievements user doesn't have yet
        user_achievement_ids = {
            ua.achievement_id
            for ua in self._user_achievement_repository.get_user_achievements(user_id)
        }

        all_achievements = self._achievement_repository.get_all_achievements()
        eligible_achievements = [
            achievement
            for achievement in all_achievements
            if (
                achievement.achievement_id not in user_achievement_ids
                or achievement.is_repeatable
            )
            and achievement.check_eligibility(user_stats)
        ]

        # Unlock eligible achievements
        for achievement in eligible_achievements:
            try:
                user_achievement, experience = self.unlock_achievement(
                    user_id,
                    achievement.achievement_id,
                    notes="Auto-unlocked based on user progress",
                    unlock_context={"auto_unlock": True, "user_stats": user_stats},
                )
                unlocked_achievements.append((user_achievement, experience))
            except ValueError:
                # Skip if already unlocked or other validation error
                continue

        return unlocked_achievements

    def update_achievement_progress(
        self, user_id: UserId, user_stats: dict[str, Any]
    ) -> list[AchievementProgress]:
        """Update progress for all achievements for a user"""
        all_achievements = self._achievement_repository.get_all_achievements()
        progress_list = []

        for achievement in all_achievements:
            # Skip if user already has this achievement (unless repeatable)
            if not achievement.is_repeatable:
                if self._user_achievement_repository.has_achievement(
                    user_id, achievement.achievement_id
                ):
                    continue

            # Calculate progress
            progress_percentage = achievement.get_progress_percentage(user_stats)
            missing_requirements = achievement.get_missing_requirements(user_stats)
            is_eligible = achievement.check_eligibility(user_stats)

            # Get existing progress or create new
            existing_progress = self._progress_repository.get_progress_for_achievement(
                user_id, achievement.achievement_id
            )

            if existing_progress:
                existing_progress.update_progress(
                    progress_percentage, missing_requirements, is_eligible
                )
                progress = self._progress_repository.save(existing_progress)
            else:
                progress = AchievementProgress(
                    user_id=user_id,
                    achievement_id=achievement.achievement_id,
                    progress_percentage=progress_percentage,
                    last_updated=datetime.now(timezone.utc),
                    missing_requirements=missing_requirements,
                    is_eligible=is_eligible,
                )
                progress = self._progress_repository.save(progress)

            progress_list.append(progress)

        return progress_list

    def get_achievement_statistics(self, user_id: UserId) -> dict[str, Any]:
        """Get comprehensive achievement statistics for a user"""
        user_achievements = self._user_achievement_repository.get_user_achievements(
            user_id
        )
        all_achievements = self._achievement_repository.get_all_achievements()

        # Create achievement lookup dict to avoid N+1 queries
        achievement_lookup = {
            achievement.achievement_id: achievement for achievement in all_achievements
        }

        # Basic statistics
        total_achievements = len(all_achievements)
        unlocked_achievements = len(user_achievements)
        completion_percentage = (
            (unlocked_achievements / total_achievements * 100)
            if total_achievements > 0
            else 0
        )

        # Tier breakdown
        tier_stats = {tier.value: 0 for tier in AchievementTier}
        tier_totals = {tier.value: 0 for tier in AchievementTier}

        # Count total achievements by tier
        for achievement in all_achievements:
            tier_totals[achievement.tier.value] += 1

        # Count unlocked achievements by tier (using lookup dict)
        for user_achievement in user_achievements:
            if user_achievement.achievement_id in achievement_lookup:
                achievement = achievement_lookup[user_achievement.achievement_id]
                tier_stats[achievement.tier.value] += 1

        # Category breakdown
        category_stats = {category.value: 0 for category in AchievementCategory}
        category_totals = {category.value: 0 for category in AchievementCategory}

        # Count total achievements by category
        for achievement in all_achievements:
            category_totals[achievement.category.value] += 1

        # Count unlocked achievements by category (using lookup dict)
        for user_achievement in user_achievements:
            if user_achievement.achievement_id in achievement_lookup:
                achievement = achievement_lookup[user_achievement.achievement_id]
                category_stats[achievement.category.value] += 1

        # Recent achievements
        recent_achievements = self._user_achievement_repository.get_recent_achievements(
            user_id, 30
        )

        # Calculate total experience from achievements (using lookup dict)
        total_experience = 0
        for user_achievement in user_achievements:
            if user_achievement.achievement_id in achievement_lookup:
                achievement = achievement_lookup[user_achievement.achievement_id]
                total_experience += achievement.calculate_final_experience_reward()

        return {
            "total_achievements": total_achievements,
            "unlocked_achievements": unlocked_achievements,
            "completion_percentage": round(completion_percentage, 2),
            "tier_breakdown": {
                tier: {
                    "unlocked": tier_stats[tier],
                    "total": tier_totals[tier],
                    "percentage": round(
                        (tier_stats[tier] / tier_totals[tier] * 100)
                        if tier_totals[tier] > 0
                        else 0,
                        2,
                    ),
                }
                for tier in tier_stats.keys()
            },
            "category_breakdown": {
                category: {
                    "unlocked": category_stats[category],
                    "total": category_totals[category],
                    "percentage": round(
                        (category_stats[category] / category_totals[category] * 100)
                        if category_totals[category] > 0
                        else 0,
                        2,
                    ),
                }
                for category in category_stats.keys()
            },
            "recent_achievements_count": len(recent_achievements),
            "total_experience_from_achievements": total_experience,
            "average_unlock_rate_per_month": self._calculate_unlock_rate(
                user_achievements
            ),
        }

    def get_recommended_achievements(
        self, user_id: UserId, limit: int = 5
    ) -> list[Achievement]:
        """Get recommended achievements for a user based on progress"""
        progress_list = self._progress_repository.get_user_progress(user_id)

        # Filter and sort by progress percentage (closest to completion first)
        close_achievements = [
            progress
            for progress in progress_list
            if progress.is_close_to_completion(70.0) and not progress.is_eligible
        ]

        # Sort by progress percentage (descending)
        close_achievements.sort(
            key=lambda p: float(p.progress_percentage), reverse=True
        )

        # Get achievement details for the limited set
        limited_progress = close_achievements[:limit]
        if not limited_progress:
            return []

        # Load all achievements once and create lookup to avoid N+1 queries
        all_achievements = self._achievement_repository.get_all_achievements()
        achievement_lookup = {
            achievement.achievement_id: achievement for achievement in all_achievements
        }

        # Use lookup to get achievement details
        recommended = []
        for progress in limited_progress:
            if progress.achievement_id in achievement_lookup:
                achievement = achievement_lookup[progress.achievement_id]
                recommended.append(achievement)

        return recommended

    def _calculate_unlock_rate(self, user_achievements: list[UserAchievement]) -> float:
        """Calculate average achievement unlock rate per month"""
        if not user_achievements:
            return 0.0

        # Find earliest achievement
        earliest_unlock = min(ua.unlocked_at for ua in user_achievements)
        months_active = max(
            1, (datetime.now(timezone.utc) - earliest_unlock).days / 30.44
        )  # Average days per month

        return round(len(user_achievements) / months_active, 2)
