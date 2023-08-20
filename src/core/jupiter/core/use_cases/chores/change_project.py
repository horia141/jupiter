"""The command for changing the project for a chore."""
from dataclasses import dataclass
from typing import Iterable, Optional, cast

from jupiter.core.domain import schedules
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class ChoreChangeProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    project_ref_id: Optional[EntityId] = None


class ChoreChangeProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreChangeProjectArgs, None]
):
    """The command for changing the project of a chore."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return (WorkspaceFeature.CHORES, WorkspaceFeature.PROJECTS)

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreChangeProjectArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        chore = await uow.chore_repository.load_by_id(args.ref_id)

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            filter_chore_ref_ids=[args.ref_id],
        )

        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                chore.gen_params.period,
                chore.name,
                cast(Timestamp, inbox_task.recurring_gen_right_now),
                user.timezone,
                chore.skip_rule,
                chore.gen_params.actionable_from_day,
                chore.gen_params.actionable_from_month,
                chore.gen_params.due_at_time,
                chore.gen_params.due_at_day,
                chore.gen_params.due_at_month,
            )

            inbox_task = inbox_task.update_link_to_chore(
                project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
                name=schedule.full_name,
                timeline=schedule.timeline,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_time,
                eisen=chore.gen_params.eisen,
                difficulty=chore.gen_params.difficulty,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )
            await uow.inbox_task_repository.save(inbox_task)
            await progress_reporter.mark_updated(inbox_task)

        chore = chore.change_project(
            project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )
        await uow.chore_repository.save(chore)
        await progress_reporter.mark_updated(chore)
