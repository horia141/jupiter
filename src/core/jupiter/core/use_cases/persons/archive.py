"""Archive a person."""
from dataclasses import dataclass

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@dataclass
class PersonArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.PERSONS)
class PersonArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[PersonArchiveArgs, None]
):
    """The command for archiving a person."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: PersonArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        person = await uow.person_repository.load_by_id(args.ref_id)

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            filter_sources=[
                InboxTaskSource.PERSON_BIRTHDAY,
                InboxTaskSource.PERSON_BIRTHDAY,
            ],
            filter_person_ref_ids=[person.ref_id],
        )

        inbox_task_archive_service = InboxTaskArchiveService()

        for inbox_task in all_inbox_tasks:
            await inbox_task_archive_service.do_it(
                context.domain_context, uow, progress_reporter, inbox_task
            )

        person = person.mark_archived(context.domain_context)
        await uow.person_repository.save(person)
        await progress_reporter.mark_updated(person)

        note_archive_service = NoteArchiveService()
        await note_archive_service.archive_for_source(
            context.domain_context, uow, NoteDomain.PERSON, person.ref_id
        )
