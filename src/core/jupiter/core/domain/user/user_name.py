"""The user name for a user of Jupiter."""
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.value import hashable_value


@hashable_value
class UserName(EntityName):
    """The user name for a user of Jupiter."""
