"""The command for archiving a habit."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.habits.service.archive_service import HabitArchiveService
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
class HabitArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class HabitArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[HabitArchiveArgs, None]
):
    """The command for archiving a habit."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.HABITS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HabitArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        habit = await uow.habit_repository.load_by_id(args.ref_id)
        await HabitArchiveService(
            EventSource.CLI,
            self._time_provider,
        ).do_it(uow, progress_reporter, habit)
