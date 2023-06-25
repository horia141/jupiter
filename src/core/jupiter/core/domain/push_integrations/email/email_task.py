"""An email task which needs to be converted into an inbox task."""
from dataclasses import dataclass

from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, LeafEntity
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class EmailTask(LeafEntity):
    """An email task which needs to be converted into an inbox task."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Update(Entity.Updated):
        """Updated event."""

    @dataclass
    class GenerateInboxTask(Entity.Updated):
        """Mark the generation of an inbox task associated with this email task event."""

    email_task_collection_ref_id: EntityId
    from_address: EmailAddress
    from_name: EmailUserName
    to_address: EmailAddress
    subject: str
    body: str
    generation_extra_info: PushGenerationExtraInfo
    has_generated_task: bool

    @staticmethod
    def new_email_task(
        email_task_collection_ref_id: EntityId,
        archived: bool,
        from_address: EmailAddress,
        from_name: EmailUserName,
        to_address: EmailAddress,
        subject: str,
        body: str,
        generation_extra_info: PushGenerationExtraInfo,
        source: EventSource,
        created_time: Timestamp,
    ) -> "EmailTask":
        """Create a Email task."""
        email_task = EmailTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[
                EmailTask.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            email_task_collection_ref_id=email_task_collection_ref_id,
            from_address=from_address,
            from_name=from_name,
            to_address=to_address,
            subject=subject,
            body=body,
            generation_extra_info=generation_extra_info,
            has_generated_task=False,
        )
        return email_task

    def update(
        self,
        from_address: UpdateAction[EmailAddress],
        from_name: UpdateAction[EmailUserName],
        to_address: UpdateAction[EmailAddress],
        subject: UpdateAction[str],
        body: UpdateAction[str],
        generation_extra_info: UpdateAction[PushGenerationExtraInfo],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "EmailTask":
        """Update email task."""
        return self._new_version(
            from_address=from_address.or_else(self.from_address),
            from_name=from_name.or_else(self.from_name),
            to_address=to_address.or_else(self.to_address),
            subject=subject.or_else(self.subject),
            body=body.or_else(self.body),
            generation_extra_info=generation_extra_info.or_else(
                self.generation_extra_info,
            ),
            new_event=EmailTask.Update.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def mark_as_used_for_generation(
        self,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "EmailTask":
        """Mark this task as used for generating an inbox task."""
        if self.has_generated_task:
            raise InputValidationError(
                f"Email task id={self.ref_id} already has an inbox task generated for it",
            )
        return self._new_version(
            has_generated_task=True,
            new_event=EmailTask.GenerateInboxTask.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.email_task_collection_ref_id

    @property
    def simple_name(self) -> EntityName:
        """A simple name for the task."""
        return EntityName(
            f"Respond to message from {self.from_name} <{self.from_address}> about {self.subject}",
        )
