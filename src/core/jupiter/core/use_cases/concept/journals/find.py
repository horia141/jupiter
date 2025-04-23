"""Use case for finding journals."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.journals.journal import Journal
from jupiter.core.domain.concept.journals.journal_collection import JournalCollection
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class JournalFindArgs(UseCaseArgsBase):
    """Args."""

    allow_archived: bool
    include_notes: bool
    include_writing_tasks: bool
    filter_ref_ids: list[EntityId] | None


@use_case_result_part
class JournalFindResultEntry(UseCaseResultBase):
    """Result part."""

    journal: Journal
    note: Note | None
    writing_task: InboxTask | None


@use_case_result
class JournalFindResult(UseCaseResultBase):
    """Result."""

    entries: list[JournalFindResultEntry]


@readonly_use_case(WorkspaceFeature.JOURNALS)
class JournalFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[JournalFindArgs, JournalFindResult]
):
    """The command for finding journals."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: JournalFindArgs,
    ) -> JournalFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        journal_collection = await uow.get_for(JournalCollection).load_by_parent(
            workspace.ref_id,
        )
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        note_collection = await uow.get_for(NoteCollection).load_by_parent(
            workspace.ref_id,
        )
        journals = await uow.get_for(Journal).find_all(
            parent_ref_id=journal_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        notes_by_journal_ref_id = {}
        if args.include_notes:
            notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.JOURNAL,
                allow_archived=True,
                source_entity_ref_id=[journal.ref_id for journal in journals],
            )
            for note in notes:
                notes_by_journal_ref_id[note.source_entity_ref_id] = note

        writing_tasks_by_journal_ref_id = {}
        if args.include_writing_tasks:
            writing_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                source=[InboxTaskSource.JOURNAL],
                allow_archived=args.allow_archived,
                source_entity_ref_id=[journal.ref_id for journal in journals],
            )
            for writing_task in writing_tasks:
                writing_tasks_by_journal_ref_id[writing_task.source_entity_ref_id] = (
                    writing_task
                )

        return JournalFindResult(
            entries=[
                JournalFindResultEntry(
                    journal=journal,
                    note=notes_by_journal_ref_id.get(journal.ref_id, None),
                    writing_task=writing_tasks_by_journal_ref_id.get(
                        journal.ref_id, None
                    ),
                )
                for journal in journals
            ]
        )
