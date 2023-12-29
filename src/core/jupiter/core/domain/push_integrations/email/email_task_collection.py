"""A collection of email tasks."""

from jupiter.core.domain.push_integrations.email.email_task import EmailTask
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
class EmailTaskCollection(TrunkEntity):
    """A collection of email tasks."""

    push_integration_group: ParentLink
    generation_project_ref_id: EntityId

    email_tasks = ContainsMany(EmailTask, email_task_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_email_task_collection(
        ctx: DomainContext,
        push_integration_group_ref_id: EntityId,
        generation_project_ref_id: EntityId,
    ) -> "EmailTaskCollection":
        """Create a email task collection."""
        return EmailTaskCollection._create(
            ctx,
            push_integration_group=ParentLink(push_integration_group_ref_id),
            generation_project_ref_id=generation_project_ref_id,
        )

    @update_entity_action
    def change_generation_project(
        self,
        ctx: DomainContext,
        generation_project_ref_id: EntityId,
    ) -> "EmailTaskCollection":
        """Change the generation project."""
        if self.generation_project_ref_id == generation_project_ref_id:
            return self
        return self._new_version(
            ctx,
            generation_project_ref_id=generation_project_ref_id,
        )
