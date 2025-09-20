"""
Dashboard API contracts - Pydantic models for request/response validation.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""

    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)

    @validator("username")
    def validate_username(cls, v):
        if not v.isalnum() and "_" not in v:
            raise ValueError(
                "Username must contain only letters, numbers, and underscores"
            )
        return v


class UserRegistrationResponse(BaseModel):
    """Response model for user registration."""

    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    success: bool = True
    message: str = "User registered successfully"


class LoginRequest(BaseModel):
    """Request model for user login."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Response model for user login."""

    user_id: Optional[int] = None
    username: Optional[str] = None
    success: bool
    message: str


class ProfileUpdateRequest(BaseModel):
    """Request model for profile updates."""

    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    bio: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=30)
    birth_date: Optional[date] = None


class ProfileResponse(BaseModel):
    """Response model for profile data."""

    user_id: int
    username: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    bio: str
    location: str
    birth_date: Optional[date]
    experience_points: int
    level: int
    experience_to_next_level: int
    level_progress_percentage: float
    created_at: datetime
    updated_at: datetime


class ExperienceAwardRequest(BaseModel):
    """Request model for awarding experience points."""

    points: int = Field(..., gt=0, le=10000)
    reason: Optional[str] = Field(None, max_length=200)


class ExperienceAwardResponse(BaseModel):
    """Response model for experience award."""

    user_id: int
    points_awarded: int
    new_experience_total: int
    new_level: int
    level_up_occurred: bool
    success: bool = True
    message: str = "Experience awarded successfully"


class OnboardingStateResponse(BaseModel):
    """Response model for onboarding state."""

    current_state: str
    next_step: Optional[str]
    progress_percentage: float
    is_complete: bool
    available_transitions: list[str]


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None
