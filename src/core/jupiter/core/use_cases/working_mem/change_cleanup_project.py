"""Update the metrics collection project."""
from typing import cast

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.working_mem.working_mem import WorkingMem
from jupiter.core.domain.working_mem.working_mem_collection import WorkingMemCollection
from jupiter.core.framework.base.entity_id import EntityId
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
class WorkingMemChangeCleanUpProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    cleanup_project_ref_id: EntityId


@mutation_use_case([WorkspaceFeature.WORKING_MEM, WorkspaceFeature.PROJECTS])
class WorkingMemChangeCleanUpProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkingMemChangeCleanUpProjectArgs, None],
):
    """The command for updating the collection up project for working mem."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: WorkingMemChangeCleanUpProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        working_mem_collection = await uow.get_for(WorkingMemCollection).load_by_parent(
            workspace.ref_id,
        )
        old_catch_up_project_ref_id = working_mem_collection.cleanup_project_ref_id

        await uow.get_for(Project).load_by_id(
            args.cleanup_project_ref_id,
        )

        working_mems = await uow.get_for(WorkingMem).find_all(
            parent_ref_id=working_mem_collection.ref_id,
            allow_archived=False,
        )

        if (
            old_catch_up_project_ref_id != args.cleanup_project_ref_id
            and len(working_mems) > 0
        ):
            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(
                workspace.ref_id,
            )
            all_collection_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=[InboxTaskSource.WORKING_MEM_CLEANUP],
                working_mem_ref_id=[m.ref_id for m in working_mems],
            )

            for inbox_task in all_collection_inbox_tasks:
                inbox_task = inbox_task.update_link_to_working_mem_cleanup(
                    context.domain_context,
                    project_ref_id=args.cleanup_project_ref_id,
                    name=inbox_task.name,
                    due_date=cast(ADate, inbox_task.due_date),
                    recurring_timeline=cast(str, inbox_task.recurring_timeline),
                )

                inbox_task = await uow.get_for(InboxTask).save(
                    inbox_task,
                )
                await progress_reporter.mark_updated(inbox_task)

            working_mem_collection = working_mem_collection.change_cleanup_project(
                context.domain_context,
                cleanup_project_ref_id=args.cleanup_project_ref_id,
            )

            await uow.get_for(WorkingMemCollection).save(working_mem_collection)
