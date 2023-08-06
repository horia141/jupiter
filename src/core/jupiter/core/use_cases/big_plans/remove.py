"""The command for removing a big plan."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.big_plans.service.remove_service import BigPlanRemoveService
from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class BigPlanRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class BigPlanRemoveUseCase(AppLoggedInMutationUseCase[BigPlanRemoveArgs, None]):
    """The command for removing a big plan."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.BIG_PLANS

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await BigPlanRemoveService(
            self._domain_storage_engine,
        ).remove(progress_reporter, context.workspace, args.ref_id)
