"""Use case for loading the current working memory file."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.working_mem.working_mem import (
    WorkingMem,
    WorkingMemRepository,
)
from jupiter.core.domain.concept.working_mem.working_mem_collection import (
    WorkingMemCollection,
)
from jupiter.core.domain.core.notes.note import Note, NoteRepository
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class WorkingMemLoadCurrentArgs(UseCaseArgsBase):
    """Working mem find args."""


@use_case_result
class WorkingMemLoadCurrentEntry(UseCaseResultBase):
    """Working mem load current entry."""

    working_mem: WorkingMem
    note: Note
    cleanup_task: InboxTask


@use_case_result
class WorkingMemLoadCurrentResult(UseCaseResultBase):
    """Working mem load current result."""

    entry: WorkingMemLoadCurrentEntry | None


@readonly_use_case(WorkspaceFeature.WORKING_MEM)
class WorkingMemLoadCurrentUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        WorkingMemLoadCurrentArgs, WorkingMemLoadCurrentResult
    ]
):
    """The command for loading the current working mem."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: WorkingMemLoadCurrentArgs,
    ) -> WorkingMemLoadCurrentResult:
        """Execute the command's action."""
        workspace = context.workspace
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id
        )
        working_mem_collection = await uow.get_for(WorkingMemCollection).load_by_parent(
            workspace.ref_id
        )
        try:
            working_mem = await uow.get(WorkingMemRepository).load_latest_working_mem(
                working_mem_collection.ref_id
            )
        except EntityNotFoundError:
            return WorkingMemLoadCurrentResult(entry=None)
        note = await uow.get(NoteRepository).load_for_source(
            NoteDomain.WORKING_MEM, working_mem.ref_id, allow_archived=True
        )
        clean_up_inbox_tasks = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.WORKING_MEM_CLEANUP,
            source_entity_ref_id=working_mem.ref_id,
        )
        if len(clean_up_inbox_tasks) == 0:
            raise EntityNotFoundError(
                "No cleanup task found for the current working memory."
            )
        return WorkingMemLoadCurrentResult(
            entry=WorkingMemLoadCurrentEntry(
                working_mem=working_mem, note=note, cleanup_task=clean_up_inbox_tasks[0]
            )
        )
