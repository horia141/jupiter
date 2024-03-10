"""The command for finding projects."""
from collections import defaultdict
from typing import List, Optional

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import NoFilter
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
class ProjectFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_notes: bool
    filter_ref_ids: Optional[List[EntityId]] = None


@use_case_result
class ProjectFindResultEntry(UseCaseResultBase):
    """A single project result."""

    project: Project
    note: Note | None


@use_case_result
class ProjectFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    entries: list[ProjectFindResultEntry]


@readonly_use_case(WorkspaceFeature.PROJECTS)
class ProjectFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[ProjectFindArgs, ProjectFindResult]
):
    """The command for finding projects."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: ProjectFindArgs,
    ) -> ProjectFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        project_collection = await uow.get_for(ProjectCollection).load_by_parent(
            workspace.ref_id,
        )
        projects = await uow.get_for(Project).find_all_generic(
            parent_ref_id=project_collection.ref_id,
            allow_archived=args.allow_archived,
            ref_id=args.filter_ref_ids or NoFilter(),
        )

        notes_by_project_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id,
            )
            notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.PROJECT,
                allow_archived=True,
                ref_id=[p.ref_id for p in projects],
            )
            for note in notes:
                notes_by_project_ref_id[note.parent_ref_id] = note

        return ProjectFindResult(
            entries=[
                ProjectFindResultEntry(
                    project=project,
                    note=notes_by_project_ref_id.get(project.ref_id, None),
                )
                for project in projects
            ]
        )
