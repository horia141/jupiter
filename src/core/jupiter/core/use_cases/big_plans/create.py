"""The command for creating a big plan."""
from typing import Optional

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class BigPlanCreateArgs(UseCaseArgsBase):
    """Big plan create args."""

    name: BigPlanName
    project_ref_id: Optional[EntityId] = None
    actionable_date: Optional[ADate] = None
    due_date: Optional[ADate] = None


@use_case_result
class BigPlanCreateResult(UseCaseResultBase):
    """Big plan create result."""

    new_big_plan: BigPlan


@mutation_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanCreateArgs, BigPlanCreateResult]
):
    """The command for creating a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: BigPlanCreateArgs,
    ) -> BigPlanCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.project_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        big_plan_collection = await uow.big_plan_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        new_big_plan = BigPlan.new_big_plan(
            context.domain_context,
            big_plan_collection_ref_id=big_plan_collection.ref_id,
            project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
            name=args.name,
            status=BigPlanStatus.ACCEPTED,
            actionable_date=args.actionable_date,
            due_date=args.due_date,
        )
        new_big_plan = await uow.big_plan_repository.create(new_big_plan)
        await progress_reporter.mark_created(new_big_plan)

        return BigPlanCreateResult(new_big_plan=new_big_plan)
