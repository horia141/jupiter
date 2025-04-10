"""An inbox task."""

import abc
import textwrap
from collections.abc import Iterable
from typing import ClassVar

from jupiter.core.domain.concept.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.concept.push_integrations.email.email_user_name import (
    EmailUserName,
)
from jupiter.core.domain.concept.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.domain.concept.push_integrations.slack.slack_channel_name import (
    SlackChannelName,
)
from jupiter.core.domain.concept.push_integrations.slack.slack_user_name import (
    SlackUserName,
)
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
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
from jupiter.core.framework.repository import LeafEntityRepository
from jupiter.core.framework.update_action import UpdateAction


class CannotModifyGeneratedTaskError(Exception):
    """Exception raised when you're trying to modify a generated task."""

    field: str

    def __init__(self, field: str) -> None:
        """Constructor."""
        super().__init__(f"Cannot modify generated inbox task field {field}")
        self.field = field


@entity
class InboxTask(LeafEntity):
    """An inbox task."""

    inbox_task_collection: ParentLink
    source: InboxTaskSource
    project_ref_id: EntityId
    name: InboxTaskName
    status: InboxTaskStatus
    eisen: Eisen
    difficulty: Difficulty
    actionable_date: ADate | None
    due_date: ADate | None
    notes: str | None
    source_entity_ref_id: EntityId | None
    recurring_timeline: str | None
    recurring_repeat_index: int | None
    recurring_gen_right_now: (
        Timestamp | None
    )  # Time for which this inbox task was generated
    working_time: Timestamp | None
    completed_time: Timestamp | None

    note = OwnsAtMostOne(
        Note, domain=NoteDomain.INBOX_TASK, source_entity_ref_id=IsRefId()
    )

    @property
    def source_entity_ref_id_for_sure(self) -> EntityId:
        """Get the source entity ref id."""
        if self.source_entity_ref_id is None:
            raise Exception("Source entity ref id is not set")
        return self.source_entity_ref_id

    @staticmethod
    @create_entity_action
    def new_inbox_task(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        status: InboxTaskStatus,
        eisen: Eisen,
        difficulty: Difficulty,
        actionable_date: ADate | None,
        due_date: ADate | None,
        project_ref_id: EntityId,
        big_plan_ref_id: EntityId | None,
        big_plan_project_ref_id: EntityId | None,
        big_plan_actionable_date: ADate | None,
        big_plan_due_date: ADate | None,
    ) -> "InboxTask":
        """Created an inbox task."""
        InboxTask._check_actionable_and_due_dates(actionable_date, due_date)

        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=(
                InboxTaskSource.USER
                if big_plan_ref_id is None
                else InboxTaskSource.BIG_PLAN
            ),
            name=name,
            status=status,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date
            or (big_plan_actionable_date if big_plan_ref_id else None),
            due_date=due_date or (big_plan_due_date if big_plan_ref_id else None),
            project_ref_id=(
                big_plan_project_ref_id if big_plan_ref_id else project_ref_id
            ),
            source_entity_ref_id=big_plan_ref_id,
            notes=None,
            recurring_timeline=None,
            recurring_repeat_index=None,
            recurring_gen_right_now=None,
            working_time=ctx.action_timestamp if status.is_working_or_more else None,
            completed_time=ctx.action_timestamp if status.is_completed else None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_working_mem_cleanup(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        due_date: ADate | None,
        project_ref_id: EntityId,
        working_mem_ref_id: EntityId,
        recurring_task_timeline: str,
        recurring_task_gen_right_now: Timestamp,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.WORKING_MEM_CLEANUP,
            name=name,
            status=InboxTaskStatus.NOT_STARTED_GEN,
            eisen=Eisen.IMPORTANT,
            difficulty=Difficulty.EASY,
            actionable_date=None,
            due_date=due_date,
            project_ref_id=project_ref_id,
            source_entity_ref_id=working_mem_ref_id,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=None,
            recurring_gen_right_now=recurring_task_gen_right_now,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_habit(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        eisen: Eisen,
        difficulty: Difficulty,
        actionable_date: ADate | None,
        due_date: ADate | None,
        project_ref_id: EntityId,
        habit_ref_id: EntityId,
        recurring_task_timeline: str,
        recurring_task_repeat_index: int | None,
        recurring_task_gen_right_now: Timestamp,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.HABIT,
            name=InboxTask._build_name_for_habit(name, recurring_task_repeat_index),
            status=InboxTaskStatus.NOT_STARTED_GEN,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            source_entity_ref_id=habit_ref_id,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=recurring_task_repeat_index,
            recurring_gen_right_now=recurring_task_gen_right_now,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_chore(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        eisen: Eisen,
        difficulty: Difficulty,
        actionable_date: ADate | None,
        due_date: ADate | None,
        project_ref_id: EntityId,
        chore_ref_id: EntityId,
        recurring_task_timeline: str,
        recurring_task_gen_right_now: Timestamp,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.CHORE,
            name=name,
            status=InboxTaskStatus.NOT_STARTED_GEN,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            source_entity_ref_id=chore_ref_id,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=None,
            recurring_gen_right_now=recurring_task_gen_right_now,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_writing_journal(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        period: RecurringTaskPeriod,
        right_now: ADate,
        project_ref_id: EntityId,
        journal_ref_id: EntityId,
        eisen: Eisen,
        difficulty: Difficulty,
        actionable_date: ADate | None,
        due_date: ADate | None,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.JOURNAL,
            name=InboxTask._build_name_for_writing_journal(period, right_now),
            status=InboxTaskStatus.NOT_STARTED_GEN,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            source_entity_ref_id=journal_ref_id,
            notes=None,
            recurring_timeline=None,
            recurring_repeat_index=None,
            recurring_gen_right_now=None,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_metric_collection(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        eisen: Eisen,
        difficulty: Difficulty,
        actionable_date: ADate | None,
        due_date: ADate | None,
        project_ref_id: EntityId,
        metric_ref_id: EntityId,
        recurring_task_timeline: str,
        recurring_task_gen_right_now: Timestamp,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.METRIC,
            name=InboxTask._build_name_for_collection_task(name),
            status=InboxTaskStatus.NOT_STARTED_GEN,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            source_entity_ref_id=metric_ref_id,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=None,
            recurring_gen_right_now=recurring_task_gen_right_now,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_person_catch_up(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        eisen: Eisen,
        difficulty: Difficulty,
        recurring_task_gen_right_now: Timestamp,
        actionable_date: ADate | None,
        due_date: ADate | None,
        project_ref_id: EntityId,
        person_ref_id: EntityId,
        recurring_task_timeline: str,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.PERSON_CATCH_UP,
            name=InboxTask._build_name_for_catch_up_task(name),
            status=InboxTaskStatus.NOT_STARTED_GEN,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            source_entity_ref_id=person_ref_id,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=None,
            recurring_gen_right_now=recurring_task_gen_right_now,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_person_birthday(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        due_date: ADate,
        project_ref_id: EntityId,
        person_ref_id: EntityId,
        recurring_task_timeline: str,
        recurring_task_gen_right_now: Timestamp,
        preparation_days_cnt: int,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.PERSON_BIRTHDAY,
            name=InboxTask._build_name_for_birthday_task(name),
            status=InboxTaskStatus.NOT_STARTED_GEN,
            eisen=Eisen.IMPORTANT,
            difficulty=Difficulty.EASY,
            actionable_date=due_date.subtract_days(preparation_days_cnt),
            due_date=due_date,
            project_ref_id=project_ref_id,
            source_entity_ref_id=person_ref_id,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=None,
            recurring_gen_right_now=recurring_task_gen_right_now,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_slack_task(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        project_ref_id: EntityId,
        slack_task_ref_id: EntityId,
        user: SlackUserName,
        channel: SlackChannelName | None,
        message: str,
        generation_extra_info: PushGenerationExtraInfo,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.SLACK_TASK,
            name=InboxTask._build_name_for_slack_task(
                user,
                channel,
                generation_extra_info,
            ),
            status=generation_extra_info.status or InboxTaskStatus.NOT_STARTED,
            eisen=generation_extra_info.eisen,
            difficulty=generation_extra_info.difficulty,
            actionable_date=generation_extra_info.actionable_date,
            due_date=generation_extra_info.due_date,
            project_ref_id=project_ref_id,
            source_entity_ref_id=slack_task_ref_id,
            notes=InboxTask._build_notes_for_slack_task(user, channel, message),
            recurring_timeline=None,
            recurring_repeat_index=None,
            recurring_gen_right_now=None,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_email_task(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        project_ref_id: EntityId,
        email_task_ref_id: EntityId,
        from_address: EmailAddress,
        from_name: EmailUserName,
        to_address: EmailAddress,
        subject: str,
        body: str,
        generation_extra_info: PushGenerationExtraInfo,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.EMAIL_TASK,
            name=InboxTask._build_name_for_email_task(
                from_address,
                from_name,
                to_address,
                generation_extra_info,
            ),
            status=generation_extra_info.status or InboxTaskStatus.NOT_STARTED,
            eisen=generation_extra_info.eisen,
            difficulty=generation_extra_info.difficulty,
            actionable_date=generation_extra_info.actionable_date,
            due_date=generation_extra_info.due_date,
            project_ref_id=project_ref_id,
            source_entity_ref_id=email_task_ref_id,
            notes=InboxTask._build_notes_for_email_task(
                from_address,
                from_name,
                to_address,
                subject,
                body,
            ),
            recurring_timeline=None,
            recurring_repeat_index=None,
            recurring_gen_right_now=None,
            working_time=None,
            completed_time=None,
        )

    @update_entity_action
    def update_link_to_working_mem_cleanup(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        name: InboxTaskName,
        due_date: ADate | None,
        recurring_timeline: str,
    ) -> "InboxTask":
        """Update all the info associated with a working memory cleanup."""
        if self.source is not InboxTaskSource.WORKING_MEM_CLEANUP:
            raise Exception(
                f"Cannot associate a task which is not for a working memory cleanup '{self.name}'",
            )
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
            name=name,
            due_date=due_date,
            recurring_timeline=recurring_timeline,
        )

    @update_entity_action
    def update_link_to_big_plan(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        big_plan_ref_id: EntityId,
    ) -> "InboxTask":
        """Update all the info associated with a big plan."""
        if self.source is not InboxTaskSource.BIG_PLAN:
            raise InputValidationError(
                f"Cannot reassociate a task which isn't a big plan one '{self.name}'",
            )
        if self.source_entity_ref_id != big_plan_ref_id:
            raise InputValidationError(
                f"Cannot reassociate a task which is not with the big plan '{self.name}'",
            )

        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
        )

    @update_entity_action
    def update_link_to_habit(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        name: InboxTaskName,
        timeline: str,
        repeat_index: int | None,
        actionable_date: ADate | None,
        due_date: ADate,
        eisen: Eisen,
        difficulty: Difficulty,
    ) -> "InboxTask":
        """Update all the info associated with a habit."""
        if self.source is not InboxTaskSource.HABIT:
            raise Exception(
                f"Cannot associate a task which is not a habit for '{self.name}'",
            )
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
            name=InboxTask._build_name_for_habit(name, repeat_index),
            actionable_date=actionable_date,
            due_date=due_date,
            eisen=eisen,
            difficulty=difficulty,
            recurring_timeline=timeline,
            recurring_repeat_index=repeat_index,
        )

    @update_entity_action
    def update_link_to_chore(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        name: InboxTaskName,
        timeline: str,
        actionable_date: ADate | None,
        due_date: ADate,
        eisen: Eisen,
        difficulty: Difficulty,
    ) -> "InboxTask":
        """Update all the info associated with a chore."""
        if self.source is not InboxTaskSource.CHORE:
            raise Exception(
                f"Cannot associate a task which is not a chore for '{self.name}'",
            )
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
            name=name,
            actionable_date=actionable_date,
            due_date=due_date,
            eisen=eisen,
            difficulty=difficulty,
            recurring_timeline=timeline,
        )

    @update_entity_action
    def update_link_to_metric(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        name: InboxTaskName,
        recurring_timeline: str,
        eisen: Eisen,
        difficulty: Difficulty,
        actionable_date: ADate | None,
        due_time: ADate,
    ) -> "InboxTask":
        """Update all the info associated with a metric."""
        if self.source is not InboxTaskSource.METRIC:
            raise Exception(
                f"Cannot associate a task which is not for a metric '{self.name}'",
            )
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
            name=self._build_name_for_collection_task(name),
            actionable_date=actionable_date,
            due_date=due_time,
            eisen=eisen,
            difficulty=difficulty,
            recurring_timeline=recurring_timeline,
        )

    @update_entity_action
    def update_link_to_person_catch_up(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        name: InboxTaskName,
        recurring_timeline: str,
        eisen: Eisen,
        difficulty: Difficulty,
        actionable_date: ADate | None,
        due_time: ADate,
    ) -> "InboxTask":
        """Update all the info associated with a person."""
        if self.source is not InboxTaskSource.PERSON_CATCH_UP:
            raise Exception(
                f"Cannot associate a task which is not for a person catch up'{self.name}'",
            )
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
            name=self._build_name_for_catch_up_task(name),
            actionable_date=actionable_date,
            due_date=due_time,
            eisen=eisen,
            difficulty=difficulty,
            recurring_timeline=recurring_timeline,
        )

    @update_entity_action
    def update_link_to_person_birthday(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        name: InboxTaskName,
        recurring_timeline: str,
        preparation_days_cnt: int,
        due_time: ADate,
    ) -> "InboxTask":
        """Update all the info associated with a person."""
        if self.source is not InboxTaskSource.PERSON_BIRTHDAY:
            raise Exception(
                f"Cannot associate a task which is not for a person birthday '{self.name}'",
            )
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
            name=self._build_name_for_birthday_task(name),
            actionable_date=due_time.subtract_days(preparation_days_cnt),
            due_date=due_time,
            recurring_timeline=recurring_timeline,
        )

    @update_entity_action
    def update_link_to_slack_task(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        user: SlackUserName,
        channel: SlackChannelName | None,
        message: str,
        generation_extra_info: PushGenerationExtraInfo,
    ) -> "InboxTask":
        """Update all the info associated with a person."""
        if self.source is not InboxTaskSource.SLACK_TASK:
            raise Exception(
                f"Cannot update a task which is not a Slack one '{self.name}'",
            )
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
            name=self._build_name_for_slack_task(user, channel, generation_extra_info),
            eisen=generation_extra_info.eisen,
            difficulty=generation_extra_info.difficulty,
            actionable_date=generation_extra_info.actionable_date,
            due_date=generation_extra_info.due_date,
            notes=InboxTask._build_notes_for_slack_task(user, channel, message),
        )

    @update_entity_action
    def update_link_to_email_task(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        from_address: EmailAddress,
        from_name: EmailUserName,
        to_address: EmailAddress,
        subject: str,
        body: str,
        generation_extra_info: PushGenerationExtraInfo,
    ) -> "InboxTask":
        """Update all the info associated with a person."""
        if self.source is not InboxTaskSource.EMAIL_TASK:
            raise Exception(
                f"Cannot update a task which is not a email one '{self.name}'",
            )
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
            name=self._build_name_for_email_task(
                from_address,
                from_name,
                to_address,
                generation_extra_info,
            ),
            eisen=generation_extra_info.eisen,
            difficulty=generation_extra_info.difficulty,
            actionable_date=generation_extra_info.actionable_date,
            due_date=generation_extra_info.due_date,
            notes=InboxTask._build_notes_for_email_task(
                from_address,
                from_name,
                to_address,
                subject,
                body,
            ),
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[InboxTaskName],
        status: UpdateAction[InboxTaskStatus],
        project_ref_id: UpdateAction[EntityId],
        big_plan_ref_id: UpdateAction[EntityId | None],
        actionable_date: UpdateAction[ADate | None],
        due_date: UpdateAction[ADate | None],
        eisen: UpdateAction[Eisen],
        difficulty: UpdateAction[Difficulty],
    ) -> "InboxTask":
        """Update the inbox task."""
        if name.should_change:
            if not self.source.allow_user_changes:
                raise CannotModifyGeneratedTaskError("name")
            the_name = name.just_the_value
        else:
            the_name = self.name

        the_status = self.status
        the_working_time = self.working_time
        the_completed_time = self.completed_time
        if status.should_change:
            if (
                self.source.allow_user_changes
                and status.just_the_value == InboxTaskStatus.NOT_STARTED_GEN
            ):
                raise InputValidationError(
                    "Trying to change a user created task to a generated-only status",
                )
            if (
                not self.source.allow_user_changes
                and status.just_the_value == InboxTaskStatus.NOT_STARTED
            ):
                raise InputValidationError(
                    "Trying to change a generated task to a user-only status",
                )

            if (
                not self.status.is_working_or_more
                and status.just_the_value.is_working_or_more
            ):
                the_working_time = ctx.action_timestamp
            elif (
                self.status.is_working_or_more
                and not status.just_the_value.is_working_or_more
            ):
                the_working_time = None

            if not self.status.is_completed and status.just_the_value.is_completed:
                the_completed_time = ctx.action_timestamp
            elif self.status.is_completed and not status.just_the_value.is_completed:
                the_completed_time = None

            the_status = status.just_the_value

        if project_ref_id.should_change:
            if (
                not self.source.allow_user_changes
                and project_ref_id.just_the_value != self.project_ref_id
            ):
                raise CannotModifyGeneratedTaskError("project")
            the_project = project_ref_id.just_the_value
        else:
            the_project = self.project_ref_id

        if big_plan_ref_id.should_change:
            if not self.source.allow_user_changes:
                raise CannotModifyGeneratedTaskError("big plan")
            the_source_entity_ref_id = big_plan_ref_id.just_the_value
        else:
            the_source_entity_ref_id = self.source_entity_ref_id

        if actionable_date.should_change or due_date.should_change:
            the_actionable_date = actionable_date.or_else(self.actionable_date)
            the_due_date = due_date.or_else(self.due_date)
            InboxTask._check_actionable_and_due_dates(the_actionable_date, the_due_date)
        else:
            the_actionable_date = self.actionable_date
            the_due_date = self.due_date

        if eisen.should_change:
            if not self.source.allow_user_changes:
                raise CannotModifyGeneratedTaskError("eisen")
            the_eisen = eisen.just_the_value
        else:
            the_eisen = self.eisen

        if difficulty.should_change:
            if not self.source.allow_user_changes:
                raise CannotModifyGeneratedTaskError("difficulty")
            the_difficulty = difficulty.just_the_value
        else:
            the_difficulty = self.difficulty

        return self._new_version(
            ctx,
            name=the_name,
            source=(
                InboxTaskSource.BIG_PLAN
                if big_plan_ref_id.should_change
                and big_plan_ref_id.just_the_value is not None
                else (
                    InboxTaskSource.USER
                    if big_plan_ref_id.should_change
                    and big_plan_ref_id.just_the_value is None
                    else self.source
                )
            ),
            status=the_status,
            project_ref_id=the_project,
            source_entity_ref_id=the_source_entity_ref_id,
            actionable_date=the_actionable_date,
            due_date=the_due_date,
            working_time=the_working_time,
            completed_time=the_completed_time,
            eisen=the_eisen,
            difficulty=the_difficulty,
        )

    @update_entity_action
    def change_due_date_via_time_plan(
        self,
        ctx: DomainContext,
        due_date: ADate,
    ) -> "InboxTask":
        """Update the inbox task."""
        if not self.allow_user_changes:
            raise CannotModifyGeneratedTaskError("name")

        actionable_date = self.actionable_date
        if actionable_date is not None and actionable_date > due_date:
            actionable_date = None

        self._check_actionable_and_due_dates(actionable_date, due_date)

        return self._new_version(
            ctx, actionable_date=actionable_date, due_date=due_date
        )

    @property
    def allow_user_changes(self) -> bool:
        """Allow user changes for an inbox task."""
        return self.source.allow_user_changes

    @property
    def is_working_or_more(self) -> bool:
        """Whether this task is being worked on or not."""
        return self.status.is_working_or_more

    @property
    def is_completed(self) -> bool:
        """Whether this task is complete or not."""
        return self.status.is_completed

    @staticmethod
    def _build_name_for_habit(
        name: InboxTaskName,
        repeat_index: int | None,
    ) -> InboxTaskName:
        if repeat_index is not None:
            return InboxTaskName(f"{name} [{repeat_index + 1}]")
        else:
            return name

    @staticmethod
    def _build_name_for_writing_journal(
        period: RecurringTaskPeriod, right_now: ADate
    ) -> InboxTaskName:
        return InboxTaskName(f"Write {period} journal entry for for {right_now}")

    @staticmethod
    def _build_name_for_collection_task(name: InboxTaskName) -> InboxTaskName:
        return InboxTaskName(f"Collect value for metric {name}")

    @staticmethod
    def _build_name_for_catch_up_task(name: InboxTaskName) -> InboxTaskName:
        return InboxTaskName(f"Catch up with {name}")

    @staticmethod
    def _build_name_for_birthday_task(name: InboxTaskName) -> InboxTaskName:
        return InboxTaskName(f"Wish happy birthday to {name}")

    @staticmethod
    def _build_name_for_slack_task(
        user: SlackUserName,
        channel: SlackChannelName | None,
        generation_extra_info: PushGenerationExtraInfo,
    ) -> InboxTaskName:
        if generation_extra_info.name is not None:
            return generation_extra_info.name
        if channel is not None:
            return InboxTaskName(f"Respond to {user} on {channel}")
        return InboxTaskName(f"Respond to {user}'s DM")

    @staticmethod
    def _build_name_for_email_task(
        from_address: EmailAddress,
        from_name: EmailUserName,
        to_address: EmailAddress,
        generation_extra_info: PushGenerationExtraInfo,
    ) -> InboxTaskName:
        if generation_extra_info.name is not None:
            return generation_extra_info.name
        return InboxTaskName(
            f"Respond to {from_name}'s <{from_address}> message sent to {to_address}",
        )

    @staticmethod
    def _build_notes_for_slack_task(
        user: SlackUserName,
        channel: SlackChannelName | None,
        message: str,
    ) -> str:
        message = textwrap.dedent(
            f"""
            **user**: {user}
            **channel**: {str(channel) if channel else "DM"}
            **message**: {message}
            """,
        ).strip()
        return message

    @staticmethod
    def _build_notes_for_email_task(
        from_address: EmailAddress,
        from_name: EmailUserName,
        to_address: EmailAddress,
        subject: str,
        body: str,
    ) -> str:
        message = textwrap.dedent(
            f"""
            **from**: {from_name} <{from_address}>
            **to**: {to_address}
            **subject**: {subject}
            **body**: {body}""",
        ).strip()
        return message

    @staticmethod
    def _check_actionable_and_due_dates(
        actionable_date: ADate | None,
        due_date: ADate | None,
    ) -> None:
        if actionable_date is None or due_date is None:
            return

        if actionable_date > due_date:
            raise InputValidationError(
                f"The actionable date {actionable_date} should be before the due date {due_date}",
            )


