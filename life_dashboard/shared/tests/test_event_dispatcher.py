"""
Unit tests for the event dispatcher system.

Tests event handler registration, version compatibility checking,
event publishing, and privacy-aware processing.
"""

import logging
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from life_dashboard.shared.domain.event_dispatcher import (
    EventDispatcher,
    EventHandler,
    PrivacyAwareEventDispatcher,
    get_event_dispatcher,
    handles,
    is_consent_required,
    publish_event,
    validate_privacy_consent,
)
from life_dashboard.shared.domain.events import (
    BaseEvent,
    ExperienceAwarded,
    QuestCompleted,
)


class TestEventHandler:
    """Test the EventHandler dataclass."""

    def test_handler_creation(self):
        """Test EventHandler creation with required fields."""
        mock_func = Mock()
        handler = EventHandler(
            handler_func=mock_func,
            event_type=QuestCompleted,
            min_version="1.0.0",
            handler_name="test_handler",
        )

        assert handler.handler_func == mock_func
        assert handler.event_type == QuestCompleted
        assert handler.min_version == "1.0.0"
        assert handler.max_version is None
        assert handler.handler_name == "test_handler"

    def test_version_compatibility_exact_match(self):
        """Test version compatibility with exact version match."""
        handler = EventHandler(
            handler_func=Mock(), event_type=QuestCompleted, min_version="1.0.0"
        )

        assert handler.is_compatible("1.0.0") is True

    def test_version_compatibility_newer_version(self):
        """Test version compatibility with newer event version."""
        handler = EventHandler(
            handler_func=Mock(), event_type=QuestCompleted, min_version="1.0.0"
        )

        assert handler.is_compatible("1.1.0") is True
        assert handler.is_compatible("2.0.0") is True

    def test_version_compatibility_older_version(self):
        """Test version compatibility with older event version."""
        handler = EventHandler(
            handler_func=Mock(), event_type=QuestCompleted, min_version="1.1.0"
        )

        assert handler.is_compatible("1.0.0") is False

    def test_version_compatibility_with_max_version(self):
        """Test version compatibility with max version constraint."""
        handler = EventHandler(
            handler_func=Mock(),
            event_type=QuestCompleted,
            min_version="1.0.0",
            max_version="2.0.0",
        )

        assert handler.is_compatible("1.0.0") is True
        assert handler.is_compatible("1.5.0") is True
        assert handler.is_compatible("2.0.0") is True
        assert handler.is_compatible("2.1.0") is False

    def test_version_compatibility_invalid_version(self):
        """Test version compatibility with invalid version string."""
        handler = EventHandler(
            handler_func=Mock(), event_type=QuestCompleted, min_version="1.0.0"
        )

        # Should return False for invalid versions
        assert handler.is_compatible("invalid") is False
        assert handler.is_compatible("") is False


