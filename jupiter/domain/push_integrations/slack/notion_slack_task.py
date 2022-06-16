"""A Notion slack task."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.domain.push_integrations.slack.slack_channel_name import SlackChannelName
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.domain.timezone import Timezone
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionLeafEntity, NotionLeafApplyToEntityResult
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionSlackTask(NotionLeafEntity[SlackTask, None, "NotionSlackTask.InverseInfo"]):
    """A Slack task on Notion side."""

    @dataclass(frozen=True)
    class InverseInfo:
        """Info when copying from the app to Notion."""

        timezone: Timezone

    user: str
    channel: Optional[str]
    message: str
    generation_extra_info: Optional[str]

    @staticmethod
    def new_notion_entity(entity: SlackTask, extra_info: None) -> "NotionSlackTask":
        """Construct a new Notion row from a given Slack task."""
        return NotionSlackTask(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            archived=entity.archived,
            user=str(entity.user),
            channel=str(entity.channel) if entity.channel else None,
            message=entity.message,
            generation_extra_info=entity.generation_extra_info.to_raw_message_data(),
        )

    def new_entity(self, parent_ref_id: EntityId, extra_info: InverseInfo) -> SlackTask:
        """Create a new Slack task from this."""
        user = SlackUserName.from_raw(self.user)
        channel = SlackChannelName.from_raw(self.channel) if self.channel else None
        message = self.message
        generation_extra_info = PushGenerationExtraInfo.from_raw_message_data(
            extra_info.timezone, self.generation_extra_info
        )
        return SlackTask.new_slack_task(
            slack_task_collection_ref_id=parent_ref_id,
            archived=self.archived,
            user=user,
            channel=channel,
            message=message,
            generation_extra_info=generation_extra_info,
            source=EventSource.NOTION,
            created_time=self.last_edited_time,
        )

    def apply_to_entity(
        self, entity: SlackTask, extra_info: InverseInfo
    ) -> NotionLeafApplyToEntityResult[SlackTask]:
        """Apply to an already existing Slack task."""
        user = SlackUserName.from_raw(self.user)
        channel = SlackChannelName.from_raw(self.channel) if self.channel else None
        message = self.message
        generation_extra_info = PushGenerationExtraInfo.from_raw_message_data(
            extra_info.timezone, self.generation_extra_info
        )
        new_entity = entity.update(
            user=UpdateAction.change_to(user),
            channel=UpdateAction.change_to(channel),
            message=UpdateAction.change_to(message),
            generation_extra_info=UpdateAction.change_to(generation_extra_info),
            source=EventSource.NOTION,
            modification_time=self.last_edited_time,
        )

        new_entity = new_entity.change_archived(
            archived=self.archived,
            source=EventSource.NOTION,
            archived_time=self.last_edited_time,
        )
        return NotionLeafApplyToEntityResult(new_entity, False)

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        if self.channel:
            return f"Slack message from {self.user} on {self.channel}"
        else:
            return f"Direct message from {self.user}"
