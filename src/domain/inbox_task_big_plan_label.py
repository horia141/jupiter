"""A value for an inbox task big plan label."""
import uuid
from dataclasses import dataclass

from domain.entity_name import EntityName


@dataclass()
class InboxTaskBigPlanLabel:
    """A value for an inbox task big plan label."""
    notion_link_uuid: uuid.UUID
    name: EntityName