class InboxTaskRepository(LeafEntityRepository[InboxTask], abc.ABC):
    """A repository of inbox tasks."""

    PAGE_SIZE: ClassVar[int] = 10

    @abc.abstractmethod
    async def count_all_for_source(
        self,
        parent_ref_id: EntityId,
        source: InboxTaskSource,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> int:
        """Count all inbox tasks for a source."""

    @abc.abstractmethod
    async def find_all_for_source_created_desc(
        self,
        parent_ref_id: EntityId,
        source: InboxTaskSource,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
        retrieve_offset: int | None = None,
        retrieve_limit: int | None = None,
    ) -> list[InboxTask]:
        """Find all inbox tasks for a source."""

    @abc.abstractmethod
    async def find_modified_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Iterable[EntityId] | None = None,
        filter_sources: Iterable[InboxTaskSource] | None = None,
        filter_project_ref_ids: Iterable[EntityId] | None = None,
        filter_last_modified_time_start: ADate | None = None,
        filter_last_modified_time_end: ADate | None = None,
    ) -> list[InboxTask]:
        """Find all inbox tasks."""

    @abc.abstractmethod
    async def find_completed_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        filter_start_completed_date: ADate,
        filter_end_completed_date: ADate,
        filter_include_sources: Iterable[InboxTaskSource],
        filter_exclude_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[InboxTask]:
        """Find all completed inbox tasks in a time range."""
