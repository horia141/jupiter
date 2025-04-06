"""An email task which needs to be converted into an inbox task."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.push_integrations.email.email_user_name import (
    EmailUserName,
)
from jupiter.core.domain.concept.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.domain.core.email_address import EmailAddress
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
class EmailTask(LeafEntity):
    """An email task which needs to be converted into an inbox task."""

    email_task_collection: ParentLink
    from_address: EmailAddress
    from_name: EmailUserName
    to_address: EmailAddress
    subject: str
    body: str
    generation_extra_info: PushGenerationExtraInfo
    has_generated_task: bool

    generated_task = OwnsAtMostOne(
        InboxTask, source=InboxTaskSource.EMAIL_TASK, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_email_task(
        ctx: DomainContext,
        email_task_collection_ref_id: EntityId,
        from_address: EmailAddress,
        from_name: EmailUserName,
        to_address: EmailAddress,
        subject: str,
        body: str,
        generation_extra_info: PushGenerationExtraInfo,
    ) -> "EmailTask":
        """Create a Email task."""
        return EmailTask._create(
            ctx,
            name=EmailTask.build_name(from_address, from_name, subject),
            email_task_collection=ParentLink(email_task_collection_ref_id),
            from_address=from_address,
            from_name=from_name,
            to_address=to_address,
            subject=subject,
            body=body,
            generation_extra_info=generation_extra_info,
            has_generated_task=False,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        from_address: UpdateAction[EmailAddress],
        from_name: UpdateAction[EmailUserName],
        to_address: UpdateAction[EmailAddress],
        subject: UpdateAction[str],
        body: UpdateAction[str],
        generation_extra_info: UpdateAction[PushGenerationExtraInfo],
    ) -> "EmailTask":
        """Update email task."""
        return self._new_version(
            ctx,
            from_address=from_address.or_else(self.from_address),
            from_name=from_name.or_else(self.from_name),
            to_address=to_address.or_else(self.to_address),
            subject=subject.or_else(self.subject),
            body=body.or_else(self.body),
            generation_extra_info=generation_extra_info.or_else(
                self.generation_extra_info,
            ),
        )

    @update_entity_action
    def mark_as_used_for_generation(
        self,
        ctx: DomainContext,
    ) -> "EmailTask":
        """Mark this task as used for generating an inbox task."""
        if self.has_generated_task:
            raise InputValidationError(
                f"Email task id={self.ref_id} already has an inbox task generated for it",
            )
        return self._new_version(
            ctx,
            has_generated_task=True,
        )

    @staticmethod
    def build_name(
        from_address: EmailAddress, from_name: EmailUserName, subject: str
    ) -> EntityName:
        """Construct the name for this task."""
        return EntityName(
            f"Respond to message from {from_name} <{from_address}> about {subject}",
        )
