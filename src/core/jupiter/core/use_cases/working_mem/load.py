"""Use case for loading the  working memory file."""
from jupiter.core.domain.core.notes.note import Note, NoteRepository
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.working_mem.working_mem import WorkingMem, WorkingMemRepository
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import EntityNotFoundError
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
class WorkingMemLoadArgs(UseCaseArgsBase):
    """Working mem find args."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class WorkingMemLoadResult(UseCaseResultBase):
    """Working mem load  result."""

    working_mem: WorkingMem
    note: Note
    cleanup_task: InboxTask


@readonly_use_case(WorkspaceFeature.WORKING_MEM)
class WorkingMemLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[WorkingMemLoadArgs, WorkingMemLoadResult]
):
    """The command for loading the  working mem."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: WorkingMemLoadArgs,
    ) -> WorkingMemLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id
        )
        working_mem = await uow.get(WorkingMemRepository).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        note = await uow.get(NoteRepository).load_for_source(
            NoteDomain.WORKING_MEM, working_mem.ref_id, allow_archived=True
        )
        clean_up_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            working_mem_ref_id=[working_mem.ref_id],
            source=[InboxTaskSource.WORKING_MEM_CLEANUP],
        )
        if len(clean_up_inbox_tasks) == 0:
            raise EntityNotFoundError("No cleanup task found for the  working memory.")
        return WorkingMemLoadResult(
            working_mem=working_mem, note=note, cleanup_task=clean_up_inbox_tasks[0]
        )
