"""An inbox task."""
import textwrap
from typing import Optional

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.domain.push_integrations.slack.slack_channel_name import (
    SlackChannelName,
)
from jupiter.core.domain.push_integrations.slack.slack_user_name import SlackUserName
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
    difficulty: Optional[Difficulty] = None
    actionable_date: Optional[ADate] = None
    due_date: Optional[ADate] = None
    notes: Optional[str] = None
    habit_ref_id: Optional[EntityId] = None
    chore_ref_id: Optional[EntityId] = None
    big_plan_ref_id: Optional[EntityId] = None
    journal_ref_id: Optional[EntityId] = None
    metric_ref_id: Optional[EntityId] = None
    person_ref_id: Optional[EntityId] = None
    slack_task_ref_id: Optional[EntityId] = None
    email_task_ref_id: Optional[EntityId] = None
    recurring_timeline: Optional[str] = None
    recurring_repeat_index: Optional[int] = None
    recurring_gen_right_now: Optional[
        Timestamp
    ] = None  # Time for which this inbox task was generated
    accepted_time: Optional[Timestamp] = None
    working_time: Optional[Timestamp] = None
    completed_time: Optional[Timestamp] = None

    note = OwnsAtMostOne(
        Note, domain=NoteDomain.INBOX_TASK, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_inbox_task(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        status: InboxTaskStatus,
        difficulty: Optional[Difficulty],
        actionable_date: Optional[ADate],
        due_date: Optional[ADate],
        project_ref_id: EntityId,
        big_plan_ref_id: Optional[EntityId],
        big_plan_project_ref_id: Optional[EntityId],
        big_plan_actionable_date: Optional[ADate],
        big_plan_due_date: Optional[ADate],
        eisen: Optional[Eisen],
    ) -> "InboxTask":
        """Created an inbox task."""
        InboxTask._check_actionable_and_due_dates(actionable_date, due_date)

        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.USER
            if big_plan_ref_id is None
            else InboxTaskSource.BIG_PLAN,
            name=name,
            status=status,
            eisen=eisen if eisen else Eisen.REGULAR,
            difficulty=difficulty,
            actionable_date=actionable_date
            or (big_plan_actionable_date if big_plan_ref_id else None),
            due_date=due_date or (big_plan_due_date if big_plan_ref_id else None),
            project_ref_id=big_plan_project_ref_id
            if big_plan_ref_id
            else project_ref_id,
            habit_ref_id=None,
            chore_ref_id=None,
            big_plan_ref_id=big_plan_ref_id,
            journal_ref_id=None,
            metric_ref_id=None,
            person_ref_id=None,
            slack_task_ref_id=None,
            email_task_ref_id=None,
            notes=None,
            recurring_timeline=None,
            recurring_repeat_index=None,
            recurring_gen_right_now=None,
            accepted_time=ctx.action_timestamp if status.is_accepted_or_more else None,
            working_time=ctx.action_timestamp if status.is_working_or_more else None,
            completed_time=ctx.action_timestamp if status.is_completed else None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_habit(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        eisen: Optional[Eisen],
        difficulty: Optional[Difficulty],
        actionable_date: Optional[ADate],
        due_date: Optional[ADate],
        project_ref_id: EntityId,
        habit_ref_id: EntityId,
        recurring_task_timeline: str,
        recurring_task_repeat_index: Optional[int],
        recurring_task_gen_right_now: Timestamp,
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.HABIT,
            name=InboxTask._build_name_for_habit(name, recurring_task_repeat_index),
            status=InboxTaskStatus.RECURRING,
            eisen=eisen if eisen else Eisen.REGULAR,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            habit_ref_id=habit_ref_id,
            chore_ref_id=None,
            big_plan_ref_id=None,
            journal_ref_id=None,
            metric_ref_id=None,
            person_ref_id=None,
            slack_task_ref_id=None,
            email_task_ref_id=None,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=recurring_task_repeat_index,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=ctx.action_timestamp,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_chore(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        eisen: Optional[Eisen],
        difficulty: Optional[Difficulty],
        actionable_date: Optional[ADate],
        due_date: Optional[ADate],
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
            status=InboxTaskStatus.RECURRING,
            eisen=eisen if eisen else Eisen.REGULAR,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            habit_ref_id=None,
            chore_ref_id=chore_ref_id,
            big_plan_ref_id=None,
            journal_ref_id=None,
            metric_ref_id=None,
            person_ref_id=None,
            slack_task_ref_id=None,
            email_task_ref_id=None,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=None,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=ctx.action_timestamp,
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
        eisen: Optional[Eisen],
        difficulty: Optional[Difficulty],
        actionable_date: Optional[ADate],
        due_date: Optional[ADate],
    ) -> "InboxTask":
        """Create an inbox task."""
        return InboxTask._create(
            ctx,
            inbox_task_collection=ParentLink(inbox_task_collection_ref_id),
            source=InboxTaskSource.JOURNAL,
            name=InboxTask._build_name_for_writing_journal(period, right_now),
            status=InboxTaskStatus.RECURRING,
            eisen=eisen or Eisen.REGULAR,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            habit_ref_id=None,
            chore_ref_id=None,
            big_plan_ref_id=None,
            journal_ref_id=journal_ref_id,
            metric_ref_id=None,
            person_ref_id=None,
            slack_task_ref_id=None,
            email_task_ref_id=None,
            notes=None,
            recurring_timeline=None,
            recurring_repeat_index=None,
            recurring_gen_right_now=None,
            accepted_time=ctx.action_timestamp,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_metric_collection(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        eisen: Optional[Eisen],
        difficulty: Optional[Difficulty],
        actionable_date: Optional[ADate],
        due_date: Optional[ADate],
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
            status=InboxTaskStatus.RECURRING,
            eisen=eisen if eisen else Eisen.REGULAR,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            habit_ref_id=None,
            chore_ref_id=None,
            big_plan_ref_id=None,
            journal_ref_id=None,
            metric_ref_id=metric_ref_id,
            person_ref_id=None,
            slack_task_ref_id=None,
            email_task_ref_id=None,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=None,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=ctx.action_timestamp,
            working_time=None,
            completed_time=None,
        )

    @staticmethod
    @create_entity_action
    def new_inbox_task_for_person_catch_up(
        ctx: DomainContext,
        inbox_task_collection_ref_id: EntityId,
        name: InboxTaskName,
        eisen: Optional[Eisen],
        difficulty: Optional[Difficulty],
        recurring_task_gen_right_now: Timestamp,
        actionable_date: Optional[ADate],
        due_date: Optional[ADate],
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
            status=InboxTaskStatus.RECURRING,
            eisen=eisen if eisen else Eisen.REGULAR,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            project_ref_id=project_ref_id,
            habit_ref_id=None,
            chore_ref_id=None,
            big_plan_ref_id=None,
            journal_ref_id=None,
            metric_ref_id=None,
            person_ref_id=person_ref_id,
            slack_task_ref_id=None,
            email_task_ref_id=None,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=None,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=ctx.action_timestamp,
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
            status=InboxTaskStatus.RECURRING,
            eisen=Eisen.IMPORTANT,
            difficulty=Difficulty.EASY,
            actionable_date=due_date.subtract_days(preparation_days_cnt),
            due_date=due_date,
            project_ref_id=project_ref_id,
            habit_ref_id=None,
            chore_ref_id=None,
            big_plan_ref_id=None,
            journal_ref_id=None,
            metric_ref_id=None,
            person_ref_id=person_ref_id,
            slack_task_ref_id=None,
            email_task_ref_id=None,
            notes=None,
            recurring_timeline=recurring_task_timeline,
            recurring_repeat_index=None,
            recurring_gen_right_now=recurring_task_gen_right_now,
            accepted_time=ctx.action_timestamp,
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
        channel: Optional[SlackChannelName],
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
            status=generation_extra_info.status or InboxTaskStatus.ACCEPTED,
            eisen=generation_extra_info.eisen or Eisen.REGULAR,
            difficulty=generation_extra_info.difficulty,
            actionable_date=generation_extra_info.actionable_date,
            due_date=generation_extra_info.due_date,
            project_ref_id=project_ref_id,
            habit_ref_id=None,
            chore_ref_id=None,
            big_plan_ref_id=None,
            journal_ref_id=None,
            metric_ref_id=None,
            person_ref_id=None,
            slack_task_ref_id=slack_task_ref_id,
            email_task_ref_id=None,
            notes=InboxTask._build_notes_for_slack_task(user, channel, message),
            recurring_timeline=None,
            recurring_repeat_index=None,
            recurring_gen_right_now=None,
            accepted_time=ctx.action_timestamp,
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
            status=generation_extra_info.status or InboxTaskStatus.ACCEPTED,
            eisen=generation_extra_info.eisen or Eisen.REGULAR,
            difficulty=generation_extra_info.difficulty,
            actionable_date=generation_extra_info.actionable_date,
            due_date=generation_extra_info.due_date,
            project_ref_id=project_ref_id,
            habit_ref_id=None,
            chore_ref_id=None,
            big_plan_ref_id=None,
            metric_ref_id=None,
            journal_ref_id=None,
            person_ref_id=None,
            slack_task_ref_id=None,
            email_task_ref_id=email_task_ref_id,
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
            accepted_time=ctx.action_timestamp,
            working_time=None,
            completed_time=None,
        )

    @update_entity_action
    def change_project(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
    ) -> "InboxTask":
        """Change the project for the inbox task."""
        if not self.source.allow_user_changes:
            raise CannotModifyGeneratedTaskError("project")
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
        )

    @update_entity_action
    def associate_with_big_plan(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
        big_plan_ref_id: EntityId,
    ) -> "InboxTask":
        """Associate an inbox task with a big plan."""
        if not self.source.allow_user_changes:
            raise CannotModifyGeneratedTaskError("big plan")

        return self._new_version(
            ctx,
            source=InboxTaskSource.BIG_PLAN,
            project_ref_id=project_ref_id,
            big_plan_ref_id=big_plan_ref_id,
        )

    @update_entity_action
    def release_from_big_plan(
        self,
        ctx: DomainContext,
    ) -> "InboxTask":
        """Release an inbox task from a big plan."""
        if not self.source.allow_user_changes:
            raise CannotModifyGeneratedTaskError("big plan")

        return self._new_version(
            ctx,
            source=InboxTaskSource.USER,
            big_plan_ref_id=None,
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
        if self.big_plan_ref_id != big_plan_ref_id:
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
        repeat_index: Optional[int],
        actionable_date: Optional[ADate],
        due_date: ADate,
        eisen: Optional[Eisen],
        difficulty: Optional[Difficulty],
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
            eisen=eisen if eisen else Eisen.REGULAR,
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
        actionable_date: Optional[ADate],
        due_date: ADate,
        eisen: Optional[Eisen],
        difficulty: Optional[Difficulty],
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
            eisen=eisen if eisen else Eisen.REGULAR,
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
        eisen: Optional[Eisen],
        difficulty: Optional[Difficulty],
        actionable_date: Optional[ADate],
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
            eisen=eisen if eisen else Eisen.REGULAR,
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
        eisen: Optional[Eisen],
        difficulty: Optional[Difficulty],
        actionable_date: Optional[ADate],
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
            eisen=eisen if eisen else Eisen.REGULAR,
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
        channel: Optional[SlackChannelName],
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
            eisen=generation_extra_info.eisen or Eisen.REGULAR,
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
            eisen=generation_extra_info.eisen or Eisen.REGULAR,
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
        actionable_date: UpdateAction[Optional[ADate]],
        due_date: UpdateAction[Optional[ADate]],
        eisen: UpdateAction[Eisen],
        difficulty: UpdateAction[Optional[Difficulty]],
    ) -> "InboxTask":
        """Update the inbox task."""
        if name.should_change:
            if not self.source.allow_user_changes:
                raise CannotModifyGeneratedTaskError("name")
            the_name = name.just_the_value
        else:
            the_name = self.name

        the_status = self.status
        the_accepted_time = self.accepted_time
        the_working_time = self.working_time
        the_completed_time = self.completed_time
        if status.should_change:
            if (
                self.source.allow_user_changes
                and status.just_the_value == InboxTaskStatus.RECURRING
            ):
                raise InputValidationError(
                    "Trying to change a user created task to a generated-only status",
                )
            if (
                not self.source.allow_user_changes
                and status.just_the_value == InboxTaskStatus.ACCEPTED
            ):
                raise InputValidationError(
                    "Trying to change a generated task to a user-only status",
                )

            if (
                not self.status.is_accepted_or_more
                and status.just_the_value.is_accepted_or_more
            ):
                the_accepted_time = ctx.action_timestamp
            elif (
                self.status.is_accepted_or_more
                and not status.just_the_value.is_accepted_or_more
            ):
                the_accepted_time = None

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
            status=the_status,
            actionable_date=the_actionable_date,
            due_date=the_due_date,
            accepted_time=the_accepted_time,
            working_time=the_working_time,
            completed_time=the_completed_time,
            eisen=the_eisen,
            difficulty=the_difficulty,
        )

    @property
    def allow_user_changes(self) -> bool:
        """Allow user changes for an inbox task."""
        return self.source.allow_user_changes

    @staticmethod
    def _build_name_for_habit(
        name: InboxTaskName,
        repeat_index: Optional[int],
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
        channel: Optional[SlackChannelName],
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
        channel: Optional[SlackChannelName],
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
        actionable_date: Optional[ADate],
        due_date: Optional[ADate],
    ) -> None:
        if actionable_date is None or due_date is None:
            return

        if actionable_date > due_date:
            raise Exception(
                f"The actionable date {actionable_date} should be before the due date {due_date}",
            )
