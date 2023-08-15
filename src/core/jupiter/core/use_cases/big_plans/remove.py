"""The command for removing a big plan."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.big_plans.service.remove_service import BigPlanRemoveService
from jupiter.core.domain.features import Feature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class BigPlanRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class BigPlanRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanRemoveArgs, None]
):
    """The command for removing a big plan."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.BIG_PLANS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await BigPlanRemoveService().remove(
            uow, progress_reporter, context.workspace, args.ref_id
        )
