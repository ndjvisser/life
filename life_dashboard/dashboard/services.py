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
        """
        Return a lazily-initialized singleton instance of DjangoUserRepository stored on the class.
        
        If no repository exists yet, one is created and assigned to the class attribute `_user_repo`. Returns the repository instance.
        """
        if cls._user_repo is None:
            cls._user_repo = DjangoUserRepository()
        return cls._user_repo

    @classmethod
    def get_profile_repository(cls):
        """
        Return the singleton DjangoUserProfileRepository instance, creating it lazily.
        
        This classmethod provides the shared profile repository used when constructing services. If the repository has not been initialized yet, it instantiates DjangoUserProfileRepository and caches it on the class.
        
        Returns:
            DjangoUserProfileRepository: The cached profile repository instance.
        """
        if cls._profile_repo is None:
            cls._profile_repo = DjangoUserProfileRepository()
        return cls._profile_repo

    @classmethod
    def get_user_service(cls):
        """
        Return a configured UserService instance.
        
        The returned UserService is constructed with the factory's user and profile repositories so callers receive a service wired with the shared repository instances.
        
        Returns:
            UserService: A UserService configured with the factory's user_repo and profile_repo.
        """
        return UserService(
            user_repo=cls.get_user_repository(),
            profile_repo=cls.get_profile_repository(),
        )

    @classmethod
    def get_authentication_service(cls):
        """
        Return a configured AuthenticationService using the factory's repositories.
        
        Produces an AuthenticationService instance wired with the ServiceFactory's
        shared user and profile repositories (lazily initialized).
        Returns:
            AuthenticationService: A ready-to-use authentication service instance.
        """
        return AuthenticationService(
            user_repo=cls.get_user_repository(),
            profile_repo=cls.get_profile_repository(),
        )

    @classmethod
    def get_onboarding_service(cls):
        """
        Return a configured OnboardingService instance.
        
        The returned service is constructed with the factory's shared user and profile repositories
        (obtained via ServiceFactory.get_user_repository and ServiceFactory.get_profile_repository),
        ensuring consistent dependency wiring across callers.
        
        Returns:
            OnboardingService: An OnboardingService configured with the factory repositories.
        """
        return OnboardingService(
            user_repo=cls.get_user_repository(),
            profile_repo=cls.get_profile_repository(),
        )


# Convenience functions for getting services
def get_user_service() -> UserService:
    """
    Return a configured UserService wired with the module's shared user and profile repositories.
    
    Returns:
        UserService: A UserService instance created by ServiceFactory.
    """
    return ServiceFactory.get_user_service()


def get_authentication_service() -> AuthenticationService:
    """
    Return a configured AuthenticationService instance wired with the module's shared repositories.
    
    The returned service is created by ServiceFactory and uses the factory's singleton-like
    user and profile repositories so callers receive a consistently configured AuthenticationService.
    
    Returns:
        AuthenticationService: An AuthenticationService ready for use.
    """
    return ServiceFactory.get_authentication_service()


def get_onboarding_service() -> OnboardingService:
    """
    Return a configured OnboardingService wired with the application's user and profile repositories.
    
    Returns:
        OnboardingService: An instance of OnboardingService created by ServiceFactory.
    """
    return ServiceFactory.get_onboarding_service()
