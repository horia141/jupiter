"""The command for removing a chore."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.chores.service.remove_service import ChoreRemoveService
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
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
class ChoreRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class ChoreRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreRemoveArgs, None]
):
    """The command for removing a chore."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.CHORES

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await ChoreRemoveService().remove(uow, progress_reporter, args.ref_id)
