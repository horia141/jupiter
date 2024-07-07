"""The name of an inbox task."""
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.value import hashable_value


@hashable_value
class InboxTaskName(EntityName):
    """The name of an inbox task."""
