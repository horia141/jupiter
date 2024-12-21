"""The name of a schedule stream."""
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.value import hashable_value


@hashable_value
class ScheduleStreamName(EntityName):
    """The name of a schedule stream."""
