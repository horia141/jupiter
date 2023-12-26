"""The command for changing the project for a habit."""
from dataclasses import dataclass
from typing import Optional, cast

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
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@dataclass
class HabitChangeProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    project_ref_id: Optional[EntityId] = None


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
        user = context.user
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.project_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

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
                context.domain_context,
                project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
                name=schedule.full_name,
                timeline=schedule.timeline,
                repeat_index=inbox_task.recurring_repeat_index,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_time,
                eisen=habit.gen_params.eisen,
                difficulty=habit.gen_params.difficulty,
            )

            await uow.inbox_task_repository.save(inbox_task)
            await progress_reporter.mark_updated(inbox_task)

        habit = habit.change_project(
            context.domain_context,
            project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
        )
        await uow.habit_repository.save(habit)
        await progress_reporter.mark_updated(habit)
