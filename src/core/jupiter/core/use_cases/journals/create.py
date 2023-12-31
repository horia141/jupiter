"""Use case for creating a journal."""
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.journal.journal import Journal
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase, UseCaseResultBase, use_case_args, use_case_result
from jupiter.core.use_cases.infra.use_cases import AppLoggedInMutationUseCaseContext, AppTransactionalLoggedInMutationUseCase, mutation_use_case


@use_case_args
class JournalCreateArgs(UseCaseArgsBase):
    """Args."""

    right_now: ADate
    period: RecurringTaskPeriod


@use_case_result
class JournalCreateResult(UseCaseResultBase):
    """Result."""

    new_journal: Journal
    new_note: Note


@mutation_use_case(WorkspaceFeature.JOURNALS)
class JournalCreateUseCase(AppTransactionalLoggedInMutationUseCase[JournalCreateArgs, JournalCreateResult]):
    """Use case for creating a journal."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: JournalCreateArgs,
    ) -> JournalCreateResult:
        """Execute the command's actions."""
        workspace = context.workspace

        journal_collection = await uow.journal_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        note_collection = await uow.note_collection_repository.load_by_parent(
            workspace.ref_id
        )

        new_journal = Journal.new_journal_for_user(
            context.domain_context,
            journal_collection_ref_id=journal_collection.ref_id,
            right_now=args.right_now,
            period=args.period,
        )
        new_journal = await generic_creator(uow, progress_reporter, new_journal)

        new_note = Note.new_note(context.domain_context, 
                                 note_collection_ref_id=note_collection.ref_id, 
                                 domain=NoteDomain.JOURNAL, 
                                 source_entity_ref_id=new_journal.ref_id,
                                 content=[])
        new_note = await uow.note_repository.create(new_note)

        return JournalCreateResult(
            new_journal=new_journal, new_note=new_note
        )
