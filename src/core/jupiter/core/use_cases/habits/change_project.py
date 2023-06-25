"""The command for changing the project for a habit."""
from dataclasses import dataclass
from typing import Optional, cast

from jupiter.core.domain import schedules
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class HabitChangeProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    project_ref_id: Optional[EntityId] = None


class HabitChangeProjectUseCase(
    AppLoggedInMutationUseCase[HabitChangeProjectArgs, None]
):
    """The command for changing the project of a habit."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HabitChangeProjectArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            habit = await uow.habit_repository.load_by_id(args.ref_id)

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_habit_ref_ids=[args.ref_id],
            )

        for inbox_task in all_inbox_tasks:
            async with progress_reporter.start_updating_entity(
                "inbox task",
                inbox_task.ref_id,
                str(inbox_task.name),
            ) as entity_reporter:
                async with self._storage_engine.get_unit_of_work() as uow:
                    schedule = schedules.get_schedule(
                        habit.gen_params.period,
                        habit.name,
                        cast(Timestamp, inbox_task.recurring_gen_right_now),
                        user.timezone,
                        habit.skip_rule,
                        habit.gen_params.actionable_from_day,
                        habit.gen_params.actionable_from_month,
                        habit.gen_params.due_at_time,
                        habit.gen_params.due_at_day,
                        habit.gen_params.due_at_month,
                    )

                    inbox_task = inbox_task.update_link_to_habit(
                        project_ref_id=args.project_ref_id
                        or workspace.default_project_ref_id,
                        name=schedule.full_name,
                        timeline=schedule.timeline,
                        repeat_index=inbox_task.recurring_repeat_index,
                        actionable_date=schedule.actionable_date,
                        due_date=schedule.due_time,
                        eisen=habit.gen_params.eisen,
                        difficulty=habit.gen_params.difficulty,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    await entity_reporter.mark_known_name(str(inbox_task.name))

                    await uow.inbox_task_repository.save(inbox_task)
                    await entity_reporter.mark_local_change()

        async with progress_reporter.start_updating_entity(
            "habit",
            args.ref_id,
            str(habit.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                habit = habit.change_project(
                    project_ref_id=args.project_ref_id
                    or workspace.default_project_ref_id,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                await uow.habit_repository.save(habit)
                await entity_reporter.mark_local_change()
