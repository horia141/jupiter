"""A Slack task which needs to be converted into an inbox task."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.entity_name import EntityName
from jupiter.domain.push_integrations.push_generation_extra_info import PushGenerationExtraInfo
from jupiter.domain.push_integrations.slack.slack_channel_name import SlackChannelName
from jupiter.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.entity import LeafEntity, Entity, FIRST_VERSION
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class SlackTask(LeafEntity):
    """A Slack task which needs to be converted into an inbox task."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Update(Entity.Updated):
        """Updated event."""

    @dataclass(frozen=True)
    class GenerateInboxTask(Entity.Updated):
        """Mark the generation of an inbox task associated with this Slack task event."""

    slack_task_collection_ref_id: EntityId
    user: SlackUserName
    channel: Optional[SlackChannelName]
    message: str
    generation_extra_info: PushGenerationExtraInfo
    has_generated_task: bool

    @staticmethod
    def new_slack_task(
            slack_task_collection_ref_id: EntityId, user: SlackUserName, channel: Optional[SlackChannelName],
            message: str, generation_extra_info: PushGenerationExtraInfo, source: EventSource,
            created_time: Timestamp) -> 'SlackTask':
        """Create a Slack task."""
        slack_task = SlackTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[SlackTask.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            slack_task_collection_ref_id=slack_task_collection_ref_id,
            user=user,
            channel=channel,
            message=message,
            generation_extra_info=generation_extra_info,
            has_generated_task=False)
        return slack_task

    def update(
            self, user: UpdateAction[SlackUserName], channel: UpdateAction[Optional[SlackChannelName]],
            message: UpdateAction[str], generation_extra_info: UpdateAction[PushGenerationExtraInfo],
            source: EventSource, modification_time: Timestamp) -> 'SlackTask':
        """Update slack task."""
        return self._new_version(
            user=user.or_else(self.user),
            channel=channel.or_else(self.channel),
            message=message.or_else(self.message),
            generation_extra_info=generation_extra_info.or_else(self.generation_extra_info),
            new_event=SlackTask.Update.make_event_from_frame_args(source, self.version, modification_time))

    def mark_as_used_for_generation(self, source: EventSource, modification_time: Timestamp) -> 'SlackTask':
        """Mark this task as used for generating an inbox task."""
        if self.has_generated_task:
            raise InputValidationError(f"Slack task id={self.ref_id} already has an inbox task generated for it")
        return self._new_version(
            has_generated_task=True,
            new_event=SlackTask.GenerateInboxTask.make_event_from_frame_args(source, self.version, modification_time))

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.slack_task_collection_ref_id

    @property
    def simple_name(self) -> EntityName:
        """A simple name for the task."""
        return EntityName(f"Respond to {self.user} on channel {self.channel}")
