"""
Journals domain value objects - immutable values with validation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EntryId:
    """Value object for journal entry IDs."""

    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Entry ID must be a non-empty string")
        if len(self.value) > 100:
            raise ValueError("Entry ID cannot exceed 100 characters")


@dataclass(frozen=True)
class EntryTitle:
    """Value object for journal entry titles."""

    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Entry title must be a non-empty string")
        if len(self.value) > 200:
            raise ValueError("Entry title cannot exceed 200 characters")


@dataclass(frozen=True)
class EntryContent:
    """Value object for journal entry content."""

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValueError("Entry content must be a string")
        if len(self.value) > 10000:
            raise ValueError("Entry content cannot exceed 10,000 characters")

    def word_count(self) -> int:
        """Return the word count of the content."""
        return len(self.value.split()) if self.value else 0

    def character_count(self) -> int:
        """Return the character count of the content."""
        return len(self.value)


@dataclass(frozen=True)
class MoodRating:
    """Value object for mood ratings (1-10 scale)."""

    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise ValueError("Mood rating must be an integer")
        if not 1 <= self.value <= 10:
            raise ValueError("Mood rating must be between 1 and 10")

    def is_positive(self) -> bool:
        """Return True if mood is positive (6 or higher)."""
        return self.value >= 6

    def is_negative(self) -> bool:
        """Return True if mood is negative (4 or lower)."""
        return self.value <= 4

    def is_neutral(self) -> bool:
        """Return True if mood is neutral (5)."""
        return self.value == 5


@dataclass(frozen=True)
class Tag:
    """Value object for journal entry tags."""

    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Tag must be a non-empty string")
        if len(self.value) > 50:
            raise ValueError("Tag cannot exceed 50 characters")
        if not self.value.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Tag must contain only alphanumeric characters, hyphens, and underscores"
            )

    def normalized(self) -> str:
        """Return the tag in normalized form (lowercase, trimmed)."""
        return self.value.lower().strip()


@dataclass(frozen=True)
class UserId:
    """Value object for user IDs."""

    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise ValueError("User ID must be an integer")
        if self.value <= 0:
            raise ValueError("User ID must be positive")
