"""The command for finding a chore."""
from dataclasses import dataclass
from typing import Iterable, Optional, List

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.chores.chore import Chore
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class ChoreFindUseCase(
    AppReadonlyUseCase["ChoreFindUseCase.Args", "ChoreFindUseCase.Result"]
):
    """The command for finding a chore."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        show_archived: bool
        filter_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]

    @dataclass(frozen=True)
    class ResultEntry:
        """A single entry in the load all chores response."""

        chore: Chore
        project: Project
        inbox_tasks: List[InboxTask]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """The result."""

        chores: Iterable["ChoreFindUseCase.ResultEntry"]

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> "Result":
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )
            filter_project_ref_ids: Optional[List[EntityId]]
            if args.filter_project_keys:
                projects = uow.project_repository.find_all_with_filters(
                    parent_ref_id=project_collection.ref_id,
                    filter_keys=args.filter_project_keys,
                )
                filter_project_ref_ids = [p.ref_id for p in projects]
            else:
                projects = uow.project_repository.find_all(
                    parent_ref_id=project_collection.ref_id
                )
                filter_project_ref_ids = None
            project_by_ref_id = {p.ref_id: p for p in projects}

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            chore_collection = uow.chore_collection_repository.load_by_parent(
                workspace.ref_id
            )

            chores = uow.chore_repository.find_all_with_filters(
                parent_ref_id=chore_collection.ref_id,
                allow_archived=args.show_archived,
                filter_ref_ids=args.filter_ref_ids,
                filter_project_ref_ids=filter_project_ref_ids,
            )

            inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_chore_ref_ids=(bp.ref_id for bp in chores),
            )

        return ChoreFindUseCase.Result(
            chores=[
                ChoreFindUseCase.ResultEntry(
                    chore=rt,
                    project=project_by_ref_id[rt.project_ref_id],
                    inbox_tasks=[
                        it for it in inbox_tasks if it.chore_ref_id == rt.ref_id
                    ],
                )
                for rt in chores
            ]
        )
