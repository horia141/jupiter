"""Use case for archiving a note."""

from jupiter.core.domain.app import AppCore
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class NoteArchiveArgs(UseCaseArgsBase):
    """NoteArchive args."""

    ref_id: EntityId


@mutation_use_case(exclude_app=[AppCore.CLI])
class NoteArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[NoteArchiveArgs, None]
):
    """Use case for archiving a note."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: NoteArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        note = await uow.get_for(Note).load_by_id(args.ref_id)
        await NoteArchiveService().archive(context.domain_context, uow, note)
