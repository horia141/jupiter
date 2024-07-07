"""The command for archiving a big plan."""

from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.service.archive_service import (
    BigPlanArchiveService,
)
from jupiter.core.domain.features import WorkspaceFeature
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
class BigPlanArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanArchiveArgs, None]
):
    """The command for archiving a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: BigPlanArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        big_plan = await uow.get_for(BigPlan).load_by_id(args.ref_id)

        await BigPlanArchiveService().do_it(
            context.domain_context, uow, progress_reporter, big_plan
        )
