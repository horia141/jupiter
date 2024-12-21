"""The command for hard removing a metric."""

from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.domain.concept.metrics.service.remove_service import (
    MetricRemoveService,
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
class MetricRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.METRICS)
class MetricRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricRemoveArgs, None]
):
    """The command for removing a metric."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        metric = await uow.get_for(Metric).load_by_id(args.ref_id, allow_archived=True)

        await MetricRemoveService().execute(
            context.domain_context, uow, progress_reporter, workspace, metric
        )
