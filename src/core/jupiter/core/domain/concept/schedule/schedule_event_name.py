"""The name of a schedule event."""

from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.value import hashable_value


@hashable_value
class ScheduleEventName(EntityName):
    """The name of a schedule event."""
