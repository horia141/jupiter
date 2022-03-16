"""A chore."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.adate import ADate
from jupiter.domain.chores.chore_name import ChoreName
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.entity import Entity, FIRST_VERSION, LeafEntity
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class Chore(LeafEntity):
    """A chore."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class ChangeProject(Entity.Updated):
        """Changed the project event."""

    @dataclass(frozen=True)
    class Updated(Entity.Updated):
        """Updated event."""

    @dataclass(frozen=True)
    class Suspended(Entity.Updated):
        """Suspended event."""

    @dataclass(frozen=True)
    class Unsuspended(Entity.Updated):
        """Unsuspend event."""

    chore_collection_ref_id: EntityId
    project_ref_id: EntityId
    name: ChoreName
    gen_params: RecurringTaskGenParams
    suspended: bool
    must_do: bool
    skip_rule: Optional[RecurringTaskSkipRule]
    start_at_date: ADate
    end_at_date: Optional[ADate]

    @staticmethod
    def new_chore(
            chore_collection_ref_id: EntityId, archived: bool, project_ref_id: EntityId, name: ChoreName,
            gen_params: RecurringTaskGenParams, skip_rule: Optional[RecurringTaskSkipRule],
            start_at_date: Optional[ADate], end_at_date: Optional[ADate], suspended: bool, must_do: bool,
            source: EventSource, created_time: Timestamp) -> 'Chore':
        """Create a chore."""
        today = ADate.from_date(created_time.as_date())
        Chore._check_actionable_and_due_date_configs(
            gen_params.actionable_from_day, gen_params.actionable_from_month,
            gen_params.due_at_day, gen_params.due_at_month)

        if start_at_date is not None and end_at_date is not None and start_at_date >= end_at_date:
            raise InputValidationError(f"Start date {start_at_date} is after {end_at_date}")
        if start_at_date is None and end_at_date is not None and end_at_date < today:
            raise InputValidationError(f"End date {end_at_date} is before {today}")

        chore = Chore(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[Chore.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            chore_collection_ref_id=chore_collection_ref_id,
            project_ref_id=project_ref_id,
            name=name,
            gen_params=gen_params,
            suspended=suspended,
            must_do=must_do,
            skip_rule=skip_rule,
            start_at_date=start_at_date if start_at_date else today,
            end_at_date=end_at_date)
        return chore

    def change_project(
            self, project_ref_id: EntityId, source: EventSource, modification_time: Timestamp) -> 'Chore':
        """Change the project for the chore task."""
        if self.project_ref_id == project_ref_id:
            return self
        return self._new_version(
            project_ref_id=project_ref_id,
            new_event=Chore.ChangeProject.make_event_from_frame_args(source, self.version, modification_time))

    def update(
            self, name: UpdateAction[ChoreName], gen_params: UpdateAction[RecurringTaskGenParams],
            must_do: UpdateAction[bool], skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]],
            start_at_date: UpdateAction[ADate], end_at_date: UpdateAction[Optional[ADate]], source: EventSource,
            modification_time: Timestamp) -> 'Chore':
        """Update the chore."""
        if gen_params.should_change:
            Chore._check_actionable_and_due_date_configs(
                gen_params.value.actionable_from_day, gen_params.value.actionable_from_month,
                gen_params.value.due_at_day, gen_params.value.due_at_month)
            the_gen_params = gen_params.value
        else:
            the_gen_params = self.gen_params

        if start_at_date.should_change or end_at_date.should_change:
            the_start_at_date = start_at_date.or_else(self.start_at_date)
            the_end_at_date = end_at_date.or_else(self.end_at_date)
            if the_end_at_date is not None and the_start_at_date >= the_end_at_date:
                raise InputValidationError(f"Start date {the_start_at_date} is after end date {the_end_at_date}")
        else:
            the_start_at_date = self.start_at_date
            the_end_at_date = self.end_at_date

        return self._new_version(
            name=name.or_else(self.name),
            gen_params=the_gen_params,
            must_do=must_do.or_else(self.must_do),
            skip_rule=skip_rule.or_else(self.skip_rule),
            start_at_date=the_start_at_date,
            end_at_date=the_end_at_date,
            new_event=Chore.Updated.make_event_from_frame_args(source, self.version, modification_time))

    def suspend(self, source: EventSource, modification_time: Timestamp) -> 'Chore':
        """Suspend the chore."""
        if self.suspended:
            return self
        return self._new_version(
            suspended=True,
            new_event=Chore.Suspended.make_event_from_frame_args(source, self.version, modification_time))

    def unsuspend(self, source: EventSource, modification_time: Timestamp) -> 'Chore':
        """Unsuspend the chore."""
        if not self.suspended:
            return self
        return self._new_version(
            suspended=False,
            new_event=Chore.Unsuspended.make_event_from_frame_args(source, self.version, modification_time))

    def is_in_active_interval(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this active interval."""
        chore_start_date = self.start_at_date
        chore_end_date = self.end_at_date.end_of_day() if self.end_at_date else None

        if chore_end_date is None:
            # Just a start date interval, so at least the end date should be in it
            return end_date >= chore_start_date
        else:
            # Both a start date and an end date are present. At least one of the start date or end date of
            # the interval we're comparing against should be in this interval.
            return chore_start_date <= start_date <= chore_end_date or \
                chore_start_date <= end_date <= chore_end_date

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

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.chore_collection_ref_id
