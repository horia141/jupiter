"""The person name."""
from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.framework.value import hashable_value


@hashable_value
class PersonName(EntityName):
    """The person name."""
