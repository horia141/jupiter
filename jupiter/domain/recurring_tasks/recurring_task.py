"""A recurring task."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.adate import ADate
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.domain.recurring_task_type import RecurringTaskType
from jupiter.domain.recurring_tasks.recurring_task_name import RecurringTaskName
from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.update_action import UpdateAction


@dataclass()
class RecurringTask(AggregateRoot):
    """A recurring task."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    @dataclass(frozen=True)
    class Suspended(AggregateRoot.Updated):
        """Suspended event."""

    @dataclass(frozen=True)
    class Unsuspended(AggregateRoot.Updated):
        """Unsuspend event."""

    recurring_task_collection_ref_id: EntityId
    name: RecurringTaskName
    period: RecurringTaskPeriod
    the_type: RecurringTaskType
    gen_params: RecurringTaskGenParams
    suspended: bool
    skip_rule: Optional[RecurringTaskSkipRule]
    must_do: bool
    start_at_date: ADate
    end_at_date: Optional[ADate]

    @staticmethod
    def new_recurring_task(
            recurring_task_collection_ref_id: EntityId, archived: bool, name: RecurringTaskName,
            period: RecurringTaskPeriod, the_type: Optional[RecurringTaskType], gen_params: RecurringTaskGenParams,
            must_do: bool, skip_rule: Optional[RecurringTaskSkipRule], start_at_date: Optional[ADate],
            end_at_date: Optional[ADate], suspended: bool, created_time: Timestamp) -> 'RecurringTask':
        """Create a recurring task."""
        today = ADate.from_date(created_time.as_date())
        RecurringTask._check_actionable_and_due_date_configs(
            gen_params.actionable_from_day, gen_params.actionable_from_month,
            gen_params.due_at_day, gen_params.due_at_month)

        if start_at_date is not None and end_at_date is not None and start_at_date >= end_at_date:
            raise InputValidationError(f"Start date {start_at_date} is after {end_at_date}")
        if start_at_date is None and end_at_date is not None and end_at_date < today:
            raise InputValidationError(f"End date {end_at_date} is before {today}")

        recurring_task = RecurringTask(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[],
            recurring_task_collection_ref_id=recurring_task_collection_ref_id,
            name=name,
            period=period,
            the_type=the_type or RecurringTaskType.CHORE,
            gen_params=gen_params,
            must_do=must_do,
            skip_rule=skip_rule,
            start_at_date=start_at_date if start_at_date else today,
            end_at_date=end_at_date,
            suspended=suspended)
        recurring_task.record_event(RecurringTask.Created.make_event_from_frame_args(created_time))

        return recurring_task

    def update(
            self, name: UpdateAction[RecurringTaskName], period: UpdateAction[RecurringTaskPeriod],
            the_type: UpdateAction[RecurringTaskType], gen_params: UpdateAction[RecurringTaskGenParams],
            must_do: UpdateAction[bool], skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]],
            start_at_date: UpdateAction[ADate], end_at_date: UpdateAction[Optional[ADate]],
            modification_time: Timestamp) -> 'RecurringTask':
        """Update the recurring task."""
        self.name = name.or_else(self.name)
        self.period = period.or_else(self.period)
        self.the_type = the_type.or_else(self.the_type)

        if gen_params.should_change:
            RecurringTask._check_actionable_and_due_date_configs(
                gen_params.value.actionable_from_day, gen_params.value.actionable_from_month,
                gen_params.value.due_at_day, gen_params.value.due_at_month)
            self.gen_params = gen_params.value

        self.must_do = must_do.or_else(self.must_do)
        self.skip_rule = skip_rule.or_else(self.skip_rule)

        if start_at_date.should_change or end_at_date.should_change:
            the_start_at_date = start_at_date.or_else(self.start_at_date)
            the_end_at_date = end_at_date.or_else(self.end_at_date)
            today = ADate.from_date(modification_time.as_date())
            if the_end_at_date is not None and the_start_at_date >= end_at_date:
                raise InputValidationError(f"Start date {the_start_at_date} is after end date {the_end_at_date}")
            if the_end_at_date is not None and the_end_at_date < today:
                raise InputValidationError(f"End date {the_end_at_date} is before start date {today}")
            self.start_at_date = the_start_at_date
            self.end_at_date = the_end_at_date

        self.record_event(RecurringTask.Updated.make_event_from_frame_args(modification_time))
        return self

    def suspend(self, modification_time: Timestamp) -> 'RecurringTask':
        """Suspend the recurring task."""
        if self.suspended:
            return self
        self.suspended = True
        self.record_event(RecurringTask.Suspended.make_event_from_frame_args(modification_time))
        return self

    def unsuspend(self, modification_time: Timestamp) -> 'RecurringTask':
        """Unsuspend the recurring task."""
        if self.suspended:
            return self
        self.suspended = False
        self.record_event(RecurringTask.Unsuspended.make_event_from_frame_args(modification_time))
        return self

    def is_in_active_interval(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this active interval."""
        recurring_task_start_date = self.start_at_date
        recurring_task_end_date = self.end_at_date.end_of_day() if self.end_at_date else None

        if recurring_task_end_date is None:
            # Just a start date interval, so at least the end date should be in it
            return end_date >= recurring_task_start_date
        else:
            # Both a start date and an end date are present. At least one of the start date or end date of
            # the interval we're comparing against should be in this interval.
            return recurring_task_start_date <= start_date <= recurring_task_end_date or \
                recurring_task_start_date <= end_date <= recurring_task_end_date

    @property
    def project_ref_id(self) -> EntityId:
        """The project id this task belongs to."""
        # TODO(horia141): fix this uglyness
        return self.recurring_task_collection_ref_id

    @staticmethod
    def _check_actionable_and_due_date_configs(
            actionable_from_day: Optional[RecurringTaskDueAtDay],
            actionable_from_month: Optional[RecurringTaskDueAtMonth], due_at_day: Optional[RecurringTaskDueAtDay],
            due_at_month: Optional[RecurringTaskDueAtMonth]) -> None:
        actionable_from_day = actionable_from_day or RecurringTaskDueAtDay(0)
        actionable_from_month = actionable_from_month or RecurringTaskDueAtMonth(0)
        due_at_day = due_at_day or RecurringTaskDueAtDay(1000)
        due_at_month = due_at_month or RecurringTaskDueAtMonth(1000)
        if actionable_from_month.as_int() > due_at_month.as_int():
            raise InputValidationError(
                f"Actionable month {actionable_from_month} should be before due month {due_at_month}")
        if actionable_from_month == due_at_month and actionable_from_day.as_int() > due_at_day.as_int():
            raise InputValidationError(
                f"Actionable day {actionable_from_day} should be before due day {due_at_day}")
