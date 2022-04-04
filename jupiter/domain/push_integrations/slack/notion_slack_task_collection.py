"""A Notion slack task collection."""
from dataclasses import dataclass

from jupiter.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionSlackTaskCollection(NotionTrunkEntity[SlackTaskCollection]):
    """A slack task collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: SlackTaskCollection) -> "NotionSlackTaskCollection":
        """Construct a new Notion row from a given entity."""
        return NotionSlackTaskCollection(notion_id=BAD_NOTION_ID, ref_id=entity.ref_id)
