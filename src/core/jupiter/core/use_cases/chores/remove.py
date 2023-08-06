"""The command for removing a chore."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.chores.service.remove_service import ChoreRemoveService
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
class ChoreRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class ChoreRemoveUseCase(AppLoggedInMutationUseCase[ChoreRemoveArgs, None]):
    """The command for removing a chore."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.CHORES

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await ChoreRemoveService(
            self._domain_storage_engine,
        ).remove(progress_reporter, args.ref_id)
