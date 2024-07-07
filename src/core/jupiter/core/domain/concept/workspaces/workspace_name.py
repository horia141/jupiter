"""The workspace name."""
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.value import hashable_value


@hashable_value
class WorkspaceName(EntityName):
    """The workspace name."""
