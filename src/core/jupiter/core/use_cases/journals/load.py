"""Retrieve details about a journal."""
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.journals.journal import Journal
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class JournalLoadArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class JournalLoadResult(UseCaseResultBase):
    """Result."""

    journal: Journal
    note: Note
    writing_task: InboxTask | None


@readonly_use_case(WorkspaceFeature.JOURNALS)
class JournalLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[JournalLoadArgs, JournalLoadResult]
):
    """The command for loading details about a journal."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: JournalLoadArgs,
    ) -> JournalLoadResult:
        """Execute the command's actions."""
        journal, note, writing_task = await generic_loader(
            uow,
            Journal,
            args.ref_id,
            Journal.note,
            Journal.writing_task,
            allow_archived=args.allow_archived,
        )
        return JournalLoadResult(journal=journal, note=note, writing_task=writing_task)
