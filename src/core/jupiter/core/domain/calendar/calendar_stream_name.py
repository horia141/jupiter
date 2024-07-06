"""The name of a calendar stream."""
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.value import hashable_value


@hashable_value
class CalendarStreamName(EntityName):
    """The name of a calendar stream."""
