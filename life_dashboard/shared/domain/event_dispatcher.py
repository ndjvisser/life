"""
Domain Event Dispatcher

Lightweight event dispatcher with version compatibility checking and
handler registration. Supports both synchronous and asynchronous event
processing.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps

from packaging import version

from .events import BaseEvent

logger = logging.getLogger(__name__)


@dataclass
class EventHandler:
    """Event handler registration information."""

    handler_func: Callable[[BaseEvent], None]
    event_type: type[BaseEvent]
    min_version: str
    max_version: str | None = None
    handler_name: str = ""

    def is_compatible(self, event_version: str) -> bool:
        """Check if handler is compatible with event version."""
        try:
            event_ver = version.parse(event_version)
            min_ver = version.parse(self.min_version)

            if event_ver < min_ver:
                return False

            if self.max_version:
                max_ver = version.parse(self.max_version)
                if event_ver > max_ver:
                    return False

            return True
        except Exception as e:
            logger.warning(f"Version compatibility check failed: {e}")
            return False


class EventDispatcher:
    """
    Lightweight in-process event dispatcher with version compatibility.

    Supports synchronous event handling for fast tests and immediate
    consistency while maintaining type safety and version compatibility.
    """

    def __init__(self):
        self._handlers: dict[type[BaseEvent], list[EventHandler]] = {}
        self._event_log: list[BaseEvent] = []
        self._enable_logging = True

    def register_handler(
        self,
        event_type: type[BaseEvent],
        handler_func: Callable[[BaseEvent], None],
        min_version: str = "1.0.0",
        max_version: str | None = None,
        handler_name: str = "",
    ) -> None:
        """Register an event handler for a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        handler = EventHandler(
            handler_func=handler_func,
            event_type=event_type,
            min_version=min_version,
            max_version=max_version,
            handler_name=handler_name
            or getattr(handler_func, "__name__", "anonymous_handler"),
        )

        self._handlers[event_type].append(handler)
        logger.info(
            f"Registered handler {handler.handler_name} for {event_type.__name__}"
        )

    def publish(self, event: BaseEvent) -> None:
        """
        Publish an event to all compatible handlers.

        Args:
            event: The domain event to publish
        """
        if self._enable_logging:
            self._event_log.append(event)

        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        logger.debug(f"Publishing {event_type.__name__} event {event.event_id}")

        compatible_handlers = []
        incompatible_handlers = []

        for handler in handlers:
            if handler.is_compatible(event.version):
                compatible_handlers.append(handler)
            else:
                incompatible_handlers.append(handler)

        # Log version compatibility issues
        for handler in incompatible_handlers:
            logger.warning(
                f"Handler {handler.handler_name} incompatible with "
                f"{event_type.__name__} v{event.version} "
                f"(requires v{handler.min_version}+)"
            )

        # Execute compatible handlers
        for handler in compatible_handlers:
            try:
                logger.debug(f"Executing handler {handler.handler_name}")
                handler.handler_func(event)
            except Exception as e:
                logger.error(
                    f"Error in handler {handler.handler_name} "
                    f"for event {event_type.__name__}: {e}",
                    exc_info=True,
                )
                # Continue processing other handlers

        logger.debug(
            f"Published {event_type.__name__} to {len(compatible_handlers)} handlers"
        )

    def get_event_log(self) -> list[BaseEvent]:
        """Get the event log for debugging and testing."""
        return self._event_log.copy()

    def clear_event_log(self) -> None:
        """Clear the event log."""
        self._event_log.clear()

    def enable_event_logging(self, enabled: bool = True) -> None:
        """Enable or disable event logging."""
        self._enable_logging = enabled

    def get_handlers(self, event_type: type[BaseEvent]) -> list[EventHandler]:
        """Get all handlers for a specific event type."""
        return self._handlers.get(event_type, []).copy()

    def unregister_handler(
        self, event_type: type[BaseEvent], handler_name: str
    ) -> bool:
        """Unregister a handler by name."""
        handlers = self._handlers.get(event_type, [])
        for i, handler in enumerate(handlers):
            if handler.handler_name == handler_name:
                del handlers[i]
                logger.info(
                    f"Unregistered handler {handler_name} for {event_type.__name__}"
                )
                return True
        return False

    def clear_handlers(self, event_type: type[BaseEvent] | None = None) -> None:
        """Clear all handlers for a specific event type or all handlers."""
        if event_type:
            self._handlers[event_type] = []
            logger.info(f"Cleared all handlers for {event_type.__name__}")
        else:
            self._handlers.clear()
            logger.info("Cleared all event handlers")


# Global event dispatcher instance
_event_dispatcher = EventDispatcher()


def get_event_dispatcher() -> EventDispatcher:
    """Get the global event dispatcher instance."""
    return _event_dispatcher


def publish_event(event: BaseEvent) -> None:
    """Convenience function to publish an event."""
    _event_dispatcher.publish(event)


def handles(
    event_type: type[BaseEvent],
    min_version: str = "1.0.0",
    max_version: str | None = None,
) -> Callable:
    """
    Decorator to register a function as an event handler.

    Args:
        event_type: The event type to handle
        min_version: Minimum compatible event version
        max_version: Maximum compatible event version (optional)

    Example:
        @handles(QuestCompleted, min_version="1.0.0")
        def award_quest_experience(event: QuestCompleted):
            # Handler implementation
            pass
    """

    def decorator(func: Callable[[BaseEvent], None]) -> Callable[[BaseEvent], None]:
        _event_dispatcher.register_handler(
            event_type=event_type,
            handler_func=func,
            min_version=min_version,
            max_version=max_version,
            handler_name=func.__name__,
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Privacy-aware event processing utilities


def is_consent_required(event: BaseEvent) -> bool:
    """
    Check if an event requires user consent for processing.

    Uses a domain-type marker attribute to identify privacy-sensitive events
    instead of relying on string name comparisons. Events that require consent
    should have privacy_sensitive = True as a class attribute.

    This is a placeholder for privacy-aware event processing.
    In a full implementation, this would check against user
    consent preferences and data processing purposes.
    """
    return getattr(type(event), "privacy_sensitive", False)


def validate_privacy_consent(event: BaseEvent, user_id: int) -> bool:
    """
    Validate that user has given consent for this type of event processing.

    This is a placeholder for privacy consent validation.
    In a full implementation, this would check the user's consent
    preferences from the privacy context.
    """
    # Placeholder implementation - always return True for now
    # In real implementation, would check user consent preferences
    return True


class PrivacyAwareEventDispatcher(EventDispatcher):
    """
    Event dispatcher with privacy-aware processing.

    Extends the base dispatcher to include consent validation
    for events that process personal data.
    """

    def publish(self, event: BaseEvent) -> None:
        """Publish event with privacy consent validation."""
        # Check if consent is required for this event type
        if is_consent_required(event):
            # Extract user_id from event (most events have this field)
            user_id = getattr(event, "user_id", None)
            if user_id and not validate_privacy_consent(event, user_id):
                logger.info(
                    f"Skipping {type(event).__name__} processing - "
                    f"user {user_id} has not consented"
                )
                return

        # Proceed with normal event processing
        super().publish(event)


# Optional privacy-aware dispatcher
def get_privacy_aware_dispatcher() -> PrivacyAwareEventDispatcher:
    """Get a privacy-aware event dispatcher instance."""
    return PrivacyAwareEventDispatcher()
