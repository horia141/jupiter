"""A habit."""
from jupiter.core.domain.concept.habits.habit_name import HabitName
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
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
class Habit(LeafEntity):
    """A habit."""

    habit_collection: ParentLink
    project_ref_id: EntityId
    name: HabitName
    gen_params: RecurringTaskGenParams
    suspended: bool
    repeats_in_period_count: int | None

    inbox_tasks = OwnsMany(
        InboxTask, source=InboxTaskSource.HABIT, source_entity_ref_id=IsRefId()
    )
    note = OwnsAtMostOne(Note, domain=NoteDomain.HABIT, source_entity_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_habit(
        ctx: DomainContext,
        habit_collection_ref_id: EntityId,
        project_ref_id: EntityId,
        name: HabitName,
        gen_params: RecurringTaskGenParams,
        repeats_in_period_count: int | None,
        suspended: bool,
    ) -> "Habit":
        """Create a habit."""
        if repeats_in_period_count is not None:
            if gen_params.period == RecurringTaskPeriod.DAILY:
                raise InputValidationError("Repeats for daily habits are not allowed")
            if repeats_in_period_count < 2:
                raise InputValidationError(
                    "Repeats in period needs to be strictly greater than 1 if specified",
                )

        return Habit._create(
            ctx,
            habit_collection=ParentLink(habit_collection_ref_id),
            project_ref_id=project_ref_id,
            name=name,
            gen_params=gen_params,
            repeats_in_period_count=repeats_in_period_count,
            suspended=suspended,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[HabitName],
        project_ref_id: UpdateAction[EntityId],
        gen_params: UpdateAction[RecurringTaskGenParams],
        repeats_in_period_count: UpdateAction[int | None],
    ) -> "Habit":
        """Update the habit."""
        if gen_params.should_change:
            the_gen_params = gen_params.just_the_value
        else:
            the_gen_params = self.gen_params

        if (
            repeats_in_period_count.should_change
            and repeats_in_period_count.just_the_value is not None
        ):
            if the_gen_params.period == RecurringTaskPeriod.DAILY:
                raise InputValidationError("Repeats for daily habits are not allowed")
            if repeats_in_period_count.just_the_value < 2:
                raise InputValidationError(
                    "Repeats in period needs to be strictly greater than 1 if specified",
                )

        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            project_ref_id=project_ref_id.or_else(self.project_ref_id),
            gen_params=the_gen_params,
            repeats_in_period_count=repeats_in_period_count.or_else(
                self.repeats_in_period_count,
            ),
        )

    @update_entity_action
    def suspend(self, ctx: DomainContext) -> "Habit":
        """Suspend the habit."""
        if self.suspended:
            return self
        return self._new_version(
            ctx,
            suspended=True,
        )

    @update_entity_action
    def unsuspend(self, ctx: DomainContext) -> "Habit":
        """Unsuspend the habit."""
        if not self.suspended:
            return self
        return self._new_version(
            ctx,
            suspended=False,
        )
