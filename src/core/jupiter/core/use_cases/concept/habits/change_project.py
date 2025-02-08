"""The command for changing the project for a habit."""
from typing import cast

from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core import schedules
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class HabitChangeProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    project_ref_id: EntityId


@mutation_use_case([WorkspaceFeature.HABITS, WorkspaceFeature.PROJECTS])
class HabitChangeProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[HabitChangeProjectArgs, None]
):
    """The command for changing the project of a habit."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HabitChangeProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.project_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        habit = await uow.get_for(Habit).load_by_id(args.ref_id)

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        all_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            habit_ref_id=[args.ref_id],
        )

        await uow.get_for(Project).load_by_id(args.project_ref_id)

        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                habit.gen_params.period,
                habit.name,
                cast(Timestamp, inbox_task.recurring_gen_right_now),
                habit.gen_params.skip_rule,
                habit.gen_params.actionable_from_day,
                habit.gen_params.actionable_from_month,
                habit.gen_params.due_at_day,
                habit.gen_params.due_at_month,
            )

            inbox_task = inbox_task.update_link_to_habit(
                context.domain_context,
                project_ref_id=args.project_ref_id,
                name=schedule.full_name,
                timeline=schedule.timeline,
                repeat_index=inbox_task.recurring_repeat_index,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_date,
                eisen=habit.gen_params.eisen,
                difficulty=habit.gen_params.difficulty,
            )

            await uow.get_for(InboxTask).save(inbox_task)
            await progress_reporter.mark_updated(inbox_task)

        habit = habit.change_project(
            context.domain_context,
            project_ref_id=args.project_ref_id,
        )
        await uow.get_for(Habit).save(habit)
        await progress_reporter.mark_updated(habit)
