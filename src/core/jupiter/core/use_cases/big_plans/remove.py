"""The command for removing a big plan."""
from dataclasses import dataclass

from jupiter.core.domain.big_plans.service.remove_service import BigPlanRemoveService
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

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await BigPlanRemoveService(
            self._storage_engine,
        ).remove(progress_reporter, context.workspace, args.ref_id)