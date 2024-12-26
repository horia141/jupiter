"""A domain-level context for calls that are made."""
from dataclasses import dataclass

from jupiter.core.domain.app import AppCore, AppShell
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.event import EventSource


@dataclass(frozen=True)
class DomainContext:
    """A domain-level context for calls that are made."""

    event_source: EventSource
    app_core: AppCore | None
    app_shell: AppShell | None
    action_timestamp: Timestamp

    @staticmethod
    def from_app(
        app_core: AppCore, app_shell: AppShell, action_timestamp: Timestamp
    ) -> "DomainContext":
        """Create a domain context from an app."""
        return DomainContext(
            event_source=EventSource.APP,
            app_core=app_core,
            app_shell=app_shell,
            action_timestamp=action_timestamp,
        )

    @staticmethod
    def from_sys(
        event_source: EventSource, action_timestamp: Timestamp
    ) -> "DomainContext":
        """Create a domain context from an event."""
        assert event_source != EventSource.APP
        return DomainContext(
            event_source=event_source,
            app_core=None,
            app_shell=None,
            action_timestamp=action_timestamp,
        )
