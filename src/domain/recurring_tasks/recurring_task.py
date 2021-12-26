"""A recurring task."""
from dataclasses import dataclass
from typing import Optional

from domain.adate import ADate
from domain.entity_name import EntityName
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from domain.recurring_task_skip_rule import RecurringTaskSkipRule
from domain.recurring_task_type import RecurringTaskType
from framework.aggregate_root import AggregateRoot
from framework.base.entity_id import EntityId, BAD_REF_ID
from framework.base.timestamp import Timestamp
from framework.errors import InputValidationError
from framework.event import Event2


@dataclass()
class RecurringTask(AggregateRoot):
    """A recurring task."""

    @dataclass(frozen=True)
    class Created(Event2):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(Event2):
        """Updated event."""

    _recurring_task_collection_ref_id: EntityId
    _name: EntityName
    _period: RecurringTaskPeriod
    _the_type: RecurringTaskType
    _gen_params: RecurringTaskGenParams
    _suspended: bool
    _skip_rule: Optional[RecurringTaskSkipRule]
    _must_do: bool
    _start_at_date: ADate
    _end_at_date: Optional[ADate]

    @staticmethod
    def new_recurring_task(
            recurring_task_collection_ref_id: EntityId, archived: bool, name: EntityName,
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
            _ref_id=BAD_REF_ID,
            _archived=archived,
            _created_time=created_time,
            _archived_time=created_time if archived else None,
            _last_modified_time=created_time,
            _events=[],
            _recurring_task_collection_ref_id=recurring_task_collection_ref_id,
            _name=name,
            _period=period,
            _the_type=the_type or RecurringTaskType.CHORE,
            _gen_params=gen_params,
            _must_do=must_do,
            _skip_rule=skip_rule,
            _start_at_date=start_at_date if start_at_date else today,
            _end_at_date=end_at_date,
            _suspended=suspended)
        recurring_task.record_event(Event2.make_event_from_frame_args(RecurringTask.Created, created_time))

        return recurring_task

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'RecurringTask':
        """Change the name."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(Event2.make_event_from_frame_args(RecurringTask.Updated, modification_time))
        return self

    def change_period(self, period: RecurringTaskPeriod, modification_time: Timestamp) -> 'RecurringTask':
        """Change the period."""
        if self._period == period:
            return self
        self._period = period
        self.record_event(Event2.make_event_from_frame_args(RecurringTask.Updated, modification_time))
        return self

    def change_type(self, the_type: RecurringTaskType, modification_time: Timestamp) -> 'RecurringTask':
        """Change the type."""
        if self._the_type == the_type:
            return self
        self._the_type = the_type
        self.record_event(Event2.make_event_from_frame_args(RecurringTask.Updated, modification_time))
        return self

    def change_gen_params(self, gen_params: RecurringTaskGenParams, modification_time: Timestamp) -> 'RecurringTask':
        """Change the generation params."""
        RecurringTask._check_actionable_and_due_date_configs(
            gen_params.actionable_from_day, gen_params.actionable_from_month,
            gen_params.due_at_day, gen_params.due_at_month)
        if self._gen_params == gen_params:
            return self
        self._gen_params = gen_params
        self.record_event(Event2.make_event_from_frame_args(RecurringTask.Updated, modification_time))
        return self

    def change_must_do(self, must_do: bool, modification_time: Timestamp) -> 'RecurringTask':
        """Change the must do status."""
        if self._must_do == must_do:
            return self
        self._must_do = must_do
        self.record_event(Event2.make_event_from_frame_args(RecurringTask.Updated, modification_time))
        return self

    def change_skip_rule(
            self, skip_rule: Optional[RecurringTaskSkipRule], modification_time: Timestamp) -> 'RecurringTask':
        """Change the skip rule."""
        if self._skip_rule == skip_rule:
            return self
        self._skip_rule = skip_rule
        self.record_event(Event2.make_event_from_frame_args(RecurringTask.Updated, modification_time))
        return self

    def change_active_interval(
            self, start_at_date: ADate, end_at_date: Optional[ADate], modification_time: Timestamp) -> 'RecurringTask':
        """Change the active interval."""
        today = ADate.from_date(modification_time.as_date())
        if end_at_date is not None and start_at_date >= end_at_date:
            raise InputValidationError(f"Start date {start_at_date} is after end date {end_at_date}")
        if end_at_date is not None and end_at_date < today:
            raise InputValidationError(f"End date {end_at_date} is before start date {today}")
        if self._start_at_date == start_at_date and self._end_at_date == end_at_date:
            return self
        self._start_at_date = start_at_date
        self._end_at_date = end_at_date
        self.record_event(Event2.make_event_from_frame_args(RecurringTask.Updated, modification_time))
        return self

    def change_suspended(self, suspended: bool, modification_time: Timestamp) -> 'RecurringTask':
        """Change the suspended time."""
        if self._suspended == suspended:
            return self
        self._suspended = suspended
        self.record_event(Event2.make_event_from_frame_args(RecurringTask.Updated, modification_time))
        return self

    def is_in_active_interval(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this active interval."""
        recurring_task_start_date = self._start_at_date
        recurring_task_end_date = self._end_at_date.end_of_day() if self._end_at_date else None

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
        return self._recurring_task_collection_ref_id

    @property
    def recurring_task_collection_ref_id(self) -> EntityId:
        """The recurring task collection this one belongs to."""
        # TODO(horia141): fix this uglyness
        return self._recurring_task_collection_ref_id

    @property
    def name(self) -> EntityName:
        """The name."""
        return self._name

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period."""
        return self._period

    @property
    def the_type(self) -> RecurringTaskType:
        """The type of the task."""
        return self._the_type

    @property
    def gen_params(self) -> RecurringTaskGenParams:
        """The gen params."""
        return self._gen_params

    @property
    def suspended(self) -> bool:
        """Whether the task is suspended or not."""
        return self._suspended

    @property
    def skip_rule(self) -> Optional[RecurringTaskSkipRule]:
        """A skip rule for the task."""
        return self._skip_rule

    @property
    def must_do(self) -> bool:
        """The must do status for the task."""
        return self._must_do

    @property
    def start_at_date(self) -> ADate:
        """When the recurring task is usable."""
        return self._start_at_date

    @property
    def end_at_date(self) -> Optional[ADate]:
        """When the recurring task should not generate inbox tasks anymore."""
        return self._end_at_date

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
