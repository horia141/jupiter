"""A domain-level context for calls that are made."""
from dataclasses import dataclass

from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.event import EventSource


@dataclass(frozen=True)
class DomainContext:
    """A domain-level context for calls that are made."""

    event_source: EventSource
    action_timestamp: Timestamp