class TestEventDispatcher:
    """Test the EventDispatcher class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dispatcher = EventDispatcher()
        self.mock_handler = Mock()

    def test_dispatcher_initialization(self):
        """Test dispatcher initializes with empty state."""
        dispatcher = EventDispatcher()

        assert len(dispatcher._handlers) == 0
        assert len(dispatcher._event_log) == 0
        assert dispatcher._enable_logging is True

    def test_register_handler(self):
        """Test handler registration."""
        self.dispatcher.register_handler(
            event_type=QuestCompleted,
            handler_func=self.mock_handler,
            min_version="1.0.0",
            handler_name="test_handler",
        )

        handlers = self.dispatcher.get_handlers(QuestCompleted)
        assert len(handlers) == 1
        assert handlers[0].handler_func == self.mock_handler
        assert handlers[0].min_version == "1.0.0"
        assert handlers[0].handler_name == "test_handler"

    def test_register_multiple_handlers(self):
        """Test registering multiple handlers for same event type."""
        handler1 = Mock()
        handler2 = Mock()

        self.dispatcher.register_handler(
            QuestCompleted, handler1, handler_name="handler1"
        )
        self.dispatcher.register_handler(
            QuestCompleted, handler2, handler_name="handler2"
        )

        handlers = self.dispatcher.get_handlers(QuestCompleted)
        assert len(handlers) == 2

    def test_publish_event_calls_compatible_handlers(self):
        """Test that publishing an event calls compatible handlers."""
        self.dispatcher.register_handler(
            event_type=QuestCompleted,
            handler_func=self.mock_handler,
            min_version="1.0.0",
        )

        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
        )

        self.dispatcher.publish(event)

        self.mock_handler.assert_called_once_with(event)

    def test_publish_event_skips_incompatible_handlers(self):
        """Test that incompatible handlers are not called."""
        self.dispatcher.register_handler(
            event_type=QuestCompleted,
            handler_func=self.mock_handler,
            min_version="2.0.0",  # Incompatible with v1.0.0 event
        )

        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
            version="1.0.0",
        )

        self.dispatcher.publish(event)

        self.mock_handler.assert_not_called()

    def test_publish_event_logs_event(self):
        """Test that published events are logged."""
        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
        )

        self.dispatcher.publish(event)

        event_log = self.dispatcher.get_event_log()
        assert len(event_log) == 1
        assert event_log[0] == event

    def test_publish_event_handles_handler_exceptions(self):
        """Test that handler exceptions don't stop other handlers."""
        failing_handler = Mock(side_effect=Exception("Handler error"))
        working_handler = Mock()

        self.dispatcher.register_handler(
            QuestCompleted, failing_handler, handler_name="failing"
        )
        self.dispatcher.register_handler(
            QuestCompleted, working_handler, handler_name="working"
        )

        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
        )

        # Should not raise exception
        self.dispatcher.publish(event)

        # Both handlers should have been called
        failing_handler.assert_called_once_with(event)
        working_handler.assert_called_once_with(event)

    def test_clear_event_log(self):
        """Test clearing the event log."""
        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
        )

        self.dispatcher.publish(event)
        assert len(self.dispatcher.get_event_log()) == 1

        self.dispatcher.clear_event_log()
        assert len(self.dispatcher.get_event_log()) == 0

    def test_disable_event_logging(self):
        """Test disabling event logging."""
        self.dispatcher.enable_event_logging(False)

        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
        )

        self.dispatcher.publish(event)
        assert len(self.dispatcher.get_event_log()) == 0

    def test_unregister_handler(self):
        """Test unregistering a handler."""
        self.dispatcher.register_handler(
            QuestCompleted, self.mock_handler, handler_name="test_handler"
        )

        assert len(self.dispatcher.get_handlers(QuestCompleted)) == 1

        result = self.dispatcher.unregister_handler(QuestCompleted, "test_handler")
        assert result is True
        assert len(self.dispatcher.get_handlers(QuestCompleted)) == 0

    def test_unregister_nonexistent_handler(self):
        """Test unregistering a handler that doesn't exist."""
        result = self.dispatcher.unregister_handler(QuestCompleted, "nonexistent")
        assert result is False

    def test_clear_handlers(self):
        """Test clearing all handlers for an event type."""
        self.dispatcher.register_handler(
            QuestCompleted, Mock(), handler_name="handler1"
        )
        self.dispatcher.register_handler(
            QuestCompleted, Mock(), handler_name="handler2"
        )
        self.dispatcher.register_handler(
            ExperienceAwarded, Mock(), handler_name="handler3"
        )

        assert len(self.dispatcher.get_handlers(QuestCompleted)) == 2
        assert len(self.dispatcher.get_handlers(ExperienceAwarded)) == 1

        self.dispatcher.clear_handlers(QuestCompleted)

        assert len(self.dispatcher.get_handlers(QuestCompleted)) == 0
        assert len(self.dispatcher.get_handlers(ExperienceAwarded)) == 1

    def test_clear_all_handlers(self):
        """Test clearing all handlers."""
        self.dispatcher.register_handler(
            QuestCompleted, Mock(), handler_name="handler1"
        )
        self.dispatcher.register_handler(
            ExperienceAwarded, Mock(), handler_name="handler2"
        )

        self.dispatcher.clear_handlers()

        assert len(self.dispatcher.get_handlers(QuestCompleted)) == 0
        assert len(self.dispatcher.get_handlers(ExperienceAwarded)) == 0


