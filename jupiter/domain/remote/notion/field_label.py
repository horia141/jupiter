"""A field label for Notion."""
import uuid
from dataclasses import dataclass

from jupiter.domain.entity_name import EntityName
from jupiter.framework.base.timestamp import Timestamp


@dataclass(frozen=True)
class NotionFieldLabel:
    """A value for a Notion collection 'select' field label."""

    notion_link_uuid: uuid.UUID
    name: EntityName
    created_time: Timestamp
