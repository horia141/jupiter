"""A chore."""

from jupiter.core.domain.chores.chore_name import ChoreName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    OwnsMany,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction


@entity
class Chore(LeafEntity):
    """A chore."""

    chore_collection: ParentLink
    project_ref_id: EntityId
    name: ChoreName
    gen_params: RecurringTaskGenParams
    suspended: bool
    must_do: bool
    start_at_date: ADate
    end_at_date: ADate | None
    skip_rule: RecurringTaskSkipRule | None

    inbox_tasks = OwnsMany(
        InboxTask, source=InboxTaskSource.CHORE, chore_ref_id=IsRefId()
    )
    note = OwnsAtMostOne(Note, domain=NoteDomain.CHORE, source_entity_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_chore(
        ctx: DomainContext,
        chore_collection_ref_id: EntityId,
        project_ref_id: EntityId,
        name: ChoreName,
        gen_params: RecurringTaskGenParams,
        start_at_date: ADate | None,
        end_at_date: ADate | None,
        skip_rule: RecurringTaskSkipRule | None,
        suspended: bool,
        must_do: bool,
    ) -> "Chore":
        """Create a chore."""
        today = ADate.from_date(ctx.action_timestamp.as_date())
        Chore._check_actionable_and_due_date_configs(
            gen_params.period,
            gen_params.actionable_from_day,
            gen_params.actionable_from_month,
            gen_params.due_at_day,
            gen_params.due_at_month,
        )

        if (
            start_at_date is not None
            and end_at_date is not None
            and start_at_date >= end_at_date
        ):
            raise InputValidationError(
                f"Start date {start_at_date} is after {end_at_date}",
            )
        if start_at_date is None and end_at_date is not None and end_at_date < today:
            raise InputValidationError(f"End date {end_at_date} is before {today}")

        return Chore._create(
            ctx,
            chore_collection=ParentLink(chore_collection_ref_id),
            project_ref_id=project_ref_id,
            name=name,
            gen_params=gen_params,
            suspended=suspended,
            must_do=must_do,
            skip_rule=skip_rule,
            start_at_date=start_at_date if start_at_date else today,
            end_at_date=end_at_date,
        )

    @update_entity_action
    def change_project(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
    ) -> "Chore":
        """Change the project for the chore task."""
        if self.project_ref_id == project_ref_id:
            return self
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[ChoreName],
        gen_params: UpdateAction[RecurringTaskGenParams],
        must_do: UpdateAction[bool],
        start_at_date: UpdateAction[ADate],
        end_at_date: UpdateAction[ADate | None],
        skip_rule: UpdateAction[RecurringTaskSkipRule | None],
    ) -> "Chore":
        """Update the chore."""
        if gen_params.should_change:
            Chore._check_actionable_and_due_date_configs(
                gen_params.just_the_value.period,
                gen_params.just_the_value.actionable_from_day,
                gen_params.just_the_value.actionable_from_month,
                gen_params.just_the_value.due_at_day,
                gen_params.just_the_value.due_at_month,
            )
            the_gen_params = gen_params.just_the_value
        else:
            the_gen_params = self.gen_params

        if start_at_date.should_change or end_at_date.should_change:
            the_start_at_date = start_at_date.or_else(self.start_at_date)
            the_end_at_date = end_at_date.or_else(self.end_at_date)
            if the_end_at_date is not None and the_start_at_date >= the_end_at_date:
                raise InputValidationError(
                    f"Start date {the_start_at_date} is after end date {the_end_at_date}",
                )
        else:
            the_start_at_date = self.start_at_date
            the_end_at_date = self.end_at_date

        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            gen_params=the_gen_params,
            must_do=must_do.or_else(self.must_do),
            start_at_date=the_start_at_date,
            end_at_date=the_end_at_date,
            skip_rule=skip_rule.or_else(self.skip_rule),
        )

    @update_entity_action
    def suspend(self, ctx: DomainContext) -> "Chore":
        """Suspend the chore."""
        if self.suspended:
            return self
        return self._new_version(
            ctx,
            suspended=True,
        )

    @update_entity_action
    def unsuspend(self, ctx: DomainContext) -> "Chore":
        """Unsuspend the chore."""
        if not self.suspended:
            return self
        return self._new_version(
            ctx,
            suspended=False,
        )

    def is_in_active_interval(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this active interval."""
        chore_start_date = self.start_at_date
        chore_end_date = self.end_at_date if self.end_at_date else None

        if chore_end_date is None:
            # Just a start date interval, so at least the end date should be in it
            return end_date >= chore_start_date
        else:
            # Both a start date and an end date are present. At least one of the start date or end date of
            # the interval we're comparing against should be in this interval.
            return (
                chore_start_date <= start_date <= chore_end_date
                or chore_start_date <= end_date <= chore_end_date
            )

    @staticmethod
    def _check_actionable_and_due_date_configs(
        period: RecurringTaskPeriod,
        actionable_from_day: RecurringTaskDueAtDay | None,
        actionable_from_month: RecurringTaskDueAtMonth | None,
        due_at_day: RecurringTaskDueAtDay | None,
        due_at_month: RecurringTaskDueAtMonth | None,
    ) -> None:
        actionable_from_day = actionable_from_day or RecurringTaskDueAtDay.first_of(
            period
        )
        actionable_from_month = (
            actionable_from_month or RecurringTaskDueAtMonth.first_of(period)
        )
        due_at_day = due_at_day or RecurringTaskDueAtDay.end_of(period)
        due_at_month = due_at_month or RecurringTaskDueAtMonth.end_of(period)
        if actionable_from_month.as_int() > due_at_month.as_int():
            raise InputValidationError(
                f"Actionable month {actionable_from_month} should be before due month {due_at_month}",
            )
        if (
            actionable_from_month == due_at_month
            and actionable_from_day.as_int() > due_at_day.as_int()
        ):
            raise InputValidationError(
                f"Actionable day {actionable_from_day} should be before due day {due_at_day}",
            )
