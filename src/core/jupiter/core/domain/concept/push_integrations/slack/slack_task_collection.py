"""A collection of slack tasks."""

from jupiter.core.domain.concept.push_integrations.slack.slack_task import SlackTask
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
    update_entity_action,
)


@entity
class SlackTaskCollection(TrunkEntity):
    """A collection of slack tasks."""

    push_integration_group: ParentLink
    generation_project_ref_id: EntityId

    slack_tasks = ContainsMany(SlackTask, slack_task_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_slack_task_collection(
        ctx: DomainContext,
        push_integration_group_ref_id: EntityId,
        generation_project_ref_id: EntityId,
    ) -> "SlackTaskCollection":
        """Create a slack task collection."""
        return SlackTaskCollection._create(
            ctx,
            push_integration_group=ParentLink(push_integration_group_ref_id),
            generation_project_ref_id=generation_project_ref_id,
        )

    @update_entity_action
    def change_generation_project(
        self,
        ctx: DomainContext,
        generation_project_ref_id: EntityId,
    ) -> "SlackTaskCollection":
        """Change the catch up project."""
        if self.generation_project_ref_id == generation_project_ref_id:
            return self
        return self._new_version(
            ctx,
            generation_project_ref_id=generation_project_ref_id,
        )
