"""The command for archiving a big plan milestone."""

from jupiter.core.domain.concept.big_plans.big_plan_milestone import BigPlanMilestone
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_crown_archiver import generic_crown_archiver
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class BigPlanMilestoneArchiveArgs(UseCaseArgsBase):
    """Big plan milestone archive args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanMilestoneArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanMilestoneArchiveArgs, None]
):
    """The command for archiving a big plan milestone."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: BigPlanMilestoneArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        await generic_crown_archiver(
            context.domain_context,
            uow,
            progress_reporter,
            BigPlanMilestone,
            args.ref_id,
            ArchivalReason.USER,
        )
