"""The command for unsuspending a chore."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class ChoreUnsuspendArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class ChoreUnsuspendUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreUnsuspendArgs, None]
):
    """The command for unsuspending a chore."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.CHORES

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreUnsuspendArgs,
    ) -> None:
        """Execute the command's action."""
        chore = await uow.chore_repository.load_by_id(args.ref_id)
        chore = chore.unsuspend(
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )
        await uow.chore_repository.save(chore)
        await progress_reporter.mark_updated(chore)
