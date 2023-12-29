"""Use case for loading big plans."""

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class BigPlanLoadArgs(UseCaseArgsBase):
    """BigPlanLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class BigPlanLoadResult(UseCaseResultBase):
    """BigPlanLoadResult."""

    big_plan: BigPlan
    project: Project
    inbox_tasks: list[InboxTask]


@readonly_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[BigPlanLoadArgs, BigPlanLoadResult]
):
    """The use case for loading a particular big plan."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: BigPlanLoadArgs,
    ) -> BigPlanLoadResult:
        """Execute the command's action."""
        workspace = context.workspace

        big_plan = await uow.big_plan_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        project = await uow.project_repository.load_by_id(big_plan.project_ref_id)
        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            filter_big_plan_ref_ids=[args.ref_id],
        )

        return BigPlanLoadResult(
            big_plan=big_plan, project=project, inbox_tasks=inbox_tasks
        )
