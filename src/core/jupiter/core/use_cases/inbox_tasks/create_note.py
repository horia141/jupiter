"""The command for creating a note for a inbox task."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.notes.note import Note
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class InboxTaskCreateNoteArgs(UseCaseArgsBase):
    """InboxTaskCreateNote args."""

    ref_id: EntityId


@dataclass
class InboxTaskCreateNoteResult(UseCaseResultBase):
    """InboxTaskCreate result."""

    new_note: Note


class InboxTaskCreateNoteUseCase(
    AppTransactionalLoggedInMutationUseCase[
        InboxTaskCreateNoteArgs, InboxTaskCreateNoteResult
    ],
):
    """The command for creating a inbox task note."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return [WorkspaceFeature.INBOX_TASKS, WorkspaceFeature.NOTES]

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskCreateNoteArgs,
    ) -> InboxTaskCreateNoteResult:
        """Execute the command's action."""
        inbox_task = await uow.inbox_task_repository.load_by_id(args.ref_id)
        note_collection = await uow.note_collection_repository.load_by_parent(
            context.workspace.ref_id
        )

        new_note = Note.new_note_for_inbox_task(
            note_collection_ref_id=note_collection.ref_id,
            inbox_task_name=inbox_task.name,
            inbox_task_ref_id=inbox_task.ref_id,
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )
        new_note = await uow.note_repository.create(new_note)
        await progress_reporter.mark_created(new_note)

        return InboxTaskCreateNoteResult(new_note=new_note)
