"""The command for archiving a chore."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.chores.service.archive_service import ChoreArchiveService
from jupiter.core.domain.features import Feature
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

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.CHORES

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            chore = await uow.chore_repository.load_by_id(args.ref_id)
        await ChoreArchiveService(
            EventSource.CLI,
            self._time_provider,
            self._domain_storage_engine,
        ).do_it(progress_reporter, chore)
