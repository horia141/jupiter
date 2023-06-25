"""The command for removing a chore."""
from dataclasses import dataclass

from jupiter.core.domain.chores.service.remove_service import ChoreRemoveService
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
class ChoreRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class ChoreRemoveUseCase(AppLoggedInMutationUseCase[ChoreRemoveArgs, None]):
    """The command for removing a chore."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await ChoreRemoveService(
            self._storage_engine,
        ).remove(progress_reporter, args.ref_id)
