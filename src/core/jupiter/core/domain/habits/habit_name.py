"""The habit name."""
from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.framework.value import hashable_value


@hashable_value
class HabitName(EntityName):
    """The habit name."""
