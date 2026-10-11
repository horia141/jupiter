"""A habit."""

from jupiter.core.apps.habits.repeats_strategy import (
    HabitRepeatsStrategy,
)
from jupiter.core.apps.habits.streak_mark import HabitStreakMark
from jupiter.core.apps.habits.sub.habit.name import HabitName
from jupiter.core.apps.habits.sub.streak_inactive_period.root import (
    HabitStreakInactivePeriod,
)
from jupiter.core.common.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.common.recurring_task_period import RecurringTaskPeriod
from jupiter.core.common.scheduling_params import SchedulingParams
from jupiter.core.common.sub.inbox_tasks.root import InboxTask
from jupiter.core.common.sub.locations.sub.link.root import LocationLink
from jupiter.core.common.sub.notes.root import Note
from jupiter.core.common.sub.publish.sub.entity.root import PublishEntity
from jupiter.core.common.sub.tags.sub.link.root import TagLink
from jupiter.core.common.sub.time_events.sub.in_day_block.root import (
    TimeEventInDayBlock,
)
from jupiter.core.named_entity_tag import NamedEntityTag
from jupiter.framework.base.adate import ADate
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.context import DomainContext
from jupiter.framework.entity import (
    IsEntityLinkStd,
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    OwnsMany,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.framework.errors import InputValidationError
from jupiter.framework.record import ContainsManyRecords
from jupiter.framework.update_action import UpdateAction


@entity("HabitCollection")
class Habit(LeafEntity):
    """A habit."""

    habit_collection: ParentLink
    aspect_ref_id: EntityId
    chapter_ref_id: EntityId | None
    goal_ref_id: EntityId | None
    stack_ref_id: EntityId | None
    name: HabitName
    is_key: bool
    gen_params: RecurringTaskGenParams
    scheduling_params: SchedulingParams
    suspended: bool
    repeats_strategy: HabitRepeatsStrategy | None
    repeats_in_period_count: int | None

    inbox_tasks = OwnsMany(
        InboxTask,
        owner=IsEntityLinkStd(NamedEntityTag.HABIT.value),
    )
    time_event_in_day_blocks = OwnsMany(
        TimeEventInDayBlock,
        owner=IsEntityLinkStd(NamedEntityTag.HABIT.value),
    )
    tag_link = OwnsAtMostOne(TagLink, owner=IsEntityLinkStd(NamedEntityTag.HABIT.value))
    location_link = OwnsAtMostOne(
        LocationLink, owner=IsEntityLinkStd(NamedEntityTag.HABIT.value)
    )
    note = OwnsAtMostOne(Note, owner=IsEntityLinkStd(NamedEntityTag.HABIT.value))
    publish_entity = OwnsAtMostOne(
        PublishEntity, owner=IsEntityLinkStd(NamedEntityTag.HABIT.value)
    )
    streak_marks = ContainsManyRecords(
        HabitStreakMark,
        habit_ref_id=IsRefId(),
    )
    streak_inactive_periods = OwnsMany(
        HabitStreakInactivePeriod,
        habit_ref_id=IsRefId(),
    )

    @staticmethod
    @create_entity_action
    def new_habit(
        ctx: DomainContext,
        habit_collection_ref_id: EntityId,
        aspect_ref_id: EntityId,
        chapter_ref_id: EntityId | None,
        goal_ref_id: EntityId | None,
        stack_ref_id: EntityId | None,
        name: HabitName,
        is_key: bool,
        gen_params: RecurringTaskGenParams,
        scheduling_params: SchedulingParams,
        suspended: bool,
        repeats_strategy: HabitRepeatsStrategy | None,
        repeats_in_period_count: int | None,
    ) -> "Habit":
        """Create a habit."""
        if repeats_in_period_count is not None:
            if gen_params.period == RecurringTaskPeriod.DAILY:
                raise InputValidationError("Repeats for daily habits are not allowed")
            if repeats_in_period_count < 2:
                raise InputValidationError(
                    "Repeats in period needs to be strictly greater than 1 if specified",
                )
        if repeats_strategy is not None and repeats_in_period_count is None:
            raise InputValidationError(
                "Repeats in period count is required if repeats strategy is specified"
            )
        if repeats_in_period_count is not None and repeats_strategy is None:
            raise InputValidationError(
                "Repeats strategy is required if repeats in period is specified",
            )

        return Habit._create(
            ctx,
            habit_collection=ParentLink(habit_collection_ref_id),
            aspect_ref_id=aspect_ref_id,
            chapter_ref_id=chapter_ref_id,
            goal_ref_id=goal_ref_id,
            stack_ref_id=stack_ref_id,
            name=name,
            is_key=is_key,
            gen_params=gen_params,
            scheduling_params=scheduling_params,
            suspended=suspended,
            repeats_strategy=repeats_strategy,
            repeats_in_period_count=repeats_in_period_count,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[HabitName],
        aspect_ref_id: UpdateAction[EntityId],
        chapter_ref_id: UpdateAction[EntityId | None],
        goal_ref_id: UpdateAction[EntityId | None],
        stack_ref_id: UpdateAction[EntityId | None],
        is_key: UpdateAction[bool],
        gen_params: UpdateAction[RecurringTaskGenParams],
        scheduling_params: UpdateAction[SchedulingParams],
        repeats_in_period_count: UpdateAction[int | None],
        repeats_strategy: UpdateAction[HabitRepeatsStrategy | None],
        suspended: UpdateAction[bool],
    ) -> "Habit":
        """Update the habit."""
        if gen_params.should_change:
            the_gen_params = gen_params.just_the_value
            if the_gen_params.period != self.gen_params.period:
                raise InputValidationError(
                    "Habit period cannot be changed, create a new habit instead"
                )
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
        if repeats_strategy.should_change and not repeats_in_period_count.should_change:
            raise InputValidationError(
                "Repeats in period count is required if repeats strategy is specified"
            )
        if repeats_in_period_count.should_change and not repeats_strategy.should_change:
            raise InputValidationError(
                "Repeats strategy is required if repeats in period count is specified"
            )
        if repeats_strategy.should_change and repeats_in_period_count.should_change:
            if (
                repeats_strategy.just_the_value is None
                and repeats_in_period_count.just_the_value is not None
            ):
                raise InputValidationError(
                    "Repeats strategy is required if repeats in period count is specified"
                )
            if (
                repeats_strategy.just_the_value is not None
                and repeats_in_period_count.just_the_value is None
            ):
                raise InputValidationError(
                    "Repeats in period count is required if repeats strategy is specified"
                )

        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            aspect_ref_id=aspect_ref_id.or_else(self.aspect_ref_id),
            chapter_ref_id=chapter_ref_id.or_else(self.chapter_ref_id),
            goal_ref_id=goal_ref_id.or_else(self.goal_ref_id),
            stack_ref_id=stack_ref_id.or_else(self.stack_ref_id),
            is_key=is_key.or_else(self.is_key),
            gen_params=the_gen_params,
            scheduling_params=scheduling_params.or_else(self.scheduling_params),
            repeats_strategy=repeats_strategy.or_else(self.repeats_strategy),
            repeats_in_period_count=repeats_in_period_count.or_else(
                self.repeats_in_period_count,
            ),
            suspended=suspended.or_else(self.suspended),
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

    @update_entity_action
    def change_stack(
        self, ctx: DomainContext, stack_ref_id: EntityId | None
    ) -> "Habit":
        """Assign or clear the habit stack."""
        if self.stack_ref_id == stack_ref_id:
            return self
        return self._new_version(
            ctx,
            stack_ref_id=stack_ref_id,
        )

    def would_generate_in_time_plan(
        self, time_plan_start_date: ADate, time_plan_end_date: ADate
    ) -> bool:
        """Whether gen would create a habit task overlapping a time plan."""
        if self.suspended:
            return False
        return self.gen_params.would_generate_in_time_plan(
            time_plan_start_date, time_plan_end_date, self.name
        )
