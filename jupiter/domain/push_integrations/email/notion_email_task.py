"""A Notion email task."""
import re
import textwrap
from dataclasses import dataclass
from typing import Tuple, Optional

from jupiter.domain.email_address import EmailAddress
from jupiter.domain.push_integrations.email.email_task import EmailTask
from jupiter.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.domain.timezone import Timezone
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionLeafEntity, NotionLeafApplyToEntityResult
from jupiter.framework.update_action import UpdateAction


_FROM_INFO_RE = re.compile(r"From:\s+(.+)\s<(.+)>")
_GENERATION_EXTRA_INFO_RE = re.compile(
    r"(.*)---------- Forwarded message ---------", flags=re.MULTILINE | re.DOTALL
)


@dataclass(frozen=True)
class NotionEmailTask(NotionLeafEntity[EmailTask, None, "NotionEmailTask.InverseInfo"]):
    """A Email task on Notion side."""

    @dataclass(frozen=True)
    class InverseInfo:
        """Info when copying from the app to Notion."""

        timezone: Timezone

    subject: str
    to_address: str
    body: Optional[str]

    @staticmethod
    def new_notion_entity(entity: EmailTask, extra_info: None) -> "NotionEmailTask":
        """Construct a new Notion row from a given Email task."""
        return NotionEmailTask(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            archived=entity.archived,
            subject=entity.subject,
            to_address=str(entity.to_address),
            body=NotionEmailTask._body_from_entity(entity),
        )

    def new_entity(self, parent_ref_id: EntityId, extra_info: InverseInfo) -> EmailTask:
        """Create a new Email task from this."""
        if self.body is None:
            raise InputValidationError("Body should not be empty")

        clean_body = self.body.replace("—", "--").replace("’", "'")

        from_address, from_name = self._from_info_from_body(clean_body)
        generation_extra_info = self._generation_extra_info_from_body(
            extra_info.timezone, clean_body
        )
        return EmailTask.new_email_task(
            email_task_collection_ref_id=parent_ref_id,
            archived=self.archived,
            from_address=from_address,
            from_name=from_name,
            to_address=EmailAddress.from_raw(self.to_address),
            subject=self.subject,
            body=clean_body,
            generation_extra_info=generation_extra_info,
            source=EventSource.NOTION,
            created_time=self.last_edited_time,
        )

    def apply_to_entity(
        self, entity: EmailTask, extra_info: InverseInfo
    ) -> NotionLeafApplyToEntityResult[EmailTask]:
        """Apply to an already existing Email task."""
        if self.body is None:
            raise InputValidationError("Body should not be empty")

        clean_body = self.body.replace("—", "--").replace("’", "'")

        from_address, from_name = self._from_info_from_body(clean_body)
        generation_extra_info = self._generation_extra_info_from_body(
            extra_info.timezone, clean_body
        )

        new_entity = entity.update(
            from_address=UpdateAction.change_to(from_address),
            from_name=UpdateAction.change_to(from_name),
            to_address=UpdateAction.change_to(EmailAddress.from_raw(self.to_address)),
            subject=UpdateAction.change_to(self.subject),
            body=UpdateAction.change_to(clean_body),
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
        return f"Email message to {self.to_address} about {self.subject}"

    @staticmethod
    def _body_from_entity(entity: EmailTask) -> str:
        return textwrap.dedent(
            f"""
            {entity.generation_extra_info.to_raw_message_data()}
            ---------- Forwarded message ---------
            From: {entity.from_name} <{entity.from_address}>
            To: {entity.to_address}
            Subject: {entity.subject}

            {entity.body}
        """
        ).strip()

    @staticmethod
    def _from_info_from_body(body: str) -> Tuple[EmailAddress, EmailUserName]:
        match = _FROM_INFO_RE.search(body)
        if match is None:
            raise InputValidationError("Email does not have proper from info")

        from_address = EmailAddress.from_raw(match.group(2))
        from_name = EmailUserName.from_raw(match.group(1))

        return from_address, from_name

    @staticmethod
    def _generation_extra_info_from_body(
        timezone: Timezone, body: str
    ) -> PushGenerationExtraInfo:
        match = _GENERATION_EXTRA_INFO_RE.match(body)
        if match is None:
            raise InputValidationError(
                "Email does not have proper generation extra info"
            )

        generation_extra_info = PushGenerationExtraInfo.from_raw_message_data(
            timezone, match.group(1)
        )

        return generation_extra_info
