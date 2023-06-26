"""The command for archiving a chore."""
from dataclasses import dataclass

from jupiter.core.domain.chores.service.archive_service import ChoreArchiveService
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class ChoreArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class ChoreArchiveUseCase(AppLoggedInMutationUseCase[ChoreArchiveArgs, None]):
    """The command for archiving a chore."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            chore = await uow.chore_repository.load_by_id(args.ref_id)
        await ChoreArchiveService(
            EventSource.CLI,
            self._time_provider,
            self._storage_engine,
        ).do_it(progress_reporter, chore)