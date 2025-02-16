"""Update various bits and bobs about changing the generation period."""
from typing import cast

from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.working_mem.working_mem import (
    WorkingMem,
    WorkingMemRepository,
)
from jupiter.core.domain.concept.working_mem.working_mem_collection import (
    WorkingMemCollection,
)
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.repository import EntityNotFoundError
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
class WorkingMemChangeGenerationPeriodArgs(UseCaseArgsBase):
    """WorkingMemChangeGenerationPeriodArgs."""

    generation_period: RecurringTaskPeriod


@mutation_use_case(WorkspaceFeature.WORKING_MEM)
class WorkingMemChangeGenerationPeriodUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkingMemChangeGenerationPeriodArgs, None],
):
    """The command for updating the generation period for working mem."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: WorkingMemChangeGenerationPeriodArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        working_mem_collection = await uow.get_for(WorkingMemCollection).load_by_parent(
            workspace.ref_id,
        )
        old_generation_period = working_mem_collection.generation_period
        working_mem_collection = working_mem_collection.change_generation_period(
            context.domain_context, args.generation_period
        )
        await uow.get_for(WorkingMemCollection).save(working_mem_collection)

        if old_generation_period != args.generation_period:
            try:
                current_working_mem = await uow.get(
                    WorkingMemRepository
                ).load_latest_working_mem(working_mem_collection.ref_id)
            except EntityNotFoundError:
                return
            current_working_mem = current_working_mem.change_generation_period(
                context.domain_context, args.generation_period
            )
            await uow.get_for(WorkingMem).save(current_working_mem)
            await progress_reporter.mark_updated(current_working_mem)

            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(
                workspace.ref_id,
            )
            inbox_tasks = await uow.get(
                InboxTaskRepository
            ).find_all_for_source_created_desc(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=InboxTaskSource.WORKING_MEM_CLEANUP,
                source_entity_ref_id=current_working_mem.ref_id,
            )

            for inbox_task in inbox_tasks:
                task_right_now = cast(Timestamp, inbox_task.recurring_gen_right_now)
                schedule = schedules.get_schedule(
                    working_mem_collection.generation_period,
                    EntityName("Cleanup WorkingMem.txt"),
                    task_right_now,
                    None,
                    None,
                    None,
                    None,
                    None,
                )

                inbox_task = inbox_task.update_link_to_working_mem_cleanup(
                    context.domain_context,
                    project_ref_id=working_mem_collection.cleanup_project_ref_id,
                    name=schedule.full_name,
                    due_date=schedule.due_date,
                    recurring_timeline=schedule.timeline,
                )
                await uow.get_for(InboxTask).save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)
