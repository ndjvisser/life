"""
Dashboard domain repository interfaces - abstract data access contracts.
"""
from abc import ABC, abstractmethod
from typing import Optional

from .entities import UserProfile


class UserProfileRepository(ABC):
    """Abstract repository for UserProfile persistence."""

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """
        Retrieve the UserProfile for the given user ID.
        
        Parameters:
            user_id (int): The ID of the user whose profile should be retrieved.
        
        Returns:
            Optional[UserProfile]: The user's profile if it exists, otherwise None.
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserProfile]:
        """
        Return the UserProfile matching the given username, or None if no profile exists.
        
        Lookup should match the provided username exactly; implementations may translate or normalise input (e.g., case) if appropriate.
        """
        pass

    @abstractmethod
    def save(self, profile: UserProfile) -> UserProfile:
        """
        Persist the given UserProfile and return the saved entity.
        
        If the profile is new or updated, the implementation must persist changes and return the persisted UserProfile instance (including any persistence-assigned fields, e.g., id).
        profile: UserProfile to create or update.
        
        Returns:
            UserProfile: The persisted UserProfile with current stored state.
        """
        pass

    @abstractmethod
    def create(self, profile: UserProfile) -> UserProfile:
        """
        Create and persist a new UserProfile.
        
        Parameters:
            profile (UserProfile): Domain UserProfile to create; required fields on the entity must be populated.
        
        Returns:
            UserProfile: The created UserProfile, typically with persistence-generated fields populated (e.g. id).
        """
        pass

    @abstractmethod
    def exists_by_user_id(self, user_id: int) -> bool:
        """
        Return True if a UserProfile exists for the given user ID, otherwise False.
        
        Parameters:
            user_id (int): The ID of the user to check for an associated profile.
        
        Returns:
            bool: True when a profile exists for `user_id`, False otherwise.
        """
        pass


class UserRepository(ABC):
    """Abstract repository for User management."""

    @abstractmethod
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ) -> int:
        """
        Create a new user and return the newly created user's ID.
        
        Returns:
            int: The ID of the newly created user.
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """
        Retrieve a user's data by their numeric ID.
        
        Returns a dictionary containing the user's fields (e.g., username, email, profile references) if a user with the given ID exists; otherwise returns None.
        
        Parameters:
            user_id (int): The unique identifier of the user to look up.
        
        Returns:
            Optional[dict]: A mapping of user attributes or None when no matching user is found.
        """
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """
        Retrieve a user's data by their username.
        
        Returns a dictionary containing the user's fields (e.g., id, username, email, first_name, last_name) if a matching user exists, otherwise None.
        """
        pass

    @abstractmethod
    def update_user(self, user_id: int, **kwargs) -> bool:
        """
        Update fields of an existing user.
        
        Parameters:
            user_id (int): ID of the user to update.
            **kwargs: User attributes to update (for example: `username`, `email`, `password`, `first_name`, `last_name`).
        
        Returns:
            bool: True if the update succeeded, False otherwise.
        """
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """
        Authenticate a user with the provided credentials and return their user ID if authentication succeeds.
        
        Authenticate using `username` (login identifier) and `password` (plain-text credential). Returns the authenticated user's numeric ID on success, or `None` if the credentials are invalid.
        """
        pass
