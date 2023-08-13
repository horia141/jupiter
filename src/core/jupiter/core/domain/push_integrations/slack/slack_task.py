"""A Slack task which needs to be converted into an inbox task."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.domain.push_integrations.slack.slack_channel_name import (
    SlackChannelName,
)
from jupiter.core.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, LeafEntity
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class SlackTask(LeafEntity):
    """A Slack task which needs to be converted into an inbox task."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Update(Entity.Updated):
        """Updated event."""

    @dataclass
    class GenerateInboxTask(Entity.Updated):
        """Mark the generation of an inbox task associated with this Slack task event."""

    slack_task_collection_ref_id: EntityId
    user: SlackUserName
    message: str
    generation_extra_info: PushGenerationExtraInfo
    has_generated_task: bool
    channel: Optional[SlackChannelName] = None

    @staticmethod
    def new_slack_task(
        slack_task_collection_ref_id: EntityId,
        archived: bool,
        user: SlackUserName,
        channel: Optional[SlackChannelName],
        message: str,
        generation_extra_info: PushGenerationExtraInfo,
        source: EventSource,
        created_time: Timestamp,
    ) -> "SlackTask":
        """Create a Slack task."""
        slack_task = SlackTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[
                SlackTask.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            name=SlackTask.build_name(user, channel),
            slack_task_collection_ref_id=slack_task_collection_ref_id,
            user=user,
            channel=channel,
            message=message,
            generation_extra_info=generation_extra_info,
            has_generated_task=False,
        )
        return slack_task

    def update(
        self,
        user: UpdateAction[SlackUserName],
        channel: UpdateAction[Optional[SlackChannelName]],
        message: UpdateAction[str],
        generation_extra_info: UpdateAction[PushGenerationExtraInfo],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "SlackTask":
        """Update slack task."""
        return self._new_version(
            user=user.or_else(self.user),
            channel=channel.or_else(self.channel),
            message=message.or_else(self.message),
            generation_extra_info=generation_extra_info.or_else(
                self.generation_extra_info,
            ),
            new_event=SlackTask.Update.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def mark_as_used_for_generation(
        self,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "SlackTask":
        """Mark this task as used for generating an inbox task."""
        if self.has_generated_task:
            raise InputValidationError(
                f"Slack task id={self.ref_id} already has an inbox task generated for it",
            )
        return self._new_version(
            has_generated_task=True,
            new_event=SlackTask.GenerateInboxTask.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.slack_task_collection_ref_id

    @staticmethod
    def build_name(user: SlackUserName, channel: SlackChannelName | None) -> EntityName:
        """Construct a name."""
        return EntityName(f"Respond to {user} on channel {channel}")
