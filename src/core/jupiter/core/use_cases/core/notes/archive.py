"""Use case for archiving a note."""
from dataclasses import dataclass

from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class NoteArchiveArgs(UseCaseArgsBase):
    """NoteArchive args."""

    ref_id: EntityId


class NoteArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[NoteArchiveArgs, None]
):
    """Use case for archiving a note."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: NoteArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        note = await uow.note_repository.load_by_id(args.ref_id)
        await NoteArchiveService(
            EventSource.CLI,
            self._time_provider,
        ).archive(uow, note)
