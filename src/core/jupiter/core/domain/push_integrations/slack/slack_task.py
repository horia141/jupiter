"""A Slack task which needs to be converted into an inbox task."""
from typing import Optional

from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.domain.push_integrations.slack.slack_channel_name import (
    SlackChannelName,
)
from jupiter.core.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction


@entity
class SlackTask(LeafEntity):
    """A Slack task which needs to be converted into an inbox task."""

    slack_task_collection: ParentLink
    user: SlackUserName
    message: str
    generation_extra_info: PushGenerationExtraInfo
    has_generated_task: bool
    channel: Optional[SlackChannelName] = None

    generated_task = OwnsAtMostOne(
        InboxTask, source=InboxTaskSource.SLACK_TASK, slack_task_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_slack_task(
        ctx: DomainContext,
        slack_task_collection_ref_id: EntityId,
        user: SlackUserName,
        channel: Optional[SlackChannelName],
        message: str,
        generation_extra_info: PushGenerationExtraInfo,
    ) -> "SlackTask":
        """Create a Slack task."""
        return SlackTask._create(
            ctx,
            name=SlackTask.build_name(user, channel),
            slack_task_collection=ParentLink(slack_task_collection_ref_id),
            user=user,
            channel=channel,
            message=message,
            generation_extra_info=generation_extra_info,
            has_generated_task=False,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        user: UpdateAction[SlackUserName],
        channel: UpdateAction[Optional[SlackChannelName]],
        message: UpdateAction[str],
        generation_extra_info: UpdateAction[PushGenerationExtraInfo],
    ) -> "SlackTask":
        """Update slack task."""
        return self._new_version(
            ctx,
            user=user.or_else(self.user),
            channel=channel.or_else(self.channel),
            message=message.or_else(self.message),
            generation_extra_info=generation_extra_info.or_else(
                self.generation_extra_info,
            ),
        )

    @update_entity_action
    def mark_as_used_for_generation(
        self,
        ctx: DomainContext,
    ) -> "SlackTask":
        """Mark this task as used for generating an inbox task."""
        if self.has_generated_task:
            raise InputValidationError(
                f"Slack task id={self.ref_id} already has an inbox task generated for it",
            )
        return self._new_version(
            ctx,
            has_generated_task=True,
        )

    @staticmethod
    def build_name(user: SlackUserName, channel: SlackChannelName | None) -> EntityName:
        """Construct a name."""
        return EntityName(f"Respond to {user} on channel {channel}")
