"""Use case for loading a particular chore."""
from jupiter.core.domain.concept.chores.chore import Chore
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core.notes.note import Note, NoteRepository
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
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
class ChoreLoadArgs(UseCaseArgsBase):
    """ChoreLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class ChoreLoadResult(UseCaseResultBase):
    """ChoreLoadResult."""

    chore: Chore
    project: Project
    inbox_tasks: list[InboxTask]
    note: Note | None


@readonly_use_case(WorkspaceFeature.CHORES)
class ChoreLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[ChoreLoadArgs, ChoreLoadResult]
):
    """Use case for loading a particular chore."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: ChoreLoadArgs,
    ) -> ChoreLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        chore = await uow.get_for(Chore).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        project = await uow.get_for(Project).load_by_id(chore.project_ref_id)
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            chore_ref_id=[args.ref_id],
        )

        note = await uow.get(NoteRepository).load_optional_for_source(
            NoteDomain.CHORE,
            chore.ref_id,
            allow_archived=args.allow_archived,
        )

        return ChoreLoadResult(
            chore=chore, project=project, inbox_tasks=inbox_tasks, note=note
        )
