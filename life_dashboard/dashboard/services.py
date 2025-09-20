"""
Dashboard service factory - dependency injection and service wiring.
"""
from .application.services import AuthenticationService, OnboardingService, UserService
from .infrastructure.repositories import (
    DjangoUserProfileRepository,
    DjangoUserRepository,
)


class ServiceFactory:
    """Factory for creating configured service instances."""

    _user_repo = None
    _profile_repo = None

    @classmethod
    def get_user_repository(cls):
        """Get or create user repository instance."""
        if cls._user_repo is None:
            cls._user_repo = DjangoUserRepository()
        return cls._user_repo

    @classmethod
    def get_profile_repository(cls):
        """Get or create profile repository instance."""
        if cls._profile_repo is None:
            cls._profile_repo = DjangoUserProfileRepository()
        return cls._profile_repo

    @classmethod
    def get_user_service(cls):
        """Get configured UserService instance."""
        return UserService(
            user_repo=cls.get_user_repository(),
            profile_repo=cls.get_profile_repository(),
        )

    @classmethod
    def get_authentication_service(cls):
        """Get configured AuthenticationService instance."""
        return AuthenticationService(
            user_repo=cls.get_user_repository(),
            profile_repo=cls.get_profile_repository(),
        )

    @classmethod
    def get_onboarding_service(cls):
        """Get configured OnboardingService instance."""
        return OnboardingService(
            user_repo=cls.get_user_repository(),
            profile_repo=cls.get_profile_repository(),
        )


# Convenience functions for getting services
def get_user_service() -> UserService:
    """Get UserService instance."""
    return ServiceFactory.get_user_service()


def get_authentication_service() -> AuthenticationService:
    """Get AuthenticationService instance."""
    return ServiceFactory.get_authentication_service()


def get_onboarding_service() -> OnboardingService:
    """Get OnboardingService instance."""
    return ServiceFactory.get_onboarding_service()
