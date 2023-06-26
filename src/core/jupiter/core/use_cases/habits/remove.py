"""The command for removing a habit."""
from dataclasses import dataclass

from jupiter.core.domain.habits.service.remove_service import HabitRemoveService
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
class HabitRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class HabitRemoveUseCase(AppLoggedInMutationUseCase[HabitRemoveArgs, None]):
    """The command for removing a habit."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HabitRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await HabitRemoveService(
            self._storage_engine,
        ).remove(progress_reporter, args.ref_id)