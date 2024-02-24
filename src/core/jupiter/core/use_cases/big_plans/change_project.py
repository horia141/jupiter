"""The command for changing the project for a big plan."""
from typing import Optional
from jupiter.core.domain.big_plans.big_plan import BigPlan

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class BigPlanChangeProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    project_ref_id: Optional[EntityId] = None


@mutation_use_case([WorkspaceFeature.BIG_PLANS, WorkspaceFeature.PROJECTS])
class BigPlanChangeProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanChangeProjectArgs, None]
):
    """The command for changing the project of a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: BigPlanChangeProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        big_plan = await uow.repository_for(BigPlan).load_by_id(args.ref_id)
        big_plan = big_plan.change_project(
            context.domain_context,
            project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
        )

        await uow.repository_for(BigPlan).save(big_plan)
        await progress_reporter.mark_updated(big_plan)

        inbox_task_collection = (
            await uow.repository_for(InboxTaskCollection).load_by_parent(
                workspace.ref_id,
            )
        )
        all_inbox_tasks = await uow.repository_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            big_plan_ref_id=[big_plan.ref_id],
        )

        for inbox_task in all_inbox_tasks:
            inbox_task = inbox_task.update_link_to_big_plan(
                context.domain_context,
                big_plan.project_ref_id,
                big_plan.ref_id,
            )
            await uow.repository_for(InboxTask).save(inbox_task)
            await progress_reporter.mark_updated(inbox_task)
