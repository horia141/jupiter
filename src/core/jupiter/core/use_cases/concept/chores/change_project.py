"""The command for changing the project for a chore."""
from typing import cast

from jupiter.core.domain.concept.chores.chore import Chore
from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core import schedules
from jupiter.core.domain.features import WorkspaceFeature
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
class ChoreChangeProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    project_ref_id: EntityId


@mutation_use_case([WorkspaceFeature.CHORES, WorkspaceFeature.PROJECTS])
class ChoreChangeProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreChangeProjectArgs, None]
):
    """The command for changing the project of a chore."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ChoreChangeProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        chore = await uow.get_for(Chore).load_by_id(args.ref_id)

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        all_inbox_tasks = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.CHORE,
            source_entity_ref_id=args.ref_id,
        )

        await uow.get_for(Project).load_by_id(args.project_ref_id)

        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                chore.gen_params.period,
                chore.name,
                cast(Timestamp, inbox_task.recurring_gen_right_now),
                chore.gen_params.skip_rule,
                chore.gen_params.actionable_from_day,
                chore.gen_params.actionable_from_month,
                chore.gen_params.due_at_day,
                chore.gen_params.due_at_month,
            )

            inbox_task = inbox_task.update_link_to_chore(
                ctx=context.domain_context,
                project_ref_id=args.project_ref_id,
                name=schedule.full_name,
                timeline=schedule.timeline,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_date,
                eisen=chore.gen_params.eisen,
                difficulty=chore.gen_params.difficulty,
            )
            await uow.get_for(InboxTask).save(inbox_task)
            await progress_reporter.mark_updated(inbox_task)

        chore = chore.change_project(
            ctx=context.domain_context,
            project_ref_id=args.project_ref_id,
        )
        await uow.get_for(Chore).save(chore)
        await progress_reporter.mark_updated(chore)