class TestGlobalDispatcher:
    """Test global dispatcher functions."""

    def test_get_event_dispatcher(self):
        """Test getting the global event dispatcher."""
        dispatcher = get_event_dispatcher()
        assert isinstance(dispatcher, EventDispatcher)

        # Should return the same instance
        dispatcher2 = get_event_dispatcher()
        assert dispatcher is dispatcher2

    def test_publish_event_function(self):
        """Test the global publish_event function."""
        # Clear any existing handlers
        get_event_dispatcher().clear_handlers()

        mock_handler = Mock()
        get_event_dispatcher().register_handler(
            QuestCompleted, mock_handler, handler_name="test"
        )

        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
        )

        publish_event(event)

        mock_handler.assert_called_once_with(event)


class TestHandlesDecorator:
    """Test the @handles decorator."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear global dispatcher
        get_event_dispatcher().clear_handlers()

    def test_handles_decorator_registers_handler(self):
        """Test that @handles decorator registers the handler."""

        @handles(QuestCompleted, min_version="1.0.0")
        def test_handler(event: QuestCompleted):
            pass

        handlers = get_event_dispatcher().get_handlers(QuestCompleted)
        assert len(handlers) == 1
        assert handlers[0].handler_name == "test_handler"
        assert handlers[0].min_version == "1.0.0"

    def test_handles_decorator_with_version_constraints(self):
        """Test @handles decorator with version constraints."""

        @handles(QuestCompleted, min_version="1.0.0", max_version="2.0.0")
        def test_handler(event: QuestCompleted):
            pass

        handlers = get_event_dispatcher().get_handlers(QuestCompleted)
        assert len(handlers) == 1
        assert handlers[0].min_version == "1.0.0"
        assert handlers[0].max_version == "2.0.0"

    def test_handles_decorator_preserves_function(self):
        """Test that @handles decorator preserves the original function."""

        @handles(QuestCompleted)
        def test_handler(event: QuestCompleted):
            return "test_result"

        result = test_handler(Mock())
        assert result == "test_result"


class TestPrivacyAwareDispatcher:
    """Test privacy-aware event processing."""

    def test_is_consent_required(self):
        """Test consent requirement detection."""

        # Create a privacy-sensitive event class
        class PrivacySensitiveEvent(BaseEvent):
            privacy_sensitive = True

        # Events that require consent
        consent_event = PrivacySensitiveEvent()
        assert is_consent_required(consent_event) is True

        # Events that don't require consent
        no_consent_event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
        )
        assert is_consent_required(no_consent_event) is False

    def test_validate_privacy_consent(self):
        """Test privacy consent validation."""
        event = BaseEvent()
        # Placeholder implementation always returns True
        assert validate_privacy_consent(event, 123) is True

    def test_privacy_aware_dispatcher_processes_non_consent_events(self):
        """Test that non-consent events are processed normally."""
        dispatcher = PrivacyAwareEventDispatcher()
        mock_handler = Mock()

        dispatcher.register_handler(QuestCompleted, mock_handler)

        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
        )

        dispatcher.publish(event)

        mock_handler.assert_called_once_with(event)

    @patch("life_dashboard.shared.domain.event_dispatcher.is_consent_required")
    @patch("life_dashboard.shared.domain.event_dispatcher.validate_privacy_consent")
    def test_privacy_aware_dispatcher_skips_non_consented_events(
        self, mock_validate_consent, mock_is_consent_required
    ):
        """Test that events without consent are skipped."""
        mock_is_consent_required.return_value = True
        mock_validate_consent.return_value = False

        dispatcher = PrivacyAwareEventDispatcher()
        mock_handler = Mock()

        dispatcher.register_handler(QuestCompleted, mock_handler)

        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=datetime.now(timezone.utc),
            auto_completed=False,
        )

        dispatcher.publish(event)

        # Handler should not be called
        mock_handler.assert_not_called()

        # Consent validation should have been called
        mock_validate_consent.assert_called_once_with(event, 123)

    def test_privacy_aware_dispatcher_missing_user_id(self, caplog):
        """Test that events missing user_id are skipped with clear logging."""

        class MissingUserEvent(BaseEvent):
            privacy_sensitive = True

        dispatcher = PrivacyAwareEventDispatcher()
        mock_handler = Mock()
        dispatcher.register_handler(MissingUserEvent, mock_handler)

        event = MissingUserEvent()

        with caplog.at_level(logging.ERROR):
            dispatcher.publish(event)

        mock_handler.assert_not_called()
        assert "missing user_id" in caplog.text
